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

# Liste pour stocker les commentaires déjà traités
comment_history = set()

# Vérifie si l'heure est entre 9h et 23h
def is_within_active_hours():
    now = datetime.now().hour
    return 9 <= now < 23

# Simule des commentaires Threads (à remplacer par scraping réel)
def get_mock_comments():
    return [
        "Tu es magnifique ❤️",
        "T'es dispo ce soir ? 😏",
        "C’est quoi ton secret beauté ?"
    ]

# Utilise GPT-4 pour générer une réponse style Isabella
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

# Simule la réponse + le like
def simulate_post_and_like(comment, reply):
    print(f"\n🗨️ Commentaire reçu : {comment}")
    print(f"🤖 Réponse d'Isabella : {reply}")
    print("❤️ Like automatique envoyé")

# Boucle principale du bot
async def run_bot():
    print("🔁 Lancement de la boucle principale...")
    while True:
        if not is_within_active_hours():
            print("⏸️ Bot en pause (hors horaires 9h-23h).")
            await asyncio.sleep(300)
            continue

        print("\n🔎 Vérification des nouveaux commentaires...")
        comments = get_mock_comments()

        for comment in comments:
            if comment in comment_history:
                print(f"🔁 Commentaire déjà traité : {comment}")
                continue

            reply = generate_reply(comment)
            simulate_post_and_like(comment, reply)
            comment_history.add(comment)
            await asyncio.sleep(4)

        await asyncio.sleep(120)

if __name__ == "__main__":
    print("🔧 Le bot est bien dans main.py et prêt à démarrer la boucle.")
    asyncio.run(run_bot())
