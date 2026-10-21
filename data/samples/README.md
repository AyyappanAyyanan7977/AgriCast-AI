# AgriCast test dataset

`AgriCast_test_dataset_synthetic.csv` is a copy of the bundled **synthetic demo dataset**. It is intended to test CSV upload, schema inspection, model training/evaluation, and yield prediction workflows. Values are synthetic and must not be used for real agricultural decisions or presented as field-validated measurements.

Columns:
- `rainfall_mm`: rainfall in millimetres
- `mean_temperature_c`: mean temperature in degrees Celsius
- `soil_type`: categorical soil type
- `fertilizer_kg_ha`: fertilizer application in kg/ha
- `irrigation_method`: categorical irrigation method
- `yield_tonnes_ha`: target yield in tonnes/ha

For the current bundled model, keep the column names and data types unchanged. The target column is `yield_tonnes_ha`.
