# GitHub Workflow Guide

**For 3-Person Team Collaboration**

---

## Initial Repository Setup

### 1. Create Repository

**Owner (You) creates the repository:**

1. Go to https://github.com/new
2. Fill in:
   - **Repository name:** `image-analysis-system`
   - **Description:** "Local-first image analysis with semantic search using vision models"
   - **Visibility:** Private (switch to Public before release)
   - **Initialize:**
     - ✅ Add a README file
     - ✅ Add .gitignore: Python template
     - ✅ Choose a license: MIT License
3. Click **Create repository**

### 2. Add Team Members

1. Go to repository **Settings** → **Collaborators**
2. Click **Add people**
3. Enter teammate GitHub usernames/emails
4. They'll receive invitation emails

### 3. Clone Repository

**Everyone on the team:**

```bash
# Navigate to your projects folder
cd C:\Users\YourName\Projects

# Clone the repo (replace YOUR_USERNAME)
git clone https://github.com/YOUR_USERNAME/image-analysis-system.git
cd image-analysis-system
```

---

## Branching Strategy

We use **Git Flow** branching model:

```
main (protected) ─────────────────────────────────→ Production releases
  ↑
develop ──────────────────────────────────────────→ Integration branch
  ↑          ↑         ↑
feature/A  feature/B  feature/C ─────────────────→ Individual features
```

### Branch Types

1. **`main`** - Production-ready code only
   - Protected branch (no direct commits)
   - Tagged releases (v0.1.0, v0.2.0, etc.)
   - Only merge from `develop` via Pull Request

2. **`develop`** - Integration branch
   - Latest development changes
   - All features merge here first
   - Periodically merged to `main` for releases

3. **`feature/feature-name`** - Feature branches
   - Created from `develop`
   - One feature per branch
   - Merged back to `develop` via Pull Request

---

## Daily Workflow

### Starting Work on a Feature

```bash
# 1. Make sure you're up to date
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/ingestion-module
# Naming: feature/descriptive-name (use hyphens, lowercase)

# 3. Work on your code...
# ... make changes ...

# 4. Check what changed
git status
git diff

# 5. Stage changes
git add .
# Or selectively: git add src/ingestion/loader.py

# 6. Commit with clear message
git commit -m "Add image file loader with format validation"

# 7. Push to GitHub
git push origin feature/ingestion-module

# If first time pushing this branch:
# git push -u origin feature/ingestion-module
```

### Commit Message Best Practices

**Format:**
```
<type>: <short description>

<optional detailed explanation>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

**Examples:**
```bash
git commit -m "feat: Add SmolVLM model loader with ONNX support"
git commit -m "fix: Handle missing image metadata gracefully"
git commit -m "docs: Update README with model setup instructions"
git commit -m "refactor: Extract database connection to utility module"
```

---

## Creating Pull Requests

### When to Create a PR

- Feature is complete and tested
- Code follows project style
- All tests pass (when we add them)
- Ready for team review

### PR Process

1. **Push your feature branch:**
   ```bash
   git push origin feature/ingestion-module
   ```

2. **Go to GitHub repository:**
   - You'll see "Compare & pull request" button
   - Or go to **Pull requests** tab → **New pull request**

3. **Create PR:**
   - **Base:** `develop` ← **Compare:** `feature/ingestion-module`
   - **Title:** Clear, descriptive (e.g., "Add image ingestion module with format validation")
   - **Description:**
     ```markdown
     ## Changes
     - Added ImageLoader class for loading images
     - Implemented format validation (jpg, png, gif)
     - Added error handling for corrupted files
     
     ## Testing
     - Tested with 100 test images
     - All formats load correctly
     - Corrupted files handled gracefully
     
     ## Related Issues
     - Addresses Phase 1 ingestion requirements
     ```
   - **Reviewers:** Assign your 2 teammates
   - **Labels:** Add relevant labels (feature, documentation, bug, etc.)

4. **Wait for review:**
   - Team reviews code
   - Discusses changes in PR comments
   - Request changes if needed

5. **Address feedback:**
   ```bash
   # Make requested changes
   git add .
   git commit -m "Address PR feedback: Add input validation"
   git push origin feature/ingestion-module
   # PR updates automatically
   ```

6. **Merge:**
   - Once approved (at least 1 reviewer)
   - Click **Merge pull request**
   - Choose: **Squash and merge** (cleaner history)
   - Delete feature branch after merge

---

## Code Review Guidelines

### As a Reviewer

**What to check:**
- Code correctness and logic
- Follows project structure and naming
- Proper error handling
- Comments for complex logic
- No hardcoded paths or sensitive data
- Performance considerations

**How to give feedback:**
- Be specific and constructive
- Suggest improvements, don't just criticize
- Ask questions if unclear
- Approve if ready, request changes if not

**Example comments:**
```
✅ "Great error handling here! Consider also logging the error message."
✅ "This function is getting large - could we split it into smaller functions?"
✅ "Could you add a docstring explaining the parameters?"
❌ "This is wrong" (not helpful)
❌ "Bad code" (not constructive)
```

---

## Keeping Your Branch Updated

### Sync with develop regularly

```bash
# On your feature branch
git checkout feature/your-feature

# Fetch latest changes
git fetch origin

# Merge develop into your branch
git merge origin/develop

# Or use rebase (cleaner but more advanced):
# git rebase origin/develop

