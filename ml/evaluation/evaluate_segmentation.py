"""
Held-Out Test Set Evaluation Pipeline for Phase 17: Customer & Persona Segmentation.

Evaluates unsupervised clustering on 1,200 held-out test profiles:
- Computes Silhouette Score, Davies-Bouldin Index, Calinski-Harabasz Index
- Measures Ground-Truth Persona Classification Purity (Adjusted Rand Index & Adjusted Mutual Info)
- Evaluates Centroid Feature Archetype Separation
"""

import json
import os
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    adjusted_mutual_info_score,
    adjusted_rand_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    homogeneity_completeness_v_measure,
    silhouette_score,
)

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.segmentation_rules import (  # noqa: E402
    ENGINEERED_NUMERICAL_FEATURES_SEGMENTATION,
    PERSONA_ARCHETYPES,
    RAW_FEATURE_COLUMNS_SEGMENTATION,
    TARGET_COLUMN_SEGMENTATION,
    engineer_segmentation_features,
)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
TEST_FILE = os.path.join(PROCESSED_DIR, "segmentation_test.csv")


def main():
    print("=" * 85)
    print("Phase 17: Customer Persona Segmentation — Held-Out Test Evaluation")
    print("=" * 85)

    if not os.path.exists(TEST_FILE):
        print(f"[error] Test file not found: {TEST_FILE}")
        sys.exit(1)

    model_path = os.path.join(MODEL_DIR, "best_segmentation_model.pkl")
    pca_path = os.path.join(MODEL_DIR, "segmentation_pca.pkl")
    scaler_path = os.path.join(MODEL_DIR, "segmentation_scaler.pkl")
    metadata_path = os.path.join(MODEL_DIR, "segmentation_metadata.json")

    if not os.path.exists(model_path) or not os.path.exists(pca_path):
        print("[error] Segmentation model artifacts not found. Run train_segmentation.py first.")
        sys.exit(1)

    model = joblib.load(model_path)
    pca = joblib.load(pca_path)
    scaler = joblib.load(scaler_path)

    with open(metadata_path, "r") as f:
        meta = json.load(f)

    raw_test_df = pd.read_csv(TEST_FILE)
    print(f"[info] Evaluating model '{meta['best_model_name']}' on {len(raw_test_df)} held-out profiles\n")

    test_df = engineer_segmentation_features(raw_test_df)
    num_cols = meta.get("engineered_numerical_features", ENGINEERED_NUMERICAL_FEATURES_SEGMENTATION)
    cluster_map = {int(k): int(v) for k, v in meta.get("cluster_to_persona_map", {}).items()}

    X_test_raw = test_df[num_cols].values
    y_test_gt = test_df[TARGET_COLUMN_SEGMENTATION].values

    # Transform
    X_test_scaled = scaler.transform(X_test_raw)
    X_test_pca = pca.transform(X_test_scaled)

    # Predict cluster labels
    raw_cluster_preds = model.predict(X_test_pca)
    mapped_persona_preds = np.array([cluster_map.get(c, c) for c in raw_cluster_preds])

    # Unsupervised Metrics
    sil = silhouette_score(X_test_pca, raw_cluster_preds)
    ch = calinski_harabasz_score(X_test_pca, raw_cluster_preds)
    db = davies_bouldin_score(X_test_pca, raw_cluster_preds)

    # Ground-truth Cluster Purity Metrics
    ari = adjusted_rand_score(y_test_gt, mapped_persona_preds)
    ami = adjusted_mutual_info_score(y_test_gt, mapped_persona_preds)
    homo, comp, v_meas = homogeneity_completeness_v_measure(y_test_gt, mapped_persona_preds)

    print("=================================================================")
    print(f"Silhouette Score (Cluster Separation):    {sil:6.4f} (Benchmark: >= 0.50)")
    print(f"Davies-Bouldin Index (Cluster Compactness):{db:6.4f} (Benchmark: <= 0.85)")
    print(f"Calinski-Harabasz Variance Ratio:         {ch:7.1f}")
    print(f"Adjusted Rand Index (ARI Purity):         {ari:6.4f}")
    print(f"Adjusted Mutual Information (AMI):        {ami:6.4f}")
    print(f"Homogeneity Score:                        {homo:6.4f}")
    print(f"V-Measure Score:                          {v_meas:6.4f}")
    print("=================================================================\n")

    print("Persona Archetype Distribution on Test Set:")
    for cid in range(6):
        p_info = PERSONA_ARCHETYPES[cid]
        count = int(np.sum(mapped_persona_preds == cid))
        print(f"  [{p_info['id']:30s}] -> {count:4d} users ({count/len(test_df)*100:5.1f}%)")


if __name__ == "__main__":
    main()
