from airflow.sdk import dag, task
from datetime import datetime
import requests
import psycopg2

@dag(schedule='@weekly', start_date=datetime(2026, 1, 1), catchup=False)
def fuel_price_pipeline():

    @task
    def extract():
        url = "https://api.data.gov.my/data-catalogue?id=fuelprice&limit=20&sort=-date&filter=level@series_type"
        response = requests.get(url)
        return response.json()

    @task
    def load(records):
        conn = psycopg2.connect(host="host.docker.internal", port=5432, dbname="setel_project", user="postgres", password="learnsql")
        cur = conn.cursor()
        for record in records:
            cur.execute(
                "INSERT INTO fuel_prices (price_date, ron95, ron97, diesel) VALUES (%s, %s, %s, %s) ON CONFLICT (price_date) DO NOTHING",
                (record['date'], record['ron95'], record['ron97'], record['diesel'])
            )
        conn.commit()
        cur.close()
        conn.close()
        return "loaded"

    @task
    def transform(_):
        conn = psycopg2.connect(host="host.docker.internal", port=5432, dbname="setel_project", user="postgres", password="learnsql")
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO fuel_prices_monthly (month, avg_ron95, avg_ron97, avg_diesel)
            SELECT DATE_TRUNC('month', price_date)::date, ROUND(AVG(ron95),2), ROUND(AVG(ron97),2), ROUND(AVG(diesel),2)
            FROM fuel_prices GROUP BY DATE_TRUNC('month', price_date)
            ON CONFLICT (month) DO UPDATE SET avg_ron95 = EXCLUDED.avg_ron95, avg_ron97 = EXCLUDED.avg_ron97, avg_diesel = EXCLUDED.avg_diesel
        """)
        conn.commit()
        cur.close()
        conn.close()

    transform(load(extract()))

fuel_price_pipeline()