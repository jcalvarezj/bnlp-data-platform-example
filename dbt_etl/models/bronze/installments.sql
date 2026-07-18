select * from {{ source('dbt_source', 'installments') }}
