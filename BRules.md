# Business Rules --WIP--

Layers of each processing stage will be stored in Schemas named with the convention `bnlp_{stage_name}`

## Bronze Layer

This layer will contain an exact copy of raw incoming data in order to preserve its original structure and value, so it serves as a reference single source of truth for auditing

## Silver Layer (Staging Area)

Input data is assumed to come dirty, as it doesn't comply with several minumin quality rules such as:

- User, product, city, state, and contry names have to be in uppercase
- Users with a risk score over 700 must have their credit limit set as 0
- User and Merchant addresses may come with trailing spaces that must be removed
- Purchases with a value equal or greater than 20000 should be discarded in the Silver layer and on
- ...

The Silver Layer will store transformations that standardize and enrich data

Furthermore, a view will be built in this layer to quickly retrieve what purchases where made by which user

## Gold Layer (Data Warehouse)

Corresponds to a Star Schema Data Warehouse of analytic tables comprised of Silver Layer's data

It will help answer aggregate queries regarding the following measures:

- payments
- installments
- credits
- purchases
- risk scores
- ...

## Quarantine Layer (Rejected Records)

Contains all the records that were filtered out as they don't comply with certain business rules

The tables with rejections can be found in the following Schema bnlp_dbt_test__audit
