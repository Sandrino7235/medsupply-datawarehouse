create table if not exists staging_raw_facility (
  facility_id INTEGER,
  facility_name VARCHAR(200),
  facility_type VARCHAR(50),
  country_name VARCHAR(100),
  region_name VARCHAR(50)
);

create table if not exists staging_raw_product (
  product_id INTEGER,
  product_name VARCHAR(100),
  category_name VARCHAR(100),
  unit_price NUMERIC(10, 2),
  is_active BOOLEAN
);

create table if not exists staging_raw_order (
  order_line_id INTEGER,
  order_id INTEGER,
  order_date DATE,
  facility_id INTEGER,
  product_id INTEGER,
  quantity INTEGER,
  unit_price_sold NUMERIC(10, 2),
  line_total NUMERIC(12, 2)
);