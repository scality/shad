from catch22_runner import run_questionnaire as run_catch22
from image_runner import run_questionnaire as run_images
from description_runner import run_questionnaire as run_descriptions


N_RUNS = 1
MODEL = "mistral-large-latest"


QUESTIONNAIRE = [

    {
        "id": "anomaly_presence",
        "type": "choice",
        "question": "Does the multivariate time series contain anomalies?",
        "options": ["Yes", "No"]
    },
    {
        "id": "anomaly_dimension",
        "type": "open",
        "question": "If an anomaly is present, name a single dimension in which you have found the anomaly. Otherwhise reply None."
    },

    {
        "id": "anomaly_time_location",
        "type": "open",
        "question": "If an anomaly is present, give a single numeric time instant range [start,end] in which the anomaly is present. Otherwhise reply None."
    },

    {
        "id": "anomaly_type",
        "type": "choice",
        "question": "If an anomaly is present, choose its type. Otherwise reply None",
        "options": [
            "Disk Failure",
            "Server Failure",
            "Software Node Failure",
            "None"
        ]
    },

    {
        "id": "anomaly_criticality",
        "type": "choice",
        "question": "If an anomaly is present, choose its criticality. Otherwise reply None",
        "options": [
            "Low",
            "Medium",
            "High",
            "None"
        ]
    },

    {
        "id": "explanation",
        "type": "open",
        "question": "Briefly explain your previous answers."
    }
]


PROMPT_TEMPLATE_CATCH22 = """You are an expert in time series analysis.
The following data represents a multivariate time series related to a cloud storage system: 
each key corresponds to one dimension of the dataset and contains its statistical features.

Your task is to answer the given questions by analyzing the statistical features.
For EACH question return exactly one line:

question_id: answer

Rules:
- Use the EXACT question_id
- Only write the answer
- No explanations

--------------------
TIME SERIES FEATURES
--------------------
{features}

--------------------
QUESTIONNAIRE
--------------------
{questions}
"""


PROMPT_TEMPLATE_IMAGES="""You are an expert in time series analysis.
The following image represents a multivariate time series related to a cloud storage system: 
each subplot corresponds to one dimension of the dataset.

Your task is to answer the given questions by analyzing the time series image.
For EACH question return exactly one line:

question_id: answer

Rules:
- Use the EXACT question_id
- Only write the answer
- No explanations

--------------------
QUESTIONNAIRE
--------------------
{questions}
"""


DESCRIPTION_PROMPT = """You are an expert in multivariate time series analysis.
You are given an image representing a cloud storage system multivariate time series.
Describe the main characteristics of the series, highligting patterns and potential anomalies."""


PROMPT_TEMPLATE_DESCRIPTION="""You are an expert in time series analysis.
The following description summarizes a multivariate time series related to a cloud storage system. 

Your task is to answer the given questions by considering the provided description.
For EACH question return exactly one line:

question_id: answer

Rules:
- Use the EXACT question_id
- Only write the answer
- No explanations

--------------------
TIME SERIES DESCRIPTION
--------------------
{description}

--------------------
QUESTIONNAIRE
--------------------
{questions}
"""

if __name__ == "__main__":

    for run_id in range(1, N_RUNS + 1):

        print(
            f"\n================ RUN {run_id} ================\n"
        )

        
        run_catch22(
            run_id=run_id,
            features_file= "Representations/Catch22/MTS-Representations/catch22_features.csv",
            output_dir="Experiments/Catch22",
            questionnaire=QUESTIONNAIRE,
            prompt_template=PROMPT_TEMPLATE_CATCH22,
            model=MODEL
        )
        
        
        run_images (
            run_id=run_id,
            images_dir=    "Representations/Images/MTS-Representations",
            features_file= "Representations/Catch22/MTS-Representations/catch22_features.csv",
            output_dir="Experiments/Images",
            questionnaire=QUESTIONNAIRE,
            prompt_template=PROMPT_TEMPLATE_IMAGES,
            model=MODEL

        )

        run_descriptions(
            run_id,
            images_dir = "Representations/Images/MTS-Representations",
            features_file = "Representations/Catch22/MTS-Representations/catch22_features.csv",
            output_dir="Experiments/Descriptions",
            questionnaire=QUESTIONNAIRE,
            description_prompt = DESCRIPTION_PROMPT,
            prompt_template=PROMPT_TEMPLATE_DESCRIPTION,
            model=MODEL
        )
