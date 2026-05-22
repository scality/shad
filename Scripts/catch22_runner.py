import os
import json
import time
import csv
import pandas as pd
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv("keys.env")


# CLIENT
# --------------------------------------------------

def get_client():
    return Mistral(os.getenv("MISTRAL_API_KEY"))


# PROMPT BUILDER
# --------------------------------------------------

def build_prompt(features, questionnaire, prompt_template):
    q_text = ""

    for q in questionnaire:
        q_text += f"\nID: {q['id']}\n"
        q_text += f"Question: {q['question']}\n"

        if q["type"] == "choice":
            q_text += "Options: " + ", ".join(q["options"]) + "\n"

        q_text += f"Answer format: {q['id']}: <answer>\n"

    return prompt_template.format(
        features=json.dumps(features, indent=2),
        questions=q_text
    )


# FEATURE BUILDER
# --------------------------------------------------

def build_multivariate_features(group):
    features = {}

    for _, row in group.iterrows():
        dim = row["dimension"]
        dim_features = row.drop(["dataset", "dimension"]).to_dict()
        features[dim] = dim_features

    return features


# LLM CALL
# --------------------------------------------------

def call_llm(prompt, model):
    client = get_client()

    start = time.time()

    response = client.chat.complete(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    elapsed = time.time() - start

    return (
        response.choices[0].message.content,
        elapsed,
        response.usage
    )


def call_llm_with_retry(prompt, model, max_retries=5):
    for i in range(max_retries):
        try:
            return call_llm(prompt, model)
        except Exception as e:
            print("LLM error:", e)
            if i < max_retries - 1:
                time.sleep(10)
            else:
                raise


# PARSE RESPONSE
# --------------------------------------------------

def parse_response(text):
    answers = {}

    for line in text.splitlines():
        if ":" not in line:
            continue

        k, v = line.split(":", 1)
        answers[k.strip()] = v.strip()

    return answers


# LOAD PROCESSED DATASETS
# --------------------------------------------------

def load_processed_datasets(output_file):
    if not os.path.exists(output_file):
        return set()

    try:
        df = pd.read_csv(output_file, on_bad_lines="skip")
        return set(df["dataset"].astype(str))
    except Exception as e:
        print("WARNING reading CSV:", e)
        return set()


# MAIN ENTRYPOINT
# --------------------------------------------------

def run_questionnaire(
    run_id,
    features_file,
    output_dir,
    questionnaire,
    prompt_template,
    model
):
    run_output_dir = os.path.join(output_dir, str(run_id))
    os.makedirs(run_output_dir, exist_ok=True)

    output_file = os.path.join(
        run_output_dir,
        "questionnaire_results_multivariate.csv"
    )

    df = pd.read_csv(features_file)

    processed_datasets = load_processed_datasets(output_file)
    write_header = not os.path.exists(output_file)

    with open(output_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if write_header:
            writer.writerow(
                ["dataset"] +
                [q["id"] for q in questionnaire] +
                [
                    "time_sec",
                    "prompt_tokens",
                    "completion_tokens",
                    "total_tokens",
                    "raw_llm_response"
                ]
            )

        for dataset_name, group in df.groupby("dataset"):

            if dataset_name in processed_datasets:
                continue

            print(f"[Run {run_id}] Processing: {dataset_name}")

            features = build_multivariate_features(group)

            prompt = build_prompt(
                features,
                questionnaire,
                prompt_template
            )

            response_text, elapsed, usage = call_llm_with_retry(
                prompt,
                model
            )

            answers = parse_response(response_text)

            clean_raw_response = response_text.replace("\r", " ").replace("\n", " ").strip()

            row_values = [dataset_name]

            for q in questionnaire:
                row_values.append(answers.get(q["id"], ""))

            row_values += [
                f"{elapsed:.3f}",
                usage.prompt_tokens,
                usage.completion_tokens,
                usage.total_tokens,
                clean_raw_response
            ]

            writer.writerow(row_values)
            f.flush()