import os
import time
import openai
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Load secrets
load_dotenv()
COOKIE = os.getenv("THREADS_COOKIE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USER_ID = os.getenv("THREADS_USER_ID")

openai.api_key = OPENAI_API_KEY

# Mémoire pour ne pas répondre deux fois
handled_comments = set()

def generate_reply(comment_text):
    print(f"[GPT-4] Génération de réponse à : {comment_text}")
    prompt = f"""Tu es Isabella, une femme de 50 ans, sensuelle, douce, élégante et provocante.
Tu réponds à ce commentaire sur Threads avec un ton sexy, chaleureux, en ajoutant quelques emojis si possible.

Commentaire : {comment_text}
Réponse :"""

    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9
    )
    return completion.choices[0].message["content"]

def run_bot():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # Injecter les cookies
        context.add_cookies([{
            "name": "ds_user_id",
            "value": USER_ID,
            "domain": ".instagram.com",
            "path": "/"
        }, {
            "name": "sessionid",
            "value": COOKIE,
            "domain": ".instagram.com",
            "path": "/"
        }])

        page = context.new_page()

        print("🔗 Connexion à Threads...")
        page.goto("https://www.threads.net")

        # Attendre chargement
        page.wait_for_timeout(5000)

        print("📥 Lecture des commentaires...")

        comments = page.locator("xpath=//span[contains(text(), '')]").all()

        for comment in comments:
            try:
                text = comment.inner_text()
                if text not in handled_comments and len(text) > 3:
                    handled_comments.add(text)
                    reply = generate_reply(text)

                    print(f"📝 Réponse : {reply}")

                    # Cliquer pour répondre
                    comment.click()
                    page.wait_for_timeout(1000)
                    input_box = page.locator("textarea").first
                    input_box.fill(reply)
                    input_box.press("Enter")

                    # Attendre envoi + like
                    time.sleep(3)
                    like_button = page.locator("xpath=//button[contains(@aria-label, 'Like')]").first
                    if like_button:
                        like_button.click()

            except Exception as e:
                print("Erreur :", e)

        print("✅ Fin de cycle. Attente avant prochain scan...")
        page.close()
        context.close()
        browser.close()

if __name__ == "__main__":
    while True:
        run_bot()
        time.sleep(300)  # toutes les 5 minutes
