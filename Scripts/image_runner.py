import os
import time
import csv
import base64
import pandas as pd
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv("keys.env")


# CLIENT
# --------------------------------------------------

def get_client():
    return Mistral(os.getenv("MISTRAL_API_KEY"))


# IMAGE UTILS
# --------------------------------------------------

def file_to_data_url(file_path):
    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    ext = os.path.splitext(file_path)[1].replace(".", "").lower()

    return f"data:image/{ext};base64,{encoded}"


# DIMENSIONS
# --------------------------------------------------

def get_dimensions_from_features(features_file):
    df = pd.read_csv(features_file)
    return sorted(df["dimension"].unique())


# PROMPT BUILDER
# --------------------------------------------------

def build_prompt(dimensions, questionnaire, prompt_template):
    q_text = ""

    for q in questionnaire:
        q_text += f"\nID: {q['id']}\n"
        q_text += f"Question: {q['question']}\n"

        if q["type"] == "choice":
            q_text += "Options: " + ", ".join(q["options"]) + "\n"

        if q["id"] == "anomaly_dimension":
            q_text += "Available dimensions: " + ", ".join(dimensions) + "\n"

        q_text += f"Answer format: {q['id']}: <answer>\n"

    return prompt_template.format(questions=q_text)


# LLM CALL
# --------------------------------------------------

def call_llm(image_path, prompt, model):
    client = get_client()
    image_data_url = file_to_data_url(image_path)

    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": image_data_url}}
        ]
    }]

    start = time.time()

    response = client.chat.complete(
        model=model,
        messages=messages
    )

    elapsed = time.time() - start

    return (
        response.choices[0].message.content,
        elapsed,
        response.usage
    )


def call_llm_with_retry(image_path, prompt, model, max_retries=35):
    for i in range(max_retries):
        try:
            return call_llm(image_path, prompt, model)
        except Exception as e:
            print("LLM error:", e)
            if i < max_retries - 1:
                time.sleep(20)
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
    images_dir,
    features_file,
    output_dir,
    questionnaire,
    prompt_template,
    model
):
    run_output_dir = os.path.join(output_dir, str(run_id))
    os.makedirs(run_output_dir, exist_ok=True)

    output_file = os.path.join(run_output_dir, "questionnaire_results_multivariate.csv")

    processed_datasets = load_processed_datasets(output_file)
    write_header = not os.path.exists(output_file)

    dimensions = get_dimensions_from_features(features_file)
    prompt = build_prompt(dimensions, questionnaire, prompt_template)

    with open(output_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if write_header:
            writer.writerow(
                ["dataset"] +
                [q["id"] for q in questionnaire] +
                ["time_sec", "prompt_tokens", "completion_tokens", "total_tokens", "raw_llm_response"]
            )

        for img in sorted(os.listdir(images_dir)):
            if not img.endswith(".png"):
                continue

            dataset_name = img.replace(".png", "")

            if dataset_name in processed_datasets:
                continue

            print(f"[Run {run_id}] Processing: {dataset_name}")

            image_path = os.path.join(images_dir, img)

            response_text, elapsed, usage = call_llm_with_retry(
                image_path,
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