# If conflicts, resolve them:
# 1. Open conflicted files
# 2. Fix conflicts (between <<<< and >>>>)
# 3. git add <resolved-files>
# 4. git commit

# Push updated branch
git push origin feature/your-feature
```

---

## Branch Protection Rules (Recommended)

**Owner sets up:**

1. Go to **Settings** → **Branches**
2. Click **Add branch protection rule**
3. **Branch name pattern:** `main`
4. Enable:
   - ✅ Require a pull request before merging
   - ✅ Require approvals: 1
   - ✅ Dismiss stale pull request approvals when new commits are pushed
   - ✅ Require review from Code Owners (optional)
   - ✅ Include administrators (even you must follow rules)

5. Repeat for `develop` branch (optional but recommended)

---

## Useful Git Commands

### Status and History

```bash
git status              # See what changed
git log --oneline       # View commit history
git log --graph         # Visual branch history
git diff                # See unstaged changes
git diff --staged       # See staged changes
```

### Undoing Changes

```bash
# Undo unstaged changes to a file
git checkout -- filename.py

# Unstage a file
git reset HEAD filename.py

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes) - CAREFUL!
git reset --hard HEAD~1
```

### Branch Management

```bash
git branch              # List local branches
git branch -a           # List all branches (including remote)
git branch -d feature/old-feature  # Delete local branch
git push origin --delete feature/old-feature  # Delete remote branch
```

### Syncing with Remote

```bash
git fetch origin        # Download changes (don't merge)
git pull origin develop # Download and merge changes
git push origin develop # Upload your commits
```

---

## Collaboration Tips

### 1. Communicate

- Use PR descriptions to explain changes
- Comment on code for clarification
- Discuss big changes before implementing
- Use GitHub Issues for tracking tasks

### 2. Small, Focused Commits

```bash
# Good: Multiple small commits
git commit -m "Add image loader class"
git commit -m "Add format validation"
git commit -m "Add error handling"

# Bad: One huge commit
git commit -m "Add entire ingestion module"
```

### 3. Regular Pushes

- Push your work daily (even if incomplete)
- Prefix with `WIP:` if not ready: `git commit -m "WIP: Image loader"`
- Team can see your progress
- Acts as backup

### 4. Stay Updated

```bash
# Daily routine
git checkout develop
git pull origin develop
git checkout feature/your-feature
git merge develop
```

---

## GitHub Issues & Project Management

### Creating Issues

1. Go to **Issues** tab → **New issue**
2. **Title:** Clear task name
3. **Description:** Details, requirements, acceptance criteria
4. **Assignee:** Who's working on it
5. **Labels:** feature, bug, documentation, etc.
6. **Milestone:** v0.1, v0.2, etc.

**Example:**
```markdown
Title: Implement SmolVLM model loader

Description:
Create loader for SmolVLM-500M ONNX model with OpenVINO acceleration.

Requirements:
- Load model from models/ directory
- Initialize OpenVINO runtime
- Handle missing model file gracefully
- Add logging for load time and memory usage

Acceptance Criteria:
- [ ] Model loads successfully
- [ ] Load time logged
- [ ] Memory usage tracked
- [ ] Unit tests added
```

### Linking PRs to Issues

In PR description:
```markdown
Closes #12
Fixes #14
Related to #15
```

---

## Release Process

### Creating a Release

```bash
# 1. Merge develop to main
git checkout main
git pull origin main
git merge develop
git push origin main

# 2. Tag the release
git tag -a v0.1.0 -m "Release v0.1: Embeddings-only semantic search"
git push origin v0.1.0

# 3. Create release on GitHub
# Go to Releases → Draft a new release
# Tag: v0.1.0
# Title: v0.1.0 - Embeddings-Only Search
# Description: Release notes (what's new, changes, fixes)
```

---

## Troubleshooting

### "Git push rejected"

```bash
# Set up Git identity (first time)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### "Merge conflict"

```bash
# 1. See conflicted files
git status

# 2. Open file, look for:
<<<<<<< HEAD
Your changes
=======
Their changes
>>>>>>> branch-name

# 3. Edit to keep what you want
# 4. Remove conflict markers (<<<<, ====, >>>>)
# 5. Stage resolved file
git add resolved-file.py

# 6. Complete merge
git commit
```

### "Accidentally committed to wrong branch"

```bash
# If not yet pushed:
git reset --soft HEAD~1  # Undo commit, keep changes
git stash                # Save changes
git checkout correct-branch
git stash pop           # Apply changes
git add .
git commit -m "Correct commit message"
```

---

## Quick Reference

```bash
# Setup
git clone <url>                              # Clone repo
git config --global user.name "Name"         # Set name
git config --global user.email "email"       # Set email

# Daily workflow
git checkout develop                         # Switch to develop
git pull origin develop                      # Get latest
git checkout -b feature/name                 # Create feature
git add .                                    # Stage changes
git commit -m "message"                      # Commit
git push origin feature/name                 # Push

# Updates
git fetch origin                             # Get remote changes
git merge origin/develop                     # Merge into current
git pull origin develop                      # Fetch + merge

# Branch management
git branch                                   # List branches
git checkout branch-name                     # Switch branch
git branch -d branch-name                    # Delete branch
```

---

**Questions about Git/GitHub?** Ask the team or check [Git documentation](https://git-scm.com/doc).

**Ready to collaborate!** 🚀
