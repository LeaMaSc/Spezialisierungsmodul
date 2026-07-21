"""
analysis_behav.py
=================
Behavioral data analysis for the multi-arrangement task.

Loads per-participant CSV exports from Meadows, computes a dissimilarity
(RDM) matrix for each participant, visualizes and saves them, then
averages across participants to produce a group-level mean RDM.

Stimulus set: 42 images across 10 letters
  - Ambiguous (b, d, q, p): 3 variants each  → 12 stimuli
  - Unambiguous (r, a, e, f, h, k): 5 variants each  → 30 stimuli
"""

import os
import numpy as np
from rsatools import visualize_rdm, compute_rdm_from_meadows

# ── Paths ─────────────────────────────────────────────────────────────────

CURRENT_PATH     = os.path.dirname(os.path.abspath(__file__))
DATA_PATH        = os.path.join(CURRENT_PATH, "../multiarrangementtask", "behavioral_data")
OUTPUT_PATH_RDMS = os.path.join(CURRENT_PATH, "results/behavior/rdms")
OUTPUT_PATH_FIGS = os.path.join(CURRENT_PATH, "figures/rdms")

if not os.path.exists(OUTPUT_PATH_RDMS):
    os.makedirs(OUTPUT_PATH_RDMS)
if not os.path.exists(OUTPUT_PATH_FIGS):
    os.makedirs(OUTPUT_PATH_FIGS)

data_files = [
    os.path.join(DATA_PATH, f)
    for f in os.listdir(DATA_PATH)
    if f.endswith(".csv")
]

# ── Stimulus order ────────────────────────────────────────────────────────

ORDER = [
    # Ambiguous letters — 3 variants each (normal, large, rot90)
    'b_normal', 'b_large', 'b_normal_rot90',
    'd_normal', 'd_large', 'd_normal_rot90',
    'q_normal', 'q_large', 'q_normal_rot90',
    'p_normal', 'p_large', 'p_normal_rot90',
    # Unambiguous letters — 5 variants each (normal, large, flip_h, flip_v, rot90)
    'r_normal', 'r_large', 'r_normal_flip_h', 'r_normal_flip_v', 'r_normal_rot90',
    'a_normal', 'a_large', 'a_normal_flip_h', 'a_normal_flip_v', 'a_normal_rot90',
    'e_normal', 'e_large', 'e_normal_flip_h', 'e_normal_flip_v', 'e_normal_rot90',
    'f_normal', 'f_large', 'f_normal_flip_h', 'f_normal_flip_v', 'f_normal_rot90',
    'h_normal', 'h_large', 'h_normal_flip_h', 'h_normal_flip_v', 'h_normal_rot90',
    'k_normal', 'k_large', 'k_normal_flip_h', 'k_normal_flip_v', 'k_normal_rot90',
]

# ── Per-participant RDMs ──────────────────────────────────────────────────

RDMs = []
stimulus_names = None

for path in data_files:
    rdm, stimulus_names = compute_rdm_from_meadows(path, desired_order=ORDER)
    RDMs.append(rdm)
    visualize_rdm(
        rdm, stimulus_names,
        name=os.path.basename(path).replace(".csv", ""),
        figures_path=OUTPUT_PATH_FIGS,
        matrix_path=OUTPUT_PATH_RDMS,
        cmap="Blues",
    )

print(f"Computed RDMs for {len(RDMs)} participants.")

# ── Mean RDM ──────────────────────────────────────────────────────────────

mean_rdm = np.mean(RDMs, axis=0)

visualize_rdm(
    mean_rdm, stimulus_names,
    name="mean_behavior",
    figures_path=os.path.join(OUTPUT_PATH_FIGS, "mean"),
    matrix_path=os.path.join(OUTPUT_PATH_RDMS, "mean"),
    cmap="Blues",
)