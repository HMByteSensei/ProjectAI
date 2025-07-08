import json
import time
import requests
import random

# ostale sumarizacije su odradjenje rucno jer se API placaju
# registrujte se za Geminy API i dodajte svoj API KEY ispod
API_KEY = ""
MODEL_NAME = "gemini-2.0-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

def generisi_sumarizaciju_gemini(tekst):
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [
                    {"text": f"Odradi sumarizaciju sljedećeg teksta:\n\n{tekst}"}
                ]
            }
        ]
    }

    for attempt in range(5):
        response = requests.post(API_URL, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"].strip()
        elif response.status_code == 429:
            print("Prekoračen rate limit, čekam 60 sekundi...")
            time.sleep(60)
        elif response.status_code == 503:
            wait = 10 * (2 ** attempt) + random.uniform(0, 5)
            print(f"503 Server Unavailable, čekam {wait:.1f} sekundi prije ponovnog pokušaja...")
            time.sleep(wait)
        else:
            response.raise_for_status()
    raise Exception("Neuspjeli pokušaji zbog 503 greške.")

def podeli_tekst(tekst, max_duzina=1500):
    delovi = []
    start = 0
    while start < len(tekst):
        end = start + max_duzina
        if end >= len(tekst):
            delovi.append(tekst[start:])
            break
        else:
            poslednja_tacka = tekst.rfind('.', start, end)
            if poslednja_tacka == -1 or poslednja_tacka <= start:
                delovi.append(tekst[start:end])
                start = end
            else:
                delovi.append(tekst[start:poslednja_tacka+1])
                start = poslednja_tacka + 1
    return delovi

# Input file
with open("buka_Podcast_RA.json", encoding="utf-8") as f_json:
    data = json.load(f_json)

# Ograniči na maksimalno 200 članaka
data = data[:200]

# Obradi svaki članak
for i, clanak in enumerate(data, start=1):
    print(f"({i}/{len(data)}) Generišem sumarizaciju (Gemini) za: {clanak['naslov']}")
    try:
        tekstovi = podeli_tekst(clanak["tekst"], max_duzina=1500)
        segmentne_sumarizacije = []

        for deo in tekstovi:
            for attempt in range(3):
                try:
                    suma = generisi_sumarizaciju_gemini(deo)
                    time.sleep(4)
                    segmentne_sumarizacije.append(suma)
                    break
                except Exception as e:
                    if "429" in str(e):
                        print("   Prekoračena kvota. Pauziram 60 sekundi...")
                        time.sleep(60)
                    else:
                        print(f"Greška pri obradi segmenta članka {clanak.get('id', 'N/A')}: {e}")
                        break
            else:
                segmentne_sumarizacije.append("")

        clanak["gemini_sumarizacija"] = " ".join(segmentne_sumarizacije).strip()

    except Exception as e:
        print(f"Greška pri obradi članka {clanak.get('id', 'N/A')}: {e}")
        clanak["gemini_sumarizacija"] = ""

# Output file
with open("buka_Podcast_RA.json", "w", encoding="utf-8") as f_out:
    json.dump(data, f_out, ensure_ascii=False, indent=2)

print("Završeno. Novi JSON sa Gemini sumarizacijama je sačuvan kao 'buka_Podcast_RA.json'.")
