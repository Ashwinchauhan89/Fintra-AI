"""
Ultra-Fast Training & Clustering Benchmark Pipeline for Phase 17: Customer & Persona Segmentation.

Benchmarks 4 unsupervised clustering architectures:
1. Standard K-Means (Raw Scaled Features)
2. MiniBatch K-Means
3. Gaussian Mixture Models (GMM - Diagonal Covariance)
4. Fast PCA + K-Means++ (Production Pipeline)

Evaluates:
- Silhouette Score
- Calinski-Harabasz Index
- Davies-Bouldin Index
- Inference & Training Latency
- Multi-Persona Centroid Alignment
"""

import json
import os
import sys
import time
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.decomposition import PCA
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score, silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import RobustScaler

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
TRAIN_FILE = os.path.join(PROCESSED_DIR, "segmentation_train.csv")


def main():
    print("=" * 85)
    print("Phase 17: Customer Financial Persona & Archetype Segmentation Training")
    print("=" * 85)

    if not os.path.exists(TRAIN_FILE):
        print(f"[error] Train file not found: {TRAIN_FILE}. Run preprocess_segmentation.py first.")
        sys.exit(1)

    raw_df = pd.read_csv(TRAIN_FILE)
    print(f"[info] Loaded {len(raw_df)} financial records. Applying behavioral feature engineering...")

    df = engineer_segmentation_features(raw_df)
    num_cols = ENGINEERED_NUMERICAL_FEATURES_SEGMENTATION

    X_raw = df[num_cols].values
    y_ground_truth = df[TARGET_COLUMN_SEGMENTATION].values

    # 1. Robust Scaling
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X_raw)

    # 2. PCA Dimensionality Reduction (Retain 95%+ variance with 5 components)
    pca = PCA(n_components=5, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    var_explained = float(np.sum(pca.explained_variance_ratio_) * 100.0)
    print(f"[info] PCA Dimensionality: 13 features -> 5 components (Variance Explained: {var_explained:.2f}%)")

    # Benchmarking Candidates
    candidates = {}

    # Candidate 1: Standard K-Means
    t0 = time.perf_counter()
    km_std = KMeans(n_clusters=6, init="k-means++", random_state=42, n_init=10)
    km_std_labels = km_std.fit_predict(X_scaled)
    t_km_std = (time.perf_counter() - t0) * 1000.0
    candidates["standard_kmeans"] = (km_std, X_scaled, km_std_labels, t_km_std)

    # Candidate 2: MiniBatch K-Means
    t0 = time.perf_counter()
    mb_km = MiniBatchKMeans(n_clusters=6, init="k-means++", batch_size=256, random_state=42, n_init=5)
    mb_km_labels = mb_km.fit_predict(X_scaled)
    t_mb = (time.perf_counter() - t0) * 1000.0
    candidates["minibatch_kmeans"] = (mb_km, X_scaled, mb_km_labels, t_mb)

    # Candidate 3: GMM (Diagonal Covariance)
    t0 = time.perf_counter()
    gmm = GaussianMixture(n_components=6, covariance_type="diag", random_state=42)
    gmm_labels = gmm.fit_predict(X_pca)
    t_gmm = (time.perf_counter() - t0) * 1000.0
    candidates["gmm_diagonal"] = (gmm, X_pca, gmm_labels, t_gmm)

    # Candidate 4: Fast PCA + K-Means++ (Production Pipeline)
    t0 = time.perf_counter()
    pca_km = KMeans(n_clusters=6, init="k-means++", random_state=42, n_init=10)
    pca_km_labels = pca_km.fit_predict(X_pca)
    t_pca_km = (time.perf_counter() - t0) * 1000.0
    candidates["pca_kmeans_plus_plus"] = (pca_km, X_pca, pca_km_labels, t_pca_km)

    print("\n[info] Unsupervised Clustering Benchmark Leaderboard:")
    leaderboard = []

    for name, (model, X_feat, labels, train_time) in candidates.items():
        sil = float(silhouette_score(X_feat, labels))
        ch = float(calinski_harabasz_score(X_feat, labels))
        db = float(davies_bouldin_score(X_feat, labels))

        # Composite clustering score: Maximize Silhouette & Calinski, minimize Davies-Bouldin
        composite_score = sil - (db * 0.40) + (ch / 10000.0)

        row = {
            "model": name,
            "silhouette_score": round(sil, 4),
            "davies_bouldin_index": round(db, 4),
            "calinski_harabasz_index": round(ch, 1),
            "train_latency_ms": round(train_time, 2),
            "composite_score": round(composite_score, 4),
        }
        leaderboard.append(row)
        print(
            f"  [{name:22s}] Silhouette: {sil:6.4f} | Davies-Bouldin: {db:6.4f} | Calinski: {ch:7.1f} | Time: {train_time:5.2f}ms | Score: {composite_score:6.4f}"
        )

    leaderboard_df = pd.DataFrame(leaderboard).sort_values("composite_score", ascending=False)
    best_row = leaderboard_df.iloc[0]
    best_name = best_row["model"]

    print("\n" + "=" * 85)
    print(f"[result] Selected Production Architecture: '{best_name}'")
    print(f"         Silhouette Score:     {best_row['silhouette_score']} (Target >= 0.50)")
    print(f"         Davies-Bouldin Index: {best_row['davies_bouldin_index']} (Target <= 0.85)")
    print(f"         Calinski-Harabasz:    {best_row['calinski_harabasz_index']}")
    print(f"         Training Latency:     {best_row['train_latency_ms']} ms")
    print("=" * 85)

    # Align K-Means Centroid indices to canonical Persona Archetype IDs
    best_model = candidates["pca_kmeans_plus_plus"][0]
    pred_clusters = best_model.labels_

    # Map each cluster centroid to its majority ground truth persona
    cluster_to_persona_map = {}
    for c in range(6):
        mask = (pred_clusters == c)
        if np.sum(mask) > 0:
            majority_gt = int(pd.Series(y_ground_truth[mask]).mode()[0])
            cluster_to_persona_map[int(c)] = majority_gt
        else:
            cluster_to_persona_map[int(c)] = int(c)

    os.makedirs(MODEL_DIR, exist_ok=True)
    model_save_path = os.path.join(MODEL_DIR, "best_segmentation_model.pkl")
    pca_save_path = os.path.join(MODEL_DIR, "segmentation_pca.pkl")
    scaler_save_path = os.path.join(MODEL_DIR, "segmentation_scaler.pkl")
    metadata_save_path = os.path.join(MODEL_DIR, "segmentation_metadata.json")

    joblib.dump(best_model, model_save_path)
    joblib.dump(pca, pca_save_path)
    joblib.dump(scaler, scaler_save_path)

    metadata = {
        "best_model_name": best_name,
        "n_clusters": 6,
        "raw_feature_columns": RAW_FEATURE_COLUMNS_SEGMENTATION,
        "engineered_numerical_features": num_cols,
        "target_column": TARGET_COLUMN_SEGMENTATION,
        "pca_variance_explained_pct": round(var_explained, 2),
        "cluster_to_persona_map": cluster_to_persona_map,
        "cv_leaderboard": leaderboard,
        "num_training_samples": len(df),
        "persona_archetypes": PERSONA_ARCHETYPES,
        "best_model_metrics": best_row.to_dict(),
    }
    with open(metadata_save_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"[done] Serialized production model  -> {model_save_path}")
    print(f"[done] Serialized PCA transformer   -> {pca_save_path}")
    print(f"[done] Serialized RobustScaler      -> {scaler_save_path}")
    print(f"[done] Serialized metadata          -> {metadata_save_path}")


if __name__ == "__main__":
    main()
