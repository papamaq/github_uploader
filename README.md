# GitHub Automated Folder Uploader

A Python script that uploads your entire app folder to GitHub as a repository — preserving the **exact folder and subfolder structure** as it is on your computer. No Git knowledge required.

---

## 📌 What It Does

Point the script at a directory containing your project folders. Each **top-level folder** becomes its own GitHub repository. Everything inside — files, folders, subfolders, deeply nested files — gets uploaded exactly as it looks on your machine.

### Example

Given this local structure:

```
/Projects
  ├── MyApp/
  │     ├── main.py               ← loose file at root → uploaded as-is
  │     ├── config.json           ← loose file at root → uploaded as-is
  │     ├── frontend/             ← folder → uploaded as-is
  │     │     ├── index.html
  │     │     └── styles/         ← subfolder → uploaded as-is
  │     │           └── main.css
  │     └── backend/
  │           ├── server.py
  │           └── utils/
  │                 └── helpers.py
  └── MyAPI/
        ├── README.md
        └── src/
              └── api.py
```

Running the script creates **2 GitHub repos**:

- `yourUsername/MyApp` — with the full tree intact inside
- `yourUsername/MyAPI` — with the full tree intact inside

GitHub mirrors your local structure **1 to 1**. Nothing is rearranged.

---

## 🛠️ Language

Written in **Python 3** — a scripting language. There is **no compiling step**. You just run the `.py` file directly with the `python` command.

---

## ⚙️ One-Time Setup

### Step 1 — Install Python

