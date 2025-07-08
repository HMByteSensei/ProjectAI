import json
import csv

# Putanje do ulaznog JSON fajla i izlaznog CSV fajla
input_json_file = 'buka_Podcast_RA.json'
output_csv_file = 'buka_Podcast_RA.csv'

# Učitaj JSON podatke
with open(input_json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Definiši nazive kolona za CSV
fieldnames = [
    "portal", "kategorija", "id", "url", "datum", "naslov",
    "tekst", "ekstraktivna_sumarizacija", "apstraktivna_sumarizacija",
    "chatgpt_sumarizacija", "gemini_sumarizacija", "claude_sumarizacija"
]

# Upis podataka u CSV (sve u jednom redu po zapisu)
with open(output_csv_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    for entry in data:
        # Pretvori višelinijske tekstove u jednovrednosne linije (zamjeni nove redove i višestruke razmake)
        clean_entry = {key: (value.replace('\n', ' ').replace('\r', ' ').strip() if isinstance(value, str) else value)
                       for key, value in entry.items()}
        writer.writerow(clean_entry)

print(f"Podaci su uspješno upisani u {output_csv_file}")
