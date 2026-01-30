# MOBILECLIP - QUICK REFERENCE

**5-Minute Setup**

---

## FILES TO COPY

```
mobileclip_setup/
├── src/analysis/mobileclip.py    → Your_Project/src/analysis/mobileclip.py
├── src/config.py                 → Your_Project/src/config.py (REPLACE)
├── test_mobileclip.py            → Your_Project/test_mobileclip.py
├── compare_models.py             → Your_Project/compare_models.py
└── run_batch_ingestion.py        → Your_Project/run_batch_ingestion.py (REPLACE)
```

---

## COMMANDS

```bash
# 1. Test MobileCLIP
python test_mobileclip.py data\test_images\test_0001.jpg

# 2. Compare models (10 images)
python compare_models.py --images 10

# 3. Batch with CLIP
python run_batch_ingestion.py --model clip

# 4. Batch with MobileCLIP
python run_batch_ingestion.py --model mobileclip
```

---

## WHAT EACH FILE DOES

**mobileclip.py** - MobileCLIP plugin (image/text → 512D embeddings)

**config.py** - Multi-model support (switch between CLIP/MobileCLIP)

**test_mobileclip.py** - Test single image with MobileCLIP

**compare_models.py** - Compare CLIP vs MobileCLIP performance

**run_batch_ingestion.py** - Batch processing with model selection

---

## EXPECTED RESULTS

### Test (3-6 seconds)
```
🎉 ALL TESTS PASSED!
✅ MobileCLIP is ready to use!
```

### Compare (1-2 minutes for 10 images)
```
📊 COMPARISON SUMMARY
✅ Both models working
⏱️  Performance comparison shown
💾 Model sizes shown
```

---

## DATABASE STRUCTURE

```
databases/
├── metadata.db                  ← Shared
├── embeddings_clip.lance/       ← CLIP only
└── embeddings_mobileclip.lance/ ← MobileCLIP only
```

**Separate databases = Easy comparison!**

---

## TROUBLESHOOTING

**"Model not found"** → Check `models/mobileclip_s2/` has 3 files

**"Module not found"** → Copy `mobileclip.py` to `src/analysis/`

**"Unknown model"** → Replace `config.py` with new version

---

## SUCCESS CHECKLIST

- [ ] 5 files copied
- [ ] Test passed
- [ ] Comparison ran
- [ ] No errors
- [ ] Ready for next phase

**Done? Report results!** ✅
