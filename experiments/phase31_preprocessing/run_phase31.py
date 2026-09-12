import os
import shutil
import csv
import numpy as np
import kagglehub
import cv2
import json
import time
import tensorflow as tf

os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEST_CSV = os.path.join(BASE_DIR, 'data', 'test', 'test.csv')
TEST_IMAGES_DIR = os.path.join(BASE_DIR, 'data', 'test', 'test_images')
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'best_model_latest.h5')
EXP_DIR = os.path.join(BASE_DIR, 'experiments', 'phase31_preprocessing')
RESULTS_JSON = os.path.join(EXP_DIR, 'results.json')
PREDS_CSV = os.path.join(EXP_DIR, 'predictions.csv')
CM_A_CSV = os.path.join(EXP_DIR, 'confusion_matrix_A.csv')
CM_B_CSV = os.path.join(EXP_DIR, 'confusion_matrix_B.csv')

os.makedirs(TEST_IMAGES_DIR, exist_ok=True)
os.makedirs(EXP_DIR, exist_ok=True)

print("=== STEP 1: READ TEST LABELS ===")
data_rows = []
with open(TEST_CSV, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        data_rows.append(row)

print(f"Total rows: {len(data_rows)}")
# Verify unique IDs
id_codes = [r['id_code'] for r in data_rows]
assert len(set(id_codes)) == len(data_rows)

class_counts = {0:0, 1:0, 2:0, 3:0, 4:0}
for r in data_rows:
    diag = int(r['diagnosis'])
    assert diag in class_counts
    class_counts[diag] += 1

print("\nClass Distribution:")
for cls in range(5):
    count = class_counts[cls]
    print(f"Class {cls}: {count} ({(count/len(data_rows))*100:.2f}%)")

print("\n=== STEP 2: DOWNLOAD THE 366 TEST IMAGES ===")
start_time = time.time()
downloaded_count = 0
for idx, row in enumerate(data_rows):
    id_code = row['id_code']
    target_path = os.path.join(TEST_IMAGES_DIR, f"{id_code}.png")
    if not os.path.exists(target_path):
        try:
            cached_path = kagglehub.dataset_download(
                'mariaherrerot/aptos2019',
                path=f'test_images/test_images/{id_code}.png'
            )
            shutil.copy(cached_path, target_path)
            downloaded_count += 1
            if downloaded_count % 50 == 0:
                print(f"Downloaded {downloaded_count} / {len(data_rows)} images...")
        except Exception as e:
            print(f"Error downloading {id_code}: {e}")
            
print(f"Download complete. Fetched {downloaded_count} new images in {time.time() - start_time:.2f}s.")

print("\n=== STEP 3: VALIDATE DATASET COMPLETELY ===")
images = os.listdir(TEST_IMAGES_DIR)
print(f"Images in dir: {len(images)}")
assert len(images) == len(data_rows)

for idx, row in enumerate(data_rows):
    id_code = row['id_code']
    img_path = os.path.join(TEST_IMAGES_DIR, f"{id_code}.png")
    assert os.path.exists(img_path)
    # Open image
    img = cv2.imread(img_path)
    assert img is not None
    if idx == 0:
        print(f"Sample image shape: {img.shape}")

print("\n=== STEP 4: LOAD DEPLOYED MODEL ===")
model = tf.keras.models.load_model(MODEL_PATH, compile=False)
print("Model loaded successfully.")
print(f"Input shape: {model.input_shape}")
print(f"Output shape: {model.output_shape}")

print("\n=== STEP 5 & 6: PIPELINE A & B INFERENCE ===")
results = []

def preprocess_A(img):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (224, 224))
    img_float = img_resized.astype('float32')
    img_norm = img_float / 255.0
    return np.expand_dims(img_norm, axis=0)

def preprocess_B(img):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (224, 224))
    img_float = img_resized.astype('float32')
    img_norm = img_float / 255.0
    
    mean = np.array([0.485, 0.456, 0.406], dtype='float32')
    std = np.array([0.229, 0.224, 0.225], dtype='float32')
    img_norm = (img_norm - mean) / std
    return np.expand_dims(img_norm, axis=0)

for idx, row in enumerate(data_rows):
    id_code = row['id_code']
    label = int(row['diagnosis'])
    img_path = os.path.join(TEST_IMAGES_DIR, f"{id_code}.png")
    img = cv2.imread(img_path)
    
    # Pipeline A
    input_A = preprocess_A(img)
    preds_A = model.predict(input_A, verbose=0)[0]
    pred_A_label = int(np.argmax(preds_A))
    conf_A = float(np.max(preds_A))
    
    # Pipeline B
    input_B = preprocess_B(img)
    preds_B = model.predict(input_B, verbose=0)[0]
    pred_B_label = int(np.argmax(preds_B))
    conf_B = float(np.max(preds_B))
    
    results.append({
        'id_code': id_code,
        'true_label': label,
        'pred_A': pred_A_label,
        'conf_A': conf_A,
        'probs_A': preds_A.tolist(),
        'pred_B': pred_B_label,
        'conf_B': conf_B,
        'probs_B': preds_B.tolist()
    })
    
    if (idx + 1) % 50 == 0:
        print(f"Processed {idx + 1} / {len(data_rows)}")

