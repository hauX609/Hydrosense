param(
    [string]$Remote = 'https://github.com/harshbohra22/flood-project.git',
    [int]$ThresholdMB = 50,
    [string]$Branch = 'main'
)

# Push repository files one-by-one, using Git LFS for large files.
# Usage example:
#   .\scripts\push_one_file_at_a_time.ps1 -Remote 'https://github.com/owner/repo.git' -ThresholdMB 50 -Branch main

function Write-Log { param($m) Write-Host "[push-script] $m" }

# Ensure we're in a git repo (or initialize)
try {
    git rev-parse --is-inside-work-tree > $null 2>&1
    $inside = $LASTEXITCODE -eq 0
} catch {
    $inside = $false
}

if (-not $inside) {
    Write-Log "Not inside a git repository. Initializing repository."
    git init
    git remote remove origin 2>$null
    git remote add origin $Remote
} else {
    # Ensure remote origin exists and matches provided URL (if origin missing, add it)
    $remotes = git remote -v 2>$null
    if (-not ($remotes -match "^origin")) {
        Write-Log "Adding remote origin $Remote"
        git remote add origin $Remote
    } else {
        Write-Log "Remote origin exists."
    }
}

# Install/enable Git LFS
Write-Log "Running 'git lfs install' (may require git-lfs installed on this machine)."
git lfs install

$repoRoot = (Get-Location).ProviderPath
Write-Log "Repository root: $repoRoot"

# Collect all files (exclude .git directory)
$allFiles = Get-ChildItem -Recurse -File -Force | Where-Object { $_.FullName -notmatch "\\\.git\\" }

$thresholdBytes = $ThresholdMB * 1024 * 1024
$largeFiles = $allFiles | Where-Object { $_.Length -ge $thresholdBytes }

if ($largeFiles.Count -gt 0) {
    Write-Log "Found $($largeFiles.Count) large files (>= $ThresholdMB MB). Tracking them with Git LFS."
    foreach ($f in $largeFiles) {
        $rel = $f.FullName.Substring($repoRoot.Length + 1) -replace '\\','/'
        Write-Log "Tracking $rel"
        git lfs track --no-smudge "$rel" | Out-Null
    }
    # Add and commit .gitattributes if changed
    if (Test-Path ".gitattributes") {
        git add .gitattributes
        if (-not (git diff --cached --quiet)) {
            git commit -m "chore: track large files with Git LFS (.gitattributes)"
            Write-Log "Committed .gitattributes"
        } else {
            Write-Log ".gitattributes unchanged"
        }
    }
} else {
    Write-Log "No large files found >= $ThresholdMB MB."
}

# Build list of files to add/push (exclude script files and .git folder)
$excludePatterns = @('^.git/', '^scripts/', '^\.gitignore$')

$orderedFiles = $allFiles | ForEach-Object {
    $rel = $_.FullName.Substring($repoRoot.Length + 1) -replace '\\','/'
    [PSCustomObject]@{ Path = $rel; Size = $_.Length }
} | Where-Object {
    $p = $_.Path
    -not ($excludePatterns | Where-Object { $p -match $_ })
} | Sort-Object Path

Write-Log "Preparing to add and push $($orderedFiles.Count) files, one commit per file."

foreach ($item in $orderedFiles) {
    $file = $item.Path
    Write-Log "Processing: $file"

    # Add file
    git add -- "$file"

    # Only commit if there are staged changes
    git diff --cached --quiet
    if ($LASTEXITCODE -ne 0) {
        git commit -m "Add file: $file"
        Write-Log "Committed $file"

        Write-Log "Pushing commit for $file to origin/$Branch (you may be prompted for credentials)."
        git push origin $Branch
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Push returned non-zero exit code. Stopping to allow user to inspect."
            break
        }
    } else {
        Write-Log "No changes to commit for $file. Skipping."
    }
}

Write-Log "Done. Review the remote repository to confirm all files were pushed."