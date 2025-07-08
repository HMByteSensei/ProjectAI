
# pip install nltk rouge-score bert-score torch

import os
import json
import csv
from rouge_score import rouge_scorer
from bert_score import score as bert_score
import nltk
import torch
from nltk.tokenize import TreebankWordTokenizer

# Ensure tokenizer is downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

tokenizer = TreebankWordTokenizer()
device = "cuda" if torch.cuda.is_available() else "cpu"

def calculate_compression(original, summary):
    return len(tokenizer.tokenize(original)) / max(1, len(tokenizer.tokenize(summary)))

def calculate_coverage(original, summary):
    orig_tokens = set(w.lower() for w in tokenizer.tokenize(original) if w.isalpha())
    summ_tokens = set(w.lower() for w in tokenizer.tokenize(summary) if w.isalpha())
    return len(orig_tokens & summ_tokens) / len(orig_tokens) if orig_tokens else 0

def calculate_density(original, summary, max_n=3):
    original_tokens = tokenizer.tokenize(original.lower())
    summary_tokens = tokenizer.tokenize(summary.lower())
    summary_len = len(summary_tokens)
    match_count = 0
    for n in range(1, max_n + 1):
        original_ngrams = set(tuple(original_tokens[i:i+n]) for i in range(len(original_tokens)-n+1))
        summary_ngrams = [tuple(summary_tokens[i:i+n]) for i in range(len(summary_tokens)-n+1)]
        match_count += sum(1 for ngram in summary_ngrams if ngram in original_ngrams)
    return match_count / max(1, summary_len)

def process_json_files(folder_path, output_csv):
    fieldnames = ["Kategorija", "ID", "Model", "Compression", "Coverage", "Density", "ROUGE-1", "ROUGE-2", "ROUGE-L", "BERTScore"]
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

    metadata = []
    all_summaries = []
    all_references = []

    for filename in os.listdir(folder_path):
        if not filename.endswith(".json"):
            continue

        with open(os.path.join(folder_path, filename), encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            original = item.get("tekst", "")
            kategorija = item.get("kategorija", "")
            tekst_id = item.get("id", "")
            reference = item.get("apstraktivna_sumarizacija", "")

            models = {
                "Ekstraktivna_sumarizacija": item.get("ekstraktivna_sumarizacija", ""),
                "ChatGPT": item.get("chatgpt_sumarizacija", ""),
                "Gemini": item.get("gemini_sumarizacija", ""),
                "Claude": item.get("claude_sumarizacija", "")
            }

            for model_name, summary in models.items():
                if not summary.strip():
                    continue

                compression = calculate_compression(original, summary)
                coverage = calculate_coverage(original, summary)
                density = calculate_density(original, summary)
                rouge = scorer.score(reference, summary)
                rouge1 = rouge["rouge1"].fmeasure
                rouge2 = rouge["rouge2"].fmeasure
                rougeL = rouge["rougeL"].fmeasure

                # Store everything to apply BERTScore in batch
                all_summaries.append(summary)
                all_references.append(reference)
                metadata.append({
                    "Kategorija": kategorija,
                    "ID": tekst_id,
                    "Model": model_name,
                    "Compression": round(compression, 2),
                    "Coverage": round(coverage, 2),
                    "Density": round(density * 100, 2),
                    "ROUGE-1": round(rouge1, 2),
                    "ROUGE-2": round(rouge2, 2),
                    "ROUGE-L": round(rougeL, 2)
                })

    print("Calculating BERTScore for", len(all_summaries), "pairs...")
    _, _, f1_scores = bert_score(all_summaries, all_references, lang="en", device=device, verbose=True)

    # Attach BERTScore to rows
    for i, row in enumerate(metadata):
        row["BERTScore"] = round(float(f1_scores[i]), 2)

    # Write to CSV
    with open(output_csv, "w", newline="", encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metadata)

# Folder s json fajlovima za racunanje matrika
folder_path = "faza3"  # Update if needed
output_csv = "Metrike_sumarizacija_inicijali.csv"
process_json_files(folder_path, output_csv)
