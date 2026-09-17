"""Pure, dependency-free file-organizing logic.

Everything in this module operates on paths passed in and is fully unit
testable without touching the command-line layer. Keeping this logic separate
from the CLI is a deliberate design choice: the same functions could be
reused from a GUI, a script, or a scheduler later.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

#: Map of file extensions (lowercase, with leading dot) to destination folders.
EXTENSION_CATEGORIES: dict[str, str] = {
    # images
    ".png": "images", ".jpg": "images", ".jpeg": "images", ".gif": "images",
    ".webp": "images", ".bmp": "images", ".svg": "images", ".tiff": "images",
    ".heic": "images", ".ico": "images",
    # documents
    ".pdf": "documents", ".doc": "documents", ".docx": "documents",
    ".txt": "documents", ".md": "documents", ".rtf": "documents",
    ".odt": "documents", ".xls": "documents", ".xlsx": "documents",
    ".csv": "documents", ".ppt": "documents", ".pptx": "documents",
    # audio
    ".mp3": "audio", ".wav": "audio", ".flac": "audio", ".aac": "audio",
    ".ogg": "audio", ".m4a": "audio", ".wma": "audio",
    # video
    ".mp4": "video", ".mov": "video", ".avi": "video", ".mkv": "video",
    ".webm": "video", ".wmv": "video",
    # archives
    ".zip": "archives", ".tar": "archives", ".gz": "archives",
    ".rar": "archives", ".7z": "archives", ".bz2": "archives",
    ".xz": "archives", ".tgz": "archives",
    # code
    ".py": "code", ".js": "code", ".ts": "code", ".jsx": "code",
    ".tsx": "code", ".java": "code", ".c": "code", ".cpp": "code",
    ".h": "code", ".go": "code", ".rs": "code", ".html": "code",
    ".css": "code", ".scss": "code", ".json": "code", ".yaml": "code",
    ".yml": "code", ".toml": "code", ".sh": "code", ".sql": "code",
    # installers
    ".exe": "installers", ".msi": "installers", ".dmg": "installers",
    ".deb": "installers", ".rpm": "installers", ".apk": "installers",
}


@dataclass(frozen=True)
class MovePlan:
    """A single planned file move from ``source`` to ``destination``."""

    source: Path
    destination: Path


def categorize(extension: str) -> str:
    """Return the destination category for a file extension.

    ``extension`` should include the leading dot (e.g. ``".png"``). The lookup
    is case-insensitive and unknown extensions map to ``"other"``.
    """
    return EXTENSION_CATEGORIES.get(extension.lower(), "other")


def _type_destination(root: Path, file_path: Path) -> Path:
    return root / categorize(file_path.suffix) / file_path.name


def _date_destination(root: Path, file_path: Path) -> Path:
    stat = file_path.stat()
    stamp = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
    return root / f"{stamp.year:04d}-{stamp.month:02d}" / file_path.name


def _unique_destination(destination: Path, taken: set[Path]) -> Path:
    """Return ``destination``, adding a `` (n)`` suffix to avoid collisions.

    A collision happens when the destination already exists on disk, or when an
    earlier plan in this run already claimed that exact path.
    """
    candidate = destination
    counter = 1
    while candidate in taken or candidate.exists():
        candidate = destination.with_name(
            f"{destination.stem} ({counter}){destination.suffix}"
        )
        counter += 1
    taken.add(candidate)
    return candidate


def plan_moves(
    directory: Path,
    mode: str = "type",
    exclude: set[str] | None = None,
) -> list[MovePlan]:
    """Compute the list of moves for top-level files in ``directory``.

    Subdirectories and dotfiles are skipped. ``mode`` is ``"type"`` (group by
    extension) or ``"date"`` (group by last-modified month). This function
    performs no filesystem mutations, so it is safe to use for a ``--dry-run``.
    """
    if not directory.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    exclude = set(exclude) if exclude else set()
    taken: set[Path] = set()
    plans: list[MovePlan] = []

    for entry in sorted(directory.iterdir(), key=lambda p: p.name.lower()):
        if not entry.is_file():
            continue
        if entry.name.startswith(".") or entry.name in exclude:
            continue

        if mode == "date":
            destination = _date_destination(directory, entry)
        else:
            destination = _type_destination(directory, entry)

        if destination == entry:
            continue

        plans.append(
            MovePlan(source=entry, destination=_unique_destination(destination, taken))
        )

    return plans


def execute(plans: list[MovePlan], dry_run: bool = False) -> list[MovePlan]:
    """Execute a list of :class:`MovePlan` objects.

    Creates destination folders as needed and renames each file. Returns the
    plans that were actually executed (empty when ``dry_run`` is true).
    """
    executed: list[MovePlan] = []
    for plan in plans:
        if dry_run:
            continue
        plan.destination.parent.mkdir(parents=True, exist_ok=True)
        plan.source.rename(plan.destination)
        executed.append(plan)
    return executed
