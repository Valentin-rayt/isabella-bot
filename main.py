# main.py
import os
import time
import random
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from undetected_chromedriver import Chrome, ChromeOptions
import openai

load_dotenv()

# Config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
THREADS_URL = os.getenv("THREADS_URL")
openai.api_key = OPENAI_API_KEY

# Fonction GPT
async def generate_reply(comment_text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Tu es Isabella, une femme confiante, séductrice, qui répond toujours avec élégance."},
            {"role": "user", "content": f"Commentaire : {comment_text}\nRéponds comme Isabella."}
        ]
    )
    return response.choices[0].message.content.strip()

# Setup navigateur
options = ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = Chrome(options=options)

def run_bot():
    driver.get(THREADS_URL)
    time.sleep(5)

    print("🔍 Lecture des commentaires...")
    comments = driver.find_elements(By.CLASS_NAME, "_acomment")  # Adapter au sélecteur correct
    for comment in comments:
        try:
            content = comment.text.strip()
            if content:
                print(f"💬 Commentaire : {content}")
                reply = asyncio.run(generate_reply(content))
                print(f"🧠 Réponse : {reply}")

                # Simule un like (à adapter selon structure Threads)
                like_button = comment.find_element(By.CLASS_NAME, "_like")
                if like_button:
                    like_button.click()
                    print("❤️ Like envoyé")

                # Ajoute un délai aléatoire
                time.sleep(random.randint(5, 10))
        except Exception as e:
            print(f"⚠️ Erreur : {e}")

    driver.quit()

if __name__ == "__main__":
    run_bot()
