# Malaysia Fuel Price Pipeline

An automated ETL pipeline that extracts weekly Malaysian fuel price data from the official government open data API, loads it into PostgreSQL, and transforms it into monthly aggregates — orchestrated end-to-end with Apache Airflow.

## Why this project

Built as hands-on preparation for a Data Engineering internship (Setel), whose product touches fuel pricing and mobility data directly. This pipeline mirrors the kind of batch data infrastructure a DE team would maintain: scheduled extraction, idempotent loading, and SQL-based transformation.

## Architecture

```
data.gov.my API  -->  Extract (Python/requests)  -->  Load (PostgreSQL)  -->  Transform (SQL aggregation)
                                                              |
                                                    Orchestrated by Airflow
                                                    (scheduled weekly)
```

**Tables:**
- `fuel_prices` — raw weekly prices (RON95, RON97, diesel), keyed by `price_date`
- `fuel_prices_monthly` — monthly average prices, derived via `DATE_TRUNC` + `GROUP BY`

## Key design decisions

- **Filtering `series_type = 'level'`**: the source API mixes actual price records with week-over-week change records in the same dataset. Filtering at extraction time avoids corrupting downstream aggregates.
- **`price_date` as primary key**: naturally unique after filtering, avoids an unnecessary surrogate key.
- **`ON CONFLICT DO NOTHING` / `DO UPDATE`**: makes both the load and transform steps idempotent — safe to re-run without creating duplicates, which matters since pipelines get retried after failures in production.
- **`host.docker.internal`**: Airflow's containers and the Postgres container run on separate Docker networks; this hostname lets Airflow reach back out to the host-mapped Postgres instance.

## Stack

- Python (requests, psycopg2)
- PostgreSQL (via Docker)
- Apache Airflow 3.1 (via Docker Compose)
- Data source: [api.data.gov.my](https://developer.data.gov.my/static-api/data-catalogue) (`fuelprice` dataset)

## Running it

1. `docker compose up airflow-init`
2. `docker compose up -d`
3. Open `localhost:8080`, trigger `fuel_price_pipeline`

## Sample output

| month | avg_ron95 | avg_ron97 | avg_diesel |
|---|---|---|---|
| 2026-08-01 | 3.70 | 4.25 | 4.52 |
| 2026-07-01 | 3.52 | 4.12 | 4.21 |
| 2026-06-01 | 3.66 | 4.29 | 4.45 |
