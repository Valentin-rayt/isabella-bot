import os
import time
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import httpx

load_dotenv()

THREADS_COOKIE = os.getenv("THREADS_COOKIE")
THREADS_USER_ID = os.getenv("THREADS_USER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai = OpenAI(api_key=OPENAI_API_KEY)

# Stocker les commentaires déjà traités
comment_history = set()

def is_within_active_hours():
    now = datetime.now().hour
    return 9 <= now < 23

# Fonction de scraping des commentaires sous les posts de l'utilisateur
async def get_real_comments():
    headers = {
        "cookie": THREADS_COOKIE,
        "user-agent": "Mozilla/5.0"
    }

    # Récupération des posts de l'utilisateur
    user_posts_url = f"https://www.threads.net/api/graphql?doc_id=6218965737422034&variables={{\"userID\":\"{THREADS_USER_ID}\",\"count\":10}}"
    comments = []

    async with httpx.AsyncClient() as client:
        response = await client.get(user_posts_url, headers=headers)
        try:
            posts_data = response.json()
            edges = posts_data["data"]["mediaData"]["edges"]
            for edge in edges:
                post_id = edge["node"]["id"]

                comments_url = f"https://www.threads.net/api/graphql?doc_id=7715618461853193&variables={{\"mediaID\":\"{post_id}\",\"count\":20}}"
                comment_response = await client.get(comments_url, headers=headers)
                comment_data = comment_response.json()

                for comment_edge in comment_data["data"]["feedback"]["comment_list_renderer"]["feedback_comments"]["edges"]:
                    comment = comment_edge["node"]["body"]["text"]
                    if comment not in comment_history:
                        comments.append(comment)
                        comment_history.add(comment)

        except Exception as e:
            print(f"[❌ Erreur scraping] {str(e)}")

    return comments

def generate_reply(comment):
    prompt = f"Tu es Isabella, une femme douce, sexy, confiante, de 50 ans, très élégante et un peu provocante. Réponds à ce commentaire : \"{comment}\" avec charme, humour et un ou deux emojis. Garde un ton féminin, classe et accessible."

    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85,
            max_tokens=150
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"[Erreur GPT] {str(e)}"

def simulate_post_and_like(comment, reply):
    print(f"\n💬 Commentaire reçu : {comment}")
    print(f"🤖 Réponse d'Isabella : {reply}")
    print("❤️ Like automatique envoyé")

async def run_bot():
    print("⚙️ Le bot est bien dans main.py et prêt à démarrer la boucle.")
    while True:
        if not is_within_active_hours():
            print("⏸️ Bot en pause (hors horaires 9h-23h).")
            await asyncio.sleep(300)
            continue

        print("\n🔁 Lancement de la boucle principale...")
        print("🔎 Vérification des nouveaux commentaires...")
        comments = await get_real_comments()

        for comment in comments:
            reply = generate_reply(comment)
            simulate_post_and_like(comment, reply)
            await asyncio.sleep(4)

        await asyncio.sleep(120)

if __name__ == "__main__":
    asyncio.run(run_bot())
