import os
import time
import random
import logging
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

THREADS_COOKIE = os.getenv("THREADS_COOKIE")
THREADS_USER_ID = os.getenv("THREADS_USER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

logging.basicConfig(level=logging.INFO)
openai = OpenAI(api_key=OPENAI_API_KEY)

def generate_response(comment):
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es Isabella, une femme de 50 ans séduisante et confiante, toujours aimable et joueuse. Tu réponds aux commentaires comme si tu étais sur Threads."},
                {"role": "user", "content": comment}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"[GPT-4] Error: {e}")
        return None

def like_comment(driver, comment_element):
    try:
        like_button = comment_element.find_element(By.XPATH, ".//button[contains(@aria-label, 'Like')]")
        like_button.click()
        logging.info("❤️ Like automatique envoyé")
    except Exception as e:
        logging.warning(f"Like non envoyé : {e}")

def reply_to_comment(driver, comment_element, response):
    try:
        reply_button = comment_element.find_element(By.XPATH, ".//button[contains(text(),'Reply') or contains(text(),'Répondre')]")
        reply_button.click()
        time.sleep(1)
        reply_box = driver.switch_to.active_element
        ActionChains(driver).send_keys(response).perform()
        time.sleep(0.5)
        ActionChains(driver).send_keys(Keys.RETURN).perform()
        logging.info(f"💬 Réponse d'Isabella : {response}")
    except Exception as e:
        logging.warning(f"Impossible de répondre : {e}")

def run_bot():
    logging.info("🤖 Lancement du bot Isabella...")
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    driver = uc.Chrome(options=options)

    try:
        driver.get("https://www.threads.net/@" + THREADS_USER_ID)
        driver.add_cookie({"name": "sessionid", "value": THREADS_COOKIE, "domain": ".threads.net"})
        driver.refresh()
        time.sleep(5)

        logging.info("🔍 Vérification des nouveaux commentaires...")
        comments = driver.find_elements(By.XPATH, "//div[contains(@class, 'x1iorvi4')]//span")

        for comment_element in comments:
            comment = comment_element.text.strip()
            if comment:
                logging.info(f"💬 Commentaire reçu : {comment}")
                reply = generate_response(comment)
                if reply:
                    reply_to_comment(driver, comment_element, reply)
                    like_comment(driver, comment_element)
                time.sleep(random.uniform(2, 4))

    except Exception as e:
        logging.error(f"Erreur globale : {e}")
    finally:
        driver.quit()

if __name__ == '__main__':
    run_bot()
