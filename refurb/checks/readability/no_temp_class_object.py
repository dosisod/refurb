from dataclasses import dataclass

from mypy.nodes import (
    CallExpr,
    Decorator,
    FuncDef,
    MemberExpr,
    NameExpr,
    TypeInfo,
)

from refurb.error import Error


@dataclass
class ErrorInfo(Error):
    """
    You don't need to construct a class object to call a static method or a
    class method, just invoke the method on the class directly:

    Bad:

    ```
    cwd = Path().cwd()
    ```

    Good:

    ```
    cwd = Path.cwd()
    ```
    """

    name = "no-temp-class-object"
    code = 165
    categories = ("readability",)


def check(node: CallExpr, errors: list[Error]) -> None:
    match node:
        case CallExpr(
            callee=MemberExpr(
                expr=CallExpr(
                    callee=NameExpr(node=TypeInfo() as klass),
                    args=class_args,
                ),
                name=func_name,
            ),
            args=func_args,
        ):
            for func in klass.defn.defs.body:
                if isinstance(func, Decorator):
                    func = func.func  # noqa: PLW2901

                elif not isinstance(func, FuncDef):
                    continue

                if func.name == func_name and (
                    func.is_class or func.is_static
                ):
                    class_name = klass.defn.name

                    class_args = "..." if class_args else ""  # type: ignore
                    func_args = "..." if func_args else ""  # type: ignore

                    old = f"{class_name}({class_args}).{func_name}({func_args})"  # noqa: E501
                    new = f"{class_name}.{func_name}({func_args})"

                    errors.append(
                        ErrorInfo.from_node(
                            node, f"Replace `{old}` with `{new}`"
                        )
                    )
