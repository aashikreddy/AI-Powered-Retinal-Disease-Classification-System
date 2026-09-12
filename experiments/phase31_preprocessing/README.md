# Phase 31 Preprocessing Experiment Results

## 1. Dataset Acquisition
- Dataset: `mariaherrerot/aptos2019`
- Sourced via KaggleHub using the selective file download strategy.

## 2. Number of images downloaded
- Downloaded **366** images based exactly on the `id_code` entries in `data/test/test.csv`.
- Images were individually queried and saved to `data/test/test_images/`.
- No full dataset bundle (~8.6 GB) was downloaded.

## 3. Dataset Validation
- Verified exactly 366 rows in `test.csv`.
- Verified exactly 366 corresponding image files in `test_images/`.
- Zero missing, extra, or duplicate images.
- Images successfully open (Sample shape: 1050x1050x3).

## 4. Class Distribution (Test Set)
- Class 0: 199 (54.37%)
- Class 1: 30 (8.20%)
- Class 2: 87 (23.77%)
- Class 3: 17 (4.64%)
- Class 4: 33 (9.02%)

## 5. Model Information
- Deployed Model: `models/best_model_latest.h5`
- Input Shape: `(None, 224, 224, 3)`
- Output Shape: `(None, 5)` (DenseNet121)

## 6. Pipeline A Metrics (Rescale Only /255)
- **Accuracy:** 82.79%
- **Macro Precision:** 70.82%
- **Macro Recall:** 64.96%
- **Macro F1:** 66.45%
- **Weighted Precision:** 83.17%
- **Weighted Recall:** 82.79%
- **Weighted F1:** 82.05%

## 7. Pipeline B Metrics (ImageNet Normalization)
- **Accuracy:** 75.96%
- **Macro Precision:** 60.10%
- **Macro Recall:** 56.40%
- **Macro F1:** 56.55%
- **Weighted Precision:** 78.43%
- **Weighted Recall:** 75.96%
- **Weighted F1:** 76.45%

## 8. Pipeline A Confusion Matrix
```
190,  1,  8,  0,  0
  3, 15, 11,  0,  1
  2,  8, 68,  1,  8
  0,  0,  8,  3,  6
  0,  1,  4,  1, 27
```

## 9. Pipeline B Confusion Matrix
```
184,  5,  3,  0,  7
  1, 19,  4,  0,  6
  0, 17, 47,  1, 22
  0,  1,  9,  2,  5
  0,  2,  4,  1, 26
```

## 10. Per-class Comparison
*(See `results.json` for full detailed stats)*
- Pipeline A generally dominated across the most heavily populated classes (Class 0 and Class 2). 
- Pipeline B misclassified significantly more of Class 2 (moderate DR) as Class 1 or Class 4, severely dropping overall weighted F1.

## 11. Confidence Comparison
- Pipeline A Mean Confidence: 0.821 (Correct: 0.871, Incorrect: 0.582)
- Pipeline A Median Confidence: 0.887
- Pipeline B Mean Confidence: 0.771 (Correct: 0.849, Incorrect: 0.528)
- Pipeline B Median Confidence: 0.796

## 12. A/B Agreement Analysis
- **Total Predictions Agreed:** 305 (83.33%)
- **A Correct / B Incorrect:** 36 cases
- **B Correct / A Incorrect:** 11 cases
- **Both Correct:** 267 cases
- **Both Incorrect:** 52 cases

## 13. Disagreement Analysis
There are 61 total cases where Pipeline A and Pipeline B disagreed. In these disagreements, Pipeline A was correct ~76% of the time (36 vs 11). Pipeline B struggled specifically to resolve features corresponding to Class 2 correctly compared to A.

## 14. Best Empirical Pipeline
**Pipeline A** (Rescale /255 only). 
It significantly outperformed Pipeline B across Accuracy (+6.8%) and Weighted F1 (+5.6%).

## 15. Scientific Interpretation
Pipeline A is empirically more compatible with the deployed model on this labeled test set.
*Note: The experiment measures empirical compatibility of the candidate preprocessing pipelines with the deployed model on the available labeled test set. It does not prove the exact original training preprocessing.*

## 16. Limitations
- We only evaluated on 366 test images. 
- Some classes (Class 1, Class 3) are severely underrepresented (<35 images), which reduces statistical confidence on per-class metrics for those classes.

## 17. Exact files created
- `data/test/test_images/*.png` (366 files)
- `experiments/phase31_preprocessing/run_phase31.py`
- `experiments/phase31_preprocessing/analyze_results.py`
- `experiments/phase31_preprocessing/predictions.csv`
- `experiments/phase31_preprocessing/results.json`
- `experiments/phase31_preprocessing/confusion_matrix_A.csv`
- `experiments/phase31_preprocessing/confusion_matrix_B.csv`
- `experiments/phase31_preprocessing/README.md`

## 18. Exact files modified
- None.

## 19. Exact production files untouched
- `backend/inference.py`
- `models/best_model_latest.h5`
- All frontend files, database configuration, and authentication endpoints.

## 20. Confirmation no retraining occurred
Confirmed. The existing `.h5` model was loaded with `compile=False` strictly for inference.

## 21. Confirmation no production preprocessing was changed
Confirmed. The experiment was run offline in a sandbox script (`run_phase31.py`). `backend/inference.py` remains perfectly intact.

## 22. Confirmation no full dataset was downloaded
Confirmed. Individual file paths were used via KaggleHub to download precisely 366 images (~357.5 MB total).

## 23. Confirmation no commit/push occurred
Confirmed.
