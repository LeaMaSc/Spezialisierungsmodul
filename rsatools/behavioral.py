from itertools import combinations
import numpy as np
import pandas as pd
from scipy.stats import norm, spearmanr



def compute_rdm_from_meadows(df, desired_order=None):
    """
    Compute a Representational Dissimilarity Matrix (RDM) from multi-arrangement data
    collected via the Meadows platform.

    Pairwise Euclidean distances between stimuli are averaged across all trials
    in which a pair co-occurred, yielding a symmetric dissimilarity matrix.
    Pairs that never co-occurred are left as NaN.

    Parameters
    ----------
    df : str or pd.DataFrame
        Path to a CSV file or a pre-loaded DataFrame with columns:
        'phase', 'trial', 'stim1_name', 'x', 'y'.
    desired_order : list of str, optional
        Subset of stimuli to include, in the specified row/column order.
        If None, all stimuli are included in alphabetical order.

    Returns
    -------
    rdm : np.ndarray, shape (n, n)
        Symmetric matrix of mean pairwise distances; diagonal is zero.
    stimulus_names : list of str
        Stimulus labels corresponding to each row/column.
    """

    # Load from disk if a path was provided
    if isinstance(df, str):
        df = pd.read_csv(df)

    # Retain only arrangement-phase trials
    df = df[df['phase'] == 'arrangement'].copy()

    # Determine stimulus order; validate against data if order is specified
    unique_stimuli = df['stim1_name'].unique()
    if desired_order is not None:
        df = df[df['stim1_name'].isin(desired_order)]
        missing = [s for s in desired_order if s not in unique_stimuli]
        if missing:
            raise ValueError(f"Stimuli not found in data: {missing}")
        stimulus_names = desired_order
    else:
        stimulus_names = sorted(unique_stimuli)

    n = len(stimulus_names)
    stim_to_idx = {s: i for i, s in enumerate(stimulus_names)}

    # Accumulate pairwise distances and co-occurrence counts across trials
    distance_sum   = np.zeros((n, n))
    distance_count = np.zeros((n, n))

    for trial in df['trial'].unique():
        trial_data = df[df['trial'] == trial]
        positions = {
            row['stim1_name']: np.array([row['x'], row['y']])
            for _, row in trial_data.iterrows()
        }
        for s1, s2 in combinations(positions.keys(), 2):
            d = np.linalg.norm(positions[s1] - positions[s2])
            i, j = stim_to_idx[s1], stim_to_idx[s2]
            distance_sum[i, j]   += d
            distance_sum[j, i]   += d
            distance_count[i, j] += 1
            distance_count[j, i] += 1

    # Average distances; pairs with no co-occurrences remain NaN
    with np.errstate(divide='ignore', invalid='ignore'):
        rdm = distance_sum / distance_count

    np.fill_diagonal(rdm, 0)

    return rdm, stimulus_names


def rdm_to_vector(rdm):
    """Return upper-triangular RDM entries (without diagonal)."""
    return rdm[np.triu_indices_from(rdm, k=1)]


def build_similarity_matrix(vectors):
    """Compute participant-by-participant Spearman similarity matrix."""
    n = len(vectors)
    sim = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            sim[i, j] = spearmanr(vectors[i], vectors[j]).correlation

    return sim