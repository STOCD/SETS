"""
Splash screen helpers.

Progress and status text are updated via a QTimer polling a shared state dict —
no Qt widget is ever touched from a worker thread.

Layout of the splash screen (set up in app.py):
  row 1 — loading image
  row 2 — loading_label: phase text + ETA  e.g. "Downloading Icons (ETA: 12s)"
  row 3 — progress_bar  (optional, hidden until progress is reported)
  row 4 — progress_detail: file counter  e.g. "234 / 3 500"

The progress_bar and progress_detail widgets are optional: if they are not
present on self.widgets the helpers degrade gracefully to text-only updates.
"""

from time import monotonic
from PySide6.QtCore import QTimer


# Shared state written by worker thread (plain Python dict — GIL-safe)
_state = {
    'text': '',
    'current': 0,
    'total': 0,
    'hidden': True,
}

# Timer that polls _state and updates widgets — runs only in MainThread
_timer: QTimer | None = None

# ETA tracking — reset each time total changes
_eta = {
    'start': 0.0,
    'start_current': 0,
    'last_total': 0,
}


def _format_eta(seconds: float) -> str:
    s = int(seconds)
    if s < 60:
        return f'{s}s'
    return f'{s // 60}m {s % 60:02d}s'


def _start_poll_timer(self):
    global _timer
    if _timer is not None:
        return
    _timer = QTimer()
    _timer.setInterval(50)
    _timer.timeout.connect(lambda: _poll(self))
    _timer.start()


def _poll(self):
    """Called every 50 ms in MainThread. Reads _state and updates widgets."""
    text    = _state['text']
    current = _state['current']
    total   = _state['total']
    hidden  = _state['hidden']

    bar    = getattr(self.widgets, 'progress_bar', None)
    detail = getattr(self.widgets, 'progress_detail', None)
    lbl    = self.widgets.loading_label

    if hidden or total <= 0:
        if bar is not None and bar.isVisible():
            bar.hide()
        if detail is not None and detail.isVisible():
            detail.hide()
        if text and lbl.text() != text:
            lbl.setText(text)
        return

    # ── total changed → reset ETA baseline ───────────────────────────────
    if total != _eta['last_total']:
        _eta['start'] = monotonic()
        _eta['start_current'] = current
        _eta['last_total'] = total

    # ── compute ETA ───────────────────────────────────────────────────────
    eta_str = ''
    done = current - _eta['start_current']
    remaining = total - current
    elapsed = monotonic() - _eta['start']
    if done > 0 and remaining > 0:
        rate = done / elapsed
        eta_str = f' (ETA: {_format_eta(remaining / rate)})'

    label_text = f'{text}{eta_str}'
    if lbl.text() != label_text:
        lbl.setText(label_text)

    if bar is not None:
        bar.setRange(0, total)
        bar.setValue(current)
        if not bar.isVisible():
            bar.show()

    if detail is not None:
        detail_text = f'{current:,} / {total:,}'
        if detail.text() != detail_text:
            detail.setText(detail_text)
        if not detail.isVisible():
            detail.show()


# ── public API (MainThread) ───────────────────────────────────────────────────

def enter_splash(self):
    """Shows splash screen."""
    _state['text'] = 'Loading...'
    _state['hidden'] = True
    _state['total'] = 0
    _eta['last_total'] = 0

    self.widgets.loading_label.setText('Loading...')
    bar = getattr(self.widgets, 'progress_bar', None)
    if bar is not None:
        bar.hide()
    detail = getattr(self.widgets, 'progress_detail', None)
    if detail is not None:
        detail.hide()

    self.widgets.splash_tabber.setCurrentIndex(1)
    _start_poll_timer(self)


def exit_splash(self):
    """Leaves splash screen."""
    global _timer
    if _timer is not None:
        _timer.stop()
        _timer = None

    bar = getattr(self.widgets, 'progress_bar', None)
    if bar is not None:
        bar.hide()
    detail = getattr(self.widgets, 'progress_detail', None)
    if detail is not None:
        detail.hide()

    self.widgets.splash_tabber.setCurrentIndex(0)


# ── called from worker thread (write to _state only — no Qt calls) ───────────

def splash_text(self, new_text: str):
    """Update status text. Safe to call from any thread."""
    _state['text'] = new_text


def splash_progress(self, current: int, total: int):
    """
    Update progress bar state. Safe to call from any thread.
    Call with total=0 to hide the bar.
    """
    if total <= 0:
        _state['hidden'] = True
        _state['total'] = 0
        _state['current'] = 0
    else:
        _state['hidden'] = False
        _state['total'] = total
        _state['current'] = current
