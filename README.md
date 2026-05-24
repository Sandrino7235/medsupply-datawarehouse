# MedSupply Data Warehouse - Business Intelligence Assignment

A complete end-to-end business intelligence solution featuring a cloud-hosted data warehouse on Supabase, incremental ETL pipeline in Python, and interactive Power BI dashboards.

---

## 📋 Project Overview

**Objective:** Build a scalable data warehouse to analyze medical supply orders across multiple facilities and regions.

**Architecture:**
- **Source System:** SQL Server (OLTP) - Local
- **Cloud Data Warehouse:** PostgreSQL on Supabase
- **ETL Orchestrator:** Python (incremental loading with timestamp comparison)
- **Analytics Layer:** OLAP views + Power BI dashboards
- **Reporting:** Power BI Service (cloud-based interactive dashboards)

**Key Metrics:**
- 20 facilities across 4 regions
- 50 products across 5 categories
- 1,536 order lines (3 years of data: 2025-2027)
- 1,095 date dimension rows

---

## 📁 Project Structure

```
THA/
├── README.md                                    # This file
├── SUPABASE_CONNECTION.md                       # Supabase project details
├── .gitignore                                   # Git ignore rules
├── etl.py                                       # Python ETL pipeline
├── medsupply_theme.json                         # Power BI theme
├── report.pbix                                  # Power BI Desktop file
│
├── queries/
│   ├── 01_supabase_medsupply_dw.sql            # Supabase DDL (dimensions + fact)
│   ├── 02_supabase_medsupply_views.sql         # OLAP views (monthly revenue, product rank)
│   └── README.md                                # SQL script documentation
│
├── sourcedata/
│   ├── 01_MedSupply_Source.sql                 # SQL Server source database
│   └── 02_MedSupply_DW.sql                     # SQL Server local DW (staging + dimensions)
│
└── docs/
    ├── BIR - Assignment 2 - Brief.docx         # Assignment specification
    └── BIR - Assignment 2 - Cover Sheet.docx   # Cover page
```

---

## 🚀 Setup Instructions

### Prerequisites
- **Windows Machine** (for Power BI Desktop publishing)
- **SQL Server** (2019 or later) running on `localhost,1433`
- **Python 3.8+** with pip
- **Power BI Desktop** (latest version)
- **Supabase Account** (free tier)

### Step 1: Set Up Local SQL Server

On your local Windows machine:

```bash
# Open SQL Server Management Studio and run:
01_MedSupply_Source.sql     # Creates source OLTP database
02_MedSupply_DW.sql         # Creates local data warehouse with staging
```

**Verify:**
```sql
USE MedSupply_Source;
SELECT COUNT(*) FROM Ref.Facility;        -- Should return 20
SELECT COUNT(*) FROM Ref.Product;         -- Should return 50
SELECT COUNT(*) FROM Sales.PurchaseOrder; -- Should return 500
```

### Step 2: Set Up Supabase Cloud Database

