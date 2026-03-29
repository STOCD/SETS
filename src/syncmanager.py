"""
SyncManager — detects and downloads changed/new assets from GitHub.

Uses GitHub Tree API (SHA1 + size) to find changed/missing files,
then downloads only what's needed using a bounded thread pool.

Download discipline:
  - Max 5 concurrent threads (numbered T-1..T-5)
  - 404 = permanent failure, no retry
  - 403 = Cloudflare/Forbidden; after 3 occurrences the source is
    disabled for the remainder of the session (circuit breaker)
  - Other errors retried up to MAX_RETRIES times with RETRY_DELAY_S pause
  - Stall timeout: STALL_TIMEOUT_S seconds of no data = abort attempt

Logging:
  - Terminal (stderr): one progress bar line per group, overwritten with \\r
  - Python logging: final result per file (OK / FAILED), never per-attempt noise
  - Log prefix: always includes asset group name for easy filtering

Asset groups (GitHub-backed, synced by SyncManager.run()):
  1. Item Icons    — images/
  2. Ship Images   — ship_images/
  3. Cargo Data    — cargo/

Wiki-only groups (no GitHub mirror, use Downloader directly):
  4. Boff Abilities — wiki suffix _icon_(Federation).png
  5. Skill Icons    — wiki suffix .png
"""

from __future__ import annotations

import hashlib
import logging
import queue
import sys
import time
from pathlib import Path
from threading import Lock, Thread
from typing import Callable
from urllib.parse import quote, unquote_plus

from .constants import GITHUB_CACHE_URL, WIKI_IMAGE_URL

_log = logging.getLogger(__name__)

GITHUB_API_TREE     = 'https://api.github.com/repos/STOCD/SETS-Data/git/trees/main?recursive=1'
GITHUB_RAW_BASE     = GITHUB_CACHE_URL  # raw.githubusercontent.com/STOCD/SETS-Data/main
TREE_CACHE_FILENAME = 'github_tree_cache.json'
TREE_CACHE_MAX_AGE  = 60 * 60   # 1 hour

MAX_RETRIES     = 1
RETRY_DELAY_S   = 3
STALL_TIMEOUT_S = 10
MAX_THREADS     = 5
MAX_FORBIDDEN   = 3   # Disable source after 3 x 403 errors

BAR_WIDTH = 20   # characters for the progress bar fill

ASSET_GROUPS = [
    ('Item Icons',  'images/',      'icon'),
    ('Ship Images', 'ship_images/', 'ship'),
    ('Cargo Data',  'cargo/',       'cargo'),
]


# ---------------------------------------------------------------------------
# Terminal progress bar
# ---------------------------------------------------------------------------

class _TermProgress:
    """
    Renders a single overwritten line on stderr for one asset group.
    Thread-safe: update() may be called from any thread.
    """

    def __init__(self, label: str, total: int):
        self._label   = f'[{label:<13}]'
        self._total   = max(total, 1)
        self._lock    = Lock()

    def _bar(self, done: int) -> str:
        filled = int(BAR_WIDTH * done / self._total)
        return '█' * filled + '░' * (BAR_WIDTH - filled)

    def _render(self, current: int, suffix: str) -> str:
        line = f'{self._label}  {self._bar(current)}  {current}/{self._total}  {suffix}'
        try:
            width = max(40, __import__('shutil').get_terminal_size().columns - 1)
        except Exception:
            width = 119
        line = line[:width].ljust(width)
        return '\r' + line

    def start(self):
        sys.stderr.write(self._render(0, 'starting…'))
        sys.stderr.flush()

    def update(self, current: int, filename: str = ''):
        short = (filename[:40] + '…') if len(filename) > 41 else filename
        sys.stderr.write(self._render(current, short))
        sys.stderr.flush()

    def finish(self, summary: str):
        sys.stderr.write(self._render(self._total, summary) + '\n')
        sys.stderr.flush()


# ---------------------------------------------------------------------------
# SHA helpers
# ---------------------------------------------------------------------------

def _git_sha1(filepath: Path) -> str | None:
    try:
        data = filepath.read_bytes()
        header = f'blob {len(data)}\0'.encode()
        return hashlib.sha1(header + data).hexdigest()
    except OSError:
        return None


# ---------------------------------------------------------------------------
# GitHub tree fetch / cache
# ---------------------------------------------------------------------------

def _fetch_github_tree(session) -> list[dict] | None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.get(GITHUB_API_TREE, timeout=(10, STALL_TIMEOUT_S))
            if resp.ok:
                blobs = [e for e in resp.json().get('tree', []) if e['type'] == 'blob']
                _log.info(f'SyncManager: tree fetched — {len(blobs)} files')
                return blobs
            if resp.status_code == 404:
                _log.warning('SyncManager: tree 404 — repo not found?')
                return None
            error = f'HTTP {resp.status_code}'
        except Exception as e:
            error = str(e)
        _log.warning(f'SyncManager: tree attempt {attempt}/{MAX_RETRIES} — {error}')
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY_S)
    return None


