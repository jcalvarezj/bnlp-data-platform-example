SELECT *
  FROM {{ source('dbt_source', 'payments') }}
