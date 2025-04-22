import os
import time
import requests
from openai import OpenAI
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
THREADS_COOKIE = os.getenv("THREADS_COOKIE")
THREADS_USER_ID = os.getenv("THREADS_USER_ID")

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_reply(comment):
    system = "Tu es Isabella, une femme de 50 ans très séduisante, sensuelle, douce et malicieuse. Tu parles avec charme et assurance."
    user = f"Quelqu’un t’a laissé ce commentaire : {comment}\nRéponds-lui avec ta personnalité en 1 ou 2 phrases + ajoute un emoji à la fin."
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
    )
    return response.choices[0].message.content.strip()

def run_bot():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Authentification Threads
        page.add_init_script(f"""() => {{
            document.cookie = "sessionid={THREADS_COOKIE}";
        }}""")

        print("Connexion à Threads...")
        page.goto(f"https://www.threads.net/@{THREADS_USER_ID}")
        page.wait_for_timeout(5000)

        print("Récupération des derniers commentaires...")
        comments = page.query_selector_all("article div[role='button']")

        for comment in comments[:5]:  # ⛔ limiter à 5 pour test
            try:
                text = comment.inner_text()
                print(f"> Commentaire : {text}")
                reply = generate_reply(text)
                print(f"→ Réponse IA : {reply}")

                comment.click()
                page.wait_for_timeout(1000)
                reply_box = page.query_selector("textarea")
                reply_box.fill(reply)
                page.keyboard.press("Enter")
                time.sleep(2)

                # Like auto après avoir posté
                like_btn = page.query_selector("svg[aria-label='Like']") or page.query_selector("svg[aria-label='J’aime']")
                if like_btn:
                    like_btn.click()
                    print("❤️ Like envoyé")
            except Exception as e:
                print(f"Erreur sur un commentaire : {e}")
                continue

        print("✅ Bot Isabella terminé")
        browser.close()

if __name__ == "__main__":
    run_bot()

