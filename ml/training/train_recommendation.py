"""
Multi-Model Training & Benchmark Pipeline for Phase 16: Financial Product Recommendation.

Benchmarks 4 recommender architectures:
1. Popularity Baseline Ranker
2. Matrix Factorization (TruncatedSVD Collaborative Filtering)
3. Content-Based Cosine Embedding Matcher
4. Multi-Stage Hybrid Net-Annual-Value Ranker (Selected Production Pipeline)

Evaluates:
- NDCG@5 (Normalized Discounted Cumulative Gain)
- Precision@3, Recall@5, and Hit Rate@5
- Mean Reciprocal Rank (MRR)
- Sub-Millisecond Execution Latency
"""

import json
import os
import sys
import time
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.recommendation_rules import (  # noqa: E402
    PRODUCT_CATALOG,
    SPEND_CATEGORIES_ORDER,
    calculate_product_net_annual_value,
    get_product_reward_vector,
    get_user_spend_vector,
)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "datasets", "processed")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
TRAIN_FILE = os.path.join(PROCESSED_DIR, "recommendation_train.csv")


def compute_ndcg_at_k(actual_top_pid: str, ranked_pids: List[str], k: int = 5) -> float:
    """
    Computes NDCG@K for single-target relevance.
    """
    ranked_k = ranked_pids[:k]
    if actual_top_pid in ranked_k:
        rank_idx = ranked_k.index(actual_top_pid)  # 0-indexed
        return float(1.0 / np.log2(rank_idx + 2.0))
    return 0.0


def compute_mrr(actual_top_pid: str, ranked_pids: List[str]) -> float:
    """
    Computes Mean Reciprocal Rank (MRR).
    """
    if actual_top_pid in ranked_pids:
        rank_idx = ranked_pids.index(actual_top_pid)
        return float(1.0 / (rank_idx + 1.0))
    return 0.0


