# Push One File at a Time (with Git LFS)

This script helps push the repository files to a remote GitHub repository one file per commit, and uses Git LFS for large files.

Usage (PowerShell, run from repository root):

```powershell
.\scripts\push_one_file_at_a_time.ps1 -Remote 'https://github.com/harshbohra22/flood-project.git' -ThresholdMB 50 -Branch main
```

Notes:
- The script runs `git lfs install`; ensure `git-lfs` is installed on your machine.
- For files >= `ThresholdMB` (default 50 MB) the script will add LFS tracking and commit `.gitattributes`.
- Pushing will prompt for GitHub credentials. For a smoother non-interactive flow, use a Personal Access Token (PAT) with repo permissions and configure it in your credential manager or use an authenticated remote URL.
- The script excludes the `scripts/` folder and `.git` from the auto-commit loop.

Before running, confirm you want to push all repository files one-by-one — this will create many commits (one per file).