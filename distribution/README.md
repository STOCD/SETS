# Development Notes

These are currently reflecting the state of the app, but are subject ot change.

## Windows
- [Currently Testing With Inno Setup](https://jrsoftware.org/isinfo.php)
  - [SETS.iss](./SETS.iss)

## Linux

#### System Wide Paths
- /opt/sets/
  - This is the ideal loation for Linux, all assets are located here.
- /usr/bin/sets -> /opt/sets/SETS
  - shell script to execute the binary from a PATH location
- /usr/share/applications/sets.desktop
  - The `.desktop` entry that registers the application.
- /usr/share/icons/hicolor/256x256/apps/sets.png
  - Location for the application icon, referred to in the `.desktop` entry.

#### Config Paths
1. If `$XDG_CONFIG_HOME` is set, takes priority. Is supposed to be a directory. Don't use if it is a file. Don't create it if it doesn't exist.
2. `$HOME/.config` if the `.config` folder exists, but do not create it if it does not.
3. [`$HOME/.<filename>` if you can keep the settings in one file (and the dot here is important)] -> not used, because SETS requires a folder
4. ` $HOME/.sets/<config-files>`

##### .desktop entry template
```
[Desktop Entry]
Type=Application
Name=SETS
Comment=STO Equipment and Trait Selector
Icon=/usr/share/icons/hicolor/256x256/apps/sets.png
Exec=/opt/sets/SETS
Terminal=False
Categories=Utility;GameTool;
StartupWMClass=STO Equipment and Trait Selector
```

#### Debian `.deb` Package Approach

```bash
apt install -f ./sets-<version>-<pkgver>-x86_64.deb
```
- Unpacks the contents to `/opt/sets`, `/usr/share/applications/sets.desktop`, etc
- Automatically registers the package manager metadata with `dpkg` so the system becomes aware which files belong to which package
  - This is the biggest advantage.
- Allows uninstallation by name (apt remove sets), because it recorded which files it put there.
  - Does not remove settings.
- uses `-f` flag to install dependencies

To check whether it was installed correctly: `apt list --installed sets`

Use `dpkg -L sets` to list registered files for SETS.


#### Arch `PKGBUILD` File Structure
###### Note: to public to AUR we need a PKGBUILD that builds from source

On Arch there is similar tools, but there is no standard format like `.deb`, rather it's usually just a compressed archive `sets.pkg.tar.zst` by a `PKGBUILD` script, which can then be fed into `pacman`/`paru`/`yay`.

Run `makepkg` from the directory that contains the `PKGBUILD` file and that spits out the `sets-<version>-<pkgver>-x86_64.pkg.tar.zst` file, which can then be installed via pacman: 

```
sudo pacman -U ./sets-<version>-<pkgver>-x86_64.pkg.tar.zst
```

And `pacman -Qs sets` to confirm that it is registered, just as a sanity check.

For debugging `pacman -Ql sets` lists where everything registers under that package is located (the assets and `.desktop` files, to ensure the `PKGBUILD` file was defined properly)

