select * from {{ source('dbt_source', 'payments') }}
