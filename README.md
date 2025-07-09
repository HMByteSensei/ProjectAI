# ProjectAI - Balkan News Summarizer (mT5-small)

This project features a fine-tuned `google/mt5-small` model for abstractive text summarization of news articles written in Balkan languages (Bosnian, Croatian, Serbian). The model was trained on a custom-curated dataset from the Bosnian news portal [Buka.ba](https://www.buka.ba/).

## Project Goal

The main goal of this project was to fine-tune a model that can create good summaries for news articles in Bosnian. This is an interesting challenge because there aren't many robust NLP tools available for languages from our region.

## Key Features

- **Fine-tuned Model:** Utilizes `google/mt5-small`, a multilingual T5 model, fine-tuned specifically for summarization.
- **Custom Dataset:** Trained on a unique dataset of news articles from Buka.ba. The dataset is enriched with five different types of reference summaries for each article:
    1.  **Extractive Summary** (human-generated)
    2.  **Abstractive Summary** (human-generated)
    3.  **ChatGPT Summary** (AI-generated)
    4.  **Gemini Summary** (AI-generated)
    5.  **Claude Summary** (AI-generated)
- **Comprehensive Workflow:** The entire pipeline, from data loading to model evaluation, is implemented in a Google Colab notebook (`ModelTraining.py`).
- **Reproducibility:** The repository includes the training script and clear instructions to replicate the results and use the trained model.

## Project Workflow & Algorithm

The project is structured into several distinct phases, as implemented in the `ModelTraining.py` script.

1.  **Data Preparation (Prerequisite)**
    -   News articles were scraped from the Buka.ba portal.
    -   For each article, five different reference summaries were generated as described in the project specification (see "Dataset" section below).
    -   The collected data (original text + 5 summaries) was stored in multiple JSON files, one for each news category.

2.  **Environment Setup**
    -   Installs necessary Python libraries, including `transformers`, `datasets`, `evaluate`, and `torch`.

3.  **Data Loading & Aggregation**
    -   The script prompts the user to upload all `*.json` data files.
    -   It loads each JSON file into a pandas DataFrame.
    -   All DataFrames are concatenated into a single master DataFrame.
    -   Duplicate articles are removed based on their unique `id`.

4.  **Data Preprocessing for Training**
    -   To leverage all available summaries, the dataset is restructured. For each article, five `(text, summary)` pairs are created, one for each summary type (`claude_sumarizacija`, `chatgpt_sumarizacija`, etc.).
    -   This consolidated DataFrame is then cleaned by removing entries with short or missing text/summary fields.
    -   The final dataset is split into a 90% training set and a 10% testing set.

5.  **Tokenization**
    -   The `AutoTokenizer` for `google/mt5-small` is used.
    -   A `preprocess_function` prepares the data for the model:
        -   The prefix `"summarize: "` is added to the input text to instruct the model on the task.
        -   Input texts are tokenized up to a `max_input_length` of 1024.
        -   Target summaries are tokenized up to a `max_target_length` of 128.
        -   The tokenized summaries are set as the `labels` for the model.

6.  **Model Training**
    -   `Seq2SeqTrainingArguments` are configured for the training process. Key parameters include:
        -   `max_steps=2000`
        -   `learning_rate=2e-5`
        -   `per_device_train_batch_size=4`
        -   `eval_strategy="steps"` (evaluation is performed every 500 steps).
    -   The `Seq2SeqTrainer` orchestrates the training using the tokenized datasets, a data collator, and a `compute_metrics` function to calculate ROUGE scores during evaluation.

7.  **Evaluation & Inference**
    -   After training, a final evaluation is run on the test set to get the final performance metrics.
    -   The best-performing model checkpoint is loaded into a `summarization` pipeline for easy use in generating new summaries.

## Performance & Results

The model was evaluated on the test set after completing 2000 training steps. The final evaluation yielded the following ROUGE scores, which measure the overlap between the model-generated summaries and the reference summaries.

| Metric          | Score   |
| --------------- | ------- |
| **eval_loss**   | `3.054` |
| **eval_rouge1** | `0.128` |
| **eval_rouge2** | `0.053` |
| **eval_rougeL** | `0.107` |
| **eval_gen_len**| `19.05` |

**Analysis:**
The ROUGE scores indicate that the model has begun to learn the summarization task, but the performance is still at a basic level. The low scores, combined with the observed repetitive and sometimes incoherent output during testing, suggest that the model is under-trained. This is expected for a small model (`mt5-small`) trained for only 2000 steps on a small dataset. For a production-ready system, a larger model, more training data, and extended training time would be required. Nevertheless, the key result is that the entire workflow is successfully implemented, showing that the program correctly handles data processing, training, and summary generation.


## Demo: How to Use the Trained Model

You can easily use the final trained model for inference on new text. The trained model is provided in the `model.zip` file.

### 1. Prerequisites

- Python 3.8+
- PyTorch and Transformers
- The trained model checkpoint

### 2. Setup

First, clone the repository and install the required packages:

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
pip install transformers[torch] sentencepiece
```

Next, unzip the trained model. The training script saves the final model in a path like ./mt5-small-balkan-news-summarizer/checkpoint-2000. Make sure this folder exists in your project directory.

```bash
# Unzip the provided model archive
unzip model.zip
```
### 3. Inference Script

Create a Python file (e.g., summarize.py) and use the following code to generate a summary.
```py
from transformers import pipeline
import torch

# Path to the best-performing model checkpoint
# This path is created after unzipping model.zip
MODEL_PATH = "./mt5-small-balkan-news-summarizer/checkpoint-2000"

# Check if GPU is available
device = 0 if torch.cuda.is_available() else -1

# Load the summarization pipeline
summarizer = pipeline("summarization", model=MODEL_PATH, device=device)

# Example article text (in Bosnian/Serbian/Croatian)
# Replace this with any news article you want to summarize
article_text = """
Pomijeranjem za jedan sat unaprijed u nedjelju rano ujutro počinje ljetno računanje vremena, 
koje će trajati do 29. oktobra. Ljetno računanje vremena počinje posljednje nedjelje u martu 
pomicanjem za jedan sat unaprijed pa se tako vrijeme u dva sata ujutro računa kao tri sata ujutro. 
Ljetno računanje vremena završava posljednje nedjelje u oktobru, odnosno ove godine 29. oktobra, 
pomijeranjem za jedan sat unazad, kada će se tri sata ujutro računati kao dva sata ujutro. 
Ovaj mehanizam uveden je radi uštede energije, jer se dnevno svjetlo produžava u večernje sate.
"""

# Generate the summary
generated_summary = summarizer(
    article_text,
    max_length=150,  # Maximum length of the summary
    min_length=30,   # Minimum length of the summary
    do_sample=False
)[0]['summary_text']

print("--- ORIGINAL ARTICLE ---")
print(article_text)
print("\n--- GENERATED SUMMARY ---")
print(generated_summary)
```

### 4. Run the script

```bash
python summarize.py
```

## Future Work

- **Larger Model:** Experiment with fine-tuning a larger model like google/mt5-base for potentially higher quality summaries, at the cost of more computational resources.
- **Dataset Expansion:** Enlarge the dataset with articles from other regional news portals to improve generalization.
