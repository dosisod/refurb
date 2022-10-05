from dataclasses import dataclass

from mypy.nodes import ComparisonExpr, ForStmt, GeneratorExpr, ListExpr

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    Since tuple, list, and set literals can be used with the `in` operator, it
    is best to pick one and stick with it.

    Bad:

    ```
    for x in [1, 2, 3]:
        pass

    nums = [str(x) for x in [1, 2, 3]]
    ```

    Good:

    ```
    for x in (1, 2, 3):
        pass

    nums = [str(x) for x in (1, 2, 3)]
    ```
    """

    code = 109


def error_msg(oper: str) -> str:
    return f"Replace `{oper} [x, y, z]` with `{oper} (x, y, z)`"


def check(
    node: ComparisonExpr | ForStmt | GeneratorExpr, errors: list[Error]
) -> None:
    match node:
        case ComparisonExpr(
            operators=["in" | "not in" as oper],
            operands=[_, ListExpr() as expr],
        ):
            errors.append(ErrorInfo(expr.line, expr.column, error_msg(oper)))

        case ForStmt(expr=ListExpr() as expr):
            errors.append(ErrorInfo(expr.line, expr.column, error_msg("in")))

        case GeneratorExpr():
            for expr in node.sequences:  # type: ignore
                if isinstance(expr, ListExpr):
                    errors.append(
                        ErrorInfo(expr.line, expr.column, error_msg("in"))
                    )
