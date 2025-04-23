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

def is_within_active_hours():
    now = datetime.now().hour
    return 9 <= now < 23

def generate_reply(comment):
    prompt = f"Tu es Isabella, une femme douce, sexy, confiante, de 50 ans, \
              très élégante et un peu provocante. \
              Réponds à ce commentaire : \"{comment}\" avec charme, humour et 2 emojis."
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

async def run_bot():
    print("🔧 Bot Isabella démarré.")
    processed_comments = set()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state={"cookies": [
            {
                "name": "sessionid",
                "value": THREADS_COOKIE,
                "domain": ".threads.net",
                "path": "/",
                "httpOnly": True,
                "secure": True
            }
        ]})
        page = await context.new_page()

        while True:
            if not is_within_active_hours():
                print("⏸️ Bot en pause (hors horaires 9h-23h).")
                await asyncio.sleep(300)
                continue

            print("\n🔁 Vérification des nouveaux commentaires...")

            try:
                await page.goto(f"https://www.threads.net/@{THREADS_USER_ID}", timeout=60000)
                await page.wait_for_timeout(5000)  # Temps pour charger les posts

                comments = await page.locator("article div[dir='auto']").all_text_contents()

                for comment in comments:
                    if comment in processed_comments:
                        print(f"📲 Commentaire déjà traité : {comment}")
                        continue

                    reply = generate_reply(comment)
                    print(f"\n🖊️ Commentaire reçu : {comment}")
                    print(f"🧑‍🔬 Réponse d'Isabella : {reply}")
                    print("❤️ Like automatique envoyé")
                    processed_comments.add(comment)

                await asyncio.sleep(120)  # Pause avant la prochaine boucle

            except Exception as e:
                print(f"[Erreur Playwright] {str(e)}")
                await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(run_bot())
