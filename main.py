# main.py - Bot Isabella pour Threads

import os
import time
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

THREADS_COOKIE = os.getenv("THREADS_COOKIE")
THREADS_USER_ID = os.getenv("THREADS_USER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai = OpenAI(api_key=OPENAI_API_KEY)

# Définir les heures d'activité (9h à 23h)
def is_within_active_hours():
    now = datetime.now().hour
    return 9 <= now < 23

# Simuler la récupération des commentaires Threads
def get_mock_comments():
    return ["Tu es trop belle", "Je veux te parler"]  # À remplacer plus tard par du scraping réel

# Simuler une réponse GPT-4
def generate_reply(comment):
    prompt = f"Tu es Isabella, une femme sensuelle, douce et élégante. Réponds à ce commentaire : {comment}"
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Erreur GPT-4] {str(e)}"

# Simulation de réponse et like sur Threads
def simulate_post_and_like(comment, reply):
    print(f"\n[💬] Commentaire: {comment}")
    print(f"[🤖] Réponse: {reply}")
    print("[❤️] Like envoyé")

async def run_bot():
    while True:
        if not is_within_active_hours():
            print("[Pause] En dehors des heures d'activité (9h-23h). Attente...")
            time.sleep(300)
            continue

        print("\n[🔁] Vérification des nouveaux commentaires...")
        comments = get_mock_comments()

        for comment in comments:
            reply = generate_reply(comment)
            simulate_post_and_like(comment, reply)
            time.sleep(5)

        time.sleep(120)  # Attente de 2 minutes avant le prochain cycle

if __name__ == "__main__":
    asyncio.run(run_bot())
