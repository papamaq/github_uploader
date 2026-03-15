#!/usr/bin/env python3
"""
GitHub Automated Folder Uploader
---------------------------------
Uploads folders (including nested subfolders) to GitHub.
Each top-level folder becomes its own repository named after the folder.

Requirements:
    pip install PyGithub

Usage:
    python github_uploader.py /path/to/parent/folder

Example:
    python github_uploader.py ~/Projects
    → Creates repos: Projects/MyApp, Projects/MyAPI, etc.

Setup:
    Set your GitHub Personal Access Token (PAT) as an env variable:
        export GITHUB_TOKEN=ghp_yourTokenHere
    Or hardcode it below (not recommended for shared machines).

    Generate a PAT at: https://github.com/settings/tokens
    Required scopes: repo (full control)
"""

import os
import sys
import base64
import argparse
from datetime import datetime
from pathlib import Path

try:
    from github import Github, GithubException
except ImportError:
    print("❌  PyGithub not installed. Run: pip install PyGithub")
    sys.exit(1)


# ─────────────────────────────────────────────
#  CONFIGURATION  ← Edit these if needed
# ─────────────────────────────────────────────

GITHUB_TOKEN   = os.environ.get("GITHUB_TOKEN", "")   # or paste token here as fallback
REPO_VISIBILITY = "public"    # "public" or "private"
EXISTING_REPO   = "ask"       # "skip" | "update" | "ask"
COMMIT_MESSAGE  = "Initial commit"  # "auto" | "ask" | any fixed string

# Files/folders to always ignore
IGNORE_PATTERNS = {
    ".git", ".DS_Store", "__pycache__", "node_modules",
    ".env", ".venv", "venv", ".idea", ".vscode",
    "*.pyc", "*.pyo", "*.log", "Thumbs.db"
}

# ─────────────────────────────────────────────


def should_ignore(name: str) -> bool:
    """Check if a file or folder should be skipped."""
    if name in IGNORE_PATTERNS:
        return True
    for pattern in IGNORE_PATTERNS:
        if pattern.startswith("*") and name.endswith(pattern[1:]):
            return True
    return False


def get_commit_message() -> str:
    if COMMIT_MESSAGE == "auto":
        return f"Upload via script — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    if COMMIT_MESSAGE == "ask":
        msg = input("\n💬  Commit message (applied to all repos this run): ").strip()
        return msg or f"Upload via script — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    return COMMIT_MESSAGE


def collect_files(folder_path: Path) -> dict:
    """
    Recursively collect all files in folder.
    Returns dict of { 'relative/path/file.ext': b'file_bytes' }
    """
    files = {}
    for root, dirs, filenames in os.walk(folder_path):
        # Filter ignored dirs in-place (stops os.walk from descending)
        dirs[:] = [d for d in dirs if not should_ignore(d)]

        for filename in filenames:
            if should_ignore(filename):
                continue
            full_path = Path(root) / filename
            rel_path  = full_path.relative_to(folder_path)
            try:
                with open(full_path, "rb") as f:
                    files[str(rel_path)] = f.read()
            except Exception as e:
                print(f"    ⚠️  Could not read {rel_path}: {e}")
    return files


def sanitize_repo_name(name: str) -> str:
    """GitHub repo names: alphanumeric, hyphens, underscores, dots only."""
    import re
    name = name.strip().replace(" ", "-")
    name = re.sub(r"[^a-zA-Z0-9._-]", "-", name)
    name = re.sub(r"-+", "-", name).strip("-")
    return name or "unnamed-repo"


