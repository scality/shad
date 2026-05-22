import os
import pandas as pd
import numpy as np
import warnings
import pycatch22

warnings.filterwarnings("ignore")

INPUT_DIR = "Dataset"
OUTPUT_DIR = "Representations/Catch22/MTS-Representations"


def extract_catch22_from_folder_multivariate(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # Recursive scan for CSV files
    csv_files = []
    for root, _, files in os.walk(input_dir):
        for f in files:
            if f.endswith(".csv"):
                csv_files.append(os.path.join(root, f))

    print(f"Found {len(csv_files)} time series files (recursive)")

    output_path = os.path.join(output_dir, "catch22_features.csv")

    processed_datasets = set()
    if os.path.exists(output_path):
        try:
            existing_index = pd.read_csv(output_path, usecols=["dataset", "dimension"])
            processed_datasets = set(
                (row["dataset"], row["dimension"])
                for _, row in existing_index.iterrows()
            )
            print(f"Found {len(processed_datasets)} already processed dimensions")
        except Exception as e:
            print("Warning: could not parse existing CSV:", e)

    first_write = not os.path.exists(output_path)

    for file_path in csv_files:

        file = os.path.basename(file_path)

        dataset_name = os.path.splitext(file)[0]

        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            print(f"Skipping {dataset_name}: could not read CSV ({e})")
            continue

        # Exclude per-dimension labels and the timestamp column
        exclude_cols = {
            c for c in df.columns
            if "label" in c.lower()
        }
        exclude_cols.add("metric_timestamp")

        numeric_cols = [
            c for c in df.select_dtypes(include=[np.number]).columns
            if c not in exclude_cols
        ]

        for col in numeric_cols:

            if (dataset_name, col) in processed_datasets:
                print(f"Skipping already processed {dataset_name} dimension {col}")
                continue

            ts = df[col].dropna().astype(float).values

            try:
                res = pycatch22.catch22_all(ts, catch24=True)
                feature_names = res.get("names", [])
                feature_values = res.get("values", [])

                final_values = []
                for v in feature_values:
                    if v is None or (isinstance(v, float) and pd.isna(v)):
                        final_values.append("NA")
                    else:
                        final_values.append(v)

                if not final_values:
                    final_values = ["NA"] * len(feature_names)

                features_df = pd.DataFrame([final_values], columns=feature_names)
                features_df.insert(0, "dimension", col)
                features_df.insert(0, "dataset", dataset_name)

                features_df.to_csv(
                    output_path,
                    mode="w" if first_write else "a",
                    header=first_write,
                    index=False,
                )

                first_write = False
                print(f"Processed {dataset_name} dimension {col}")

            except Exception as e:
                print(
                    f"{dataset_name} dimension {col}: catch22 error ({e}) → writing NA"
                )

                feature_names = pycatch22.catch22_all(
                    np.arange(10), catch24=True
                )["names"]

                features_df = pd.DataFrame(
                    [["NA"] * len(feature_names)], columns=feature_names
                )
                features_df.insert(0, "dimension", col)
                features_df.insert(0, "dataset", dataset_name)

                features_df.to_csv(
                    output_path,
                    mode="a",
                    header=False,
                    index=False,
                )

    print(f"\nSaved catch22 features to: {output_path}")


def main():
    extract_catch22_from_folder_multivariate(INPUT_DIR, OUTPUT_DIR)


if __name__ == "__main__":
    main()