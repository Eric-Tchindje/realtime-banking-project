

{{ 
  config(
    materialized='incremental',
    unique_key='transaction_id',
    incremental_strategy='merge'
  ) 
}}

WITH deduped_transactions AS (

    SELECT
        t.transaction_id,
        t.account_id,
        t.amount,
        t.related_account_id,
        t.status,
        t.transaction_type,
        t.transaction_time,
        ROW_NUMBER() OVER (
            PARTITION BY t.transaction_id
            ORDER BY t.transaction_time DESC
        ) AS rn
    FROM {{ ref('stg_transactions') }} t

    {% if is_incremental() %}
      WHERE t.transaction_time > (
          SELECT COALESCE(MAX(transaction_time), '1900-01-01')
          FROM {{ this }}
      )
    {% endif %}

)

SELECT
    t.transaction_id,
    t.account_id,
    a.customer_id,
    t.amount,
    t.related_account_id,
    t.status,
    t.transaction_type,
    t.transaction_time,
    CURRENT_TIMESTAMP AS load_timestamp
FROM deduped_transactions t
LEFT JOIN {{ ref('stg_accounts') }} a
    ON t.account_id = a.account_id
WHERE t.rn = 1
