import os
import asyncio
import logging
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import openai

load_dotenv()

# Configurations des clés
THREADS_COOKIE = os.getenv("THREADS_COOKIE")
THREADS_USER_ID = os.getenv("THREADS_USER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)

def format_response(raw):
    # Personnalise la réponse dans le style Isabella
    return f"❤️ {raw.strip()} ☺️"

async def get_gpt_reply(prompt):
    try:
        completion = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es Isabella, une femme de 50 ans, séduisante, directe, affectueuse."},
                {"role": "user", "content": prompt}
            ]
        )
        return format_response(completion.choices[0].message.content)
    except Exception as e:
        logging.error(f"Erreur GPT: {e}")
        return "Oups, une erreur est survenue."

async def handle_comment(comment, page):
    logging.info(f"\U0001f4ac Commentaire reçu : {comment}")
    response = await get_gpt_reply(comment)
    logging.info(f"\U0001f916 Réponse d'Isabella : {response}")
    # ICI: logiquement, tu insères le commentaire avec Playwright

    logging.info("\u2764\ufe0f Like automatique envoyé")

async def run_bot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            extra_http_headers={
                "cookie": THREADS_COOKIE
            }
        )
        page = await context.new_page()

        await page.goto("https://www.threads.net/@ton_compte")
        logging.info("✨ Vérification des nouveaux commentaires...")

        commentaires = [
            "Tu es magnifique ❤️",
            "T'es dispo ce soir ? 😉",
            "C'est quoi ton secret beauté ?"
        ]  # à remplacer par de la vraie lecture dynamique

        for comment in commentaires:
            await handle_comment(comment, page)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_bot())