def _load_tree_cache(cache_path: Path) -> list[dict] | None:
    import json
    if not cache_path.exists():
        return None
    age = time.time() - cache_path.stat().st_mtime
    if age > TREE_CACHE_MAX_AGE:
        _log.info(f'SyncManager: tree cache {age/60:.0f}min old — refreshing')
        return None
    try:
        data = json.loads(cache_path.read_text(encoding='utf-8'))
        _log.info(f'SyncManager: tree cache hit ({age/60:.0f}min old, {len(data)} files)')
        return data
    except Exception:
        return None


def _save_tree_cache(cache_path: Path, tree: list[dict]):
    import json
    try:
        cache_path.write_text(json.dumps(tree), encoding='utf-8')
    except Exception as e:
        _log.warning(f'SyncManager: could not save tree cache: {e}')


# ---------------------------------------------------------------------------
# SyncManager
# ---------------------------------------------------------------------------

class SyncManager:

    def __init__(self, images_dir, ship_images_dir, cargo_dir, cache_dir, downloader):
        self._images_dir       = Path(images_dir)
        self._ship_images_dir  = Path(ship_images_dir)
        self._cargo_dir        = Path(cargo_dir)
        self._tree_cache_path  = Path(cache_dir) / TREE_CACHE_FILENAME
        self._session          = downloader._session

        # Circuit breaker state
        self._github_blocked   = False
        self._github_403_count = 0
        self._wiki_blocked     = False
        self._wiki_403_count   = 0
        self._cb_lock          = Lock()

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def run(self, on_progress: Callable[[str, int, int], None] | None = None) -> dict:
        """
        Sync all GitHub-backed asset groups. Returns summary dict.

        on_progress(label, current, total) is called with progress updates
        and can be used to update a splash screen or progress bar.
        """
        prog = on_progress or (lambda t, c, n: None)
        prog('Checking for updates…', 0, 0)

        tree = _load_tree_cache(self._tree_cache_path)
        if tree is None:
            prog('Fetching update manifest…', 0, 0)
            tree = _fetch_github_tree(self._session)
            if tree is None:
                _log.warning('SyncManager: cannot reach GitHub — skipping sync')
                prog('Update check failed (offline?)', 0, 0)
                return {'checked': 0, 'updated': 0, 'failed': 0, 'cargo_updated': False}
            _save_tree_cache(self._tree_cache_path, tree)

        total_updated     = 0
        total_failed      = 0
        cargo_was_updated = False

        for (label, prefix, type_tag) in ASSET_GROUPS:
            entries   = [e for e in tree if e['path'].startswith(prefix)]
            to_update = self._diff_group(entries, type_tag)
            count     = len(to_update)

            _log.info(f'SyncManager [{label}]: {count}/{len(entries)} need download')

            if count == 0:
                prog(f'{label}: up to date', 0, 0)
                sys.stderr.write(
                    f'\r[{label:<13}]  {"█" * BAR_WIDTH}  {len(entries)}/{len(entries)}'
                    f'  up to date\n')
                sys.stderr.flush()
                continue

            tprog = _TermProgress(label, count)
            tprog.start()
            prog(f'{label}', 0, count)

            job_q    = queue.Queue()
            for item in to_update:
                job_q.put(item)

            counter  = [0]
            n_failed = [0]
            lock     = Lock()

            def _worker(thread_num: int, _label=label, _count=count, _type=type_tag):
                while True:
                    try:
                        entry, local_path = job_q.get_nowait()
                    except queue.Empty:
                        return

                    fname = entry['path'].split('/', 1)[1]
                    ok, source, attempts, failed_url = self._download_with_result(
                        entry, local_path, _type)

                    with lock:
                        counter[0] += 1
                        if not ok:
                            n_failed[0] += 1
                        c = counter[0]

                    attempt_word = f'{attempts} attempt{"s" if attempts > 1 else ""}'
                    if ok:
                        _log.info(
                            f'SyncManager [{_label}] T-{thread_num}: '
                            f'OK {source} ({attempt_word}) — {fname}')
                    else:
                        _log.warning(
                            f'SyncManager [{_label}] T-{thread_num}: '
                            f'FAILED ({attempt_word}) — {fname} (URL: {failed_url or "unknown"})')

                    tprog.update(c, f'T-{thread_num}: {fname}')
                    prog(f'{_label}', c, _count)
                    job_q.task_done()

            n_threads = min(MAX_THREADS, count)
            threads   = [
                Thread(target=_worker, args=(i + 1,), name=f'sync-T{i+1}')
                for i in range(n_threads)
            ]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            updated = counter[0] - n_failed[0]
            total_updated += updated
            total_failed  += n_failed[0]
            if type_tag == 'cargo' and updated > 0:
                cargo_was_updated = True

            summary = f'{updated} updated'
            if n_failed[0]:
                summary += f', {n_failed[0]} FAILED'
            _log.info(f'SyncManager [{label}]: done — {summary}')
            tprog.finish(summary)
            prog(f'{label}: {summary}', count, count)

        report = {
            'checked':       len(tree),
            'updated':       total_updated,
            'failed':        total_failed,
            'cargo_updated': cargo_was_updated,
        }
        _log.info(f'SyncManager: complete — {report}')

        if total_updated == 0 and total_failed == 0:
            prog('All assets up to date', 0, 0)
        else:
            prog(f'Sync done: {total_updated} updated, {total_failed} failed', 0, 0)

        return report

    def download_one(self, name: str, type_tag: str) -> bool:
        """
        Download a single asset on-demand (e.g. ship image clicked in UI).
        type_tag: 'ship' | 'icon'
        Returns True on success.
        """
        if type_tag == 'ship':
            filename   = quote(name)
            entry      = {'path': f'ship_images/{filename}', 'sha': '', 'size': -1}
            local_path = self._ship_images_dir / filename
        else:
            filename   = quote(name) + '.png'
            entry      = {'path': f'images/{filename}', 'sha': '', 'size': -1}
            local_path = self._images_dir / filename

        ok, source, _, failed_url = self._download_with_result(entry, local_path, type_tag)
        if ok:
            _log.debug(f'SyncManager.download_one: OK ({source}) — {name!r}')
        else:
            _log.warning(f'SyncManager.download_one: FAILED — {name!r} (URL: {failed_url or "unknown"})')
        return ok

    # -----------------------------------------------------------------------
    # Diff
    # -----------------------------------------------------------------------

    def _diff_group(self, entries, type_tag) -> list[tuple]:
        return [
            (entry, lp)
            for entry in entries
            if (lp := self._local_path(entry['path'], type_tag)) and self._needs_update(lp, entry)
        ]

    def _local_path(self, github_path: str, type_tag: str) -> Path | None:
        filename = github_path.split('/', 1)[1]
        if type_tag == 'icon':  return self._images_dir      / filename
        if type_tag == 'ship':  return self._ship_images_dir / filename
        if type_tag == 'cargo': return self._cargo_dir       / filename
        return None

    def _needs_update(self, local_path: Path, entry: dict) -> bool:
        if not local_path.exists():
            return True
        if entry.get('size', -1) >= 0 and local_path.stat().st_size != entry['size']:
            return True
        return _git_sha1(local_path) != entry['sha']

    # -----------------------------------------------------------------------
    # Download
    # -----------------------------------------------------------------------

    def _download_with_result(
            self, entry: dict, local_path: Path,
            type_tag: str) -> tuple[bool, str, int, str | None]:
        """Returns (success, source_label, total_attempts, failed_url)."""

        encoded_path = quote(entry['path'])
        url = f'{GITHUB_RAW_BASE}/{encoded_path}'

        if not self._github_blocked:
            data, attempts, status = self._fetch(url, min_size=10)
            if data is not None:
                local_path.parent.mkdir(parents=True, exist_ok=True)
                local_path.write_bytes(data)
                return True, 'github', attempts, None

            if status == 403:
                with self._cb_lock:
                    self._github_403_count += 1
                    if self._github_403_count >= MAX_FORBIDDEN and not self._github_blocked:
                        self._github_blocked = True
                        _log.error('SyncManager: GitHub access BLOCKED after repeated 403 errors.')
        else:
            attempts = 0

        # Wiki fallback for ship images only
        if type_tag == 'ship' and not self._wiki_blocked:
            filename = entry['path'].split('/', 1)[1]
            name     = unquote_plus(unquote_plus(filename))
            wiki_url = WIKI_IMAGE_URL + quote(name.replace(' ', '_'), safe='._-')
            wdata, wa, wstatus = self._fetch(wiki_url, min_size=100)
            total = attempts + wa
            if wdata is not None:
                local_path.parent.mkdir(parents=True, exist_ok=True)
                local_path.write_bytes(wdata)
                return True, 'wiki', total, None

            if wstatus == 403:
                with self._cb_lock:
                    self._wiki_403_count += 1
                    if self._wiki_403_count >= MAX_FORBIDDEN and not self._wiki_blocked:
                        self._wiki_blocked = True
                        _log.error('SyncManager: STOWiki access BLOCKED after repeated 403 errors.')

            return False, 'all', total, wiki_url

        return False, 'github', attempts, url

    def _fetch(self, url: str, min_size: int = 10) -> tuple[bytes | None, int, int | None]:
        """
        Fetch with retry. 404 = instant permanent failure.
        Returns (data_or_None, attempts_made, last_status_code).
        """
        last_status = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = self._session.get(url, timeout=(10, STALL_TIMEOUT_S), stream=False)
                last_status = resp.status_code
                if resp.ok and len(resp.content) >= min_size:
                    return resp.content, attempt, last_status
                if resp.status_code == 404:
                    return None, attempt, 404
                error = f'HTTP {resp.status_code}'
            except Exception as e:
                error = str(e)
                last_status = None
            _log.warning(f'SyncManager: attempt {attempt}/{MAX_RETRIES} — {url} → {error}')
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_S)
        return None, MAX_RETRIES, last_status