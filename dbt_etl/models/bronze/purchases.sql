select * from {{ source('dbt_source', 'purchases') }}
