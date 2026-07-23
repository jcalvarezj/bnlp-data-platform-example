SELECT *
  FROM {{ source('dbt_source', 'installments') }}
