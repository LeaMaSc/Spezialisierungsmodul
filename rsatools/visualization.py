import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def visualize_rdm(
    rdm,
    labels,
    name=None,
    save_path=None,
    figures_path=None,
    matrix_path=None,
    cmap="Blues",
    vmin=None,
    vmax=None,
):
    """
    Visualize a Representational Dissimilarity Matrix (RDM) as a labeled heatmap.

    Optionally saves the figure as a PNG and the raw matrix as a CSV file.
    The figure is saved under 'figures/<figures_path>/' and the matrix
    under 'rdms/<matrix_path>/'.

    Parameters
    ----------
    rdm : np.ndarray, shape (n, n)
        The dissimilarity matrix to visualize.
    labels : list of str
        Stimulus labels for the rows and columns.
    name : str, optional
        Title of the plot and base name for saved files. Defaults to 'RDM'.
    figures_path : str, optional
        Subdirectory under 'figures/' where the PNG is saved.
        If None, the figure is not saved.
    matrix_path : str, optional
        Subdirectory under 'rdms/' where the CSV is saved.
        If None, the matrix is not saved.
    cmap : str, optional
        Matplotlib colormap (default: 'Blues').
    vmin : float, optional
        Lower bound for colormap normalization.
    vmax : float, optional
        Upper bound for colormap normalization.
    """
    title = name or "RDM"
    safe_name = title.replace(" ", "_").replace("—", "-").replace(":", "")

    fig, ax = plt.subplots(figsize=(10, 9))
    im = ax.imshow(rdm, cmap=cmap, aspect="auto", vmin=vmin, vmax=vmax)
    ax.set_title(title, fontsize=16, pad=20)
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=90, fontsize=8)
    ax.set_yticklabels(labels, fontsize=8)

    plt.colorbar(im, ax=ax, label="Dissimilarity", fraction=0.046, pad=0.04)
    plt.tight_layout()

    if save_path:
        os.makedirs(save_path, exist_ok=True)
        plt.savefig(os.path.join(save_path, f"{safe_name}.png"), dpi=300, bbox_inches="tight")

    if figures_path:
        out_dir = figures_path
        os.makedirs(out_dir, exist_ok=True)
        plt.savefig(os.path.join(out_dir, f"{safe_name}_rdm.png"), dpi=300, bbox_inches="tight")

    if matrix_path:
        out_dir = matrix_path
        os.makedirs(out_dir, exist_ok=True)
        pd.DataFrame(rdm, index=labels, columns=labels).to_csv(
            os.path.join(out_dir, f"{safe_name}_rdm.csv")
        )

    plt.close()
