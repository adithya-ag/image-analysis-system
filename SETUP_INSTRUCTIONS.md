# Local-First Image Analysis System - Setup Instructions

**Version:** v0.1.0  
**Date:** December 19, 2025  
**Python Required:** 3.11.x

---

## 📋 Table of Contents

1. [Fix Python PATH](#1-fix-python-path)
2. [Project Setup](#2-project-setup)
3. [GitHub Repository Setup](#3-github-repository-setup)
4. [Virtual Environment](#4-virtual-environment)
5. [Install Dependencies](#5-install-dependencies)
6. [Download Models](#6-download-models)
7. [Prepare Test Data](#7-prepare-test-data)
8. [Verify Installation](#8-verify-installation)
9. [Run First Test](#9-run-first-test)

---

## 1. Fix Python PATH

Since you forgot to add Python 3.11 to PATH during installation:

### Option A: Re-run Installer (Recommended)

1. Find the Python 3.11.9 installer you downloaded
2. Run it again
3. Choose **"Modify"**
4. Click **Next**
5. Check **"Add Python to environment variables"**
6. Click **Install**

### Option B: Manual PATH Setup

1. Find your Python 3.11 installation directory (usually `C:\Users\YourName\AppData\Local\Programs\Python\Python311`)
2. Press `Win + X` → **System** → **Advanced system settings**
3. Click **Environment Variables**
4. Under **User variables**, select **Path** → **Edit**
5. Click **New** and add: `C:\Users\YourName\AppData\Local\Programs\Python\Python311`
6. Click **New** and add: `C:\Users\YourName\AppData\Local\Programs\Python\Python311\Scripts`
7. Click **OK** on all windows
8. **Restart your terminal/IDE**

### Verify Python 3.11 is Working

Open **new** Command Prompt or PowerShell:

```bash
python --version
# Should show: Python 3.11.x
```

If it still shows 3.13, use `py -3.11 --version` to check if 3.11 is available.

---

## 2. Project Setup

### Create Project Directory

Open **Command Prompt** or **PowerShell** and run:

```bash
# Navigate to where you want the project
cd C:\Users\YourName\Projects  # or wherever you keep projects

# Create project directory
mkdir image-analysis-system
cd image-analysis-system
```

### Download Project Files

Once GitHub repo is set up (see section 3), you'll clone it here. For now, we'll create the structure manually.

---

## 3. GitHub Repository Setup

### A. Create Repository

1. **Go to GitHub:** https://github.com/new
2. **Repository name:** `image-analysis-system` (or your preferred name)
3. **Description:** "Local-first image analysis with semantic search using vision models"
4. **Visibility:**
   - Private (for now during development)
   - Public (when ready for open source release)
5. **Initialize repository:**
   - ✅ Check "Add a README file"
   - ✅ Add .gitignore: **Python** template
   - ✅ Choose License: **MIT** (recommended for open source)
6. Click **Create repository**

### B. Clone Repository Locally

```bash
# In Command Prompt/PowerShell, navigate to your projects folder
cd C:\Users\YourName\Projects

# Clone the repository (replace YOUR_USERNAME with your GitHub username)
git clone https://github.com/YOUR_USERNAME/image-analysis-system.git
cd image-analysis-system
```

### C. Team Collaboration Setup

Since you have 3 people on the team:

1. **Add Collaborators:**

   - Go to repo → **Settings** → **Collaborators**
   - Click **Add people**
   - Add your 2 teammates by username/email

2. **Branch Protection (Recommended):**

   - Go to **Settings** → **Branches**
   - Click **Add branch protection rule**
   - Branch name pattern: `main`
   - Enable:
     - ✅ Require pull request reviews before merging
     - ✅ Require status checks to pass (later when CI is set up)

3. **Branching Strategy:**
   ```
   main (protected, production-ready code)
   └── develop (integration branch)
       ├── feature/ingestion-module
       ├── feature/analysis-module
       └── feature/search-module
   ```

**Your workflow:**

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, commit
git add .
git commit -m "Add feature description"

# Push to GitHub
git push origin feature/your-feature-name

# Create Pull Request on GitHub for team review
```

---

## 4. Virtual Environment

**CRITICAL:** Always use virtual environment to avoid dependency conflicts.

### Create Virtual Environment

In your project directory (`image-analysis-system`):

```bash
# Using Python 3.11 specifically
python -m venv venv

# If python still points to 3.13, use:
py -3.11 -m venv venv
```

### Activate Virtual Environment

**Every time you work on this project, activate the virtual environment first!**

```bash
# Windows Command Prompt
venv\Scripts\activate

# Windows PowerShell (if you get execution policy error, see below)
venv\Scripts\Activate.ps1
```

**PowerShell Execution Policy Error?**
If you get "cannot be loaded because running scripts is disabled":

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### When Virtual Environment is Active

You'll see `(venv)` prefix in your terminal:

```
(venv) C:\Users\YourName\Projects\image-analysis-system>
```

**Important:**

- ✅ Install packages ONLY when `(venv)` is active
- ✅ Run scripts ONLY when `(venv)` is active
- ❌ Never install packages globally

### Deactivate (when done working)

```bash
deactivate
```

---

## 5. Install Dependencies

**Make sure virtual environment is activated first!** (you should see `(venv)`)

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist yet (we'll create it), manually install:

```bash
pip install numpy==1.24.3
pip install opencv-python==4.8.1.78
pip install pillow==10.1.0
pip install onnxruntime==1.16.3
pip install openvino==2023.2.0
pip install lancedb==0.3.3
pip install transformers==4.36.0
pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu
pip install requests==2.31.0
pip install tqdm==4.66.1
```

**Why these specific versions?** Tested compatibility with Python 3.11 and ONNX Runtime.

---

## 6. Download Models

We'll use an automated script to download and prepare models.

### Run Model Setup Script

**Make sure virtual environment is activated!**

```bash
# In project root directory
python scripts/setup_models.py
```

**What this script does:**

1. Creates `models/` directory
2. Downloads SmolVLM-500M ONNX model (~500MB)
3. Downloads MobileCLIP-S2 ONNX model (~100MB)
4. Verifies model integrity
5. Creates model config file

**Expected output:**

```
🔧 Model Setup Starting...
📥 Downloading SmolVLM-500M...
✅ SmolVLM-500M downloaded (500.2 MB)
📥 Downloading MobileCLIP-S2...
✅ MobileCLIP-S2 downloaded (98.7 MB)
✅ All models ready!
```

**If download fails:** Script will provide direct download links for manual download.

---

## 7. Prepare Test Data

You downloaded Unsplash Lite - great choice!

### Extract and Organize Images

1. **Extract Unsplash Lite:**

   - Extract the downloaded zip file
   - You'll get a folder with ~25,000 images

2. **Select 100 Test Images:**

   ```bash
   # We'll create a script to copy 100 random images
   python scripts/prepare_test_data.py --source "C:\path\to\unsplash\photos" --count 100
   ```

3. **Result:**
   - Creates `data/test_images/` folder
   - Copies 100 diverse images
   - Creates metadata file with image info

**Manual alternative:** Just copy 100 images manually to `data/test_images/`

---

## 8. Verify Installation

Run the verification script:

```bash
python scripts/verify_setup.py
```

**Expected output:**

```
✅ Python version: 3.11.x
✅ Virtual environment: Active
✅ Dependencies: All installed
✅ Models: SmolVLM-500M, MobileCLIP-S2
✅ Database directories: Created
✅ Test images: 100 found
🎉 Setup complete! Ready to run Phase 1.
```

---

## 9. Run First Test

### Initialize Databases

```bash
python src/init_databases.py
```

**Creates:**

- `databases/metadata.db` (SQLite)
- `databases/embeddings.lance/` (LanceDB)

### Process Single Image Test

```bash
python src/test_single_image.py data/test_images/sample_001.jpg
```

**Expected output:**

```
🖼️  Loading image: sample_001.jpg
🤖 Loading SmolVLM-500M model...
✅ Model loaded (2.3s)
🔄 Generating embedding...
✅ Embedding generated: 512 dimensions (0.8s)
💾 Storing in databases...
✅ Stored in SQLite: image_id=img_001
✅ Stored in LanceDB: vector stored
🔍 Testing retrieval...
✅ Retrieved image_id from vector search
✅ Single image test PASSED!
```

---

## 🎯 Success Checklist

Before moving to Phase 2, verify:

- [ ] Python 3.11 installed and in PATH
- [ ] Virtual environment created and activated
- [ ] All dependencies installed without errors
- [ ] Both models downloaded successfully
- [ ] Test images prepared (100 images in `data/test_images/`)
- [ ] Databases initialized
- [ ] Single image test passed
- [ ] GitHub repository created and cloned
- [ ] Team members added as collaborators

---

## 🆘 Troubleshooting

### "Python not found" or wrong version

- Restart terminal/IDE after adding to PATH
- Use `py -3.11` instead of `python`
- Check `python --version` shows 3.11.x

### "No module named 'onnxruntime'"

- Verify virtual environment is activated (see `(venv)` prefix)
- Re-run `pip install -r requirements.txt`

### Model download fails

- Check internet connection
- Script will provide manual download links
- Download manually and place in `models/` directory

### Git push rejected

- Set up Git identity first:
  ```bash
  git config --global user.name "Your Name"
  git config --global user.email "your.email@example.com"
  ```

### PowerShell script execution error

- Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

---

## 📚 Quick Reference

### Daily Workflow

```bash
# 1. Open terminal in project directory
cd C:\Users\YourName\Projects\image-analysis-system

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Pull latest changes (if working with team)
git pull origin develop

# 4. Create feature branch (for new work)
git checkout -b feature/my-feature

# 5. Work on code...

# 6. Commit changes
git add .
git commit -m "Description of changes"

# 7. Push to GitHub
git push origin feature/my-feature

# 8. Deactivate when done
deactivate
```

---

## 📞 Next Steps

Once setup is complete:

1. ✅ Verify all checklist items above
2. 📝 Report any issues encountered
3. 🚀 Ready for **Phase 1 Implementation** (Core pipeline development)

**Setup Questions?** Document any issues you encounter - we'll address them immediately.
