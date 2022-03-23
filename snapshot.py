import sys, platform, csv
try:
    import tkinter as tk
except:
    pass

python_version = sys.version
python_version = python_version.replace('\r', '')
python_version = python_version.replace('\n', '')
system = platform.system()
release = platform.release()
try:
    build = sys.getwindowsversion().build
except:
    build = ''
if system == 'Windows' and release == 10 and build >= 22000:
    release = 11

try:
    tkinter_version = tk.Tcl().call("info", "patchlevel")
except:
    tkinter_version = 'fail'

try:
    root = tk.Tk()
    tk_screen_geometry = '{}x{}'.format(root.winfo_screenwidth(), root.winfo_screenheight())
    dpi = round(root.winfo_fpixels('1i'), 0)
    factor = (dpi / 96)
except:
    tk_screen_geometry = 'fail'
    dpi = ''
    factor = ''

try:
    with open('/etc/os-release') as f:
        os_release = csv.reader(f, delimiter='=')
        distribution = '{} {}'.format(os_release['NAME'], os_release['VERSION'])
except:
    distribution = ''

reported = dict()

snapshot = {
    'python': python_version,
    'tkinter': tkinter_version,
    'OS': '{} {} {}'.format(system, release, build),
    'dist': '{}'.format(distribution),
    'win-geometry': '{} ({}dpi x{})'.format(tk_screen_geometry, dpi, factor),
}

for type in snapshot:
    if not type in reported:
        print('{:>15}: {}'.format(type, snapshot[type]))

