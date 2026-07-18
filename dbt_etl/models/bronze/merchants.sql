select * from {{ source('dbt_source', 'merchants') }}
