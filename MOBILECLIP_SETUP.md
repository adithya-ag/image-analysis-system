# MOBILECLIP SETUP INSTRUCTIONS

**Image Analysis System v0.1**  
December 29, 2025

---

## QUICK SETUP (5 Minutes)

### Step 1: Model Files (Already Done ✅)
```
models/mobileclip_s2/
├── mobileclip_image_encoder.onnx    ← 143 MB
├── mobileclip_text_encoder.onnx     ← 254 MB
└── mobileclip_metadata.json         ← 82 bytes
```

### Step 2: Copy Code Files

Extract `mobileclip_setup.zip` and copy:

```
Your Project/
├── src/
│   ├── analysis/
│   │   └── mobileclip.py           ← NEW
│   └── config.py                   ← REPLACE
├── test_mobileclip.py              ← NEW
├── compare_models.py               ← NEW
└── run_batch_ingestion.py          ← REPLACE
```

### Step 3: Test MobileCLIP

```bash
python test_mobileclip.py data\test_images\test_0001.jpg
```

**Expected:** "🎉 ALL TESTS PASSED!"

### Step 4: Compare Models

```bash
python compare_models.py --images 10
```

**Expected:** Performance comparison of CLIP vs MobileCLIP

---

## FILE DESCRIPTIONS

### mobileclip.py (180 lines)
- MobileCLIP plugin class
- Image → 512D embedding
- Text → 512D embedding (for search)
- Same interface as CLIP

### config.py UPDATED (85 lines)
- Multi-model support
- Model selection: `Config(model_name='clip')` or `Config(model_name='mobileclip')`
- Separate LanceDB per model

### test_mobileclip.py (130 lines)
- Single image test
- Verifies MobileCLIP works
- Shows performance metrics

### compare_models.py (200 lines)
- Tests both models on same images
- Compares speed, size, quality
- Helps choose best model

### run_batch_ingestion.py UPDATED (110 lines)
- Added `--model` flag
- Usage: `--model clip` or `--model mobileclip`
- Creates separate databases per model

---

## USAGE

### Test Single Image

```bash
# CLIP
python src/test_single_image.py data\test_images\test_0001.jpg

# MobileCLIP
python test_mobileclip.py data\test_images\test_0001.jpg
```

### Compare Performance

```bash
# Test 10 images with both models
python compare_models.py --images 10

# Test 50 images
python compare_models.py --images 50
```

### Batch Processing

```bash
# Process with CLIP
python run_batch_ingestion.py --model clip

# Process with MobileCLIP
python run_batch_ingestion.py --model mobileclip
```

**Result:** Creates separate databases:
- `embeddings_clip.lance/`
- `embeddings_mobileclip.lance/`

---

## DATABASE STRUCTURE

```
databases/
├── metadata.db                      ← Shared (one SQLite)
├── embeddings_clip.lance/           ← CLIP vectors
└── embeddings_mobileclip.lance/     ← MobileCLIP vectors
```

**Why separate?**
- Compare search quality independently
- Switch models easily
- Test which works better for your photos

---

## TESTING CHECKLIST

### Phase 1: Setup
- [ ] MobileCLIP files in `models/mobileclip_s2/`
- [ ] Code files copied to project
- [ ] No file errors

### Phase 2: Single Image Test
- [ ] `python test_mobileclip.py data\test_images\test_0001.jpg`
- [ ] "ALL TESTS PASSED" message
- [ ] Embedding is 512D
- [ ] No errors

### Phase 3: Model Comparison
- [ ] `python compare_models.py --images 10`
- [ ] Both models process successfully
- [ ] Performance metrics shown
- [ ] No errors

### Phase 4: Choose Model (Optional)
- [ ] Review comparison results
- [ ] Pick CLIP or MobileCLIP based on:
  - Speed (which is faster?)
  - Size (which is smaller?)
  - Later: Quality (which searches better?)

### Phase 5: Batch Processing (Optional)
- [ ] Process with chosen model
- [ ] Or process with both to compare search quality

---

## EXPECTED RESULTS

### test_mobileclip.py
```
🎉 ALL TESTS PASSED!

MobileCLIP Performance:
   Model load: 2-5s
   Embedding generation: 0.3-0.6s
   Total: 3-6s

✅ MobileCLIP is ready to use!
```

### compare_models.py
```
📊 COMPARISON SUMMARY

✅ Success Rate:
   CLIP:       10/10 images
   MobileCLIP: 10/10 images

⏱️  Performance (Per Image):
   CLIP:       0.527s avg
   MobileCLIP: 0.XXXs avg
   → [Faster model] is XXx faster

💾 Model Size:
   CLIP:       577 MB
   MobileCLIP: 397 MB

🎉 Both models working perfectly!
```

---

## TROUBLESHOOTING

### "MobileCLIP model not found"
→ Check files in `models/mobileclip_s2/`
→ Must have both encoder files

### "Module 'mobileclip' not found"
→ Copy `mobileclip.py` to `src/analysis/`

### "Unknown model: mobileclip"
→ Replace `config.py` with updated version

### Performance is slow
→ Normal on first run
→ Model needs to warm up
→ Second run will be faster

---

## WHAT'S NEXT

After successful testing:

1. **Choose your model** based on comparison
2. **Process full dataset** with chosen model
3. **Implement search** (Phase 1 Day 3)
4. **Compare search quality** between models
5. **Pick final model** for v0.1

---

## FILES IN PACKAGE

```
mobileclip_setup.zip
├── src/
│   ├── analysis/
│   │   └── mobileclip.py           (180 lines)
│   └── config.py                   (85 lines - updated)
├── test_mobileclip.py              (130 lines)
├── compare_models.py               (200 lines)
├── run_batch_ingestion.py          (110 lines - updated)
└── MOBILECLIP_SETUP.md             (this file)
```

**Total:** 5 files, ~705 lines of code

---

**Ready to test MobileCLIP!** 🚀
