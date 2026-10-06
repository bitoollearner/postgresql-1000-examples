-- =====================================================================
-- Dataset: ecommerce   Version: v1
-- Used by: Chapters 4-26, 30, 35-43, 49
-- Sizes: ecommerce (seeded, ~5k orders) | ecommerce_lg (~2M orders)
-- The schema name is supplied by psql: -v schema=ecommerce
-- =====================================================================

DROP SCHEMA IF EXISTS :schema CASCADE;
CREATE SCHEMA :schema;
SET search_path TO :schema;

CREATE TABLE categories (
    category_id     integer PRIMARY KEY,
    category_name   text        NOT NULL,
    parent_id       integer     REFERENCES categories(category_id)
);

CREATE TABLE customers (
    customer_id     integer PRIMARY KEY,
    first_name      text        NOT NULL,
    last_name       text        NOT NULL,
    email           text,                        -- deliberately nullable: NULL-handling examples
    country         text        NOT NULL,
    city            text,
    signup_date     date        NOT NULL,
    segment         text        NOT NULL,        -- 'consumer' | 'small_business' | 'enterprise'
    is_active       boolean     NOT NULL DEFAULT true
);

CREATE TABLE products (
    product_id      integer PRIMARY KEY,
    product_name    text        NOT NULL,
    category_id     integer     NOT NULL REFERENCES categories(category_id),
    unit_price      numeric(10,2) NOT NULL CHECK (unit_price >= 0),
    cost_price      numeric(10,2),
    launched_on     date        NOT NULL,
    discontinued_on date
);

CREATE TABLE orders (
    order_id        integer PRIMARY KEY,
    customer_id     integer     NOT NULL REFERENCES customers(customer_id),
    order_ts        timestamptz NOT NULL,
    status          text        NOT NULL,        -- 'placed'|'shipped'|'delivered'|'cancelled'|'returned'
    channel         text        NOT NULL,        -- 'web'|'mobile'|'store'|'partner'
    shipping_cost   numeric(10,2) NOT NULL DEFAULT 0
);

CREATE TABLE order_items (
    order_id        integer     NOT NULL REFERENCES orders(order_id),
    line_no         smallint    NOT NULL,
    product_id      integer     NOT NULL REFERENCES products(product_id),
    quantity        integer     NOT NULL CHECK (quantity > 0),
    unit_price      numeric(10,2) NOT NULL,
    discount_pct    numeric(5,2)  NOT NULL DEFAULT 0,
    PRIMARY KEY (order_id, line_no)
);

CREATE TABLE payments (
    payment_id      integer PRIMARY KEY,
    order_id        integer     NOT NULL REFERENCES orders(order_id),
    paid_ts         timestamptz NOT NULL,
    amount          numeric(12,2) NOT NULL,
    method          text        NOT NULL         -- 'card'|'upi'|'wallet'|'cod'|'netbanking'
);

CREATE TABLE returns (
    return_id       integer PRIMARY KEY,
    order_id        integer     NOT NULL REFERENCES orders(order_id),
    line_no         smallint    NOT NULL,
    returned_on     date        NOT NULL,
    reason          text        NOT NULL,
    refund_amount   numeric(12,2) NOT NULL
);

-- Deliberately UNindexed at load time. Indexes are the subject of
-- Chapters 35-38 and are created there, by the reader, on purpose.
