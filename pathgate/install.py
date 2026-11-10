"""`pathgate install` - add Pathgate to Claude Desktop's config file.

Usage:
    uvx pathgate install C:\\Users\\me\\Documents C:\\Users\\me\\Projects
    uvx pathgate install            (prompts for folders)
    uvx pathgate install --dry-run ~/Projects
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

DEFAULT_NAME = "pathgate"
CONFIG_FILENAME = "claude_desktop_config.json"


class InstallError(Exception):
    """A problem we can explain to the user in one line."""


# --------------------------------------------------------------------------
# Finding the config file
# --------------------------------------------------------------------------

def claude_desktop_candidates() -> list[Path]:
    """Every place Claude Desktop might keep its config on this OS."""
    if sys.platform == "win32":
        found: list[Path] = []
        appdata = os.environ.get("APPDATA")
        if appdata:
            found.append(Path(appdata) / "Claude" / CONFIG_FILENAME)
        local = os.environ.get("LOCALAPPDATA")
        if local:
            # Microsoft Store (MSIX) installs keep their own private copy.
            pattern = "Claude_*/LocalCache/Roaming/Claude"
            for folder in sorted(Path(local, "Packages").glob(pattern)):
                found.append(folder / CONFIG_FILENAME)
        return found
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / "Claude"
        return [base / CONFIG_FILENAME]
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return [base / "Claude" / CONFIG_FILENAME]


def resolve_config_path(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()

    candidates = claude_desktop_candidates()
    usable = [c for c in candidates if c.exists() or c.parent.exists()]
    existing = [c for c in usable if c.exists()]

    if len(existing) == 1:
        return existing[0]
    if not existing and len(usable) == 1:
        return usable[0]
    if not usable:
        raise InstallError(
            "couldn't find Claude Desktop's config folder. Is Claude Desktop "
            "installed? You can point at a config file yourself with --config PATH."
        )
    listing = "\n  ".join(str(c) for c in usable)
    raise InstallError(
        "found more than one possible Claude Desktop config:\n  "
        f"{listing}\nRe-run with --config PATH to say which one."
    )


# --------------------------------------------------------------------------
# Building the entry
# --------------------------------------------------------------------------

def build_server_entry(paths: list[str], read_only: bool) -> dict:
    """The `mcpServers` entry that launches Pathgate.

    `pathgate@latest` makes uv check PyPI on every launch, so users always
    run the newest release without doing anything.
    """
    uvx = shutil.which("uvx")
    uv = shutil.which("uv")
    if uvx:
        command, args = uvx, ["pathgate@latest"]
    elif uv:
        command, args = uv, ["tool", "run", "pathgate@latest"]
    else:
        command, args = sys.executable, ["-m", "pathgate"]  # no uv: can't auto-update
    args = args + paths
    if read_only:
        args.append("--read-only")
    return {"command": command, "args": args}


# --------------------------------------------------------------------------
# Reading / writing the config safely
# --------------------------------------------------------------------------

def load_config(path: Path) -> dict:
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8-sig")  # tolerate a BOM
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise InstallError(
            f"{path} isn't valid JSON ({e}). I haven't changed anything - "
            "fix the file by hand, then run this again."
        ) from None
    if not isinstance(data, dict):
        raise InstallError(f"{path} doesn't contain a JSON object, so I left it alone.")
    return data


def write_config(path: Path, data: dict) -> Path | None:
    """Back up the old file, then replace it atomically. Returns the backup path."""
    path.parent.mkdir(parents=True, exist_ok=True)

    backup = None
    if path.exists():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = path.with_name(f"{path.name}.pathgate-{stamp}.bak")
        shutil.copy2(path, backup)

    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return backup


# --------------------------------------------------------------------------
# The command
# --------------------------------------------------------------------------

def _prompt_for_paths() -> list[str]:
    print("Which folders should Pathgate be allowed to access?")
    print("Enter one folder per line. Press Enter on an empty line when done.")
    paths: list[str] = []
    while True:
        line = input("> ").strip().strip('"').strip("'")
        if not line:
            break
        paths.append(line)
    return paths


def _clean_paths(raw: list[str]) -> list[str]:
    cleaned: list[str] = []
    for item in raw:
        p = Path(item).expanduser().resolve()
        if not p.is_dir():
            raise InstallError(f"not a folder: {p}")
        s = str(p)
        if s not in cleaned:
            cleaned.append(s)
    return cleaned


def _confirm(question: str) -> bool:
    answer = input(f"{question} [Y/n] ").strip().lower()
    return answer in ("", "y", "yes")


def _install(args: argparse.Namespace) -> int:
    interactive = sys.stdin.isatty()

    raw_paths = list(args.paths)
    if not raw_paths:
        if not interactive:
            raise InstallError(
                "no folders given. Example: pathgate install C:\\Users\\me\\Documents"
            )
        raw_paths = _prompt_for_paths()
        if not raw_paths:
            raise InstallError("no folders given, nothing to do.")
    paths = _clean_paths(raw_paths)

    config_path = resolve_config_path(args.config)
    data = load_config(config_path)
    entry = build_server_entry(paths, args.read_only)

    servers = data.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        raise InstallError(f'"mcpServers" in {config_path} isn\'t an object, so I left it alone.')

    existing = servers.get(args.name)
    if existing == entry:
        print(f'"{args.name}" is already set up in {config_path}. Nothing to change.')
        return 0

    print(f"Config file : {config_path}")
    print(f"Server name : {args.name}")
    print(f"Command     : {entry['command']} {' '.join(entry['args'])}")
    print("Folders     : " + ", ".join(paths))
    print("Mode        : " + ("read-only" if args.read_only else "read/write"))
    if existing is not None:
        print(f'Note        : this replaces your current "{args.name}" entry.')

    if args.dry_run:
        print("\n--dry-run: nothing was written.")
        return 0

    if not args.yes:
        if not interactive:
            raise InstallError("not running in a terminal; pass --yes to proceed.")
        if not _confirm("\nWrite this to the config?"):
            print("Cancelled. Nothing was changed.")
            return 1

    servers[args.name] = entry
    backup = write_config(config_path, data)

    print(f'\nDone. Added "{args.name}" to {config_path}.')
    if backup:
        print(f"Backup of your old config: {backup}")
    print("Now fully quit Claude Desktop (system tray -> Quit) and reopen it.")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="pathgate install",
        description="Add Pathgate to Claude Desktop's config file.",
    )
    p.add_argument("paths", nargs="*", help="Folders Pathgate may access")
    p.add_argument("--read-only", action="store_true", help="Disable write/delete/move/copy tools")
    p.add_argument("--name", default=DEFAULT_NAME, help=f"Entry name in the config (default: {DEFAULT_NAME})")
    p.add_argument("--config", metavar="PATH", help="Config file to edit (default: auto-detect Claude Desktop)")
    p.add_argument("--dry-run", action="store_true", help="Show what would change without writing")
    p.add_argument("-y", "--yes", action="store_true", help="Don't ask for confirmation")
    args = p.parse_args(argv)

    try:
        return _install(args)
    except InstallError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled. Nothing was changed.", file=sys.stderr)
        return 130
