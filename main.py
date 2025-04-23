import os
import time
import asyncio
import logging
from playwright.async_api import async_playwright
from openai import OpenAI
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

THREADS_USER_ID = os.getenv("THREADS_USER_ID")
THREADS_COOKIE = os.getenv("THREADS_COOKIE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

logging.basicConfig(level=logging.INFO)

def extract_comments(page_source):
    # Extraction naïve des commentaires à adapter selon le HTML réel
    comments = []
    # TODO : Ajoutez ici le parsing réel du DOM si nécessaire
    return comments

async def generate_reply(comment):
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Tu es Isabella, une femme mature et séductrice, tu réponds avec intelligence et mystère."},
            {"role": "user", "content": comment}
        ]
    )
    return response.choices[0].message.content

async def run_bot():
    logging.info("Lancement du bot Isabella...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            extra_http_headers={"cookie": THREADS_COOKIE}
        )
        page = await context.new_page()

        while True:
            logging.info("Vérification des nouveaux commentaires...")
            await page.goto("https://www.threads.net/@isabella")
            await page.wait_for_timeout(5000)  # Attendre que la page charge

            comments = extract_comments(await page.content())
            for comment in comments:
                logging.info(f"💬 Commentaire reçu : {comment}")
                try:
                    reply = await generate_reply(comment)
                    logging.info(f"🤖 Réponse d'Isabella : {reply}")
                    # TODO : Simuler la réponse et le like si nécessaire
                except Exception as e:
                    logging.error(f"Erreur GPT : {e}")

            await page.wait_for_timeout(60000)  # Attendre 1 minute entre chaque scan

if __name__ == "__main__":
    asyncio.run(run_bot())
