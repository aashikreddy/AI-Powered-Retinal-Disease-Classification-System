import os
import csv
import json
import numpy as np

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXP_DIR = os.path.join(BASE_DIR, 'experiments', 'phase31_preprocessing')
RESULTS_JSON = os.path.join(EXP_DIR, 'results.json')
PREDS_CSV = os.path.join(EXP_DIR, 'predictions.csv')
CM_A_CSV = os.path.join(EXP_DIR, 'confusion_matrix_A.csv')
CM_B_CSV = os.path.join(EXP_DIR, 'confusion_matrix_B.csv')

print("=== READING PREDICTIONS ===")
results = []
with open(PREDS_CSV, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        results.append({
            'id_code': row['id_code'],
            'true_label': int(row['true_label']),
            'pred_A': int(row['pred_A']),
            'conf_A': float(row['conf_A']),
            'pred_B': int(row['pred_B']),
            'conf_B': float(row['conf_B'])
        })

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
        
        precision_arr.append(float(prec))
        recall_arr.append(float(rec))
        f1_arr.append(float(f1))
        support_arr.append(int(sup))
        
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
        metrics[f'class_{c}_support'] = int(support_arr[c])
        
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
            'true_label': int(results[i]['true_label']),
            'pred_A': int(results[i]['pred_A']),
            'conf_A': float(results[i]['conf_A']),
            'pred_B': int(results[i]['pred_B']),
            'conf_B': float(results[i]['conf_B'])
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
