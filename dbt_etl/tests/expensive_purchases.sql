{{ config(severity = 'warn') }}

SELECT *
  FROM {{ source('dbt_source', 'purchases') }}
 WHERE purchase_value >= 20000
