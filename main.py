import os
import time
import openai
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

THREADS_COOKIE = os.getenv("THREADS_COOKIE")
THREADS_USER_ID = os.getenv("THREADS_USER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

def gpt4_reply(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es Isabella, une femme charismatique, douce, séductrice et sûre d’elle."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Erreur GPT-4] {str(e)}"

def launch_bot():
    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options)

    print("[✓] Lancement du bot Isabella avec Selenium...")
    driver.get(f"https://www.threads.net/@{THREADS_USER_ID}")

    # Injecter les cookies
    driver.add_cookie({
        'name': 'sessionid',
        'value': THREADS_COOKIE,
        'domain': '.threads.net',
        'path': '/',
        'secure': True,
        'httpOnly': True
    })

    driver.refresh()

    try:
        wait = WebDriverWait(driver, 15)
        comments = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[role='comment']")))
        print(f"[✓] {len(comments)} commentaire(s) détecté(s)")

        for comment in comments:
            try:
                content = comment.text.strip()
                print(f"[🗨️] Commentaire: {content}")
                response = gpt4_reply(content)

                # Simuler une réponse (à adapter selon l'UI exacte)
                reply_box = comment.find_element(By.CSS_SELECTOR, "textarea")
                reply_box.send_keys(response)
                reply_box.send_keys(Keys.ENTER)
                print(f"[💬] Réponse envoyée: {response}")

                # Liker le commentaire (à adapter si nécessaire)
                like_button = comment.find_element(By.CSS_SELECTOR, "button[aria-label='J’aime']")
                like_button.click()
                print("[❤️] Like envoyé")

                time.sleep(2)

            except Exception as err:
                print(f"[!] Erreur sur un commentaire: {err}")

    except Exception as e:
        print(f"[!] Erreur principale: {str(e)}")

    driver.quit()

if __name__ == '__main__':
    launch_bot()
