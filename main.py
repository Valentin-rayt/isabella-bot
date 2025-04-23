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

# Pour garder une trace des commentaires déjà traités
seen_comments = set()

# Vérifie si l'heure est entre 9h et 23h
def is_within_active_hours():
    now = datetime.now().hour
    return 9 <= now < 23

# Fonction pour récupérer les vrais commentaires avec Playwright
async def get_real_comments():
    comments = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            extra_http_headers={
                "cookie": THREADS_COOKIE
            }
        )
        page = await context.new_page()

        try:
            await page.goto(f"https://www.threads.net/@{THREADS_USER_ID}")
            await page.wait_for_selector("article")
            threads = await page.query_selector_all("article")

            for thread in threads:
                content = await thread.inner_text()
                if content and content not in seen_comments:
                    comments.append(content)
                    seen_comments.add(content)

        except Exception as e:
            print(f"Erreur Playwright : {e}")

        await browser.close()
    return comments

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
    print("🔧 Le bot est bien dans main.py et prêt à démarrer la boucle.")
    while True:
        if not is_within_active_hours():
            print("⏸️ Bot en pause (hors horaires 9h-23h).")
            await asyncio.sleep(300)
            continue

        print("\n🔁 Lancement de la boucle principale...")
        print("📲 Vérification des nouveaux commentaires...")

        comments = await get_real_comments()

        for comment in comments:
            reply = generate_reply(comment)
            simulate_post_and_like(comment, reply)
            await asyncio.sleep(4)

        await asyncio.sleep(120)

if __name__ == "__main__":
    print("🔧 Le bot est bien dans main.py et prêt à démarrer la boucle.")
    asyncio.run(run_bot())
