# Spezialisierungsmodul

# Transformation Invariance in Visual Letter Representations

Comparing reversible and non-reversible letters using a multi-arrangement (inverse MDS) task.

**Author:** Lea Marie Schmitt

**Supervisor:** Prof. Dr. Katharina Dobs (FB 07)

**Program:** Master Data Analytics, Justus-Liebig-Universität Gießen

**Module:** Spezialisierungsmodul, SoSe 2026

## Overview

This project investigates whether literate adults still show mirror invariance for letters,
and whether this differs between **reversible** letters (b, d, p, q — whose mirror image is
another valid letter) and **non-reversible** letters (r, a, e, f, h, k). Thirty-six participants
completed an online multi-arrangement task (Kriegeskorte & Mur, 2012) via the Meadows platform,
arranging 42 letter stimuli (transformed by mirroring, rotation, and resizing) according to
perceived similarity. Behavioral dissimilarity judgments were converted into representational
dissimilarity matrices (RDMs) and analyzed with a repeated-measures ANOVA.

## Repository structure

```
.
├── analysis_behavior.py          # Builds per-participant RDMs from Meadows CSV exports
├── outlier_analysis.py        # Detects outlier participants from RDM similarity
├── generate_letter_stimuli.py # Generates transformed letter stimuli
├── visualization_behavior.ipynb    # Figures: RDM heatmaps, participant correlation matrix,
│                               #   condition/reversibility bar plots with significance annotations
├── statistics_behavior.R      # Confirmatory statistics: 2x4 repeated-measures ANOVA,
│                               #   Holm-corrected post-hoc comparisons, paired Cohen's d
├── rsatools/                  # Shared helper module (RDM computation & visualization)
├── letter_stimuli/            # Generated stimuli, organized by base letter
├── multiarrangementtask/      # Optional external input directory (not present in this snapshot)
│   └── behavioral_data/       # Raw per-participant CSV exports from Meadows (not tracked)
├── results/behavior/rdms              # Per-participant RDMs (+ mean/ subfolder), written by analysis_behav.py
├── figures/rdms/           # Per-participant RDM plots, written by analysis_behav.py
├── figures/                    # Notebook-generated figures (mean RDM, correlation matrix, bar plots)
└── results/behavior/           # Outlier detection outputs, written by outlier_analysis.py
```

## Pipeline (run in this order)

1. **`analysis_behavior.py`**
   Reads raw Meadows CSV exports from `multiarrangementtask/behavioral_data/`, computes one
   42x42 RDM per participant (pairwise Euclidean distances between co-occurring stimuli across
   trials), and writes:
   - `results/behavior/rdms/<participant>_rdm.csv` — per-participant RDM
   - `figures/rdms/<participant>.png` — per-participant RDM heatmap
   - `results/behavior/rdms/mean/mean_behavior_rdm.csv` — group-mean RDM 
   - `figures/rdms/mean/mean_behavior_rdm.png` — group-mean RDM heatmap

2. **`outlier_analysis.py`**
   Loads all per-participant RDMs, vectorizes the upper triangle, computes a participant x
   participant Spearman similarity matrix, and flags outliers as participants whose mean
   similarity to all others falls below a one-sided z-cutoff (z < -1.645, α = .05). Writes:
   - `results/behavior/outlier_detection_per_participant.csv`
   - `results/behavior/outlier_detection_summary.txt`

3. **`statistics_behavior.R`**
   Loads all per-participant RDMs, extracts mean dissimilarity for each combination of letter
   class (reversible / non-reversible) x transformation condition (horizontal, vertical,
   90° rotation, size). Every value is a transformed-vs-original distance:
   - Reversible letters, horizontal/vertical: distance between mirror-equivalent letter pairs
     at normal size (b<->d, p<->q, b<->p, d<->q), since flipping a reversible letter produces
     the image of another letter already in the stimulus set.
   - Reversible letters, rotation/size, and all non-reversible conditions: within-letter
     distance between the `_normal` stimulus and its transformed counterpart, averaged across
     letters.

   Runs the 2x4 repeated-measures ANOVA (Greenhouse-Geisser corrected) and Holm-corrected
   post-hoc comparisons (`emmeans`) reported in the paper's Results section.

4. **`visualization_behavior.ipynb`**
   Excludes participants flagged in step 2, then generates all figures used in the paper:
   mean RDM heatmap, excluded/included participant RDM grids, participant correlation matrix,
   and the three bar plots (reversibility main effect, transformation-condition main effect,
   and the reversibility x condition interaction). `combo_df` in this notebook is built with
   the *same* transformed-vs-original logic as `statistics_behavior.R` (see "Statistics" note
   below) so that figure values and reported statistics agree.

## Statistics: where each number comes from

- **All F-, t-, and p-values reported in the paper** come from `statistics_behavior.R`
  (`afex::aov_ez()` for the ANOVA, `emmeans()` + Holm correction for post-hoc comparisons).
  This script is the authoritative statistical source.
- **Significance brackets in the notebook's bar plots** are added via a separate paired
  t-test (`scipy.stats.ttest_rel`) on the same participant-level means, Holm-corrected within
  each figure, for simplicity. This was cross-checked against the R output and found to agree
  in significance pattern and effect size for every contrast shown. If the underlying RDMs or
  either script change, this equivalence should be re-checked rather than assumed (see the
  "Information on statistics" markdown cell in the notebook).

## Dependencies

**Python:** `numpy`, `pandas`, `seaborn`, `matplotlib`, `scikit-learn`, `scipy`, `statsmodels`, plus the local
`rsatools` module (`rdm_to_vector`, `visualize_rdm`, `build_similarity_matrix`,
`compute_rdm_from_meadows`).

**R (>= 4.5):** `tidyverse`, `afex`, `emmeans`, `effectsize`, `rstatix`.

## Reproducing the analysis

```bash
# 1. Build per-participant RDMs
python analysis_behavior.py

# 2. Detect and log outlier participants
python outlier_analysis.py

# 3. Run confirmatory statistics (paper Results section)
Rscript statistics_behavior.R

# 4. Generate figures (run cells top to bottom)
jupyter notebook visualization_behavior.ipynb
```

## Data

Raw per-participant Meadows exports are not included in this repository snapshot for participant privacy; 
the pipeline scripts assume they are present under `multiarrangementtask/behavioral_data/`. In this repository snapshot, 
`multiarrangementtask/` is not included and should be added locally before running `analysis_behav.py`.
