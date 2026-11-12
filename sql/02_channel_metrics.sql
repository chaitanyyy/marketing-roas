USE marketing_db;

CREATE OR REPLACE VIEW channel_metrics AS
SELECT c.channel,
       ROUND(SUM(c.spend_inr) / 100000, 1)                        AS spend_lakh,
       ROUND(SUM(c.spend_inr) / SUM(c.leads))                     AS cpl,
       ROUND(SUM(c.spend_inr) / SUM(c.customers))                 AS cac,
       ROUND(SUM(c.revenue_inr) / SUM(c.spend_inr), 2)            AS roas,
       ROUND(a.avg_order_value_inr * (1 + a.repeat_orders_12m) * a.gross_margin) AS ltv,
       ROUND(a.avg_order_value_inr * (1 + a.repeat_orders_12m) * a.gross_margin
             / (SUM(c.spend_inr) / SUM(c.customers)), 1)          AS ltv_cac
FROM campaign_daily c
JOIN channel_assumptions a USING (channel)
GROUP BY c.channel, a.avg_order_value_inr, a.repeat_orders_12m, a.gross_margin;

SELECT * FROM channel_metrics ORDER BY roas DESC;