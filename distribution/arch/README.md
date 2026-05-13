# PKGBUILD / makepkg / AUR / Arch Build Reference

I plan to include more information regarding the AUR here as well at a later date.
For now this should serve as a quick reference/mini-instruction manual.

- `makepkg` in isolation, will create
    - sets-<version>-<pkgver>-x86_64.pkg.tar.zst
    - `v3.0.0.tar.gz`
        - It pulls the source code from this tag (which I had to create ahead of time so as not to compile the older version), though whenever new code is introduced, that code will not be part of the tag unless updated, or a new tag is made. If it is updated, then the SHA256 hash of the tarball will change as well. So you must compute it again with `sha256sum v3.0.0` and replace the old hash with the new one inside the PKGBUILD.
        - Whenever there is a new tag, the PyPi package should be updated as well, by running the one and only workflow that is still useful.
    - `./src`
        - This is the directory it will extract the tarball into. This is effectively a working directory for makepkg, in order to be able to compile/build what it needs to build first, before being able to package it.
    - `./pkg`
        - This too is a working directory; it is what the `.pkg.tar.zst` file contains. Once `src` is built, the relevant files are copied into the `pkg` folder, within which, there a directory structure that mirrors the Linux Filesystem Hierarchy. It will grab what it needs to grab from `src` and possibly other sources, place it in the `pkg` folder in the subdirectory that corresponds to the actual directory where those files will get placed when the package is actually installed through `pacman`


- `makepkg -si` will do the above, but `-i/--install` actually installs the package after it's done constructing it, and `--s/--syncdeps` will also install missing dependencies if there are any (system-wide dependencies that are not managed by us, e.g. `libssl` and the like. This is convention when installing with `-i` to mimic the behavior of `pacman` when installing.


- `pacman -U package.pkg.tar.zst` will install the package and register it with `pacman`, fetching any required dependencies that it can resolve along the way.
    - When in doubt/sanity check, `pacman -Sy` to ensure `pacman`'s  package index is up to date.