Download from [python.org](https://python.org) — get **Python 3.10 or newer**.

Verify it installed correctly by opening Terminal or CMD and typing:

```bash
python --version
```

You should see something like `Python 3.11.4`.

---

### Step 2 — Install the Dependency

This script uses one external library called **PyGithub** to talk to the GitHub API. Install it with:

```bash
pip install PyGithub
```

---

### Step 3 — Get a GitHub Personal Access Token (PAT)

The script needs permission to create repos and upload files on your behalf. GitHub uses a token for this (not your password).

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Give it any name (e.g. `uploader-script`)
4. Set an expiry date
5. Tick the **`repo`** checkbox (gives full repo access)
6. Scroll down and click **"Generate token"**
7. **Copy the token immediately** — GitHub only shows it once. It starts with `ghp_...`

---

### Step 4 — Set Your Token as an Environment Variable

This keeps your token out of the script file — important for security.

**Mac / Linux (Terminal):**
```bash
export GITHUB_TOKEN=ghp_yourTokenHere
```

**Windows (Command Prompt):**
```cmd
set GITHUB_TOKEN=ghp_yourTokenHere
```

**Windows (PowerShell):**
```powershell
$env:GITHUB_TOKEN="ghp_yourTokenHere"
```

> ⚠️ This is temporary per session. To make it permanent, add the line to your `~/.bash_profile` (Mac/Linux) or set it in System Environment Variables (Windows).

---

## 🚀 How to Run

Open Terminal or CMD, navigate to the folder where you saved `github_uploader.py`, then:

### Upload all subfolders in a directory (each becomes its own repo)
```bash
python github_uploader.py /path/to/Projects
```

### Upload one specific folder as a single repo
```bash
python github_uploader.py /path/to/Projects/MyApp --single
```

### Make repos private instead of public
```bash
python github_uploader.py /path/to/Projects --visibility private
```

### Pass your token directly without environment variable
```bash
python github_uploader.py /path/to/Projects --token ghp_yourTokenHere
```

### Skip repos that already exist instead of being asked
```bash
python github_uploader.py /path/to/Projects --existing skip
```

### Always update existing repos without being asked
```bash
python github_uploader.py /path/to/Projects --existing update
```

---

## 💬 Interactive Prompts

When you run the script it will:

1. **Authenticate** and confirm your GitHub username
2. **List** all folders it found to process
3. **Ask** if a repo with the same name already exists — type `y` to update it or press Enter to skip
4. **Show progress** for every file being uploaded

```
✅  Authenticated as: yourUsername

🚀  Found 2 folder(s) to process in: /Projects

📁  Folder : /Projects/MyApp
🏷️   Repo   : yourUsername/MyApp
    ✅ Created repo: https://github.com/yourUsername/MyApp
    📦 12 file(s) to upload...
    ➕  Created : main.py
    ➕  Created : config.json
    ➕  Created : frontend/index.html
    ➕  Created : frontend/styles/main.css
    ➕  Created : backend/server.py
    ➕  Created : backend/utils/helpers.py
    ✔️  Done — 12 uploaded, 0 failed
    🔗  https://github.com/yourUsername/MyApp

🎉  All done!
```

---

## ⚙️ Configuration

Open `github_uploader.py` and edit these lines at the top to change defaults:

| Setting | Default | Options |
|---|---|---|
| `REPO_VISIBILITY` | `public` | `private` |
| `EXISTING_REPO` | `ask` | `skip`, `update` |
| `COMMIT_MESSAGE` | `Initial commit` | Any text, `auto` (timestamp), `ask` |

---

## 🚫 Ignored Files & Folders

These are automatically skipped during upload — they are system-generated, too large, machine-specific, or security risks:

| Ignored | Reason |
|---|---|
| `.git` | Git's internal tracking folder — GitHub creates its own |
| `.DS_Store` | Mac display preferences file — useless on GitHub |
| `__pycache__` | Python auto-generated bytecode cache |
| `node_modules` | Node.js packages — too large, recreated with `npm install` |
| `.env` | Contains secrets like API keys — never upload this |
| `.venv` / `venv` | Python virtual environment — recreated with `pip install` |
| `.idea` | JetBrains editor settings (PyCharm, IntelliJ) |
| `.vscode` | VS Code editor settings |
| `*.pyc` / `*.pyo` | Compiled Python bytecode files |
| `*.log` | Runtime log files |
| `Thumbs.db` | Windows image thumbnail cache |

Everything else — your actual code, assets, configs, and docs — gets uploaded.

---

## 📋 Requirements Summary

- Python 3.10+
- `pip install PyGithub`
- A GitHub account
- A GitHub Personal Access Token with `repo` scope

---

## 📁 Files in This Package

| File | Purpose |
|---|---|
| `github_uploader.py` | The main script — run this |
| `README.md` | This documentation file |

---

## ⚡ This Script vs Git Commands — Which Saves Time?

### If you use Git commands manually:

For **every single project** you'd have to do this:

```bash
cd /Projects/MyApp
git init
git add .
git commit -m "Initial commit"
# Then go to GitHub website
# Manually create the repo
# Copy the repo URL
# Come back to terminal
git remote add origin https://github.com/you/MyApp.git
git push -u origin main
```

If you have **10 projects**, you repeat all of that **10 times**.
That's roughly **7 commands × 10 projects = 70 commands** plus manual clicking on GitHub's website each time.

### If you use this script:

```bash
python github_uploader.py /Projects
```

**One command. Done.** All 10 repos created and uploaded simultaneously — zero website clicking, zero repetition.

---

### Comparison Table

| | Git Commands | This Script |
|---|---|---|
| Single project | ~2 mins | ~5 seconds |
| 10 projects | ~20 mins | ~5 seconds |
| 50 projects | ~2 hours | ~5 seconds |
| GitHub website needed | ✅ Yes | ❌ No |
| Remembering commands | ✅ Required | ❌ Not needed |
| Handles nested folders | ✅ Yes but manual | ✅ Automatic |
| Batch upload | ❌ No | ✅ Yes |

---

### 🏆 Verdict

**The script wins every time** — especially when you have multiple projects. Git commands are powerful but designed to be used one repo at a time with full manual control. This script is built for exactly one purpose — bulk uploading entire app structures in one shot.

The only time Git commands would be better is if you need **advanced version control** — branches, pull requests, merge history, or rollbacks. This script is purely an **uploader**, not a version control system.
