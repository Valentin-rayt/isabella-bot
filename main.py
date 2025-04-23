import os
import time
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import requests

load_dotenv()

THREADS_COOKIE = os.getenv("THREADS_COOKIE")
THREADS_USER_ID = os.getenv("THREADS_USER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai = OpenAI(api_key=OPENAI_API_KEY)
seen_comments = set()

def is_within_active_hours():
    now = datetime.now().hour
    return 9 <= now < 23

def get_real_comments():
    print("📡 Tentative de récupération des commentaires Threads...")
    headers = {
        "Cookie": f"ds_user_id={THREADS_USER_ID}; sessionid={THREADS_COOKIE}",
        "User-Agent": "Instagram 254.0.0.19.109 Android"
    }

    url = f"https://www.threads.net/api/graphql?doc_id=7102739613304100&variables=%7B%22userID%22%3A%22{THREADS_USER_ID}%22%7D"

    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print(f"❌ Erreur HTTP {res.status_code} : {res.text[:200]}")
            return []

        json_data = res.json()
        threads = json_data["data"]["mediaData"]["threads"]
        comments = []

        for thread in threads:
            if not thread.get("thread_items"):
                continue
            post_id = thread["thread_items"][0]["post"]["id"]
            post_url = f"https://www.threads.net/api/graphql?doc_id=6320127741469992&variables=%7B%22postID%22%3A%22{post_id}%22%7D"
            res_post = requests.get(post_url, headers=headers)
            if res_post.status_code != 200:
                continue
            try:
                data_post = res_post.json()
                replies = data_post["data"]["containing_thread"]["thread_items"]
                for item in replies:
                    post = item.get("post", {})
                    if "text" in post and post.get("user", {}).get("pk") != THREADS_USER_ID:
                        comment_text = post["text"]
                        if comment_text not in seen_comments:
                            seen_comments.add(comment_text)
                            comments.append(comment_text)
            except Exception as e:
                print(f"⚠️ Erreur JSON dans les réponses au post : {e}")
                continue

        return comments

    except Exception as e:
        print(f"[❌ Erreur scraping] {e}")
        return []

def generate_reply(comment):
    prompt = f"Tu es Isabella, une femme douce, sexy, confiante de 50 ans, très élégante et un peu provocante. Réponds à ce commentaire : \"{comment}\" avec charme, humour et quelques emojis."
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85,
            max_tokens=100
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"[Erreur GPT] {str(e)}"

def simulate_post_and_like(comment, reply):
    print(f"\n🗨️ Commentaire reçu : {comment}")
    print(f"🤖 Réponse d'Isabella : {reply}")
    print("❤️ Like automatique envoyé")

async def run_bot():
    print("⚙️ Le bot est bien dans main.py et prêt à démarrer la boucle.")
    while True:
        if not is_within_active_hours():
            print("⏸️ Bot en pause (hors plages horaires 9h–23h).")
            await asyncio.sleep(300)
            continue

        print("🔁 Vérification des nouveaux commentaires...")
        comments = get_real_comments()

        for comment in comments:
            reply = generate_reply(comment)
            simulate_post_and_like(comment, reply)
            await asyncio.sleep(4)

        await asyncio.sleep(120)

if __name__ == "__main__":
    asyncio.run(run_bot())
