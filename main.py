import os
import time
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

load_dotenv()

THREADS_COOKIE = os.getenv("THREADS_COOKIE")
THREADS_USER_ID = os.getenv("THREADS_USER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai = OpenAI(api_key=OPENAI_API_KEY)
headers = {
    "Cookie": THREADS_COOKIE,
    "User-Agent": "Mozilla/5.0"
}

# Stockage local pour éviter les doublons
déjà_vus = set()

# Scraping Threads réel
def get_real_comments():
    url = f"https://www.threads.net/@{THREADS_USER_ID}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"⚠️ Erreur de scraping : {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    # Simule des commentaires trouvés sur la page (adapté au HTML réel si besoin)
    commentaires = [div.get_text() for div in soup.find_all("div") if "comment" in div.get("class", [])]
    nouveaux = [c for c in commentaires if c not in déjà_vus]
    
    for c in nouveaux:
        déjà_vus.add(c)
    
    return nouveaux

def generate_reply(comment):
    prompt = f"Tu es Isabella, une femme douce, sexy, confiante, de 50 ans, très élégante et un peu provocante. Réponds à ce commentaire : \"{comment}\" avec charme, humour et un ou deux emojis."
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=100
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"[Erreur GPT] {str(e)}"

def simulate_post_and_like(comment, reply):
    print(f"\n🗨️ Commentaire reçu : {comment}")
    print(f"🤖 Réponse d'Isabella : {reply}")
    print("❤️ Like automatique envoyé")

def is_within_active_hours():
    now = datetime.now().hour
    return 9 <= now < 23

async def run_bot():
    print("📌 Lancement de la boucle principale...")
    while True:
        if not is_within_active_hours():
            print("⏸️ Bot en pause (hors horaires 9h-23h).")
            await asyncio.sleep(300)
            continue

        print("🔄 Vérification des nouveaux commentaires...")
        comments = get_real_comments()

        for comment in comments:
            reply = generate_reply(comment)
            simulate_post_and_like(comment, reply)
            await asyncio.sleep(4)

        await asyncio.sleep(120)

if __name__ == "__main__":
    print("✅ Le bot est bien dans main.py et prêt à démarrer la boucle.")
    asyncio.run(run_bot())
