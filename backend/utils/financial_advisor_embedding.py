import os
import pandas as pd
import openai
from dotenv import load_dotenv
from database import connection_pool

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

file_path = "knowledge.csv"
df = pd.read_csv(file_path)

df = df.dropna(subset=["Title", "Article"])

conn = connection_pool.getconn()
cursor = conn.cursor()

try:
    for index, row in df.iterrows():
        text_to_embed = f"{row['Title']}\n\n{row['Article']}"

        response = client.embeddings.create(
            input=text_to_embed,
            model="text-embedding-ada-002"
        )
        embedding = response.data[0].embedding

        cursor.execute("""
            INSERT INTO vanguard_knowledge_base (topic, title, article, link, embedding)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            row['Topic'],
            row['Title'],
            row['Article'],
            row['Link'],
            embedding
        ))

        print(f"Uploaded: {row['Title']}")

    conn.commit()

except Exception as e:
    print(f"Error while uploading: {e}")
    conn.rollback()

finally:
    cursor.close()
    connection_pool.putconn(conn)

print("All rows uploaded successfully using connection pool!")
