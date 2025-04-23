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

# Liste des commentaires déjà traités pour éviter les doublons
treated_comments = set()

def is_within_active_hours():
    now = datetime.now().hour
    return 9 <= now < 23

def get_mock_comments():
    return [
        "Tu es magnifique ❤️",
        "T'es dispo ce soir ? 😏",
        "C’est quoi ton secret beauté ?"
    ]

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
    print("🚀 Bot Isabella démarré.")
    while True:
        try:
            if not is_within_
