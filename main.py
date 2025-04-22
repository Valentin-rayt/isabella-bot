import os
import time
import asyncio
from openai import OpenAI
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Charger les variables d'environnement
load_dotenv()
COOKIE = os.getenv("THREADS_COOKIE")
USER_ID = os.getenv("THREADS_USER_ID")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_cookies([{
            "name": "sessionid",
            "value": COOKIE,
            "domain": ".threads.net",
            "path": "/",
            "httpOnly": True,
            "secure": True,
            "sameSite": "Lax"
        }])
        page = await context.new_page()

        # Aller sur la page utilisateur Threads
        await page.goto(f"https://www.threads.net/@{USER_ID}")
        await page.wait_for_timeout(3000)

        # Trouver les commentaires sous les posts
        comments = await page.query_selector_all("article div[dir='auto']")
        for comment in comments:
            text = await comment.inner_text()
            print(f"[🗨️] Nouveau commentaire : {text}")

            # Demander à GPT-4 une réponse stylée Isabella
            gpt_reply = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es Isabella, une femme très séduisante, douce et mystérieuse. Tu réponds avec empathie, assurance et quelques emojis. Tu restes toujours élégante."
                    },
                    {"role": "user", "content": text}
                ]
            )

            final_reply = gpt_reply.choices[0].message.content.strip()
            print(f"[🤖] Réponse d'Isabella : {final_reply}")

            # Poster la réponse (à coder selon API Threads/scrap)
            print(f"[💬] (simulation) Poster : {final_reply}")

            # Liker le commentaire (à coder selon Playwright ou API Threads)
            print("[❤️] (simulation) Like du commentaire")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
