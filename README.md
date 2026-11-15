Virtual Columns in Pandas DataFrames
====================================

Project Overview
----------------

This project implements a reusable function for adding calculated (virtual) columns to pandas DataFrames.

It also includes a data processing pipeline that cleans sales transaction data, calculates revenue for each order line, and generates total revenue by region.

Technology Stack
----------------

-   Python

-   Pandas

-   Pytest

-   Git and GitHub

Project Structure
-----------------

```
virtual-columns-pandas/
│
├── solution.py
├── pipeline.py
├── sales.csv
├── revenue_by_region.csv
├── test_virtual_column.py
├── test_solution.py
├── test_pipeline.py
├── requirements.txt
├── README.md
└── .gitignore
```

1\. Installation
----------------

Clone the repository:

```
git clone https://github.com/YOUR_USERNAME/virtual-columns-pandas.git
cd virtual-columns-pandas
```

Create a virtual environment:

```
python -m venv .venv
```

Activate it on Windows:

```
.venv\Scripts\activate
```

Install dependencies:

```
pip install -r requirements.txt
```

2\. Virtual Column Function
---------------------------

The `add_virtual_column()` function accepts three parameters:

-   `df`: Input pandas DataFrame.

-   `role`: Mathematical expression.

-   `new_column`: Name of the calculated column.

### Supported operations

-   Addition (`+`)

-   Subtraction (`-`)

-   Multiplication (`*`)

The function validates column names and referenced columns. Invalid expressions, unsupported operators, invalid labels, and unknown columns return an empty DataFrame.

Python's AST module is used to parse and safely evaluate supported mathematical expressions instead of using `eval()`.

The function also preserves the original DataFrame and does not overwrite existing columns.

### Example

```
import pandas as pd
from solution import add_virtual_column

df = pd.DataFrame({
    "quantity": [10, 5],
    "unit_price": [20, 15],
    "discount": [10, 5]
})

result = add_virtual_column(
    df,
    "quantity * unit_price - discount",
    "revenue"
)

print(result)
```

Expected result:

```
   quantity  unit_price  discount  revenue
0        10          20        10      190
1         5          15         5       70
```

3\. Sales Data Pipeline
-----------------------

Run the pipeline:

```
python pipeline.py
```

The pipeline performs the following steps:

1.  Reads the original `sales.csv` file.

2.  Normalizes column names.

3.  Removes repeated header rows and summary rows.

4.  Removes exact duplicate records.

5.  Cleans whitespace from text fields.

6.  Standardizes region names and capitalization.

7.  Converts quantity, unit price, and discount values into numeric values.

8.  Handles missing discounts by replacing them with zero.

9.  Recovers missing unit prices using a product-price mapping.

10. Converts order dates into datetime values.

11. Validates required fields and business values.

12. Preserves negative quantities as possible returns.

13. Calculates revenue using `add_virtual_column()`.

14. Aggregates revenue by region.

15. Exports the results to `revenue_by_region.csv`.

### Revenue calculation

```
Revenue = (Quantity * Unit Price) - Discount
```

The discount is treated as a monetary amount deducted from the entire order line, not as a percentage.

4\. Data Quality Findings and Assumptions
-----------------------------------------

The original sales dataset is treated as raw input. The pipeline identifies and handles the detected data-quality issues before calculating revenue.

### Data quality report

| Data quality issue | Rows affected | Treatment |
| Repeated header rows | 1 | Removed |
| Summary rows | 1 | Removed |
| Exact duplicate records | 5 extra copies | Removed extra copies |
| Missing discounts | 959 after deduplication | Replaced with 0 |
| Missing unit prices | 4 | Recovered using product-price mapping |
| Region whitespace | 8 | Trimmed |
| Region capitalization | 10 | Standardized |
| Quantity thousands separators | 4 | Removed internal spaces |
| Decimal-comma prices | 7 | Converted to decimal points |
| Invalid order dates | 0 | No invalid dates found |
| Negative quantities | 6 | Preserved as possible returns |

### Row summary

| Description | Row count |
| Original rows | 1,507 |
| Repeated header rows removed | 1 |
| Summary rows removed | 1 |
| Extra duplicate records removed | 5 |
| Final transaction rows | 1,500 |

The pipeline removed seven rows in total: one repeated header, one summary row, and five extra duplicate records.

No transaction rows were lost due to missing discounts or missing unit prices. Missing discounts were replaced with zero, and missing unit prices were recovered using the product-price mapping.

### Additional assumptions

-   An empty discount represents no discount.

-   Discounts are monetary amounts, not percentages.

-   Negative quantities are preserved because they may represent product returns.

-   Negative unit prices and negative discounts are considered invalid.

-   A discount greater than the gross order-line amount is considered invalid for non-negative quantities.

-   Exact duplicate records are treated as accidental duplicate export rows and extra copies are removed.

-   Missing unit prices are recovered only when the product has a consistent, unambiguous available price in the dataset.

-   Region names are standardized by trimming whitespace and normalizing capitalization.

-   Invalid or ambiguous required data causes the pipeline to stop rather than silently inventing values.

-   Existing columns are not overwritten when creating a virtual column.

The pipeline prints a data quality report and row summary during execution.

5\. Output
----------

The pipeline generates:

`revenue_by_region.csv`

The output contains:

-   Region

-   Total revenue

Revenue is rounded to two decimal places.

### Revenue by region

| Region | Revenue |
| Central | 515,824.67 |
| East | 442,219.91 |
| North | 665,897.52 |
| South | 504,036.04 |
| West | 442,268.89 |
| **Total** | **2,570,247.03** |

6\. Running Tests
-----------------

Run all tests with one command:

```
pytest -v
```

The tests cover:

-   Addition, subtraction, and multiplication.

-   Multiple mathematical operations.

-   Invalid column names.

-   Invalid expressions and unsupported operators.

-   Missing columns.

-   Extra whitespace.

-   Original DataFrame preservation.

-   Sales pipeline execution.

-   Missing discount handling.

-   Invalid quantity handling.

-   Output CSV generation.

-   Regional revenue calculations.

7\. Author
----------

**Manish Kumar Rai**