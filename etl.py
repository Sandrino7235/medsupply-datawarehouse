"""
MedSupply DW - Python ETL Orchestrator
Extracts from local SQL Server (MedSupply_DW)
Incrementally loads into Supabase (PostgreSQL)
Only syncs records where local last_updated > cloud last_updated
"""

import pyodbc
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, date

# CONNECTION SETTINGS
SQL_SERVER_CONN = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost,1433;"
    "DATABASE=MedSupply_DW;"
    "UID=sa;"
    "PWD=<YourStrong@Passw0rd>;"
    "TrustServerCertificate=yes;"
)

SUPABASE_CONN = {
    "host": "aws-0-eu-west-1.pooler.supabase.com",
    "port": 5432,
    "dbname": "postgres",
    "user": "postgres.qjynfvpggfoumhldonzd",
    "password": "g.zrLs/QWrcsNk6",
}


# HELPER - Get the latest last_updated from Supabase table
# Returns datetime(1970,1,1) if table is empty (sync everything)
def get_cloud_watermark(pg_cur, table_name):
    pg_cur.execute(f"SELECT MAX(last_updated) FROM {table_name};")
    result = pg_cur.fetchone()[0]
    return result if result is not None else datetime(1970, 1, 1)


# SYNC dim_date
def sync_dim_date(ss_cur, pg_conn, pg_cur):
    print("\n[dim_date] Starting sync...")

    watermark = get_cloud_watermark(pg_cur, "dim_date")
    print(f"[dim_date] Fetching records updated after {watermark}")

    ss_cur.execute(
        """
        SELECT date_key, full_date, year, quarter, month, month_name,
               day_of_month, day_of_week, is_weekend, last_updated
        FROM dw.dim_date
        WHERE last_updated > ?
    """,
        watermark,
    )

    rows = ss_cur.fetchall()

    if not rows:
        print("[dim_date] No new records found.")
        return

    print(f"[dim_date] {len(rows)} new/updated records found. Inserting...")

    execute_values(
        pg_cur,
        """
        INSERT INTO dim_date
            (date_key, full_date, year, quarter, month, month_name,
             day_of_month, day_of_week, is_weekend, last_updated)
        VALUES %s
        ON CONFLICT (date_key) DO UPDATE SET
            full_date    = EXCLUDED.full_date,
            year         = EXCLUDED.year,
            quarter      = EXCLUDED.quarter,
            month        = EXCLUDED.month,
            month_name   = EXCLUDED.month_name,
            day_of_month = EXCLUDED.day_of_month,
            day_of_week  = EXCLUDED.day_of_week,
            is_weekend   = EXCLUDED.is_weekend,
            last_updated = EXCLUDED.last_updated
    """,
        [
            (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], bool(r[8]), r[9])
            for r in rows
        ],
    )

    pg_conn.commit()
    print(f"[dim_date] Sync complete. {len(rows)} rows upserted.")