def upload_folder_as_repo(gh_user, folder_path: Path, commit_msg: str):
    """Create or update a GitHub repo from a local folder."""
    repo_name = sanitize_repo_name(folder_path.name)
    print(f"\n📁  Folder : {folder_path}")
    print(f"🏷️   Repo   : {gh_user.login}/{repo_name}")

    # ── Check if repo already exists ──────────────────────────────────────
    existing_repo = None
    try:
        existing_repo = gh_user.get_repo(repo_name)
        if EXISTING_REPO == "skip":
            print(f"    ⏭️  Repo already exists — skipping.")
            return
        elif EXISTING_REPO == "ask":
            answer = input(f"    ❓ Repo '{repo_name}' exists. Update it? [y/N]: ").strip().lower()
            if answer != "y":
                print("    ⏭️  Skipped.")
                return
        # else: "update" — fall through
        print("    ♻️  Repo exists — will update files.")
    except GithubException as e:
        if e.status == 404:
            existing_repo = None  # doesn't exist yet
        else:
            print(f"    ❌ GitHub error: {e}")
            return

    # ── Create repo if needed ─────────────────────────────────────────────
    if existing_repo is None:
        try:
            is_private = (REPO_VISIBILITY == "private")
            repo = gh_user.create_repo(
                name=repo_name,
                private=is_private,
                auto_init=False,
            )
            print(f"    ✅ Created repo: {repo.html_url}")
        except GithubException as e:
            print(f"    ❌ Could not create repo: {e.data.get('message', e)}")
            return
    else:
        repo = existing_repo

    # ── Collect files ─────────────────────────────────────────────────────
    files = collect_files(folder_path)
    if not files:
        print("    ⚠️  No files found — nothing to upload.")
        return

    print(f"    📦 {len(files)} file(s) to upload...")

    # ── Upload each file ──────────────────────────────────────────────────
    success = 0
    failed  = 0

    for rel_path, content_bytes in files.items():
        github_path = rel_path.replace("\\", "/")  # Windows path fix
        try:
            # Check if file already exists (for updates)
            existing_file = None
            try:
                existing_file = repo.get_contents(github_path)
            except GithubException:
                pass  # File doesn't exist yet

            if existing_file:
                repo.update_file(
                    path=github_path,
                    message=commit_msg,
                    content=content_bytes,
                    sha=existing_file.sha,
                )
                print(f"    🔄  Updated : {github_path}")
            else:
                repo.create_file(
                    path=github_path,
                    message=commit_msg,
                    content=content_bytes,
                )
                print(f"    ➕  Created : {github_path}")

            success += 1

        except GithubException as e:
            msg = e.data.get("message", str(e)) if hasattr(e, "data") else str(e)
            print(f"    ❌  Failed  : {github_path} — {msg}")
            failed += 1

    print(f"\n    ✔️  Done — {success} uploaded, {failed} failed")
    print(f"    🔗  {repo.html_url}")


def main():
    global REPO_VISIBILITY, EXISTING_REPO

    parser = argparse.ArgumentParser(
        description="Upload folders as GitHub repos (nested folders supported)"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Parent directory containing folders to upload (default: current directory)"
    )
    parser.add_argument(
        "--token",
        help="GitHub Personal Access Token (overrides GITHUB_TOKEN env var)"
    )
    parser.add_argument(
        "--visibility",
        choices=["public", "private"],
        default=REPO_VISIBILITY,
        help="Repo visibility (default: private)"
    )
    parser.add_argument(
        "--existing",
        choices=["skip", "update", "ask"],
        default=EXISTING_REPO,
        help="What to do if repo already exists (default: update)"
    )
    parser.add_argument(
        "--single",
        action="store_true",
        help="Upload the given folder itself as one repo (instead of its subfolders)"
    )
    args = parser.parse_args()

    # Override globals from CLI args
    REPO_VISIBILITY = args.visibility
    EXISTING_REPO   = args.existing

    # ── Auth ───────────────────────────────────────────────────────────────
    token = args.token or GITHUB_TOKEN
    if not token:
        print("❌  No GitHub token found.")
        print("    Set it with:  export GITHUB_TOKEN=ghp_yourToken")
        print("    Or pass it:   python github_uploader.py /path --token ghp_xxx")
        sys.exit(1)

    try:
        gh      = Github(token)
        gh_user = gh.get_user()
        print(f"✅  Authenticated as: {gh_user.login}")
    except GithubException as e:
        print(f"❌  Authentication failed: {e}")
        sys.exit(1)

    # ── Resolve target path ────────────────────────────────────────────────
    target = Path(args.path).expanduser().resolve()
    if not target.is_dir():
        print(f"❌  Not a directory: {target}")
        sys.exit(1)

    commit_msg = get_commit_message()

    # ── Single folder mode vs multi-folder mode ────────────────────────────
    if args.single:
        upload_folder_as_repo(gh_user, target, commit_msg)
    else:
        subfolders = [f for f in sorted(target.iterdir())
                      if f.is_dir() and not should_ignore(f.name)]

        if not subfolders:
            print(f"⚠️  No subfolders found in {target}. Use --single to upload this folder directly.")
            sys.exit(0)

        print(f"\n🚀  Found {len(subfolders)} folder(s) to process in: {target}\n")
        for folder in subfolders:
            upload_folder_as_repo(gh_user, folder, commit_msg)

    print("\n🎉  All done!")


if __name__ == "__main__":
    main()
