#一个数据库两个schema。 
CREATE SCHEMA IF NOT EXISTS app;

REVOKE ALL ON SCHEMA public FROM PUBLIC;

CREATE ROLE analyst_ro LOGIN PASSWORD 'analyst_ro';
GRANT USAGE ON SCHEMA olist TO analyst_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA olist TO analyst_ro;
ALTER ROLE analyst_ro SET default_transaction_read_only = on;
ALTER ROLE analyst_ro SET statement_timeout = '10s';
ALTER ROLE analyst_ro SET search_path = olist;

CREATE ROLE app_rw LOGIN PASSWORD 'app_rw';
GRANT USAGE, CREATE ON SCHEMA app TO app_rw;