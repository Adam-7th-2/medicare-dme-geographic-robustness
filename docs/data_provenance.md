# Data provenance

[Official CMS catalog](https://data.cms.gov/provider-summary-by-type-of-service/medicare-durable-medical-equipment-devices-supplies/medicare-durable-medical-equipment-devices-supplies-by-geography-and-service): Medicare Durable Medical Equipment, Devices & Supplies by Geography and Service, 2023 reference year. Catalog consulted October 16, 2026 but requires JavaScript; no usable release or licensing metadata was returned. No redistribution license is inferred.

Raw file: data/raw/Medicare_DME_Devices_Supplies_by_Geography_and_Service_2023.csv; 38,675 records, 18 columns; SHA-256 `d877fd726df3dd77df17a82e5ef217c02da448410a3c9e1c979f6fc92651f2d7`. Original acquisition date, original filename before local naming and exact release revision are unrecorded.

Primary file: data/processed/medicare_dme_2023_51_areas.csv; 36,528 records, 51 areas, 1,250 HCPCS codes; SHA-256 `6fcc4c5dcec5b821c8e5315dd4e81da9327a097184cd6c0e99e3964898712efb`. Script 07 restricts State-labeled data to an explicit allowlist of the 50 states plus DC. Excludes 1,647 non-State rows and 500 State-labeled rows outside that allowlist. Exploratory population retains 37,028 State-labeled rows over 60 categories.

Targets: Avg_Suplr_Mdcr_Pymt_Amt and Avg_Suplr_Mdcr_Stdzd_Amt. Predictors: HCPCS_Cd and optionally Suplr_Rentl_Ind. These are aggregate records, not beneficiaries or expenditure totals. Paired/CV analyses require finite positive targets; rental-aware analysis additionally requires geography/code/rental labels. CV analysis rejects duplicate code/rental/area keys and requires at least ten areas per group. Exact operations are retained in scripts 07, 10, 12 and 13.

Raw data remain unchanged. Public availability does not alone verify redistribution permission. Raw and processed CSVs are ignored by Git pending verified sharing terms. Obtain the official 2023 file and documentation via CMS; record acquisition details and investigate any schema/hash mismatch before rerunning.
