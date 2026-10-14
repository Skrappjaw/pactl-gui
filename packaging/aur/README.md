# Pulsar — AUR packaging

Arch Linux packaging for [Pulsar](https://github.com/skomesh/pulsar), a Tkinter +
`pactl` GUI audio routing manager (fork of pactl-gui).

## Files

| File | Purpose |
|---|---|
| `PKGBUILD` | The build recipe |
| `pulsar.install` | `update-desktop-database` hooks for install/upgrade/remove |
| `.SRCINFO` | Generated metadata — regenerate with `makepkg --printsrcinfo > .SRCINFO` |

## Install

```bash
# From this directory (a clone):
makepkg -si

# Or from the AUR, once published:
yay -S pulsar
```

Useful variants:

```bash
makepkg -s            # resolve missing deps with pacman
makepkg --printsrcinfo > .SRCINFO   # regenerate .SRCINFO after edits
makepkg -e _run_tests=1             # also run upstream's pytest suite (needs pytest)
```

## What gets installed

```
/usr/bin/pulsar                                  # python3 wrapper (pyproject: pulsar = main:main)
/usr/lib/pulsar/main.py                          # entry module
/usr/lib/pulsar/{ui,utils,config}/               # importable packages
/usr/lib/pulsar/utils/presets/builtin_profiles.json
/usr/share/applications/pulsar.desktop          # Exec=/usr/bin/pulsar
/usr/share/licenses/pulsar/LICENSE               # MIT
```

The importable tree is installed to `/usr/lib/pulsar` **unmodified** rather than
built as a wheel. `src/config/paths.py` resolves the bundled presets as
`<parents-of-config>/utils/presets`, and `src/main.py` appends its own directory
to `sys.path`, so this layout makes `builtin_presets_path()` find
`builtin_profiles.json` with no source patching.

## Dependencies, and what each one actually provides

| Package | Provides | Why it's needed |
|---|---|---|
| `python` | `python3` interpreter | The app runs on Python >= 3.6 |
| `tk` | Tcl/Tk 8.6 runtime, `libtk8.6.so` | `_tkinter` links against it; every GUI module imports `tkinter` |
| `libpulse` | **`/usr/bin/pactl`** | `main.py` hard-exits if `pactl` is missing; `utils/pactl_runner.py` is the app's core |
| `pipewire` | `/usr/bin/pw-dump` | `utils/pw_diagnostics.py`, `utils/pw_app_capture.py` |
| `pipewire-audio` | `/usr/bin/pw-record` | Loopback audio capture in `utils/pw_app_capture.py` |
| `glib2` | `/usr/bin/gdbus` | `org.freedesktop.PolicyKit1` calls in `pw_app_capture.py` |

These were confirmed by reading the source: the app imports **only the Python
standard library** (`json`, `os`, `subprocess`, `tkinter`, …), so there are no
pip dependencies to install, and the only external binaries it shells out to are
`pactl`, `pw-dump`, `pw-record`, and `gdbus`.

> **`pulseaudio-utils` does not exist on Arch.** Upstream's own docs and
> `src/main.py` error message tell Debian/Fedora users to install it. On Arch,
> `pactl` ships inside **`libpulse`**. Do not add it to `depends`.

`optdepends` adds `libnotify` (desktop notifications) and `polkit` (privilege
escalation prompts) — both optional.

## The no-tag tradeoff — read this before submitting to the AUR

**Upstream has no release tags.** Verified: `git tag -l` in the repository
returns nothing. There is no `v0.1.0` release tarball to point at, and
inventing one would 404.

So this PKGBUILD pins an **exact commit** rather than tracking a version:

```bash
_srccommit='ade1bb9dc0e65094e74886ea94e25ab5b342750d'   # branch fix/wheel-missing-presets-and-entrypoint
source=("https://codeload.github.com/skomesh/pulsar/tar.gz/$_srccommit")
sha256sums=('c2e3ee867d491f5df1faac2aeb3f2bf81c0a38891a5b5af95da4b87cbe61f7f9')
```

This is deliberately **not** `sha256sums=('SKIP')`. `SKIP` is discouraged in the
AUR because it means the build is unpinned and unreviewable-by-checksum. A
commit-pinned tarball with a real checksum is reproducible and reviewable.

The tradeoff you are accepting:

- **Pro:** exact, verifiable, reproducible builds. A reviewer can confirm you
  built the code you claim.
- **Con:** `pkgver=0.1.0` is a manual label that upstream does not control.
  Bumping it is a manual maintainer action, and AUR users will not receive
  updates automatically — there is no upstream tag to track.

**Recommendation:** this packaging is correct and buildable today, but a real AUR
submission should wait for, or be accompanied by, an upstream release tag.
When upstream tags one, switch to:

```bash
_pkgver=0.1.0
source=("https://github.com/skomesh/pulsar/archive/v$_pkgver.tar.gz")
sha256sums=('<real checksum>')
```

and drop `_srccommit` and the `_topdir()` workaround (a `v`-tagged archive has a
predictable top-level directory name).

## What was validated — and what was not

This was built and checked in a **Debian 13 container** using pacman 7.0.0 and
makepkg 7.0.0, not on Arch.

**Actually validated (real command output):**

- `bash -n PKGBUILD` — syntax OK
- `shellcheck -S warning PKGBUILD pulsar.install` — **clean, zero warnings**
- `makepkg --printsrcinfo` — succeeds; produces correct `.SRCINFO` (all six
  `depends` present, no `SKIP`)
- `makepkg -f --noconfirm --nodeps --skippgpcheck` — **full build succeeded**,
  `pulsar-0.1.0-1-any.pkg.tar.gz` produced. Source download, sha256 checksum
  verification, extraction, `package()`, and fakeroot all passed.
- Package contents verified by listing the built archive: `/usr/bin/pulsar`,
  the full `/usr/lib/pulsar` tree, the desktop file, and the LICENSE are all
  present in the right places
- Desktop file: `Exec=/usr/bin/pulsar`, **zero** remaining `PLACEHOLDER`
  occurrences, and `desktop-file-validate` reports it **VALID** (one informational
  hint about multiple main categories, not an error)
- Runtime smoke test on the extracted package tree: `import main` succeeds via
  the launcher's `sys.path` mechanism; `builtin_presets_path()` resolves to the
  installed `builtin_profiles.json` and the file exists; `PresetManager` loads all
  5 built-in presets (`Stereo`, `Mono`, `5.1 Surround`, `7.1 Surround`, `Custom`)
- `.INSTALL` is embedded in the package, so the desktop-database hooks ship

**NOT validated — do not assume these:**

- **The package was never actually installed.** `makepkg --nodeps` built the
  archive; `pacman -U` was never run, and this container has no pacman database
  (`failed to initialize alpm library: could not create database`). The
  post-install hook path is unexercised.
- **The GUI was never launched.** There is no X/Wayland display here. Import and
  preset resolution were tested; rendering was not.
- **Dependency availability was not confirmed against live Arch repositories.**
  The `archlinux.org` package-file listings could not be re-fetched during this
  pass (the web-extract backend was unavailable). The mapping in the table above
  comes from an earlier verified pass plus source-level confirmation of which
  binaries are invoked.
- `check()` is a no-op unless `_run_tests=1` is set, and even then it needs
  `pytest` installed. The upstream test suite was **not** run.
- Built as `.tar.gz`, not `.tar.zst`, because this Debian host's makepkg is
  configured for gzip. On real Arch, `PKGEXT` defaults to `.pkg.tar.zst`. This is
  a host configuration difference, not a PKGBUILD defect.