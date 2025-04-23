import os
import time
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

THREADS_COOKIE = os.getenv("THREADS_COOKIE")
THREADS_USER_ID = os.getenv("THREADS_USER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai = OpenAI(api_key=OPENAI_API_KEY)

def is_within_active_hours():
    now = datetime.now().hour
    return 9 <= now < 23

# Stocke les commentaires déjà répondus
seen_comments = set()

# Mock de commentaires pour démo
MOCK_COMMENTS = [
    "Tu es magnifique ❤️",
    "T'es dispo ce soir ? 😏",
    "C’est quoi ton secret beauté ?"
]

def get_mock_comments():
    return MOCK_COMMENTS

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
    print(f"\n🗨️ Commentaire reçu : {comment}")
    print(f"🤖 Réponse d'Isabella : {reply}")
    print("❤️ Like automatique envoyé")

async def run_bot():
    print("🔧 Le bot est bien dans main.py et prêt à démarrer la boucle.")
    while True:
        if not is_within_active_hours():
            print("⏸️ Bot en pause (hors horaires 9h-23h).")
            await asyncio.sleep(300)
            continue

        print("\n🔁 Lancement de la boucle principale...")
        print("🔍 Vérification des nouveaux commentaires...")

        comments = get_mock_comments()

        for comment in comments:
            if comment in seen_comments:
                print(f"🔹 Commentaire déjà traité : {comment}")
                continue

            seen_comments.add(comment)
            reply = generate_reply(comment)
            simulate_post_and_like(comment, reply)
            await asyncio.sleep(3)

        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(run_bot())