1. Go to [supabase.com](https://supabase.com) and create a free account
2. Create a new project in region **eu-west-1**
3. Go to **SQL Editor** and run the Supabase scripts:

```bash
# In Supabase SQL Editor, run these in order:
01_supabase_medsupply_dw.sql      # Creates dimensions and fact table
02_supabase_medsupply_views.sql   # Creates OLAP views
```

**Verify in Supabase:**
```sql
SELECT COUNT(*) FROM dim_date;      -- Should return 1,095
SELECT COUNT(*) FROM dim_facility;  -- Should return 20 (+ 1 unknown)
SELECT COUNT(*) FROM dim_product;   -- Should return 52 (50 + SCD Type 2 rows)
SELECT COUNT(*) FROM fact_orders;   -- Should return 1,536
```

### Step 3: Configure and Run ETL Pipeline

1. **Update connection details in `etl.py`:**

```python
SQL_SERVER_CONN = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost,1433;"
    "DATABASE=MedSupply_DW;"
    "UID=sa;"
    "PWD=<YourStrong@Passw0rd>;"  # Replace with your SA password
    "TrustServerCertificate=yes;"
)

SUPABASE_CONN = {
    "host":     "aws-0-eu-west-1.pooler.supabase.com",
    "port":     5432,
    "dbname":   "postgres",
    "user":     "postgres.qjynfvpggfoumhldonzd",
    "password": "<YOUR_SUPABASE_PASSWORD>"  # Replace with your password
}
```

2. **Install dependencies:**

```bash
pip install pyodbc psycopg2-binary
```

3. **Run the ETL:**

```bash
python etl.py
```

**Expected Output:**
```
=======================================================
MedSupply ETL Pipeline Starting
Run time: 2026-05-12 00:14:11.060523
=======================================================
Connecting to source (SQL Server)...
Connected to source (SQL Server). OK
Connecting to target (PostgreSQL/Supabase)...
Connected to target (PostgreSQL/Supabase). OK

[dim_date] Starting sync...
[dim_date] 1095 new/updated records found. Inserting...
[dim_date] Sync complete. 1095 rows upserted.

[dim_facility] Starting sync...
[dim_facility] 20 new/updated records found. Upserting...
[dim_facility] Sync complete. 20 rows upserted.

[dim_product] Starting sync...
[dim_product] 52 new/updated records found. Upserting...
[dim_product] Sync complete. 52 rows upserted.

[fact_orders] Starting sync...
[fact_orders] 1536 new records found. Inserting...
[fact_orders] Sync complete. 1536 rows upserted.

=======================================================
Pipeline completed successfully!
Finished at: 2026-05-12 00:14:16.442997
=======================================================
```

### Step 4: Build and Publish Power BI Report

1. **On Windows (Power BI Desktop):**
   - Open `report.pbix`
   - Go to **Home → Get Data → PostgreSQL**
   - Server: `aws-0-eu-west-1.pooler.supabase.com`
   - Database: `postgres`
   - Username: `postgres.qjynfvpggfoumhldonzd`
   - Password: `[YOUR_SUPABASE_PASSWORD]`
   - Load tables: `dim_date`, `dim_facility`, `dim_product`, `fact_orders`

2. **Set up data model:**
   - Relationships (Modeling → Manage relationships):
     - `fact_orders.date_key` → `dim_date.date_key`
     - `fact_orders.facility_key` → `dim_facility.facility_key`
     - `fact_orders.product_key` → `dim_product.product_key`
   - Mark `dim_date` as date table (Table tools → Mark as date table)

3. **Publish to Power BI Service:**
   - Click **File → Publish**
   - Select **My Workspace**
   - Report goes live at `app.powerbi.com`

---

## 📊 Power BI Report Structure

### Page 1: Sales Overview
Interactive dashboard showing sales performance across time, geography, and facilities.

**Visuals:**
- **Total Sales (Card):** Aggregate revenue across all orders
- **Total Orders (Card):** Count of distinct order IDs
- **Revenue Over Time (Line Chart):** Daily/monthly sales trend
- **Sales by Country (Map):** Geographic heat map with bubble sizes representing revenue

**Slicers:**
- Date range (1/1/2025 - 12/31/2027)
- Facility name (dropdown)
- Country/Region (dropdown)

### Page 2: Product Analysis
Deep dive into product performance, pricing, and sales volume.

**Visuals:**
- **Revenue by Category (Treemap):** Proportion of revenue by product category
- **Top 5 Products by Revenue (Bar Chart):** Ranked product performance
- **Units Sold vs Unit Price (Scatter Chart):** Correlation between price and volume by category

**Slicers:**
- Shared across both pages for consistent filtering

---

## 🔄 ETL Pipeline Details

### Features
✅ **Incremental Loading:** Compares `last_updated` timestamps to sync only changed records
✅ **Watermark Logic:** Tracks the latest update from cloud for each table
✅ **SCD Type 1:** Facility dimension (overwrites on change)
✅ **SCD Type 2:** Product dimension (tracks price history)
✅ **Error Handling:** Try-catch with rollback on failure
✅ **Detailed Logging:** Console output shows progress for each table

### Workflow
1. **Extract:** Query local DW for records updated after cloud watermark
2. **Transform:** Convert data types, handle nulls, apply business logic
3. **Load:** Upsert to Supabase using `ON CONFLICT` clauses
4. **Commit:** Transaction-safe with automatic rollback on errors

### Run Frequency
Can run on schedule (daily, weekly) to keep cloud DW in sync with local source.

---

## 📈 Data Warehouse Schema

### Dimension Tables

**dim_date** (1,095 rows)
- date_key (PK, SERIAL)
- full_date (DATE, UNIQUE)
- year, quarter, month, month_name, day_of_month, day_of_week, is_weekend
- last_updated (TIMESTAMPTZ)

**dim_facility** (20 rows + 1 unknown member)
- facility_key (PK, SERIAL)
- facility_id_source (INTEGER, UNIQUE)
- facility_name, facility_type, country_name, region_name
- last_updated (TIMESTAMPTZ)
- **SCD Type 1:** Overwrites on facility detail changes

**dim_product** (52 rows + 1 unknown member)
- product_key (PK, SERIAL)
- product_id_source (INTEGER)
- product_name, category_name, unit_price, is_active
- row_start_date, row_end_date, is_current
- last_updated (TIMESTAMPTZ)
- **SCD Type 2:** Tracks price history with effective dates

### Fact Table

**fact_orders** (1,536 rows)
- order_line_key (PK, SERIAL)
- date_key (FK → dim_date)
- facility_key (FK → dim_facility)
- product_key (FK → dim_product)
- order_id, quantity, unit_price_sold, line_total
- last_updated (TIMESTAMPTZ)
- Indexes on all foreign keys for query performance

---

## 📊 OLAP Views

### vw_monthly_revenue
Monthly aggregation with month-on-month growth analysis.

```sql
SELECT year, month, month_name, revenue, order_count, units_sold,
       prev_month_revenue, mom_growth_pct
FROM vw_monthly_revenue
ORDER BY year, month;
```

**Use Case:** Track sales trends and identify seasonal patterns.

### vw_product_revenue_rank
Product ranking by total revenue with metrics.

```sql
SELECT product_name, category_name, total_revenue, total_units,
       order_count, revenue_rank
FROM vw_product_revenue_rank
ORDER BY revenue_rank;
```

**Use Case:** Identify top performers and underperforming products.

---

## 🔐 Supabase Project Details

| Detail | Value |
|--------|-------|
| **Project Name** | Sandrino7235's Project |
| **Project ID** | qjynfvpggfoumhldonzd |
| **Region** | eu-west-1 (Ireland) |
| **Database** | postgres |
| **Host (Pooler)** | aws-0-eu-west-1.pooler.supabase.com |
| **Port** | 5432 |
| **User** | postgres.qjynfvpggfoumhldonzd |
| **Tables** | dim_date, dim_facility, dim_product, fact_orders |
| **Views** | vw_monthly_revenue, vw_product_revenue_rank |

**Access Dashboard:** https://app.supabase.com/projects/qjynfvpggfoumhldonzd

---

## 📋 Key Metrics & Statistics

| Metric | Count |
|--------|-------|
| Facilities | 20 |
| Products | 50 |
| Product Categories | 5 (Equipment, Surgical, Diagnostics, Consumables, Pharmaceuticals) |
| Regions | 4 (North America, Europe, South America, Australia) |
| Countries | 4 |
| Order Lines | 1,536 |
| Date Range | 2025-01-01 to 2027-12-31 |
| Dimension Rows | 1,169 (date + facility + product) |
| Total Fact Rows | 1,536 |

---

## 🛠 Technologies Used

| Layer | Technology | Version |
|-------|-----------|---------|
| **Source** | SQL Server | 2019+ |
| **Cloud DW** | PostgreSQL (Supabase) | 14+ |
| **ETL** | Python | 3.8+ |
| **ETL Libraries** | pyodbc, psycopg2 | Latest |
| **Analytics** | Power BI Desktop | May 2026 |
| **Reporting** | Power BI Service | Cloud |
| **Version Control** | Git | - |

---

## 📝 Assignment Compliance

### Part 1: Cloud Hosted Postgres ✅
- Supabase PostgreSQL database created
- Dimension tables: `dim_date`, `dim_facility`, `dim_product`
- Fact table: `fact_orders`
- SCD Type 1 & 2 implemented
- Unknown member handling (key = -1)

### Part 2: OLAP Views ✅
- `vw_monthly_revenue` with MoM growth % and LAG window function
- `vw_product_revenue_rank` with RANK() window function
- Both views tested and returning correct results

### Part 3: Python Orchestrator ✅
- Incremental loading with timestamp comparison
- Detailed console logging for each table
- Error handling with transaction rollback
- Executes cleanly: extract → transform → load → commit

### Part 4: Power BI Report ✅
- Connected to Supabase Postgres
- Star schema relationships configured
- Date table marked
- **Page 1 (Sales):** 2 cards, line chart, map, 3 slicers
- **Page 2 (Product):** Treemap, bar chart, scatter chart
- Published to Power BI Service
- Interactive slicers across both pages

---

## 🔗 Important Links

- **Power BI Report:** [View Live Dashboard](https://app.powerbi.com/) (share link after publishing)
- **Supabase Project:** https://app.supabase.com/projects/qjynfvpggfoumhldonzd
- **GitHub Repository:** (Add your repo URL)

---

## 📧 Assignment Submission

**Deliverables:**
1. This README.md
2. `etl.py` (with credentials removed)
3. SQL scripts in `SQL_Scripts/` folder
4. Power BI report link (published to Service)
5. `SUPABASE_CONNECTION.md` with project details

---

## 👨‍💻 Author

**Stefan Bugeja**  
Semester 2 | Business Intelligence & Analytics  
Mediterranean University  

---

## 📄 License

This project is part of an academic assignment and is provided as-is for educational purposes.

---

**Last Updated:** May 2026  
**Status:** ✅ Complete
