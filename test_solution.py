import pandas as pd
from solution import add_virtual_column


def test_addition():
    df = pd.DataFrame({
        "quantity": [10, 5],
        "price": [20, 15]
    })

    result = add_virtual_column(
        df, "quantity + price", "total"
    )

    assert result["total"].tolist() == [30, 20]


def test_subtraction():
    df = pd.DataFrame({
        "price": [100, 50],
        "discount": [10, 5]
    })

    result = add_virtual_column(
        df, "price - discount", "net_price"
    )

    assert result["net_price"].tolist() == [90, 45]


def test_multiplication():
    df = pd.DataFrame({
        "quantity": [10, 5],
        "price": [20, 15]
    })

    result = add_virtual_column(
        df, "quantity * price", "revenue"
    )

    assert result["revenue"].tolist() == [200, 75]


def test_multiple_operations():
    df = pd.DataFrame({
        "quantity": [10, 5],
        "price": [20, 15],
        "discount": [10, 5]
    })

    result = add_virtual_column(
        df,
        "quantity * price - discount",
        "revenue"
    )

    assert result["revenue"].tolist() == [190, 70]


def test_invalid_column():
    df = pd.DataFrame({
        "quantity": [10],
        "price": [20]
    })

    result = add_virtual_column(
        df, "quantity + unknown", "total"
    )

    assert result.empty


def test_invalid_new_column():
    df = pd.DataFrame({
        "quantity": [10],
        "price": [20]
    })

    result = add_virtual_column(
        df, "quantity + price", "total123"
    )

    assert result.empty


def test_invalid_operator():
    df = pd.DataFrame({
        "quantity": [10],
        "price": [20]
    })

    result = add_virtual_column(
        df, "quantity / price", "total"
    )

    assert result.empty


def test_original_dataframe_unchanged():
    df = pd.DataFrame({
        "quantity": [10],
        "price": [20]
    })

    original = df.copy()

    add_virtual_column(
        df, "quantity * price", "revenue"
    )

    assert df.equals(original)


def test_extra_spaces():
    df = pd.DataFrame({
        "quantity": [10],
        "price": [20]
    })

    result = add_virtual_column(
        df, "  quantity + price  ", "total"
    )

    assert result["total"].tolist() == [30]