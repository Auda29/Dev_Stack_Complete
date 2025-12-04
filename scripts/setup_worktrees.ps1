# Dev_Stack Worktree Setup (PowerShell)
# This script creates worktrees for each agent in their respective directories

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Dev_Stack Worktree Setup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in a Git repository
if (-not (Test-Path ".git")) {
    Write-Host "ERROR: Not in a Git repository root!" -ForegroundColor Red
    Write-Host "Please run this script from the repository root."
    exit 1
}

# Ensure we're on a valid branch
$CurrentBranch = git branch --show-current
if ([string]::IsNullOrWhiteSpace($CurrentBranch)) {
    Write-Host "Creating initial commit on main branch..." -ForegroundColor Yellow
    git checkout -b main
    if ($LASTEXITCODE -ne 0) { git checkout main }
    
    if (-not (Test-Path "README.md")) {
        "# Dev_Stack Project" | Out-File "README.md" -Encoding utf8
        git add README.md
        git commit -m "chore: initial commit"
    }
}

# Create dev branch if it doesn't exist
git show-ref --verify --quiet refs/heads/dev
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating 'dev' branch..." -ForegroundColor Yellow
    git branch dev
}

Write-Host ""
Write-Host "Creating worktrees for agents..." -ForegroundColor Cyan
Write-Host ""

# Create each agent's worktree
foreach ($Agent in $Agents) {
    $AgentDir = $Agent.Name
    $Branch = $Agent.Branch
    $WorktreePath = Join-Path $WorktreeBase $AgentDir
    
    Write-Host "----------------------------------------"
    Write-Host "Agent: $AgentDir"
    Write-Host "Branch: $Branch"
    Write-Host "Path: $WorktreePath"
    
    # Check if worktree directory already exists
    if (Test-Path $WorktreePath) {
        # Check if it's a valid worktree (must contain .git file)
        if (Test-Path (Join-Path $WorktreePath ".git")) {
            Write-Host "[OK] Worktree already exists and is valid, skipping..." -ForegroundColor Green
            continue
        }
        else {
            Write-Host "[WARN] Directory exists but is NOT a valid worktree!" -ForegroundColor Red
            $BackupPath = "${WorktreePath}_backup"
            Write-Host "  Backing up to $BackupPath..." -ForegroundColor Yellow
            Move-Item -Path $WorktreePath -Destination $BackupPath -Force
            Write-Host "  Recreating worktree..." -ForegroundColor Yellow
        }
    }
    
    # Check if branch exists
    git show-ref --verify --quiet "refs/heads/$Branch"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Branch exists: $Branch" -ForegroundColor Green
    }
    else {
        Write-Host "Creating branch: $Branch" -ForegroundColor Yellow
        git branch "$Branch" dev
    }
    
    # Create worktree
    Write-Host "Creating worktree..."
    git worktree add "$WorktreePath" "$Branch"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Worktree created successfully" -ForegroundColor Green
    }
    else {
        Write-Host "[ERR] Failed to create worktree" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Worktree Setup Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Worktrees created:"
git worktree list
Write-Host ""
Write-Host "You can now start the agent containers:"
Write-Host "  docker compose -f docker-compose.yml -f docker-compose.agents.yml up -d"
Write-Host ""
Write-Host "To remove worktrees in the future:"
Write-Host "  git worktree remove [path]"
Write-Host "  or"
Write-Host "  git worktree prune"
Write-Host "================================================"
