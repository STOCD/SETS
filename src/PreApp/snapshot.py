import glob
import platform
import re
import subprocess
import sys

python_version = sys.version
python_version = python_version.replace('\r', '')
python_version = python_version.replace('\n', '')
system = platform.system()
release = platform.release()

try:
    build = sys.getwindowsversion().build
    if system == 'Windows' and release == '10' and build >= 22000:
        release = '11'
except:
    build = ''

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

try:
    import tkinter as tk
    tkinter_version = tk.Tcl().call("info", "patchlevel")
except:
    tkinter_version = 'fail'
    tk_screen_geometry = 'fail'
    dpi = ''
    factor = ''


def print_screeninfo(tkobject=None):
    """ prints screen information using the provided or generic tk window """

    min_title_width = 12
    if tkinter_version != 'fail':
        if tkobject is None:
            tkobject = tk.Tk()
        tk_screen_geometry = '{}x{}'.format(tkobject.winfo_screenwidth(), tkobject.winfo_screenheight())
        dpi = round(tkobject.winfo_fpixels('1i'), 0)
        factor = (dpi / 96)

    snapshot = {
        'screen-dpi': '{} ({}dpi x{})'.format(tk_screen_geometry, dpi, factor),
    }

    for type in snapshot:
        if len(type) > min_title_width:
            min_title_width = len(type)

    for type in snapshot:
        print('{:>{min}}: {}'.format(type, snapshot[type], min=min_title_width+1))


def print_summary():
    """ prints system, python, package version information """

    min_title_width = 12
    os_text = '{} {}'.format(system, release)
    if build:
        os_text += ' ({})'.format(build)
    if distribution:
        os_text += ' ({})'.format(distribution)

    snapshot = {
        'python': python_version,
        'OS': os_text,
        # 'screen-dpi': '{} ({}dpi x{})'.format(tk_screen_geometry, dpi, factor),
    }

    modules = {
        'tkinter': tkinter_version,
        'Pillow': PIL_version,
        'numpy': numpy_version,
        'tkLocal': tkmacosx_version,
    }

    pil_libs_cleaned = ''
    if PIL_libs:
        pil_lib_lines = PIL_libs.splitlines(True)
        for i in range(len(pil_lib_lines)):
            # pil_libs_cleaned += pil_lib_lines[i]+'\n'
            pil_libs_cleaned += re.sub(' (=>|\(0x).*$', '', pil_lib_lines[i])

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
    if pil_libs_cleaned:
        print('{:>{min}}:'.format('Pillow-libs', min=min_title_width+1))
        print(pil_libs_cleaned)
        # print(PIL_libs)


def __init__() -> None:
    """Main setup function"""
    print_summary()


if __name__ == "__main__":
    print_summary()
    print_screeninfo()
