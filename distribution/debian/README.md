# debian-package / dpkg Build Reference

## Build Preperation
Before building, make sure to complete the following steps:
- Update the app version in `DEBIAN/control`.
- Add an entry to the changelog file `changelog`.

## Building
To build and package the app for debian-based distros using docker, run 
`docker compose -f distribution/debian/build_deb.compose.yaml up` from the base directory of the
project. This will create the .deb package and put it into the `dist/` folder.

To build and package the app for debian-based distros while running a debian-based machine:
- From the base directory of the project, run `distribution/build_pyinstaller.sh` to build the
binary.
- From the base directory of the project, run `distribution/debian/package_deb.sh` to package the
app. The result will be located in  the `dist/` folder.

To build and package the app for debian-based distros using docker:
- From the base directory of the project, run
`docker compose -f distribution/debian/build_deb.compose.yaml up -d`. The result will be in the
`dist/` folder.

## File reference
*All files relative to the `distribution/debian` folder.* 
- `DEBIAN/control`: Defines the debian package and tells dpkg what to do. Will be included as is in
the package.
- `copyright`: Contains copyright information for the project. Required by dpkg and will be included
as is in the package.
- `changelog`: Contains changelog information for the project. Required by dpkg and will be included
as is in the package.
