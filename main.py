import os
import time
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from openai import OpenAI

# Chargement des variables d'environnement
load_dotenv()

THREADS_COOKIE = os.getenv("THREADS_COOKIE")
THREADS_USER_ID = os.getenv("THREADS_USER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai = OpenAI(api_key=OPENAI_API_KEY)

HEADERS = {
    "cookie": f"sessionid={THREADS_COOKIE}",
    "user-agent": "Mozilla/5.0",
    "content-type": "application/json"
}

# Vérifie si l'heure est entre 9h et 23h
def is_within_active_hours():
    now = datetime.now().hour
    return 9 <= now < 23

# Répond à un commentaire avec GPT
def generate_reply(comment):
    prompt = f"Tu es Isabella, une femme douce, sexy, confiante de 50 ans. Réponds avec charme et humour à : \"{comment}\""
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85,
            max_tokens=100
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"[Erreur GPT] {str(e)}"

# Scrape les commentaires depuis ton propre profil Threads
async def get_own_post_comments(playwright):
    try:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(f"https://www.threads.net/@{THREADS_USER_ID}")

        # Simule le cookie
        await context.add_cookies([{
            "name": "sessionid",
            "value": THREADS_COOKIE,
            "domain": ".threads.net",
            "path": "/"
        }])

        await page.reload()
        await page.wait_for_selector("article")
        posts = await page.query_selector_all("article")
        comments_data = []

        for post in posts:
            post_id = await post.get_attribute("data-id")
            if not post_id:
                continue
            # Accède à la page du post directement
            await page.goto(f"https://www.threads.net/p/{post_id}")
            await page.wait_for_timeout(2000)
            comments = await page.query_selector_all(".x1iorvi4")  # Ex. de classe
            for c in comments:
                text = await c.inner_text()
                if text:
                    comments_data.append({"post_id": post_id, "text": text})

        await browser.close()
        return comments_data
    except Exception as e:
        print(f"[❌ Erreur scraping] {e}")
        return []

# Post la réponse sur Threads (à implémenter selon API privée ou via Playwright injection)
async def post_reply_stub(comment_text):
    print(f"[🔁 Simulé] Réponse postée : {comment_text}")

# Boucle principale
async def run_bot():
    print("⚙️ Lancement de la boucle principale...")
    while True:
        if not is_within_active_hours():
            print("⏸️ Bot en pause (hors horaires autorisés)")
            await asyncio.sleep(300)
            continue

        print("🔍 Vérification des nouveaux commentaires...")
        async with async_playwright() as playwright:
            comments = await get_own_post_comments(playwright)

            for comment in comments:
                reply = generate_reply(comment['text'])
                await post_reply_stub(reply)
                print("❤️ Like automatique simulé")
                await asyncio.sleep(5)

        await asyncio.sleep(120)

if __name__ == "__main__":
    print("✅ Le bot est bien dans main.py et prêt à démarrer la boucle.")
    asyncio.run(run_bot())
