# Business Rules --WIP--

## Bronze Layer

This layer will contain an exact copy of raw incoming data in order to preserve its original structure and value, so it serves as a reference single source of truth for auditing

## Silver Layer

Input data is assumed to come dirty, as it doesn't comply with several minumin quality rules such as:

- User and Product names have to be in uppercase
- User and Merchant addresses may come with trailing spaces that must be removed
- Purchases with a value equal or greater than 20000 should be discarded in the Silver layer and on
- ...

The Silver Layer will store transformations that standardize and enrich data

Furthermore, a view will be built in this layer to quickly retrieve what purchases where made by which user

## Gold Layer

Corresponds to a Data Warehouse modelled as a Star Schema, which is comprised of Silver Layer's data

It will help answer aggregate queries regarding the following measures:

- payments
- installments
- credits
- purchases
- risk scores
- ...
