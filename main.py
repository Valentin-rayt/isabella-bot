import os
import time
import openai
from playwright.sync_api import sync_playwright

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
COOKIE = os.environ.get("THREADS_COOKIE")
TARGET_URL = os.environ.get("THREADS_POST_URL")

openai.api_key = OPENAI_API_KEY

ISABELLA_STYLE = "Réponds comme Isabella, une femme virtuelle mature, douce et séductrice. Utilise des emojis, sois intrigante et joueuse, sans vulgarité. Réponds de façon courte et mystérieuse."

def generate_reply(comment):
    prompt = f"{ISABELLA_STYLE}\n\nCommentaire: {comment}\nRéponse:" 
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=80
    )
    return response.choices[0].message.content.strip()

def run_bot():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies([{
            'name': 'sessionid',
            'value': COOKIE,
            'domain': '.threads.net',
            'path': '/',
            'httpOnly': True,
            'secure': True
        }])

        page = context.new_page()
        page.goto(TARGET_URL)
        time.sleep(5)

        comments = page.query_selector_all('div[role="comment"]')
        for comment in comments:
            try:
                text = comment.inner_text()
                like_button = comment.query_selector('svg[aria-label="J’aime"]')
                if like_button:
                    like_button.click()
                reply = generate_reply(text)
                comment.click()
                page.keyboard.type(reply)
                page.keyboard.press("Enter")
                time.sleep(5)
            except Exception as e:
                print("Erreur sur un commentaire :", e)

        browser.close()

if __name__ == "__main__":
    run_bot()
