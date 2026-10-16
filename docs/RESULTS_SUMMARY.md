# Verified experimental results

Audit: October 16, 2026. All 13 implemented scripts completed in an isolated project copy. All 17 CSVs and the processed dataset matched regenerated outputs at rtol=atol=1e-9. Expected six-decimal headline values passed absolute tolerance 0.00000051. Original results were preserved.

| Measurement | Verified value | Script number |
|---|---:|---|
| Original records | 38675.000000000 | 01 |
| Exploratory records | 37028.000000000 | 02 |
| Exploratory categories | 60.000000000 | 02 |
| Primary records | 36528.000000000 | 07 |
| Primary areas | 51.000000000 | 07 |
| Unique HCPCS codes | 1250.000000000 | 07 |
| HCPCS actual MAE | 47.838394593 | 08, 12 |
| HCPCS standardized MAE | 38.878698847 | 12 |
| Rental actual MAE | 19.894408643 | 13 |
| Rental standardized MAE | 10.300449105 | 13 |
| Rental actual RMSE | 185.665685940 | 13 |
| Rental standardized RMSE | 182.010389445 | 13 |
| Known HCPCS observations | 36391.000000000 | 09 |
| Unseen HCPCS observations | 137.000000000 | 09 |
| Unseen actual MAE | 746.996987396 | 09 |
| Comparable HCPCS/rental groups | 916.000000000 | 10 |
| Lower standardized CV | 805.000000000 | 10 |
| Areas with lower standardized rental MAE | 51.000000000 | 13 |

## Five manuscript tables

1. Dataset composition: exploratory 37,028 records, 60 categories, 1,250 codes; mean 327.78, median 39.56. Primary 36,528 records, 51 areas, 1,250 codes; mean 330.37, median 39.76.
2. Preliminary baselines: Global mean: MAE 458.62, RMSE 1210.88; HCPCS mean: MAE 48.97, RMSE 265.43.
3. Known/unseen coverage: Known: 36,391 records, MAE 45.21, error share 94.14%; Unseen: 137 records, MAE 747.00, error share 5.86%.
4. CV comparison: 916 groups; mean actual CV 0.09059, standardized 0.04744; lower/higher/equal 805/95/16.
5. Prediction comparison (MAE, RMSE, NMAE%, worst-area MAE): HCPCS Actual: 47.84, 290.78, 14.48, 103.55; HCPCS Standardized: 38.88, 284.49, 11.71, 92.72; Rental Actual: 19.89, 185.67, 6.02, 66.42; Rental Standardized: 10.30, 182.01, 3.10, 54.63.

These values agree with the five source tables at displayed precision. Repeated exploratory validation: mean random MAE 49.07356895; geographic MAE 47.59984817; positive geographic gaps 12/30. Unmatched test populations limit interpretation.

Methods are interpretable group means, not Random Forests or neural networks. Errors for actual and standardized targets are not interchangeable; smaller standardized-target errors do not establish a causal improvement in actual-payment prediction. MAE weights aggregate rows equally.
