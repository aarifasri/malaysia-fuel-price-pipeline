import requests
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

url = "https://api.data.gov.my/data-catalogue?id=fuelprice&limit=100&sort=-date&filter=level@series_type"
response = requests.get(url)
data = response.json()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cur = conn.cursor()

for record in data:
    cur.execute(
        "INSERT INTO fuel_prices (price_date, ron95, ron97, diesel) VALUES (%s, %s, %s, %s) ON CONFLICT (price_date) DO NOTHING",
        (record['date'], record['ron95'], record['ron97'], record['diesel'])
    )

conn.commit()
cur.close()
conn.close()
print(f"Loaded {len(data)} records.")