# Save PREDS_CSV
with open(PREDS_CSV, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['id_code', 'true_label', 'pred_A', 'conf_A', 'probs_A', 'pred_B', 'conf_B', 'probs_B'])
    writer.writeheader()
    for r in results:
        r_out = r.copy()
        r_out['probs_A'] = json.dumps(r_out['probs_A'])
        r_out['probs_B'] = json.dumps(r_out['probs_B'])
        writer.writerow(r_out)

print("\n=== STEP 7, 8, 9: METRICS & ANALYSIS ===")

def calc_confusion_matrix(y_true, y_pred, num_classes=5):
    cm = np.zeros((num_classes, num_classes), dtype=int)
    for t, p in zip(y_true, y_pred):
        cm[t][p] += 1
    return cm

def calc_metrics(y_true, y_pred, confs, prefix):
    cm = calc_confusion_matrix(y_true, y_pred)
    
    precision_arr = []
    recall_arr = []
    f1_arr = []
    support_arr = []
    
    for c in range(5):
        tp = cm[c][c]
        fp = sum(cm[i][c] for i in range(5)) - tp
        fn = sum(cm[c][i] for i in range(5)) - tp
        
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        sup = tp + fn
        
        precision_arr.append(prec)
        recall_arr.append(rec)
        f1_arr.append(f1)
        support_arr.append(sup)
        
    metrics = {
        'accuracy': float(np.trace(cm)) / len(y_true),
        'precision_macro': float(np.mean(precision_arr)),
        'recall_macro': float(np.mean(recall_arr)),
        'f1_macro': float(np.mean(f1_arr)),
        'mean_conf': float(np.mean(confs)),
        'median_conf': float(np.median(confs))
    }
    
    # Weighted
    total_supp = sum(support_arr)
    metrics['precision_weighted'] = float(sum(p*s for p,s in zip(precision_arr, support_arr)) / total_supp)
    metrics['recall_weighted'] = float(sum(r*s for r,s in zip(recall_arr, support_arr)) / total_supp)
    metrics['f1_weighted'] = float(sum(f*s for f,s in zip(f1_arr, support_arr)) / total_supp)
    
    correct_mask = (y_true == y_pred)
    incorrect_mask = ~correct_mask
    
    metrics['correct_conf'] = float(np.mean(np.array(confs)[correct_mask])) if np.sum(correct_mask) > 0 else 0.0
    metrics['incorrect_conf'] = float(np.mean(np.array(confs)[incorrect_mask])) if np.sum(incorrect_mask) > 0 else 0.0
    
    # Per class
    for c in range(5):
        metrics[f'class_{c}_precision'] = float(precision_arr[c])
        metrics[f'class_{c}_recall'] = float(recall_arr[c])
        metrics[f'class_{c}_f1'] = float(f1_arr[c])
        metrics[f'class_{c}_support'] = support_arr[c]
        
    return metrics, cm

y_true = np.array([r['true_label'] for r in results])
y_pred_A = np.array([r['pred_A'] for r in results])
y_pred_B = np.array([r['pred_B'] for r in results])
confs_A = np.array([r['conf_A'] for r in results])
confs_B = np.array([r['conf_B'] for r in results])

metrics_A, cm_A = calc_metrics(y_true, y_pred_A, confs_A, "A")
metrics_B, cm_B = calc_metrics(y_true, y_pred_B, confs_B, "B")

np.savetxt(CM_A_CSV, cm_A, delimiter=',', fmt='%d')
np.savetxt(CM_B_CSV, cm_B, delimiter=',', fmt='%d')

# Agreement
agreed = (y_pred_A == y_pred_B)
A_corr = (y_pred_A == y_true)
B_corr = (y_pred_B == y_true)

comparison = {
    'total_agree': int(np.sum(agreed)),
    'agree_pct': float(np.mean(agreed)),
    'A_corr_B_incorr': int(np.sum(A_corr & ~B_corr)),
    'B_corr_A_incorr': int(np.sum(B_corr & ~A_corr)),
    'both_corr': int(np.sum(A_corr & B_corr)),
    'both_incorr': int(np.sum(~A_corr & ~B_corr))
}

# Disagreements
disagreements = []
for i in range(len(results)):
    if not agreed[i]:
        disagreements.append({
            'id_code': results[i]['id_code'],
            'true_label': results[i]['true_label'],
            'pred_A': results[i]['pred_A'],
            'conf_A': results[i]['conf_A'],
            'pred_B': results[i]['pred_B'],
            'conf_B': results[i]['conf_B']
        })

final_results = {
    'metrics_A': metrics_A,
    'metrics_B': metrics_B,
    'comparison': comparison,
    'disagreements': disagreements
}

with open(RESULTS_JSON, 'w') as f:
    json.dump(final_results, f, indent=4)

print("\n=== EXPERIMENT COMPLETE ===")
print(f"Results saved to {EXP_DIR}")
