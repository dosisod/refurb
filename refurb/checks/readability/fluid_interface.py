from dataclasses import dataclass

from mypy.nodes import (
    Block,
    Statement,
    AssignmentStmt,
    MypyFile,
    CallExpr,
    MemberExpr,
    NameExpr,
)

from refurb.checks.common import check_block_like
from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    r"""When an API has a Fluent Interface (the ability to chain multiple calls together), you should chain those calls
    instead of repeatedly assigning and using the value.
    Sometimes a return statement can be written more succinctly:

    Bad:

    ```python
    def get_tensors(device: str) -> torch.Tensor:
        a = torch.ones(2, 1)
        a = a.long()
        a = a.to(device)
        return a


    def process(file_name: str):
        common_columns = ["col1_renamed", "col2_renamed", "custom_col"]
        df = spark.read.parquet(file_name)
        df = df \
            .withColumnRenamed('col1', 'col1_renamed') \
            .withColumnRenamed('col2', 'col2_renamed')
        df = df \
            .select(common_columns) \
            .withColumn('service_type', F.lit('green'))
        return df
    ```

    Good:

    ```python
    def get_tensors(device: str) -> torch.Tensor:
        a = (
            torch.ones(2, 1)
            .long()
            .to(device)
        )
        return a

    def process(file_name: str):
        common_columns = ["col1_renamed", "col2_renamed", "custom_col"]
        df = (
            spark.read.parquet(file_name)
            .withColumnRenamed('col1', 'col1_renamed')
            .withColumnRenamed('col2', 'col2_renamed')
            .select(common_columns)
            .withColumn('service_type', F.lit('green'))
        )
        return df
    ```
    """

    name = "use-fluid-interface"
    code = 184
    categories = ("readability",)


def check(node: Block | MypyFile, errors: list[Error]) -> None:
    check_block_like(check_stmts, node, errors)


def check_call(node) -> bool:
    match node:
        # Single chain
        case CallExpr(callee=MemberExpr(expr=NameExpr(name=x), name=y)):
            return True
        # Nested
        case CallExpr(callee=MemberExpr(expr=call_node, name=y)):
            return check_call(call_node)

    return False


def check_stmts(stmts: list[Statement], errors: list[Error]) -> None:
    last = ""

    for stmt in stmts:
        match stmt:
            case AssignmentStmt(lvalues=[NameExpr(name=name)], rvalue=rvalue):
                if last and f"{last}'" == name and check_call(rvalue):
                    errors.append(
                        ErrorInfo.from_node(
                            stmt,
                            f"Assignment statements should be chained",
                        )
                    )

                last = name

            case _:
                last = ""
