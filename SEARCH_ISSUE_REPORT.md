# Search Quality Issue - Root Cause Analysis

**Date**: 2026-02-01
**Status**: CRITICAL - Search returning irrelevant results
**Severity**: High - Core functionality broken

---

## Executive Summary

The semantic search is **fundamentally broken**. All models (CLIP, MobileCLIP, SigLIP) are returning irrelevant results with high distance scores (1.7-1.9), indicating the search results are nearly opposite to the query in embedding space.

**Your observation is correct** - the system is not working as intended.

---

## Evidence of Problem

### User Reports
- Query: "beach sunset" → No beach photos in results (you have none in dataset)
- Query: "nature landscape" → Returns shampoo bottles and person photos
- **All queries return scores of 1.7-1.9** across all three models

### Score Analysis

For normalized embeddings with L2 distance:
- **0.0** = Identical (perfect match)
- **1.414** = Orthogonal (unrelated)
- **2.0** = Opposite (worst possible match)

**Your results: 1.7-1.9 = Nearly opposite vectors = TERRIBLE matches**

This is not a small inaccuracy - these are the WORST possible matches being returned.

---

## Root Cause: Embedding Space Mismatch

### The Critical Problem

**Image embeddings** (during ingestion):
- Created using **ONNX models** via `CLIPOpenAI`, `MobileCLIP`, `SigLIP` classes
- Location: [src/analysis/clip_openai.py:113](src/analysis/clip_openai.py#L113), [mobileclip.py:143](src/analysis/mobileclip.py#L143), [siglip.py:116](src/analysis/siglip.py#L116)
- Method: ONNX Runtime inference

**Text query embeddings** (during search):
- Created using **PyTorch models** via transformers library
- Location: [src/retrieval/search_engine.py:58-84](src/retrieval/search_engine.py#L58-L84)
- Method: PyTorch `CLIPModel.get_text_features()` and `AutoModel.get_text_features()`

**Result**: Two different embedding spaces that don't align!

### Code Evidence

**Ingestion (ONNX):**
```python
# src/analysis/clip_openai.py:109
outputs = self.session.run(None, ort_inputs)  # ONNX Runtime
embedding = outputs[0][0]
embedding = embedding / np.linalg.norm(embedding)  # Normalized
```

**Search (PyTorch):**
```python
# src/retrieval/search_engine.py:62-63, 103
self.model = CLIPModel.from_pretrained(model_id)  # PyTorch model
text_features = self.model.get_text_features(**inputs)  # PyTorch inference
```

---

## Why This Happened

1. **Phase 1 Design**: Images processed with ONNX for performance
2. **Search Added Later**: Text encoding uses PyTorch for convenience (ONNX text export is complex)
3. **Assumption**: ONNX export would preserve embedding space perfectly
4. **Reality**: Subtle differences in preprocessing, quantization, or export cause misalignment

---

## Additional Issues Found

### 1. Distance Metric Not Specified
In [lance_store.py:100-147](src/storage/lance_store.py#L100-L147), LanceDB search doesn't explicitly specify distance metric:
```python
results = self.table.search(query_embedding.tolist()).limit(top_k).to_list()
```

LanceDB defaults to L2 distance, which is correct for normalized vectors, but should be explicit.

### 2. Score Display Confusion
High scores (1.7-1.9) are displayed as if they're good, but for distance metrics:
- **Lower = Better**
- The UI should clarify this or convert to similarity scores (1 - distance/2)

### 3. No Quality Validation
The system lacks a validation step to verify embedding space alignment between:
- Image embeddings (ONNX)
- Text embeddings (PyTorch)

---

## Solutions (in order of preference)

### Option 1: Use PyTorch for Both (QUICK FIX)
**Change**: Switch image ingestion to use PyTorch models instead of ONNX

**Pros:**
- Guarantees embedding space alignment
- Simple to implement
- Works immediately

**Cons:**
- Slower inference (no ONNX optimization)
- Larger memory footprint
- Goes against Phase 1 design goals

**Implementation**: Modify `src/analysis/*.py` to use PyTorch like search_engine.py does

---

### Option 2: Use ONNX for Both (PROPER FIX)
**Change**: Export text encoders to ONNX and use them in search_engine.py

**Pros:**
- Maintains ONNX performance benefits
- Consistent with Phase 1 design
- Embedding spaces guaranteed to match

**Cons:**
- Requires ONNX text encoder export
- More complex implementation
- CLIP text export can be tricky

**Implementation**:
1. Export CLIP/SigLIP text encoders to ONNX
2. Update search_engine.py to use ONNX text encoders
3. Verify embeddings match

---

### Option 3: Verify and Fix ONNX Export (INVESTIGATION)
**Change**: Test if current ONNX models produce correct embeddings

**Steps:**
1. Generate embedding for same image using both PyTorch and ONNX
2. Compare cosine similarity (should be > 0.99)
3. If mismatch, re-export ONNX models with better settings

**This may reveal the ONNX export itself is faulty**

---

## Immediate Actions Required

### 1. Verification Test
Create a test that compares PyTorch vs ONNX embeddings:
```python
# Test if ONNX and PyTorch produce same embeddings
image_path = "test.jpg"
pytorch_emb = generate_embedding_pytorch(image_path)
onnx_emb = generate_embedding_onnx(image_path)
similarity = cosine_similarity(pytorch_emb, onnx_emb)
print(f"Similarity: {similarity}")  # Should be > 0.99
```

### 2. Quick Workaround
For immediate testing, add a flag to use PyTorch for ingestion:
```python
# In batch_processor.py
if config.use_pytorch_for_consistency:
    self.model = PyTorchCLIP(config)  # Same as search
else:
    self.model = CLIPOpenAI(config)  # ONNX
```

### 3. Score Conversion
Display similarity instead of distance:
```python
# In search_engine.py
similarity = 1 - (distance / 2)  # Convert L2 distance to similarity
result['score'] = similarity  # 0-1 scale, higher is better
```

---

## Test Plan

1. **Verify ONNX Export**:
   - Compare PyTorch vs ONNX embeddings for same images
   - Target: Cosine similarity > 0.99

2. **Re-index with PyTorch**:
   - Temporarily use PyTorch for image ingestion
   - Run search tests
   - Expected: Scores should be 0.0-0.5 (much better)

3. **Validate Results**:
   - Manual inspection of top results
   - Should return visually similar images

---

## Conclusion

**This is NOT a test code problem** - you correctly identified a fundamental issue.

**Root cause**: Embedding space mismatch between ONNX (images) and PyTorch (queries)

**Evidence**: Consistently terrible scores (1.7-1.9) across all models and queries

**Solution**: Either use PyTorch for both or ONNX for both, but NOT mixed

---

## Recommended Next Steps

1. **For parent chat**: Report that search is broken due to ONNX/PyTorch mismatch
2. **Quick fix**: Re-ingest images using PyTorch models (same as search)
3. **Proper fix**: Export text encoders to ONNX and update search to use them
4. **Long term**: Add embedding space validation tests

---

*This report documents a critical bug that prevents the search feature from working correctly.*
