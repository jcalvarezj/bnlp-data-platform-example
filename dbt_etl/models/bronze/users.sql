select * from {{ source('dbt_source', 'users') }}
