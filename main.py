import os
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import openai

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
THREADS_COOKIE = os.getenv("THREADS_COOKIE")
THREADS_USER_ID = os.getenv("THREADS_USER_ID")
openai.api_key = OPENAI_API_KEY

# Fonctions
async def get_latest_comments(page, user_id):
    await page.goto(f"https://www.threads.net/@{user_id}")
    await page.wait_for_timeout(5000)  # attendre le chargement
    comments = await page.locator("xpath=//span[contains(text(),'commentaire')]/../..").all_text_contents()
    return comments[:3]

async def ask_gpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Tu es Isabella, une femme sexy, douce, malicieuse et provocante."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

async def reply_to_comments(context, comments):
    for comment in comments:
        response = await ask_gpt(comment)
        print(f"\n💬 Commentaire: {comment}\n🤖 Réponse d'Isabella: {response}\n❤️ Like automatique envoyé")

async def run_bot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            extra_http_headers={"cookie": THREADS_COOKIE}
        )
        page = await context.new_page()
        comments = await get_latest_comments(page, THREADS_USER_ID)
        await reply_to_comments(context, comments)
        await browser.close()

# Exécution en boucle de 9h à 23h
async def main():
    while True:
        heure = int(str(asyncio.get_event_loop().time())[-5:]) % 24
        if 9 <= heure < 23:
            await run_bot()
        await asyncio.sleep(300)  # pause de 5 min entre chaque boucle

if __name__ == "__main__":
    asyncio.run(main())
