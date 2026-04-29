#!/usr/bin/env python3
"""
Release helper for the Bugatsinho Kodi repository.

Usage examples:
    # Full release of plugin.video.sporthdme as 0.1.85
    python3 tools/release.py --addon plugin.video.sporthdme --version 0.1.85

    # Same, with custom news string for both addon.xml and addons.xml
    python3 tools/release.py --addon plugin.video.sporthdme --version 0.1.85 \
        --news "- fix super.league.st url\n- update s2watch resolver"

    # Just regen addons.xml.md5 (e.g. after a manual edit)
    python3 tools/release.py --refresh-md5

    # Dry run: show what would change without writing anything
    python3 tools/release.py --addon plugin.video.sporthdme --version 0.1.85 --dry-run

What it does for a release:
    1. Bumps version="..." in <addon_id>/addon.xml (and optionally rewrites <news>).
    2. Surgically bumps version="..." inside the matching <addon> block of root addons.xml
       (preserves the manually-maintained formatting of every other entry).
    3. Optionally rewrites the <news> block in addons.xml too.
    4. Builds _zips/<addon_id>/<addon_id>-<version>.zip containing the addon source.
    5. Copies addon.xml + icon.png + fanart.jpg into _zips/<addon_id>/ (so they are not stale).
    6. Regenerates addons.xml.md5 at the repo root.
    7. Prints a summary plus a suggested git commit command. It does NOT commit by itself.

Exclusions when zipping: __pycache__, *.pyc, *.pyo, .DS_Store, .git*, .idea, .vscode.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ADDONS_XML = REPO_ROOT / "addons.xml"
ADDONS_MD5 = REPO_ROOT / "addons.xml.md5"
ZIPS_DIR = REPO_ROOT / "_zips"

EXCLUDE_NAMES = {
    "__pycache__",
    ".DS_Store",
    ".idea",
    ".vscode",
    ".git",
}
EXCLUDE_SUFFIXES = (".pyc", ".pyo")
COPY_ASSET_NAMES = ("addon.xml", "icon.png", "fanart.jpg")

VERSION_RE = re.compile(r'^\d+(?:\.\d+)*[A-Za-z0-9.+-]*$')


def err(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)


def info(msg: str) -> None:
    print(msg)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str, dry_run: bool) -> None:
    if dry_run:
        info(f"  [dry-run] would write {path.relative_to(REPO_ROOT)} ({len(content)} chars)")
        return
    path.write_text(content, encoding="utf-8")
    info(f"  wrote {path.relative_to(REPO_ROOT)}")


def md5_of_file(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------- #
# addon.xml manipulation
# --------------------------------------------------------------------------- #

def _replace_version_attr(xml: str, addon_id: str, new_version: str) -> str:
    """
    Replace the version="..." attribute of the <addon id="addon_id" ...> opening tag.
    Works on a single-line opening tag. The addon.xml files in this repo all keep
    the opening <addon> tag on one line, which is what we rely on here.
    """
    pattern = re.compile(
        r'(<addon\b[^>]*\bid="' + re.escape(addon_id) + r'"[^>]*\bversion=")'
        r'[^"]*'
        r'(")',
        re.MULTILINE,
    )
    new_xml, count = pattern.subn(rf'\g<1>{new_version}\g<2>', xml, count=1)
    if count != 1:
        raise RuntimeError(f"could not find <addon id=\"{addon_id}\" version=\"...\"> tag")
    return new_xml


def _replace_news_block(xml: str, addon_id: str, news_text: str) -> str:
    """
    Replace <news>...</news> only inside the <addon id="addon_id"> ... </addon> block.
    We slice out that block, swap the news inside it, then splice back. This avoids
    accidentally touching other addons' <news> tags.
    """
    block_re = re.compile(
        r'(<addon\b[^>]*\bid="' + re.escape(addon_id) + r'"[^>]*>)(.*?)(</addon>)',
        re.DOTALL,
    )
    m = block_re.search(xml)
    if not m:
        raise RuntimeError(f"could not locate <addon id=\"{addon_id}\">...</addon> block")

    head, body, tail = m.group(1), m.group(2), m.group(3)
    news_re = re.compile(r'(<news>)(.*?)(</news>)', re.DOTALL)
    if not news_re.search(body):
        # No news block to replace; leave as is.
        return xml

    # Preserve indentation of the line that holds <news>.
    news_open_match = re.search(r'([ \t]*)<news>', body)
    indent = news_open_match.group(1) if news_open_match else "  "
    inner_indent = indent + "  "
    formatted = "\n".join(inner_indent + line for line in news_text.splitlines())
    new_body = news_re.sub(
        lambda m_: f"{m_.group(1)}\n{formatted}\n{indent}{m_.group(3)}",
        body,
        count=1,
    )
    return xml[: m.start()] + head + new_body + tail + xml[m.end():]


# --------------------------------------------------------------------------- #
# Zip building
# --------------------------------------------------------------------------- #

def _is_excluded(path: Path) -> bool:
    parts = set(path.parts)
    if EXCLUDE_NAMES & parts:
        return True
    if path.name in EXCLUDE_NAMES:
        return True
    if path.suffix in EXCLUDE_SUFFIXES:
        return True
    return False


def build_zip(addon_dir: Path, addon_id: str, version: str, dry_run: bool) -> Path:
    out_dir = ZIPS_DIR / addon_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{addon_id}-{version}.zip"

    if out_path.exists():
        info(f"  note: zip already exists, will overwrite: {out_path.relative_to(REPO_ROOT)}")

    if dry_run:
        info(f"  [dry-run] would build zip: {out_path.relative_to(REPO_ROOT)}")
        return out_path

    files: list[Path] = []
    for path in sorted(addon_dir.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(addon_dir)
        if _is_excluded(rel) or _is_excluded(Path(path.name)):
            continue
        files.append(path)

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for src in files:
            arcname = Path(addon_id) / src.relative_to(addon_dir)
            zf.write(src, arcname.as_posix())

    info(f"  built {out_path.relative_to(REPO_ROOT)} ({len(files)} files, {out_path.stat().st_size} bytes)")
    return out_path


def copy_assets(addon_dir: Path, addon_id: str, dry_run: bool) -> None:
    out_dir = ZIPS_DIR / addon_id
    out_dir.mkdir(parents=True, exist_ok=True)
    for asset in COPY_ASSET_NAMES:
        src = addon_dir / asset
        if not src.exists():
            continue
        dst = out_dir / asset
        if dry_run:
            info(f"  [dry-run] would copy {src.relative_to(REPO_ROOT)} -> {dst.relative_to(REPO_ROOT)}")
            continue
        shutil.copy2(src, dst)
        info(f"  copied {src.relative_to(REPO_ROOT)} -> {dst.relative_to(REPO_ROOT)}")


# --------------------------------------------------------------------------- #
# md5
# --------------------------------------------------------------------------- #

def refresh_md5(dry_run: bool) -> None:
    if not ADDONS_XML.exists():
        raise RuntimeError(f"missing {ADDONS_XML}")
    digest = md5_of_file(ADDONS_XML)
    if dry_run:
        info(f"  [dry-run] would write addons.xml.md5 = {digest}")
        return
    ADDONS_MD5.write_text(digest, encoding="utf-8")
    info(f"  wrote addons.xml.md5 = {digest}")


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #

def do_release(addon_id: str, new_version: str, news: str | None, dry_run: bool) -> None:
    addon_dir = REPO_ROOT / addon_id
    addon_xml_path = addon_dir / "addon.xml"

    if not addon_dir.is_dir():
        raise RuntimeError(f"addon folder not found: {addon_dir}")
    if not addon_xml_path.is_file():
        raise RuntimeError(f"addon.xml not found in {addon_dir}")

    info(f"== Releasing {addon_id} -> {new_version} ==")

    info("[1/5] update addon.xml")
    addon_xml = read_text(addon_xml_path)
    new_addon_xml = _replace_version_attr(addon_xml, addon_id, new_version)
    if news is not None:
        new_addon_xml = _replace_news_block(new_addon_xml, addon_id, news)
    write_text(addon_xml_path, new_addon_xml, dry_run)

    info("[2/5] update root addons.xml")
    root_xml = read_text(ADDONS_XML)
    new_root_xml = _replace_version_attr(root_xml, addon_id, new_version)
    if news is not None:
        new_root_xml = _replace_news_block(new_root_xml, addon_id, news)
    write_text(ADDONS_XML, new_root_xml, dry_run)

    info("[3/5] build zip")
    build_zip(addon_dir, addon_id, new_version, dry_run)

    info("[4/5] copy assets into _zips/")
    copy_assets(addon_dir, addon_id, dry_run)

    info("[5/5] refresh addons.xml.md5")
    refresh_md5(dry_run)

    info("")
    info("Release prepared.")
    if dry_run:
        info("(dry-run -- no files were modified)")
        return
    info("Suggested git commands:")
    info(f"  git add {addon_id}/addon.xml addons.xml addons.xml.md5 _zips/{addon_id}")
    info(f"  git commit -m 'Update {addon_id} to {new_version}'")
    info(f"  git tag {addon_id}-{new_version}")
    info(f"  git push --follow-tags")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--addon", help="Addon id (folder name), e.g. plugin.video.sporthdme")
    parser.add_argument("--version", help="New version, e.g. 0.1.85")
    parser.add_argument(
        "--news",
        help='Optional news string. Use \\n for line breaks. Will be re-indented inside <news>...</news>.',
    )
    parser.add_argument("--refresh-md5", action="store_true", help="Only refresh addons.xml.md5 and exit")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing files")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    if args.refresh_md5 and not (args.addon or args.version):
        try:
            refresh_md5(args.dry_run)
        except Exception as exc:
            err(str(exc))
            return 2
        return 0

    if not args.addon or not args.version:
        err("--addon and --version are both required for a release (or pass --refresh-md5 alone)")
        return 2

    if not VERSION_RE.match(args.version):
        err(f"version does not look valid: {args.version!r}")
        return 2

    news = args.news.replace("\\n", "\n") if args.news else None

    try:
        do_release(args.addon, args.version, news, args.dry_run)
    except Exception as exc:
        err(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
