import os
import asyncio
from openai import OpenAI
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

THREADS_COOKIE = os.getenv("THREADS_COOKIE")
THREADS_USER_ID = os.getenv("THREADS_USER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

async def reply_to_comment(comment: str) -> str:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Tu es Isabella, une femme mature, élégante, douce, sexy, confiante, qui répond aux commentaires de façon séduisante, polie et suggestive."
            },
            {"role": "user", "content": f"Commentaire : {comment}"}
        ]
    )
    return response.choices[0].message.content.strip()

async def run_bot():
    print("🤖 Bot Isabella lancé ✔️")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        context.add_cookies([
            {
                "name": "ds_user_id",
                "value": THREADS_USER_ID,
                "domain": ".instagram.com",
                "path": "/"
            },
            {
                "name": "sessionid",
                "value": THREADS_COOKIE,
                "domain": ".instagram.com",
                "path": "/"
            }
        ])
        page = await context.new_page()
        await page.goto("
