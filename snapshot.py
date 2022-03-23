import sys, platform
try:
    import tkinter as tk
except:
    pass

python_version = sys.version
system = platform.system()
release = platform.release()
if system == 'Windows' and release == 10 and sys.getwindowsversion().build >= 22000:
    release = 11

try:
    tkinter_version = tkinter.Tcl().call("info", "patchlevel")
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

snapshot = {
    'python-version': python_version,
    'system': system,
    'release': release,
    'tkinter-version': tkinter_version,
    'win-geometry': tk_screen_geometry,
    'dpi': dpi,
    'factor': factor,
}

for type in snapshot:
    print('{:>20}: {:>10}'.format(type, snapshot[type]))