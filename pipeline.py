
import re
from pathlib import Path

import pandas as pd

from solution import add_virtual_column


def normalize_column_name(column):
    """Convert source headers into consistent column names."""
    column = str(column).strip().lstrip("\ufeff")
    return re.sub(r"[^a-zA-Z0-9]", "", column).lower()


def parse_number(series, remove_spaces=False, decimal_comma=False):
    """Convert text values into numeric values."""

    values = series.astype("string").str.strip()

    if remove_spaces:
        values = values.str.replace(r"\s+", "", regex=True)

    if decimal_comma:
        values = values.str.replace(",", ".", regex=False)

    return pd.to_numeric(values, errors="coerce")


def run_pipeline(
    input_path="sales.csv",
    output_path="revenue_by_region.csv"
):
    # 1. Read the source file
    df = pd.read_csv(input_path, dtype="string")

    original_rows = len(df)

    # 2. Normalize column names
    column_mapping = {
        "orderid": "order_id",
        "region": "region",
        "product": "product",
        "quantity": "quantity",
        "unitprice": "unit_price",
        "discount": "discount",
        "orderdate": "order_date"
    }

    df.columns = [
        column_mapping.get(normalize_column_name(col))
        for col in df.columns
    ]

    required_columns = list(column_mapping.values())

    if (
        len(df.columns) != len(set(df.columns))
        or set(df.columns) != set(required_columns)
    ):
        raise ValueError("Unexpected or missing CSV columns.")

    report = {}

    # 3. Remove repeated header rows
    repeated_header = (
        df["order_id"].str.strip().str.casefold() == "order id".casefold()
    )

    report["repeated_header_rows"] = int(repeated_header.sum())

    df = df.loc[~repeated_header].copy()

    # 4. Remove the non-transaction summary row
    summary_row = (
        df["order_id"].str.strip().str.upper() == "TOTAL"
    )

    report["summary_rows"] = int(summary_row.sum())

    df = df.loc[~summary_row].copy()

    # 5. Remove exact duplicate records
    duplicate_count = int(df.duplicated().sum())

    report["duplicate_rows_removed"] = duplicate_count

    df = df.drop_duplicates().copy()

    # 6. Clean text columns

    # Count region whitespace before trimming
    report["region_whitespace"] = int(
        (
            df["region"].notna()
            & df["region"].ne(df["region"].str.strip())
        ).sum()
    )

    for column in ["order_id", "region", "product"]:
        df[column] = df[column].str.strip()

    # Normalize region capitalization
    report["region_case_normalized"] = int(
        (
            df["region"].notna()
            & df["region"].ne(df["region"].str.title())
        ).sum()
    )

    df["region"] = df["region"].str.title()

    # 7. Convert quantity
    quantity_text = df["quantity"].str.strip()

    report["quantity_space_separators"] = int(
        quantity_text.str.contains(r"\s", regex=True, na=False).sum()
    )

    df["quantity"] = parse_number(
        quantity_text,
        remove_spaces=True
    )

    if df["quantity"].isna().any():
        raise ValueError("Invalid or missing quantity values found.")

    # 8. Convert unit price
    price_text = df["unit_price"].str.strip()

    report["decimal_comma_prices"] = int(
        price_text.str.contains(",", regex=False, na=False).sum()
    )

    df["unit_price"] = parse_number(
        price_text,
        remove_spaces=True,
        decimal_comma=True
    )

    # 9. Recover missing prices using the product price mapping
    missing_prices = int(df["unit_price"].isna().sum())

    price_mapping = {}

    for product, group in df.groupby("product"):

        available_prices = group["unit_price"].dropna().unique()

        if len(available_prices) != 1:
            raise ValueError(
                f"Cannot safely infer unit price for {product}."
            )

        price_mapping[product] = available_prices[0]

    df["unit_price"] = df["unit_price"].fillna(
        df["product"].map(price_mapping)
    )

    report["unit_prices_recovered"] = missing_prices

    if df["unit_price"].isna().any():
        raise ValueError("Some unit prices could not be recovered.")

    # 10. Convert discount
    discount_text = df["discount"].str.strip()

    discount_missing = (
        discount_text.isna() | discount_text.eq("")
    )

    discount_values = parse_number(
        discount_text,
        remove_spaces=True,
        decimal_comma=True
    )

    invalid_discount = discount_values.isna() & ~discount_missing

    if invalid_discount.any():
        raise ValueError("Invalid discount values found.")

    report["missing_discounts"] = int(discount_missing.sum())

    # Empty or missing discount means no discount
    df["discount"] = discount_values.fillna(0)

    # 11. Validate remaining required fields
    for column in ["order_id", "region", "product"]:
        if df[column].isna().any() or df[column].eq("").any():
            raise ValueError(f"Missing values found in {column}.")

    # 12. Convert order date
    df["order_date"] = pd.to_datetime(
        df["order_date"],
        errors="coerce"
    )

    report["invalid_order_dates"] = int(
        df["order_date"].isna().sum()
    )

    if df["order_date"].isna().any():
        raise ValueError("Invalid order dates found.")

    # 13. Validate business values
    if (df["unit_price"] < 0).any():
        raise ValueError("Negative unit prices found.")

    if (df["discount"] < 0).any():
        raise ValueError("Negative discounts found.")

    # Negative quantities are preserved as possible returns
    report["negative_quantity_rows_preserved"] = int(
        (df["quantity"] < 0).sum()
    )

    gross_amount = df["quantity"] * df["unit_price"]

    # Validate discounts only for non-negative quantities
    valid_sales = df["quantity"] >= 0

    if (
        df.loc[valid_sales, "discount"]
        > gross_amount.loc[valid_sales]
    ).any():
        raise ValueError("Discount exceeds gross line amount.")

    # 14. Calculate revenue using Part 1 function
    result = add_virtual_column(
        df,
        "quantity * unit_price - discount",
        "revenue"
    )

    if result.empty and not df.empty:
        raise ValueError("Revenue calculation failed.")

    # 15. Aggregate revenue by region
    revenue_by_region = (
        result.groupby("region", as_index=False)["revenue"]
        .sum()
        .sort_values("region")
    )

    revenue_by_region["revenue"] = (
        revenue_by_region["revenue"].round(2)
    )

    # 16. Write output CSV
    revenue_by_region.to_csv(
        output_path,
        index=False
    )

    # 17. Print cleaning report
    print("\nDATA QUALITY REPORT")
    print("=" * 40)

    for issue, count in report.items():
        print(f"{issue}: {count}")

    print("\nROW SUMMARY")
    print("=" * 40)
    print(f"Original rows: {original_rows}")
    print(f"Final transaction rows: {len(result)}")
    print(f"Rows removed: {original_rows - len(result)}")

    print("\nREVENUE BY REGION")
    print(revenue_by_region.to_string(index=False))

    print(f"\nOutput saved to: {output_path}")

    return revenue_by_region


if __name__ == "__main__":
    run_pipeline()
