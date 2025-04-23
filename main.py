import os
import time
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from playwright.async_api import async_playwright

load_dotenv()

THREADS_COOKIE = os.getenv("THREADS_COOKIE")
THREADS_USER_ID = os.getenv("THREADS_USER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai = OpenAI(api_key=OPENAI_API_KEY)

# Vérifie si l'heure est entre 9h et 23h
def is_within_active_hours():
    now = datetime.now().hour
    return 9 <= now < 23

# Simule des commentaires Threads (à remplacer plus tard par un vrai scraping)
def get_mock_comments():
    return ["Tu es magnifique ❤️", "T'es dispo ce soir ? 😏", "C’est quoi ton secret beauté ?"]

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

# Scraping des commentaires Threads
async def get_threads_comments():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-software-rasterizer"])
        page = await browser.new_page()

        # Connexion et récupération des commentaires sous ton post
        await page.goto("https://www.threads.net/")
        await page.fill('input[name="username"]', THREADS_USER_ID)
        await page.fill('input[name="password"]', THREADS_COOKIE)
        await page.click('button[type="submit"]')

        comments = await page.query_selector_all('.comment-selector')  # Ajuste le sélecteur selon la structure HTML

        comments_text = []
        for comment in comments:
            text = await comment.text_content()
            comments_text.append(text)

        await browser.close()

    return comments_text

# Simule la réponse + le like
def simulate_post_and_like(comment, reply):
    print(f"\n🗨️ Commentaire reçu : {comment}")
    print(f"🤖 Réponse d'Isabella : {reply}")
    print("❤️ Like automatique envoyé")

# Boucle principale du bot
async def run_bot():
    while True:
        if not is_within_active_hours():
            print("⏸️ Bot en pause (hors horaires 9h-23h).")
            time.sleep(300)
            continue

        print("\n🔁 Vérification des nouveaux commentaires...")
        comments = await get_threads_comments()

        for comment in comments:
            reply = generate_reply(comment)
            simulate_post_and_like(comment, reply)
            time.sleep(4)

        time.sleep(120)

if __name__ == "__main__":
    print("🔧 Le bot est bien dans main.py et prêt à démarrer la boucle.")
    asyncio.run(run_bot())
