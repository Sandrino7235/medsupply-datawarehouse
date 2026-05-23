-- MedSupply Data Warehouse - Supabase / PostgreSQL DDL
-- Converted from SQL Server (MedSupply_DW)
-- PART 1 - Drop tables if they exist (clean slate)
drop table if exists fact_orders;

drop table if exists dim_date;

drop table if exists dim_facility;

drop table if exists dim_product;

-- PART 2 - Dimension Tables
-- dim_date
create table dim_date (
  date_key SERIAL primary key,
  full_date DATE not null unique,
  year INTEGER not null,
  quarter INTEGER not null,
  month INTEGER not null,
  month_name VARCHAR(20) not null,
  day_of_month INTEGER not null,
  day_of_week INTEGER not null,
  is_weekend BOOLEAN not null,
  last_updated TIMESTAMPTZ default NOW()
);

-- dim_facility (SCD Type 1 - Overwrite)
create table dim_facility (
  facility_key SERIAL primary key,
  facility_id_source INTEGER not null unique,
  facility_name VARCHAR(200) not null,
  facility_type VARCHAR(50) not null,
  country_name VARCHAR(100),
  region_name VARCHAR(50),
  last_updated TIMESTAMPTZ default NOW()
);

-- dim_product (SCD Type 2 - History Tracking on Price)
create table dim_product (
  product_key SERIAL primary key,
  product_id_source INTEGER not null,
  product_name VARCHAR(100) not null,
  category_name VARCHAR(100),
  unit_price NUMERIC(10, 2) not null,
  is_active BOOLEAN default true,
  row_start_date DATE not null default '2000-01-01',
  row_end_date DATE null default null,
  is_current BOOLEAN not null default true,
  last_updated TIMESTAMPTZ default NOW()
);

-- PART 3 - Fact Table
create table fact_orders (
  order_line_key SERIAL primary key,
  date_key INTEGER not null references dim_date (date_key),
  facility_key INTEGER not null references dim_facility (facility_key),
  product_key INTEGER not null references dim_product (product_key),
  order_id INTEGER not null,
  quantity INTEGER not null,
  unit_price_sold NUMERIC(10, 2) not null,
  line_total NUMERIC(12, 2) not null,
  last_updated TIMESTAMPTZ default NOW()
);

-- Index on foreign keys for query performance (replaces Columnstore index)
create index idx_fact_orders_date on fact_orders (date_key);

create index idx_fact_orders_facility on fact_orders (facility_key);

create index idx_fact_orders_product on fact_orders (product_key);

-- PART 4 - Unknown Members (surrogate key -1)
-- Unknown Facility
insert into
  dim_facility (
    facility_key,
    facility_id_source,
    facility_name,
    facility_type
  )
overriding system value
values
  (-1, -1, 'Unknown Facility', 'Unknown');

-- Unknown Product
insert into
  dim_product (
    product_key,
    product_id_source,
    product_name,
    unit_price,
    row_start_date,
    is_current
  )
overriding system value
values
  (-1, -1, 'Unknown Product', 0, '2000-01-01', true);