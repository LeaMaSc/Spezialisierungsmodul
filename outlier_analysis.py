"""
Detect outlier participants based on behavioral RDM similarity.

Vectorizes each participant's RDM (upper triangle), computes pairwise
Spearman correlations across participants, and flags anyone whose mean
similarity to all others falls below a one-sided z-cutoff (z < -1.645,
alpha = .05). Writes per-participant results and a summary to results/behavior/.
"""

import os

import numpy as np
import pandas as pd
from scipy.stats import norm, zscore
from rsatools.behavioral import rdm_to_vector, build_similarity_matrix

# -------------------------------------------------------------------------
# Settings
# -------------------------------------------------------------------------

alpha = 0.05
z_cutoff = norm.ppf(alpha)

current_path = os.path.dirname(os.path.abspath(__file__))
rdm_dir = os.path.join(current_path, "rdms", "behavior")
results_dir = os.path.join(current_path, "results", "behavior")
os.makedirs(results_dir, exist_ok=True)

# -------------------------------------------------------------------------
# Load RDMs
# -------------------------------------------------------------------------

rdm_files = sorted(
    os.path.join(rdm_dir, f)
    for f in os.listdir(rdm_dir)
    if f.endswith("_rdm.csv") and "mean_behavior" not in f
)

if not rdm_files:
    raise FileNotFoundError(f"No participant RDMs found in {rdm_dir}")

vectors = [
    rdm_to_vector(pd.read_csv(file, index_col=0).values)
    for file in rdm_files
]

# -------------------------------------------------------------------------
# Compute participant similarity
# -------------------------------------------------------------------------

similarity_matrix = build_similarity_matrix(vectors)

# Exclude self-correlations from the mean
mean_similarity = (
    similarity_matrix.sum(axis=1) - np.diag(similarity_matrix)
) / (len(vectors) - 1)

z_scores = zscore(mean_similarity)
is_outlier = z_scores < z_cutoff

# -------------------------------------------------------------------------
# Save results
# -------------------------------------------------------------------------

results = pd.DataFrame(
    {
        "participant_index": np.arange(1, len(rdm_files) + 1),
        "filename": [os.path.basename(f) for f in rdm_files],
        "mean_similarity": mean_similarity,
        "z_score": z_scores,
        "is_outlier": is_outlier,
    }
)

results.to_csv(
    os.path.join(results_dir, "outlier_detection_per_participant.csv"),
    index=False,
)

summary = [
    "Behavioral RDM Outlier Detection",
    "================================",
    f"Participants: {len(rdm_files)}",
    f"z cutoff: {z_cutoff:.3f}",
    f"Outliers: {is_outlier.sum()}",
    "",
    "Outlier files:",
]

if is_outlier.any():
    summary.extend(
        os.path.basename(rdm_files[i])
        for i in np.where(is_outlier)[0]
    )
else:
    summary.append("None")

with open(
    os.path.join(results_dir, "outlier_detection_summary.txt"),
    "w",
    encoding="utf-8",
) as f:
    f.write("\n".join(summary))

print("\n".join(summary))