CREATE DATABASE IF NOT EXISTS marketing_db;
USE marketing_db;

DROP TABLE IF EXISTS campaign_daily;
DROP TABLE IF EXISTS channel_assumptions;
DROP TABLE IF EXISTS ab_test;

CREATE TABLE campaign_daily (
    date         DATE NOT NULL,
    channel      VARCHAR(30) NOT NULL,
    spend_inr    INT,
    impressions  INT,
    clicks       INT,
    leads        INT,
    customers    INT,
    revenue_inr  INT,
    PRIMARY KEY (date, channel)
);

CREATE TABLE channel_assumptions (
    channel              VARCHAR(30) PRIMARY KEY,
    avg_order_value_inr  INT,
    repeat_orders_12m    DECIMAL(4,2),
    gross_margin         DECIMAL(3,2)
);

CREATE TABLE ab_test (
    date         DATE NOT NULL,
    variant      VARCHAR(15) NOT NULL,
    visitors     INT,
    conversions  INT,
    PRIMARY KEY (date, variant)
);