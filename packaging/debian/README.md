# Debian packaging for Pulsar

Hand-rolled `.deb` packaging — no debhelper, no fakeroot, so it runs in a
minimal container.

## Build command

```sh
cd /workspace/projects/pulsar && ./packaging/debian/build.sh
```

Output: `build/deb/pulsar_0.1.0_all.deb`

## Install / verify

```sh
dpkg -i build/deb/pulsar_0.1.0_all.deb
pulsar                      # launcher
desktop-file-validate /usr/share/applications/pulsar.desktop
```

## What lands where

| Path | Contents |
|---|---|
| `/usr/bin/pulsar` | launcher: `exec python3 /usr/share/pulsar/src/main.py "$@"` |
| `/usr/share/pulsar/src/` | application code, incl. `utils/presets/builtin_profiles.json` |
| `/usr/share/applications/pulsar.desktop` | repo template with `Exec=` substituted |
| `/usr/share/doc/pulsar/` | `copyright` (MIT), `README.md`, `packaging-debian.md` |

## User data policy

Pulsar keeps user-created presets in `$XDG_DATA_HOME/pulsar`
(default `~/.local/share/pulsar`). That directory is **not** shipped in the
`.deb`, is **not** listed in `conffiles`, and the `postrm` script removes
only `/usr` paths — `rm -f /usr/bin/pulsar`, `rm -f
/usr/share/applications/pulsar.desktop`, and `rmdir` of the empty
`/usr/share/pulsar*` directories. Uninstalling or purging never deletes a
user's profiles.

## Notes / pitfalls

- **Control fields must be one per line.** A wrapped
  `Depends:\n python3, python3-tk` makes `dpkg-deb` fail with
  "missing package name, or garbage". `build.sh` asserts this.
- `dpkg-deb --root-owner-group` replaces `fakeroot` on this image
  (`fakeroot` exists here but is not needed).
- `pulsar.desktop` at the repo root is a **template** containing
  `Exec=PLACEHOLDER_EXEC_PATH`; `build.sh` fails hard if that placeholder
  survives substitution.
- The repo-root `pulsar` launcher `cd`s relative to itself, so a symlinked
  `/usr/bin/pulsar` would break. The package ships an absolute-path
  wrapper instead.