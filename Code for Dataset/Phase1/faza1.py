import os
import json
import csv
import re

ROOT_DIR = r'D:\FAX\VI\proj\proj\faza1\buka.ba'

OUTPUT_FIELDS = [
    "portal", "kategorija", "id", "url", "datum", "naslov", "tekst",
    "ekstraktivna_sumarizacija", "apstraktivna_sumarizacija",
    "chatgpt_sumarizacija", "gemini_sumarizacija", "claude_sumarizacija"
]

def parse_article(content):
    """
    Extracts metadata and text from the article content.
    """
    fields = {
        'PORTAL': '',
        'DATUM': '',
        'RUBRIKA': '',
        'NASLOV': '',
        'LINK': ''
    }

    lines = content.strip().splitlines()
    text_lines = []
    in_text = False

    for line in lines:
        line = line.strip()
        if line.startswith('PORTAL:'):
            fields['PORTAL'] = line.replace('PORTAL:', '').strip()
        elif line.startswith('DATUM:'):
            fields['DATUM'] = line.replace('DATUM:', '').strip()
        elif line.startswith('RUBRIKA:'):
            fields['RUBRIKA'] = line.replace('RUBRIKA:', '').strip()
        elif line.startswith('NASLOV:'):
            fields['NASLOV'] = line.replace('NASLOV:', '').strip()
        elif line.startswith('LINK:'):
            fields['LINK'] = line.replace('LINK:', '').strip()
        elif line.startswith('<***>'):
            in_text = True
        elif in_text:
            text_lines.append(line)

    tekst = '\n'.join(text_lines).strip()
    return {
        "portal": fields['PORTAL'],
        "kategorija": fields['RUBRIKA'],
        "url": fields['LINK'],
        "datum": fields['DATUM'],
        "naslov": fields['NASLOV'],
        "tekst": tekst
    }

def process_category(category_path, category_name):
    articles = []

    for filename in os.listdir(category_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(category_path, filename)
            base_id = os.path.splitext(filename)[0]  # removes .txt
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                if "<***>" in content:
                    parts = content.split("<***>")
                    part_number = 1
                    for part in parts:
                        part = part.strip()
                        if part:
                            article = parse_article(part)
                            if article["url"]:  # only if valid
                                article["id"] = f"{base_id}_{part_number}"
                                part_number += 1
                                # Add empty summarization fields
                                for field in OUTPUT_FIELDS[7:]:
                                    article[field] = ""
                                articles.append(article)
    return articles


def write_json_csv(category, articles):
    json_filename = f"buka_{category}_RA.json"
    csv_filename = f"buka_{category}_RA.csv"

    with open(json_filename, "w", encoding="utf-8") as json_file:
        json.dump(articles, json_file, ensure_ascii=False, indent=2)

    with open(csv_filename, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for article in articles:
            writer.writerow(article)

def main():
    for category in os.listdir(ROOT_DIR):
        category_path = os.path.join(ROOT_DIR, category)
        if os.path.isdir(category_path):
            articles = process_category(category_path, category)
            if articles:
                write_json_csv(category, articles)
                print(f"Processed {len(articles)} articles in category '{category}'.")

if __name__ == "__main__":
    main()
