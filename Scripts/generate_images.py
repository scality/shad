import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

INPUT_DIR = "Dataset"
OUTPUT_DIR = "Representations/Images/MTS-Representations"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def compute_layout(n_dims):
    """
    Layout for hundreds or thousands of dimensions.
    """
    cols = 10 if n_dims > 20 else math.ceil(math.sqrt(n_dims))
    rows = math.ceil(n_dims / cols)

    subplot_height = 1.2
    fig_height = rows * subplot_height

    return rows, cols, fig_height


def plot_multivariate_ts(file_path, output_dir):

    file = os.path.basename(file_path)
    ts_name = os.path.splitext(file)[0]
    output_path = os.path.join(output_dir, f"{ts_name}.png")

    # Skip if the image already exists
    if os.path.exists(output_path):
        print(f"Skipping existing image: {ts_name}")
        return

    try:
        df = pd.read_csv(file_path).dropna()
    except Exception as e:
        print(f"Skipping {ts_name}: {e}")
        return

    # Drop all columns containing "label" in their name 
    label_cols = [col for col in df.columns if "label" in col.lower()]
    df = df.drop(columns=label_cols, errors="ignore")

    # Drop timestamp column
    df = df.drop(columns=["metric_timestamp"], errors="ignore")

    dims = df.columns
    n_dims = len(dims)

    if n_dims == 0:
        print(f"No usable dimensions for {ts_name}")
        return

    rows, cols, fig_height = compute_layout(n_dims)

    fig, axes = plt.subplots(
        rows,
        cols,
        figsize=(20, fig_height),
        constrained_layout=True
    )

    axes = np.array(axes).reshape(-1)

    print(f"{ts_name}: plotting {n_dims} dimensions")

    for i, col in enumerate(dims):

        ax = axes[i]
        values = df[col].values

        ax.plot(values, color="blue", linewidth=1)

        ax.set_title(col, fontsize=6, pad=2)

        ax.set_xticks([0, len(values) - 1])
        ax.set_xticklabels([0, len(values) - 1], fontsize=5)

        ymin, ymax = values.min(), values.max()
        yticks = np.linspace(ymin, ymax, 3)
        ax.set_yticks(yticks)
        ax.set_yticklabels([f"{y:.1f}" for y in yticks], fontsize=5)

    # Disable unused subplots
    for j in range(n_dims, len(axes)):
        axes[j].axis("off")

    fig.supxlabel("Time", fontsize=12)
    fig.supylabel("Value", fontsize=12)

    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved image: {output_path}")


def main():

    # Scan for CSV files
    csv_files = []
    for root, _, files in os.walk(INPUT_DIR):
        for f in files:
            if f.endswith(".csv"):
                csv_files.append(os.path.join(root, f))

    print(f"Found {len(csv_files)} CSV files (recursive)")

    for file_path in csv_files:
        plot_multivariate_ts(file_path, OUTPUT_DIR)


if __name__ == "__main__":
    main()