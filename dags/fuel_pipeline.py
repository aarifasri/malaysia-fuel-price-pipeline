import requests
import psycopg2

url = "https://api.data.gov.my/data-catalogue?id=fuelprice&limit=100&sort=-date&filter=level@series_type"
response = requests.get(url)
data = response.json()

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="setel_project",
    user="postgres",
    password="learnsql"
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