# SYNC dim_facility (SCD Type 1)
def sync_dim_facility(ss_cur, pg_conn, pg_cur):
    print("\n[dim_facility] Starting sync...")

    watermark = get_cloud_watermark(pg_cur, "dim_facility")
    print(f"[dim_facility] Fetching records updated after {watermark}")

    ss_cur.execute(
        """
        SELECT facility_key, facility_id_source, facility_name,
               facility_type, country_name, region_name, last_updated
        FROM dw.dim_facility
        WHERE last_updated > ?
    """,
        watermark,
    )

    rows = ss_cur.fetchall()

    if not rows:
        print("[dim_facility] No new records found.")
        return

    print(f"[dim_facility] {len(rows)} new/updated records found. Upserting...")

    execute_values(
        pg_cur,
        """
        INSERT INTO dim_facility
            (facility_key, facility_id_source, facility_name,
             facility_type, country_name, region_name, last_updated)
        VALUES %s
        ON CONFLICT (facility_key) DO UPDATE SET
            facility_id_source = EXCLUDED.facility_id_source,
            facility_name      = EXCLUDED.facility_name,
            facility_type      = EXCLUDED.facility_type,
            country_name       = EXCLUDED.country_name,
            region_name        = EXCLUDED.region_name,
            last_updated       = EXCLUDED.last_updated
    """,
        [(r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rows],
        page_size=500,
    )

    pg_conn.commit()
    print(f"[dim_facility] Sync complete. {len(rows)} rows upserted.")


# SYNC dim_product (SCD Type 2)
def sync_dim_product(ss_cur, pg_conn, pg_cur):
    print("\n[dim_product] Starting sync...")

    watermark = get_cloud_watermark(pg_cur, "dim_product")
    print(f"[dim_product] Fetching records updated after {watermark}")

    ss_cur.execute(
        """
        SELECT product_key, product_id_source, product_name, category_name,
               unit_price, is_active, row_start_date, row_end_date,
               is_current, last_updated
        FROM dw.dim_product
        WHERE last_updated > ?
    """,
        watermark,
    )

    rows = ss_cur.fetchall()

    if not rows:
        print("[dim_product] No new records found.")
        return

    print(f"[dim_product] {len(rows)} new/updated records found. Upserting...")

    execute_values(
        pg_cur,
        """
        INSERT INTO dim_product
            (product_key, product_id_source, product_name, category_name,
             unit_price, is_active, row_start_date, row_end_date,
             is_current, last_updated)
        VALUES %s
        ON CONFLICT (product_key) DO UPDATE SET
            product_id_source = EXCLUDED.product_id_source,
            product_name      = EXCLUDED.product_name,
            category_name     = EXCLUDED.category_name,
            unit_price        = EXCLUDED.unit_price,
            is_active         = EXCLUDED.is_active,
            row_start_date    = EXCLUDED.row_start_date,
            row_end_date      = EXCLUDED.row_end_date,
            is_current        = EXCLUDED.is_current,
            last_updated      = EXCLUDED.last_updated
    """,
        [
            (
                r[0],
                r[1],
                r[2],
                r[3],
                float(r[4]),
                bool(r[5]),
                r[6],
                r[7],
                bool(r[8]),
                r[9],
            )
            for r in rows
        ],
        page_size=500,
    )

    pg_conn.commit()
    print(f"[dim_product] Sync complete. {len(rows)} rows upserted.")


# SYNC fact_orders
def sync_fact_orders(ss_cur, pg_conn, pg_cur):
    print("\n[fact_orders] Starting sync...")

    watermark = get_cloud_watermark(pg_cur, "fact_orders")
    print(f"[fact_orders] Fetching records updated after {watermark}")

    ss_cur.execute(
        """
        SELECT order_line_key, date_key, facility_key, product_key,
               order_id, quantity, unit_price_sold, line_total, last_updated
        FROM dw.fact_orders
        WHERE last_updated > ?
    """,
        watermark,
    )

    rows = ss_cur.fetchall()

    if not rows:
        print("[fact_orders] No new records found.")
        return

    print(f"[fact_orders] {len(rows)} new records found. Inserting...")

    execute_values(
        pg_cur,
        """
        INSERT INTO fact_orders
            (order_line_key, date_key, facility_key, product_key,
             order_id, quantity, unit_price_sold, line_total, last_updated)
        VALUES %s
        ON CONFLICT (order_line_key) DO UPDATE SET
            date_key        = EXCLUDED.date_key,
            facility_key    = EXCLUDED.facility_key,
            product_key     = EXCLUDED.product_key,
            order_id        = EXCLUDED.order_id,
            quantity        = EXCLUDED.quantity,
            unit_price_sold = EXCLUDED.unit_price_sold,
            line_total      = EXCLUDED.line_total,
            last_updated    = EXCLUDED.last_updated
    """,
        [
            (r[0], r[1], r[2], r[3], r[4], r[5], float(r[6]), float(r[7]), r[8])
            for r in rows
        ],
        page_size=500,
    )

    pg_conn.commit()
    print(f"[fact_orders] Sync complete. {len(rows)} rows upserted.")


# MAIN PIPELINE
def run_pipeline():
    print("=" * 55)
    print("MedSupply ETL Pipeline Starting")
    print(f"Run time: {datetime.now()}")
    print("=" * 55)

    # Connect to SQL Server 
    print("\nConnecting to source (SQL Server)...")
    ss_conn = pyodbc.connect(SQL_SERVER_CONN)
    ss_cur = ss_conn.cursor()
    print("Connected to source (SQL Server). OK")

    # Connect to Supabase 
    print("Connecting to target (PostgreSQL/Supabase)...")
    pg_conn = psycopg2.connect(**SUPABASE_CONN)
    pg_cur = pg_conn.cursor()
    print("Connected to target (PostgreSQL/Supabase). OK")

    try:
        sync_dim_date(ss_cur, pg_conn, pg_cur)
        sync_dim_facility(ss_cur, pg_conn, pg_cur)
        sync_dim_product(ss_cur, pg_conn, pg_cur)
        sync_fact_orders(ss_cur, pg_conn, pg_cur)

        print("\n" + "=" * 55)
        print("Pipeline completed successfully!")
        print(f"Finished at: {datetime.now()}")
        print("=" * 55)

    except Exception as e:
        pg_conn.rollback()
        print(f"\n[ERROR] Pipeline failed: {e}")
        raise

    finally:
        ss_cur.close()
        ss_conn.close()
        pg_cur.close()
        pg_conn.close()


if __name__ == "__main__":
    run_pipeline()
