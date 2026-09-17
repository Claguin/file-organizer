# file-organizer

[![CI](https://github.com/Claguin/file-organizer/actions/workflows/ci.yml/badge.svg)](https://github.com/Claguin/file-organizer/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Organize a messy folder (downloads, anyone?) into clean subfolders by **file
type** or by **last-modified month** — with a safe `--dry-run` preview and
automatic name-collision handling.

## Demo

```console
$ file-organizer ~/Downloads --dry-run

                     Planned moves
┌────────────────────────────────┬──────────────────────────────────┐
│ Source                         │ Destination                      │
├────────────────────────────────┼──────────────────────────────────┤
│ ~/Downloads/report.pdf         │ ~/Downloads/documents/report.pdf │
│ ~/Downloads/photo.png          │ ~/Downloads/images/photo.png     │
│ ~/Downloads/song.mp3           │ ~/Downloads/audio/song.mp3       │
│ ~/Downloads/installer.exe      │ ~/Downloads/installers/…         │
└────────────────────────────────┴──────────────────────────────────┘

Dry run: 4 file(s) would be moved. Re-run without --dry-run to apply.

$ file-organizer ~/Downloads
Done! Moved 4 file(s).
```

## Install

```console
pip install file-organizer
# or, for development:
git clone https://github.com/Claguin/file-organizer
cd file-organizer
uv sync
```

## Usage

```console
# Group by file type (default)
file-organizer ~/Downloads

# Group by last-modified month (2020-01, 2020-02, ...)
file-organizer ~/Downloads --mode date

# Preview without changing anything
file-organizer ~/Downloads --dry-run

# Skip specific files (repeatable)
file-organizer ~/Downloads --exclude keep.pdf --exclude .env
```

## Features

- **Safe by default** — `--dry-run` shows exactly what will move before anything
  changes.
- **Collision handling** — if a file already exists at the destination, it gets
  a ` (1)`, ` (2)`, … suffix instead of being overwritten.
- **Skips dotfiles and subdirectories** — it only organizes the top level, never
  your hidden config or nested folders.
- **Exit codes** — `0` on success, `1` on error, so it composes well in scripts.

## Design notes

The file logic lives in `src/fileorganizer/core.py` with **zero CLI
dependencies**. `cli.py` is a thin wrapper. That separation means:

1. `core.py` is fully unit-tested in isolation (no shelling out).
2. The same logic could be reused from a GUI, a cron job, or a library without
   pulling in the CLI layer.

## Development

```console
uv sync          # create venv + install dependencies
uv run pytest    # run the test suite
```

## Publishing to PyPI

```console
uv build
uv publish
```

---

MIT © David Frank
