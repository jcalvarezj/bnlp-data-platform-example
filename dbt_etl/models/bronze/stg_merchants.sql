SELECT *
  FROM {{ source('dbt_source', 'merchants') }}
