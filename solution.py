import ast
import re
import pandas as pd


VALID_LABEL = re.compile(r"^[A-Za-z_]+$")


def add_virtual_column(
    df: pd.DataFrame,
    role: str,
    new_column: str
) -> pd.DataFrame:
    """
    Add a calculated column to a DataFrame.

    Supported operations:
        Addition (+)
        Subtraction (-)
        Multiplication (*)

    Returns an empty DataFrame if validation fails.
    """

    try:
        # 1. Validate input types
        if not isinstance(df, pd.DataFrame):
            return pd.DataFrame()

        if not isinstance(role, str) or not isinstance(new_column, str):
            return pd.DataFrame()

        # 2. Validate all existing column labels
        if not all(
            isinstance(col, str) and VALID_LABEL.fullmatch(col)
            for col in df.columns
        ):
            return pd.DataFrame()

        # 3. Validate the new column name
        if not VALID_LABEL.fullmatch(new_column):
            return pd.DataFrame()

        # Avoid silently overwriting an existing column
        if new_column in df.columns:
            return pd.DataFrame()

        # 4. Parse the mathematical expression
        expression = ast.parse(role.strip(), mode="eval")

        # 5. Evaluate only explicitly supported operations
        def calculate(node):

            if isinstance(node, ast.Name):
                if node.id not in df.columns:
                    raise ValueError("Unknown column")

                return df[node.id]

            if isinstance(node, ast.BinOp):

                left = calculate(node.left)
                right = calculate(node.right)

                if isinstance(node.op, ast.Add):
                    return left + right

                if isinstance(node.op, ast.Sub):
                    return left - right

                if isinstance(node.op, ast.Mult):
                    return left * right

                raise ValueError("Unsupported operation")

            raise ValueError("Invalid expression")

        result = calculate(expression.body)

        # 6. Return a new DataFrame without modifying the original
        result_df = df.copy()
        result_df[new_column] = result

        return result_df

    except Exception:
        return pd.DataFrame()