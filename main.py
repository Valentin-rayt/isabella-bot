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

seen_comments = set()

def is_within_active_hours():
    hour = datetime.now().hour
    return 9 <= hour < 23

async def get_real_comments(page):
    await page.goto(f"https://www.threads.net/@{THREADS_USER_ID}")
    await page.wait_for_timeout(3000)
    comments = await page.locator("xpath=//span[contains(text(), 'commenté')]//ancestor::div[contains(@class, 'thread')]//span").all_text_contents()
    return comments[-3:]

def generate_reply(comment):
    prompt = f"Tu es Isabella, une femme douce, sexy, confiante, de 50 ans, très élégante et un peu provocante. Réponds à ce commentaire : \"{comment}\" avec charme, humour et quelques emojis."
    try:
        completion = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85,
            max_tokens=120
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"[Erreur GPT] {str(e)}"

async def run_bot():
    print("✅ Le bot est bien dans main.py et prêt à démarrer la boucle.")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        context.add_cookies([{
            "name": "ds_user_id",
            "value": THREADS_USER_ID,
            "domain": ".threads.net",
            "path": "/",
            "httpOnly": True,
            "secure": True
        }, {
            "name": "sessionid",
            "value": THREADS_COOKIE,
            "domain": ".threads.net",
            "path": "/",
            "httpOnly": True,
            "secure": True
        }])
        page = await context.new_page()

        while True:
            if not is_within_active_hours():
                print("⏸️ En pause, hors horaires autorisés (9h-23h).")
                await asyncio.sleep(300)
                continue

            print("🔁 Vérification des nouveaux commentaires...")
            comments = await get_real_comments(page)

            for comment in comments:
                if comment in seen_comments:
                    print(f"🧠 Commentaire déjà traité : {comment}")
                    continue

                seen_comments.add(comment)
                print(f"🗨️ Nouveau commentaire reçu : {comment}")
                reply = generate_reply(comment)
                print(f"🤖 Réponse d'Isabella : {reply}")
                print("❤️ Like automatique envoyé")

            await asyncio.sleep(120)

if __name__ == "__main__":
    print("🔧 Le bot est bien dans main.py et prêt à démarrer la boucle.")
    asyncio.run(run_bot())