def main():
    print("=" * 85)
    print("Phase 16: Financial Product Recommendation & Smart Matchmaking Benchmark")
    print("=" * 85)

    if not os.path.exists(TRAIN_FILE):
        print(f"[error] Train file not found: {TRAIN_FILE}. Run preprocess_recommendation.py first.")
        sys.exit(1)

    df = pd.read_csv(TRAIN_FILE)
    print(f"[info] Loaded {len(df)} user financial records. Precomputing product matrix embeddings...")

    # Precompute catalog reward matrix P (M x 6)
    product_matrix = np.array([get_product_reward_vector(p) for p in PRODUCT_CATALOG])
    product_ids = [p["product_id"] for p in PRODUCT_CATALOG]

    # Pre-extract popularity order
    pop_order = list(df["optimal_product_id"].value_counts().index)
    for pid in product_ids:
        if pid not in pop_order:
            pop_order.append(pid)

    # Collaborative SVD Setup
    all_pids = list(product_ids)
    user_item_matrix = np.zeros((len(df), len(all_pids)))
    for idx, row in df.iterrows():
        pid = row["optimal_product_id"]
        if pid in all_pids:
            user_item_matrix[idx, all_pids.index(pid)] = 1.0

    svd = TruncatedSVD(n_components=min(5, len(all_pids) - 1), random_state=42)
    user_factors = svd.fit_transform(user_item_matrix)
    item_factors = svd.components_  # (n_components, n_items)

    print("\n[info] Benchmarking Candidate Recommender Architectures...")

    candidates = ["popularity_baseline", "matrix_factorization_svd", "content_cosine_matcher", "multi_stage_hybrid_ranker"]
    leaderboard = []

    for model_name in candidates:
        t0 = time.perf_counter()
        ndcg_list, p3_list, r5_list, mrr_list, hit5_list = [], [], [], [], []

        for _, row in df.iterrows():
            actual_best = row["optimal_product_id"]
            user_spends = {
                "dining": row["spend_dining"],
                "shopping": row["spend_shopping"],
                "groceries": row["spend_groceries"],
                "travel": row["spend_travel"],
                "fuel": row["spend_fuel"],
                "utilities": row["spend_utilities"],
                "monthly_income": row["monthly_income"],
            }
            cscore = row["credit_score"]
            income = row["monthly_income"]
            savings = row["liquid_savings"]
            debt = row["existing_debt"]

            if model_name == "popularity_baseline":
                ranked = list(pop_order)

            elif model_name == "content_cosine_matcher":
                u_vec = get_user_spend_vector(user_spends)
                sim_scores = np.dot(product_matrix, u_vec)
                ranked = [product_ids[i] for i in np.argsort(-sim_scores)]

            elif model_name == "matrix_factorization_svd":
                u_vec = get_user_spend_vector(user_spends)
                # Pseudo user factor via spend mapping
                u_proj = np.dot(u_vec[:item_factors.shape[0]], item_factors)
                ranked = [all_pids[i] for i in np.argsort(-u_proj)]

            else:  # multi_stage_hybrid_ranker
                scored_products = []
                for prod in PRODUCT_CATALOG:
                    # Stage 1: Eligibility Guardrail
                    if cscore < prod["min_credit_score"] or income < prod["min_monthly_income"]:
                        continue
                    # Stage 2: Net Annual Value & Persona Relevance
                    nav, _ = calculate_product_net_annual_value(prod, user_spends, savings, debt)
                    persona_match = 1.2 if row["persona_id"] in prod.get("target_personas", []) else 1.0
                    final_score = nav * persona_match
                    scored_products.append((prod["product_id"], final_score))

                # Sort by Net Annual Value descending
                scored_products.sort(key=lambda x: x[1], reverse=True)
                ranked = [p[0] for p in scored_products]
                if not ranked:
                    ranked = ["CC_IDFC_FIRST_WOW"]

            # Evaluation metrics
            ndcg = compute_ndcg_at_k(actual_best, ranked, k=5)
            p3 = 1.0 if actual_best in ranked[:3] else 0.0
            r5 = 1.0 if actual_best in ranked[:5] else 0.0
            mrr = compute_mrr(actual_best, ranked)
            hit5 = 1.0 if actual_best in ranked[:5] else 0.0

            ndcg_list.append(ndcg)
            p3_list.append(p3)
            r5_list.append(r5)
            mrr_list.append(mrr)
            hit5_list.append(hit5)

        eval_time_ms = (time.perf_counter() - t0) * 1000.0
        avg_latency_us = (eval_time_ms / len(df)) * 1000.0

        res = {
            "model": model_name,
            "ndcg_at_5": round(float(np.mean(ndcg_list)), 4),
            "precision_at_3_pct": round(float(np.mean(p3_list) * 100.0), 2),
            "recall_at_5_pct": round(float(np.mean(r5_list) * 100.0), 2),
            "hit_rate_at_5_pct": round(float(np.mean(hit5_list) * 100.0), 2),
            "mrr": round(float(np.mean(mrr_list)), 4),
            "avg_latency_us": round(avg_latency_us, 1),
        }
        leaderboard.append(res)
        print(
            f"  [{model_name:28s}] NDCG@5: {res['ndcg_at_5']:6.4f} | Prec@3: {res['precision_at_3_pct']:5.1f}% | Hit@5: {res['hit_rate_at_5_pct']:5.1f}% | MRR: {res['mrr']:6.4f} | Latency: {res['avg_latency_us']:5.1f}us"
        )

    leaderboard_df = pd.DataFrame(leaderboard).sort_values("ndcg_at_5", ascending=False)
    best_row = leaderboard_df.iloc[0]
    best_name = best_row["model"]

    print("\n" + "=" * 85)
    print(f"[result] Selected Production Architecture: '{best_name}'")
    print(f"         NDCG@5 Score:        {best_row['ndcg_at_5']} (Benchmark >= 0.90)")
    print(f"         Precision@3:         {best_row['precision_at_3_pct']}% (Benchmark >= 88%)")
    print(f"         Hit Rate@5:          {best_row['hit_rate_at_5_pct']}%")
    print(f"         Mean Reciprocal Rank:{best_row['mrr']}")
    print(f"         Average Latency:     {best_row['avg_latency_us']} microseconds / query")
    print("=" * 85)

    os.makedirs(MODEL_DIR, exist_ok=True)
    catalog_save_path = os.path.join(MODEL_DIR, "product_catalog.json")
    metadata_save_path = os.path.join(MODEL_DIR, "recommender_metadata.json")
    model_save_path = os.path.join(MODEL_DIR, "best_recommender_model.pkl")

    # Serialize artifacts
    with open(catalog_save_path, "w") as f:
        json.dump(PRODUCT_CATALOG, f, indent=2)

    metadata = {
        "best_model_name": best_name,
        "product_catalog_size": len(PRODUCT_CATALOG),
        "spend_categories": SPEND_CATEGORIES_ORDER,
        "benchmark_leaderboard": leaderboard,
        "best_metrics": best_row.to_dict(),
    }
    with open(metadata_save_path, "w") as f:
        json.dump(metadata, f, indent=2)

    # Save lightweight production wrapper object
    joblib.dump({"catalog": PRODUCT_CATALOG, "matrix": product_matrix, "pids": product_ids}, model_save_path)

    print(f"[done] Serialized product catalog   -> {catalog_save_path}")
    print(f"[done] Serialized metadata          -> {metadata_save_path}")
    print(f"[done] Serialized production model  -> {model_save_path}")


if __name__ == "__main__":
    main()
