CREATE SCHEMA IF NOT EXISTS olist;

CREATE TABLE olist.orders (
    order_id text,
    customer_id text,
    order_status text,
    order_purchase_timestamp timestamp,
    order_approved_at timestamp,
    order_delivered_carrier_date timestamp,
    order_delivered_customer_date timestamp,
    order_estimated_delivery_date timestamp
);

CREATE TABLE olist.order_items (
    order_id text,
    order_item_id integer,
    product_id text,
    seller_id text,
    shipping_limit_date timestamp,
    price numeric,
    freight_value numeric
);

CREATE TABLE olist.payments (
    order_id text,
    payment_sequential integer,
    payment_type text,
    payment_installments integer,
    payment_value numeric
);

CREATE TABLE olist.reviews (
    review_id text,
    order_id text,
    review_score integer,
    review_comment_title text,
    review_comment_message text,
    review_creation_date timestamp,
    review_answer_timestamp timestamp
);

CREATE TABLE olist.customers (
    customer_id text,
    customer_unique_id text,
    customer_zip_code_prefix text,
    customer_city text,
    customer_state text
);

CREATE TABLE olist.products (
    product_id text,
    product_category_name text,
    product_name_lenght integer,
    product_description_lenght integer,
    product_photos_qty integer,
    product_weight_g integer,
    product_length_cm integer,
    product_height_cm integer,
    product_width_cm integer
);

CREATE TABLE olist.sellers (
    seller_id text,
    seller_zip_code_prefix text,
    seller_city text,
    seller_state text
);

CREATE TABLE olist.geolocation (
    geolocation_zip_code_prefix text,
    geolocation_lat double precision,
    geolocation_lng double precision,
    geolocation_city text,
    geolocation_state text
);

CREATE TABLE olist.category_translation (
    product_category_name text,
    product_category_name_english text
);

CREATE INDEX orders_customer_id_idx ON olist.orders (customer_id);
CREATE INDEX orders_purchase_ts_idx ON olist.orders (order_purchase_timestamp);
CREATE INDEX order_items_order_id_idx ON olist.order_items (order_id);
CREATE INDEX order_items_product_id_idx ON olist.order_items (product_id);
CREATE INDEX order_items_seller_id_idx ON olist.order_items (seller_id);
CREATE INDEX payments_order_id_idx ON olist.payments (order_id);
CREATE INDEX reviews_order_id_idx ON olist.reviews (order_id);
CREATE INDEX customers_customer_id_idx ON olist.customers (customer_id);
CREATE INDEX customers_unique_id_idx ON olist.customers (customer_unique_id);
CREATE INDEX products_product_id_idx ON olist.products (product_id);
CREATE INDEX sellers_seller_id_idx ON olist.sellers (seller_id);
CREATE INDEX geolocation_zip_idx ON olist.geolocation (geolocation_zip_code_prefix);
CREATE INDEX category_translation_name_idx ON olist.category_translation (product_category_name);