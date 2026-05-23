# Supabase Project Connection Details

## Project Information

| Property | Value |
|----------|-------|
| **Project Name** | Sandrino7235's Project |
| **Project ID** | qjynfvpggfoumhldonzd |
| **Region** | eu-west-1 (Ireland) |
| **Database Engine** | PostgreSQL 14+ |
| **Status** | Active |

---

## Database Connection Details

### Connection Pooler (Recommended for Applications)

**Type:** Session Pooler  
**Host:** `aws-0-eu-west-1.pooler.supabase.com`  
**Port:** `5432`  
**Database:** `postgres`  
**User:** `postgres.qjynfvpggfoumhldonzd`  
**Password:** `[YOUR_PASSWORD]`

### Direct Connection (Optional)

**Host:** `db.qjynfvpggfoumhldonzd.supabase.co`  
**Port:** `5432`  
**Database:** `postgres`  
**User:** `postgres`  
**Password:** `[YOUR_PASSWORD]`

---

## Connection Strings

### PostgreSQL URI Format (Pooler)
```
postgresql://postgres.qjynfvpggfoumhldonzd:[PASSWORD]@aws-0-eu-west-1.pooler.supabase.com:5432/postgres
```

### psycopg2 Python Format
```python
SUPABASE_CONN = {
    "host":     "aws-0-eu-west-1.pooler.supabase.com",
    "port":     5432,
    "dbname":   "postgres",
    "user":     "postgres.qjynfvpggfoumhldonzd",
    "password": "[YOUR_PASSWORD]"
}
```

### Command Line
```bash
psql -h aws-0-eu-west-1.pooler.supabase.com -U postgres.qjynfvpggfoumhldonzd -d postgres -p 5432
```

---

## Tables Created

### Dimension Tables

**dim_date**
- Rows: 1,095
- Date range: 2025-01-01 to 2027-12-31
- Contains: year, quarter, month, day_of_week, is_weekend
- Purpose: Time dimension for time-based analysis

**dim_facility**
- Rows: 20 (+ 1 unknown member)
- SCD Type 1: Overwrites on facility changes
- Contains: facility_name, facility_type, country_name, region_name
- Purpose: Organization dimension

**dim_product**
- Rows: 52 (50 products + 2 SCD Type 2 rows)
- SCD Type 2: Tracks price history
- Contains: product_name, category_name, unit_price, row_start_date, row_end_date, is_current
- Purpose: Product dimension with price tracking

### Fact Table

**fact_orders**
- Rows: 1,536
- Foreign keys: date_key, facility_key, product_key
- Measures: quantity, unit_price_sold, line_total
- Indexes: On all foreign keys for performance
- Purpose: Order transaction facts

### Views

**vw_monthly_revenue**
- Aggregates: Total revenue, order count, units sold
- Calculations: Previous month revenue, month-on-month growth %
- Window function: LAG() for prior month comparison
- Purpose: Monthly sales analysis and trend identification

**vw_product_revenue_rank**
- Aggregates: Total revenue, units, order count per product
- Ranking: RANK() by revenue descending
- Filtering: Excludes unknown members
- Purpose: Product performance leaderboard

---

## Database Statistics

| Metric | Value |
|--------|-------|
| Total Rows (Fact) | 1,536 |
| Total Dimensions | 3 (date, facility, product) |
| Dimension Rows | 1,169 |
| Views Created | 2 |
| Primary Keys | 4 |
| Foreign Keys | 3 |
| Indexes | 3 (on fact table FK) |

---

## Access & Management

### Supabase Dashboard
https://app.supabase.com/projects/qjynfvpggfoumhldonzd

**Features Available:**
- SQL Editor (run queries, DDL/DML)
- Database browser (table exploration)
- User management
- API & webhooks
- Monitoring & logs
- SSL configuration
- Backups & restoration

### Useful Queries

**Check database size:**
```sql
SELECT pg_size_pretty(pg_database_size('postgres'));
```

**View table row counts:**
```sql
SELECT 
  schemaname,
  tablename,
  (SELECT COUNT(*) FROM pg_class WHERE relname = tablename) AS row_count
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
```

**List all views:**
```sql
SELECT table_name FROM information_schema.views WHERE table_schema = 'public';
```

---

## SSL Configuration

**Status:** Enforce SSL is **disabled** (allows both SSL and non-SSL)

To download the SSL certificate:
1. Go to Supabase Dashboard → Settings
2. Click "Download certificate"
3. Use for client SSL connections

---

## Security Notes

⚠️ **Important:** 
- Never commit `SUPABASE_CONN` credentials directly to GitHub
- Use `.env` files or environment variables for production
- Reset the database password after sharing this file (Supabase Dashboard → Settings → Reset password)
- Use strong, unique passwords for all user accounts
- Enable 2FA on your Supabase account

---

## Backup & Recovery

**Automatic backups:** Supabase creates daily backups (free tier: 7-day retention)

**Manual backup:**
```bash
pg_dump -h aws-0-eu-west-1.pooler.supabase.com \
  -U postgres.qjynfvpggfoumhldonzd \
  -d postgres \
  -F plain > backup.sql
```

---

## Support & Documentation

- **Supabase Docs:** https://supabase.com/docs
- **PostgreSQL Docs:** https://www.postgresql.org/docs/
- **Connection Troubleshooting:** https://supabase.com/docs/guides/database/connecting-to-postgres

---

**Last Updated:** May 2026  
**Project Status:** ✅ Active
