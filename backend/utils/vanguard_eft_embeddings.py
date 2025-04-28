import os
import pandas as pd
import openai
from dotenv import load_dotenv
from database import connection_pool

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

file_path = "vanguard_funds.csv"
df = pd.read_csv(file_path) 

df = df.dropna(subset=["Symbol", "Name", "Asset class", "Risk", "Expenseratio"])

conn = connection_pool.getconn()
cursor = conn.cursor()

try:
    for index, row in df.iterrows():
        text_to_embed = f"Fund Name: {row['Name']}\nSymbol: {row['Symbol']}\nAsset Class: {row['Asset class']}\nRisk: {row['Risk']}\nExpense Ratio: {row['Expenseratio']}\nCompare: {row['Compare']}\nTransact: {row['Transact']}\nSEC Yield: {row['SECyield']}\nYTD: {row['YTD']}\n1-year: {row['1-yr']}\n5-year: {row['5-yr']}\n10-year: {row['10-yr']}\nSince Inception: {row['Sinceinception']}\nInvestment Minimum: {row['InvestmentMinimum']}\nPrice: {row['Price']}\nChange: {row['Change']}"

        response = client.embeddings.create(
            input=text_to_embed,
            model="text-embedding-ada-002"
        )
        embedding = response.data[0].embedding

        cursor.execute("""
            INSERT INTO vanguard_funds (symbol, name, asset_class, risk, expense_ratio, compare, transact, sec_yield, ytd, one_year, five_year, ten_year, since_inception, investment_minimum, price, change, embedding)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row['Symbol'],
            row['Name'],
            row['Asset class'],
            row['Risk'],
            row['Expenseratio'],
            row['Compare'],
            row['Transact'],
            row['SECyield'],
            row['YTD'],
            row['1-yr'],
            row['5-yr'],
            row['10-yr'],
            row['Sinceinception'],
            row['InvestmentMinimum'],
            row['Price'],
            row['Change'],
            embedding
        ))

        print(f"Uploaded: {row['Name']} ({row['Symbol']})")

    conn.commit()

except Exception as e:
    print(f"Error while uploading: {e}")
    conn.rollback()

finally:
    cursor.close()
    connection_pool.putconn(conn)

print("All rows uploaded successfully using connection pool!")
