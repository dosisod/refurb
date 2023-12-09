from dataclasses import dataclass

from mypy.nodes import (
    Block,
    Statement,
    AssignmentStmt,
    MypyFile,
    CallExpr,
    MemberExpr,
    NameExpr,
    ReturnStmt,
)

from refurb.checks.common import check_block_like
from refurb.error import Error
from refurb.visitor import TraverserVisitor


@dataclass
class ErrorInfo(Error):
    r"""When an API has a Fluent Interface (the ability to chain multiple calls together), you should chain those calls
    instead of repeatedly assigning and using the value.
    Sometimes a return statement can be written more succinctly:

    Bad:

    ```python
    def get_tensors(device: str) -> torch.Tensor:
        t1 = torch.ones(2, 1)
        t2 = t1.long()
        t3 = t2.to(device)
        return t3

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
        t3 = (
            torch.ones(2, 1)
            .long()
            .to(device)
        )
        return t3

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


def check_call(node, name: str | None = None) -> bool:
    match node:
        # Single chain
        case CallExpr(callee=MemberExpr(expr=NameExpr(name=x), name=_)):
            return name is None or name == x
        # Nested
        case CallExpr(callee=MemberExpr(expr=call_node, name=_)):
            return check_call(call_node)

    return False


class NameReferenceVisitor(TraverserVisitor):
    name: NameExpr
    referenced: bool

    def __init__(self, name: NameExpr, stmt: Statement) -> None:
        super().__init__()
        self.name = name
        self.stmt = stmt
        self.referenced = False

    def visit_name_expr(self, node: NameExpr) -> None:
        if not self.referenced and node.fullname == self.name.fullname:
            self.referenced = True

    @property
    def was_referenced(self) -> bool:
        return self.referenced


def check_stmts(stmts: list[Statement], errors: list[Error]) -> None:
    last = ""
    visitors = []

    for stmt in stmts:
        for visitor in visitors:
            visitor.accept(stmt)
        # No need to track referenced variables anymore
        visitors = [visitor for visitor in visitors if not visitor.referenced]

        match stmt:
            case AssignmentStmt(lvalues=[NameExpr(name=name)], rvalue=rvalue):
                if last and check_call(rvalue, name=last):
                    if f"{last}'" == name:
                        errors.append(
                            ErrorInfo.from_node(
                                stmt,
                                f"Assignment statement should be chained",
                            )
                        )
                    else:
                        # We need to ensure that the variable is not referenced somewhere else
                        name_expr = NameExpr(name=last)
                        name_expr.fullname = last
                        visitors.append(NameReferenceVisitor(name_expr, stmt))

                last = name
            case ReturnStmt(expr=rvalue):
                if last and check_call(rvalue, name=last):
                    errors.append(
                        ErrorInfo.from_node(
                            stmt,
                            f"Return statement should be chained",
                        )
                    )
            case _:
                last = ""

    # Ensure that variables are not referenced
    for visitor in visitors:
        if not visitor.referenced:
            errors.append(
                ErrorInfo.from_node(
                    visitor.stmt,
                    f"Assignment statement should be chained",
                )
            )
