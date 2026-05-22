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
    return Mistral(
        os.getenv("MISTRAL_API_KEY")
    )


# IMAGE UTILS
# --------------------------------------------------

def file_to_data_url(file_path):

    with open(file_path, "rb") as f:

        encoded = base64.b64encode(
            f.read()
        ).decode("utf-8")

    ext = (
        os.path.splitext(file_path)[1]
        .replace(".", "")
        .lower()
    )

    return (
        f"data:image/{ext};base64,"
        f"{encoded}"
    )


# DIMENSIONS
# --------------------------------------------------

def get_dimensions_from_features(features_file):

    df = pd.read_csv(features_file)

    return sorted(df["dimension"].unique())


# PROMPT BUILDER
# --------------------------------------------------

def build_questionnaire_prompt(
    dimensions,
    description,
    questionnaire,
    prompt_template
):

    q_text = ""

    for q in questionnaire:

        q_text += f"\nID: {q['id']}\n"
        q_text += f"Question: {q['question']}\n"

        if q["type"] == "choice":
            q_text += "Options: " + ", ".join(q["options"]) + "\n"

        if q["id"] == "anomaly_dimension":
            q_text += "Available dimensions: " + ", ".join(dimensions) + "\n"

        q_text += f"Answer format: {q['id']}: <answer>\n"

    return prompt_template.format(
        description=description,
        questions=q_text
    )


# LLM CALLS
# --------------------------------------------------

def call_llm_with_image(image_path, prompt, model):

    client = get_client()

    image_data_url = file_to_data_url(image_path)

    start = time.time()

    response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_data_url}}
                ]
            }
        ]
    )

    elapsed = time.time() - start

    return (
        response.choices[0].message.content,
        elapsed,
        response.usage
    )


def call_llm_text(prompt, model):

    client = get_client()

    start = time.time()

    response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    elapsed = time.time() - start

    return (
        response.choices[0].message.content,
        elapsed,
        response.usage
    )


def retry_call(func, *args, max_retries=35):

    for i in range(max_retries):

        try:
            return func(*args)

        except Exception as e:

            print("LLM error:", e)

            if i < max_retries - 1:
                time.sleep(20)
            else:
                raise


# PARSE
# --------------------------------------------------

def parse_response(text):

    answers = {}

    for line in text.splitlines():

        if ":" not in line:
            continue

        k, v = line.split(":", 1)

        answers[k.strip()] = v.strip()

    return answers


# LOAD
# --------------------------------------------------

def load_processed_datasets(output_file):

    if not os.path.exists(output_file):
        return set()

    try:
        df = pd.read_csv(output_file, on_bad_lines="skip")
        return set(df["dataset"].astype(str))
    except Exception:
        return set()


# MAIN ENTRYPOINT
# --------------------------------------------------

def run_questionnaire(
    run_id,
    images_dir,
    features_file,
    output_dir,
    questionnaire,
    description_prompt,
    prompt_template,
    model
):

    run_output_dir = os.path.join(output_dir, str(run_id))
    os.makedirs(run_output_dir, exist_ok=True)

    output_file = os.path.join(run_output_dir, "questionnaire_results.csv")

    processed = load_processed_datasets(output_file)
    dimensions = get_dimensions_from_features(features_file)

    write_header = not os.path.exists(output_file)

    with open(output_file, "a", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        if write_header:

            writer.writerow(
                ["dataset"]
                + [q["id"] for q in questionnaire]
                + [
                    "description",
                    "desc_time_sec",
                    "qa_time_sec",
                    "total_time_sec",
                    "total_tokens"
                ]
            )

        for img in sorted(os.listdir(images_dir)):

            if not img.endswith(".png"):
                continue

            dataset_name = img.replace(".png", "")

            if dataset_name in processed:
                continue

            image_path = os.path.join(images_dir, img)

            print(f"[Run {run_id}] {dataset_name}")

            description, t1, u1 = retry_call(
                call_llm_with_image,
                image_path,
                description_prompt,
                model
            )

            questionnaire_prompt = build_questionnaire_prompt(
                dimensions,
                description,
                questionnaire,
                prompt_template
            )

            response_text, t2, u2 = retry_call(
                call_llm_text,
                questionnaire_prompt,
                model
            )

            answers = parse_response(response_text)

            writer.writerow(
                [dataset_name]
                + [answers.get(q["id"], "") for q in questionnaire]
                + [
                    description.replace("\n", " "),
                    round(t1, 3),
                    round(t2, 3),
                    round(t1 + t2, 3),
                    u1.total_tokens + u2.total_tokens
                ]
            )

            f.flush()