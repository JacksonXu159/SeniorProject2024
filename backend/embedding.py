import psycopg2
import openai
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

PGHOST = os.getenv('PGHOST')
PGDATABASE = os.getenv('PGDATABASE')
PGUSER = os.getenv('PGUSER')
PGPASSWORD = os.getenv('PGPASSWORD')

conn = psycopg2.connect(
    host=PGHOST,
    database=PGDATABASE,
    user=PGUSER,
    password=PGPASSWORD,
    port=5432,
    sslmode='require'  
)

cursor = conn.cursor()

cursor.execute("SELECT id, question FROM faq_embeddings WHERE embedding IS NULL;")
rows = cursor.fetchall()

def pad_embedding(embedding, target_dimension=2000):
    if len(embedding) < target_dimension:
        return embedding + [0.0] * (target_dimension - len(embedding))
    return embedding

# #This is to upload the file if theres nothing in there
# with open("./faqsForEmbedding.csv", "r", encoding="utf-8") as file:
#     reader = csv.DictReader(file, delimiter=",")  # Assuming comma-separated values
#     print("CSV Headers:", reader.fieldnames)  # Debugging step to check headers
#     for row in reader:
#         topic = row["Topic"].strip()
#         section = row["Section"].strip()
#         title = row["Title"].strip()
#         question = row["Question"].strip()
#         answer = row["Answer"].strip()
#         link = row["Link"].strip()
        
#         if not question:
#             continue
        
#         response = client.embeddings.create(input=question, model="text-embedding-ada-002")
#         embedding = response.data[0].embedding
#         padded_embedding = pad_embedding(embedding, target_dimension=2000)
#         embedding_str = "[" + ", ".join(map(str, padded_embedding)) + "]"
        
#         cursor.execute("""
#             INSERT INTO faq_embeddings (topic, section, title, question, answer, link, embedding)
#             VALUES (%s, %s, %s, %s, %s, %s, %s)
#         """, (topic, section, title, question, answer, link, embedding_str))


### This is for if there are already stuff in the database but with no embedding
for row in rows:
    uuid, question = row
    if not question:
        continue

    response = client.embeddings.create(input=question, model="text-embedding-ada-002")
    embedding = response.data[0].embedding

    padded_embedding = pad_embedding(embedding, target_dimension=2000)

    embedding_str = "[" + ", ".join(map(str, padded_embedding)) + "]"
    cursor.execute("UPDATE faq_embeddings SET embedding = %s WHERE id = %s;", (embedding_str, uuid))
###

conn.commit()
cursor.close()
conn.close()

print("Embeddings updated successfully!")





