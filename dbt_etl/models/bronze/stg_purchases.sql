SELECT *
  FROM {{ source('dbt_source', 'purchases') }}
