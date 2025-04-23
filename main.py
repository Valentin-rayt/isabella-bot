import os
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import requests

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
THREADS_COOKIE = os.getenv("THREADS_COOKIE")
THREADS_USER_ID = os.getenv("THREADS_USER_ID")

HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}

async def fetch_latest_comments(page):
    await page.goto(f"https://www.threads.net/@{THREADS_USER_ID}")
    await page.wait_for_timeout(5000)  # attendre le chargement
    comments = await page.locator("xpath=//div[contains(@class, 'x1iorvi4')]").all_text_contents()
    return comments[-3:]

def generate_reply(comment):
    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "Tu es Isabella, une femme charmante, réactive, mystérieuse, joueuse et séduisante."},
            {"role": "user", "content": f"Commentaire : {comment}\nRéponds de manière naturelle et engageante."}
        ]
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=HEADERS, json=data)
    return response.json()["choices"][0]["message"]["content"]

async def run_bot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state={"cookies": [{"name": "sessionid", "value": THREADS_COOKIE, "domain": ".threads.net"}]})
        page = await context.new_page()

        print("\U0001F50D Vérification des nouveaux commentaires...")
        comments = await fetch_latest_comments(page)

        for comment in comments:
            print(f"\U0001F4AC Commentaire reçu : {comment}")
            reply = generate_reply(comment)
            print(f"\U0001F4DD Réponse d'Isabella : {reply}")
            # Tu peux ajouter ici la publication de réponse automatiquement si tu veux
            print("\u2764\ufe0f Like automatique envoyé\n")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_bot())
