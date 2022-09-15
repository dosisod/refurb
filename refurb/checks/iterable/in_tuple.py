from dataclasses import dataclass

from mypy.nodes import ComparisonExpr, ForStmt, GeneratorExpr, ListExpr

from refurb.error import Error


@dataclass
class ErrorUseTupleWithInExpr(Error):
    """
    Since tuple's cannot change value over time, it is more performant to use
    them in `for` loops, generators, etc:

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
    msg: str = "Use `in (x, y, z)` instead of `in [x, y, z]`"


def check(
    node: ComparisonExpr | ForStmt | GeneratorExpr, errors: list[Error]
) -> None:
    match node:
        case (
            ComparisonExpr(
                operators=["in"],
                operands=[_, ListExpr() as expr],
            )
            | ForStmt(expr=ListExpr() as expr)
        ):
            errors.append(ErrorUseTupleWithInExpr(expr.line, expr.column))

        case GeneratorExpr():
            for expr in node.sequences:  # type: ignore
                if isinstance(expr, ListExpr):
                    errors.append(
                        ErrorUseTupleWithInExpr(expr.line, expr.column)
                    )
