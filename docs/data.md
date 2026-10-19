# SD Business Data

## Intro to what we have

We sourced the City of San Diego Open Data Portal's Business Tax Certificates dataset published by the City Treasurer. You can find the sourced information at this URL: https://data.sandiego.gov/datasets/business-tax-certificates/  

The Business Tax Certs dataset contains active and inactive business tax certificate records for the city of SD. Historical inactive periods are split into several CSV files by account creation period. 

The six files contain 633,317 total records. 

| File | Records | Status |
|---|---:|---|
| Active | 59,915 | 59,888 Active; 27 Pending |
| Inactive, 2015-current | 104,950 | Cancelled |
| Inactive, 2010-2014 | 78,250 | Cancelled |
| Inactive, 2000-2009 | 154,969 | Cancelled |
| Inactive, 1990-1999 | 125,415 | Cancelled |
| Inactive, pre-1990 | 109,818 | Cancelled |

Each file contains 27 columns. 

### Business information

- `account_key`
- `account_status`
- `business_owner_name`
- `ownership_type`
- `dba_name`
- `naics_sector`
- `naics_code`
- `naics_description`

### Dates

- `date_account_creation`
- `date_cert_expiration`
- `date_cert_effective`
- `date_business_start`

### Address and location

- `address_no`
- `address_pd`
- `address_road`
- `address_sfx`
- `address_no_fraction`
- `address_city`
- `address_state`
- `address_zip`
- `address_suite`
- `address_pmb_box`
- `address_po_box`
- `bid`
- `council_district`
- `lat`
- `lng`

The address fields and coordinates make it possible to associate
business records with locations.

## Historical Coverage

Account creation dates in the dowloaded data range from 1974 to 2026. The historical files are primarily divided by date_account_creation. 'date_business_start' predates account creation time to time, so the historical file in which a record appears shouldn't necessarily be treated as the period when the business began operating. 

## Do we have definitive business occupancy start and end dates?

Not definitively, but partially. As mentioned previously, the dataset contains 'date_business_start', providing a possible start date for the business. However, there is no explicit business closure date, move out date, or end of occupancy field. 'date_cert_expiration' records when the business tax certificate expired. Certificate expiration shouldn't automatically be treated as the date the business stopped operating or occupying an address. 

## Data Quality

Date quality problems were found during my first exploratory data analysis. 

Examples include:

- `date_business_start` values as early as year `0002` and `0021`
- `date_cert_effective` values such as year `0200` and dates as late as
  year `5201`
- `date_cert_expiration` values as early as year `0001` and as late as
  year `2201`
- some inactive records have certificate expiration dates extending
  into future years
- 11 `date_cert_effective` values in the pre-1990 file were missing or
  could not be parsed in the initial review

This should be validated and cleaned prior to usage in historical timelines. 
