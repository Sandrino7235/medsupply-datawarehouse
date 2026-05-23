-- MedSupply DW - OLAP Views
-- Part 2 - View 1 and View 2
select
  *
from
  vw_monthly_revenue;

select
  *
from
  vw_product_revenue_rank;

-- VIEW 1 - Monthly Revenue
-- Shows year, month, month_name, revenue, order_count,
-- units_sold, previous month revenue, and MoM growth %
create or replace view vw_monthly_revenue as
with
  monthly as (
    select
      d.year,
      d.month,
      d.month_name,
      SUM(f.line_total) as revenue,
      COUNT(distinct f.order_id) as order_count,
      SUM(f.quantity) as units_sold
    from
      fact_orders f
      join dim_date d on f.date_key = d.date_key
    group by
      d.year,
      d.month,
      d.month_name
  )
select
  year,
  month,
  month_name,
  revenue,
  order_count,
  units_sold,
  -- Previous month revenue using LAG, ordered by year then month
  LAG(revenue) over (
    order by
      year,
      month
  ) as prev_month_revenue,
  -- Month-on-month growth %
  -- Formula: ((current - previous) / previous) * 100
  -- NULLIF prevents division by zero if previous month revenue is 0
  ROUND(
    (
      revenue - LAG(revenue) over (
        order by
          year,
          month
      )
    ) / NULLIF(
      LAG(revenue) over (
        order by
          year,
          month
      ),
      0
    ) * 100,
    2
  ) as mom_growth_pct
from
  monthly
order by
  year,
  month;

-- VIEW 2 - Product Revenue Rank
-- Shows product_name, category_name, total_revenue,
-- total_units, order_count, and revenue_rank
create or replace view vw_product_revenue_rank as
select
  p.product_name,
  p.category_name,
  SUM(f.line_total) as total_revenue,
  SUM(f.quantity) as total_units,
  COUNT(distinct f.order_id) as order_count,
  -- Rank products by total revenue, highest first
  -- RANK() gives the same rank to ties, leaving gaps (1,2,2,4...)
  -- DENSE_RANK() would give no gaps (1,2,2,3...) - either is acceptable
  RANK() over (
    order by
      SUM(f.line_total) desc
  ) as revenue_rank
from
  fact_orders f
  join dim_product p on f.product_key = p.product_key
  -- Exclude the unknown member placeholder row
where
  p.product_key <> -1
group by
  p.product_name,
  p.category_name
order by
  revenue_rank;