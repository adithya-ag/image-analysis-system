# 🚀 Quick Start Guide

**Get up and running in 15 minutes**

---

## Prerequisites Checklist

- [ ] Windows 11
- [ ] Python 3.11.x installed (NOT 3.13)
- [ ] Unsplash Lite dataset downloaded
- [ ] GitHub account (for team collaboration)

---

## Setup Steps

### 1. Fix Python PATH (2 minutes)

If you forgot to add Python 3.11 to PATH during installation:

**Option A - Re-run installer:**
1. Run Python 3.11.9 installer again
2. Choose "Modify" → Check "Add Python to environment variables" → Install
3. **Restart your terminal**

**Option B - Quick check:**
```bash
python --version
# Should show 3.11.x (not 3.13)
```

---

### 2. GitHub Setup (3 minutes)

```bash
# Create repo on GitHub: https://github.com/new
# Name: image-analysis-system
# Visibility: Private (for now)
# Initialize with README: Yes
# .gitignore: Python
# License: MIT

# Clone to your machine
cd C:\Users\YourName\Projects
git clone https://github.com/YOUR_USERNAME/image-analysis-system.git
cd image-analysis-system
```

**Download project files:**
- Extract the ZIP I provide with all scripts and structure
- Copy contents into your cloned repo directory
- Commit: `git add . && git commit -m "Initial project structure" && git push`

---

### 3. Virtual Environment (2 minutes)

```bash
# In project directory
python -m venv venv

# Activate (every time you work on this)
venv\Scripts\activate

# You should see (venv) prefix now
```

---

### 4. Install Dependencies (3 minutes)

```bash
# Make sure (venv) is active!
python -m pip install --upgrade pip
pip install -r requirements.txt

# Wait for installation to complete...
```

---

### 5. Prepare Test Data (3 minutes)

```bash
# Copy 100 random images from Unsplash Lite
python scripts/prepare_test_data.py --source "C:\path\to\unsplash-lite\photos" --count 100

# Example:
# python scripts/prepare_test_data.py --source "C:\Downloads\unsplash-lite\photos" --count 100
```

---

### 6. Download Models (2 minutes)

```bash
python scripts/setup_models.py
```

**Note:** This creates placeholders. For actual models, see [Model Setup Guide](docs/MODEL_SETUP.md) (we'll address this later).

---

### 7. Initialize Databases (1 minute)

```bash
python src/init_databases.py
```

---

### 8. Verify Setup (1 minute)

```bash
python scripts/verify_setup.py
```

**Expected output:**
```
✅ Checks passed: 15
❌ Checks failed: 0
⚠️  Warnings: 2
```

---

## What You Should Have Now

```
image-analysis-system/
├── venv/                        # Virtual environment ✅
├── src/                         # Source code modules ✅
├── scripts/                     # Setup scripts ✅
├── models/                      # Model placeholders ⚠️
├── databases/
│   ├── metadata.db             # SQLite database ✅
│   └── embeddings.lance/       # LanceDB directory ✅
├── data/test_images/            # 100 test images ✅
├── requirements.txt             # Dependencies ✅
├── .gitignore                   # Git config ✅
└── README.md                    # Documentation ✅
```

---

## Daily Workflow

**Every time you work:**

```bash
# 1. Open terminal in project directory
cd C:\Users\YourName\Projects\image-analysis-system

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Pull latest (if working with team)
git pull origin main

# 4. Work on code...

# 5. Deactivate when done
deactivate
```

---

## Team Workflow

**Creating a feature:**

```bash
git checkout -b feature/my-feature-name
# Make changes...
git add .
git commit -m "Add feature description"
git push origin feature/my-feature-name
# Create Pull Request on GitHub
```

---

## Next Steps

Once setup is complete:

1. ✅ Verify all checklist items
2. 📝 Report any issues
3. 🚀 **Ready for Phase 1 Implementation!**

---

## Common Issues

**"Python not found"**
→ Restart terminal after adding to PATH
→ Use `py -3.11` instead of `python`

**"No module named X"**
→ Activate virtual environment: `venv\Scripts\activate`
→ Reinstall: `pip install -r requirements.txt`

**PowerShell execution policy error**
→ Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

---

## Files Reference

- **SETUP_INSTRUCTIONS.md** - Detailed setup guide
- **README.md** - Project overview
- **requirements.txt** - Python dependencies
- **.gitignore** - Git ignore rules

---

**Questions?** Check SETUP_INSTRUCTIONS.md for detailed explanations.

**Ready to code?** Let's start Phase 1! 🎉
