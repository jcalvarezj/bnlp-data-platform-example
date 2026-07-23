SELECT user_id,
       UPPER(full_name) AS full_name,
       TRIM(address) AS address,
       UPPER(city) AS city,
       UPPER(state) AS state,
       UPPER(country) AS country,
       (CASE
         WHEN risk_score > 700
         THEN 0
         ELSE credit_limit
       END) AS credit_limit,
       risk_score,
       created_at,
       updated_at
  FROM {{ ref("stg_users") }}
  
