
import pandas as pd

from pipeline import run_pipeline


def test_sales_pipeline(tmp_path):

    # Arrange: create sample sales data
    input_file = tmp_path / "sales.csv"
    output_file = tmp_path / "revenue_by_region.csv"

    df = pd.DataFrame({
        "Order ID": ["SO-001", "SO-002", "SO-003"],
        "Region": ["South", "East", "South"],
        "Product": ["Chair", "Mouse", "Desk"],
        "Quantity": [2, 3, 1],
        "Unit Price": [100, 50, 200],
        "Discount": [10, None, 20],
        "Order Date": [
            "2026-01-01",
            "2026-01-02",
            "2026-01-03"
        ]
    })

    df.to_csv(input_file, index=False)

    # Act: execute the pipeline
    result = run_pipeline(input_file, output_file)

    # Assert: verify regional revenue
    expected = pd.DataFrame({
        "region": pd.Series(["East", "South"], dtype="string"),
        "revenue": pd.Series([150.00, 370.00], dtype="Float64")
    })

    pd.testing.assert_frame_equal(
        result.reset_index(drop=True),
        expected
    )

    # Assert: verify output file exists
    assert output_file.exists()

    # Assert: verify output CSV
    saved_result = pd.read_csv(output_file)

    pd.testing.assert_frame_equal(
        saved_result,
        expected,
        check_dtype=False
    )


def test_pipeline_handles_missing_discount(tmp_path):

    input_file = tmp_path / "sales.csv"
    output_file = tmp_path / "revenue_by_region.csv"

    df = pd.DataFrame({
        "Order ID": ["SO-001"],
        "Region": ["North"],
        "Product": ["Keyboard"],
        "Quantity": [5],
        "Unit Price": [20],
        "Discount": [None],
        "Order Date": ["2026-01-01"]
    })

    df.to_csv(input_file, index=False)

    result = run_pipeline(input_file, output_file)

    assert result["revenue"].iloc[0] == 100.00


def test_pipeline_rejects_invalid_quantity(tmp_path):

    input_file = tmp_path / "sales.csv"
    output_file = tmp_path / "revenue_by_region.csv"

    df = pd.DataFrame({
        "Order ID": ["SO-001"],
        "Region": ["North"],
        "Product": ["Keyboard"],
        "Quantity": ["invalid"],
        "Unit Price": [20],
        "Discount": [0],
        "Order Date": ["2026-01-01"]
    })

    df.to_csv(input_file, index=False)

    try:
        run_pipeline(input_file, output_file)
        assert False, "Expected ValueError"
    except ValueError as error:
        assert "quantity" in str(error).lower()
