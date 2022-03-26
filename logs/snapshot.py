import sys, platform, subprocess, glob, re
python_version = sys.version
python_version = python_version.replace('\r', '')
python_version = python_version.replace('\n', '')
system = platform.system()
release = platform.release()

try:
    build = sys.getwindowsversion().build
    if system == 'Windows' and release == 10 and build >= 22000:
        release = 11
except:
    build = ''

try:
    import tkinter as tk
    tkinter_version = tk.Tcl().call("info", "patchlevel")
    root = tk.Tk()
    tk_screen_geometry = '{}x{}'.format(root.winfo_screenwidth(), root.winfo_screenheight())
    dpi = round(root.winfo_fpixels('1i'), 0)
    factor = (dpi / 96)
except:
    tkinter_version = 'fail'
    tk_screen_geometry = 'fail'
    dpi = ''
    factor = ''

try:
    import csv
    release_data = dict()
    with open('/etc/os-release') as f:
        os_release = csv.reader(f, delimiter='=')
        for row in os_release:
            release_data[row[0]] = row[1]
        distribution = '{} {}'.format(release_data['NAME'], release_data['VERSION'])
except:
    distribution = ''

os_text = '{} {}'.format(system, release)
if build:
    os_text += ' ({})'.format(build)
if distribution:
    os_text += ' ({})'.format(distribution)

try:
    import PIL
    PIL_version = PIL.__version__
except:
    PIL_version = 'fail'

try:
    PIL_location = PIL.__path__
    imaging_location = glob.glob(PIL_location[0]+'/_imaging.*so')[0]
    if system == 'Darwin':
        PIL_libs = subprocess.check_output(['otool', '-L', imaging_location]).decode("utf-8")
    else:  # Linux -- no windows method yet
        PIL_libs = subprocess.check_output(['ldd', imaging_location]).decode("utf-8")
except:
    PIL_libs = ''

PIL_libs_cleaned = ''
if PIL_libs:
    PIL_lib_lines = PIL_libs.splitlines(True)
    for i in range(len(PIL_lib_lines)):
        #PIL_libs_cleaned += PIL_lib_lines[i]+'\n'
        PIL_libs_cleaned += re.sub(' (=>|\(0x).*$', '', PIL_lib_lines[i])

try:
    import numpy
    numpy_version = numpy.__version__
except:
    numpy_version = 'fail'

try:
    import tkmacosx
    tkmacosx_version = tkmacosx.__version__
except:
    tkmacosx_version = ''

snapshot = {
    'python': python_version,
    'OS': os_text,
    'screen-dpi': '{} ({}dpi x{})'.format(tk_screen_geometry, dpi, factor),
}

modules= {
    'tkinter': tkinter_version,
    'Pillow': PIL_version,
    'numpy': numpy_version,
    'tkLocal': tkmacosx_version,
}

min_title_width = 12
for type in snapshot:
    if len(type) > min_title_width:
        min_title_width = len(type)

for type in snapshot:
    print('{:>{min}}: {}'.format(type, snapshot[type], min=min_title_width+1))

modules_text = '{:>{min}}: '.format('modules', min=min_title_width+1)

for type in modules:
    if modules[type]:
        modules_text += '({} {}) '.format(type, modules[type])

print(modules_text)
if PIL_libs_cleaned:
    print('{:>{min}}:'.format('Pillow-libs', min=min_title_width+1))
    print(PIL_libs_cleaned)
    # print(PIL_libs)

