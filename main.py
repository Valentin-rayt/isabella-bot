import os
import time
import asyncio
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

THREADS_COOKIE = os.getenv("THREADS_COOKIE")
THREADS_USER_ID = os.getenv("THREADS_USER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai = OpenAI(api_key=OPENAI_API_KEY)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Cookie": THREADS_COOKIE
}

BASE_URL = f"https://www.threads.net/@{THREADS_USER_ID}"

treated_comments = set()

def is_within_active_hours():
    now = datetime.now().hour
    return 9 <= now < 23

def get_real_comments():
    try:
        response = requests.get(BASE_URL, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        comments_html = soup.find_all("span")
        comments = [span.text.strip() for span in comments_html if span.text.strip()]
        return comments[-3:]  # dernières lignes visibles
    except Exception as e:
        print(f"[Erreur scraping] {e}")
        return []

def generate_reply(comment):
    prompt = f"Tu es Isabella, une femme douce, sexy, confiante, de 50 ans, très élégante et un peu provocante. Réponds à ce commentaire : \"{comment}\" avec charme, humour et un ou deux emojis."
    try:
        completion = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85,
            max_tokens=100
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"[Erreur GPT] {str(e)}"

def simulate_post_and_like(comment, reply):
    print(f"\n🔈 Commentaire reçu : {comment}")
    print(f"🤖 Réponse d'Isabella : {reply}")
    print("❤️ Like automatique envoyé")

async def run_bot():
    print("🔧 Le bot est bien dans main.py et prêt à démarrer la boucle.")
    while True:
        if not is_within_active_hours():
            print("⏸️ Bot en pause (hors horaires 9h-23h).")
            time.sleep(300)
            continue

        print("\n📁 Lancement de la boucle principale...")
        print("🔹 Vérification des nouveaux commentaires...")
        comments = get_real_comments()

        for comment in comments:
            if comment in treated_comments:
                print(f"📂 Commentaire déjà traité : {comment}")
                continue

            reply = generate_reply(comment)
            simulate_post_and_like(comment, reply)
            treated_comments.add(comment)
            time.sleep(5)

        time.sleep(120)

if __name__ == "__main__":
    asyncio.run(run_bot())
