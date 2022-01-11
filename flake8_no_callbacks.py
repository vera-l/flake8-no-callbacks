import ast
from typing import Any, Generator, List, Tuple, Type

VERSION = '0.0.1'

# Rules
NOC101 = 'NOC101 Callbacks are deprecated. Use coroutines instead.'

METHODS = {'get_url', 'post_url', 'put_url', 'delete_url'}


class Call(ast.Call):
    def __init__(self, orig: ast.Call) -> None:
        self.func = orig.func
        self.args = orig.args
        self.keywords = orig.keywords
        # For all ast.*:
        self.lineno = orig.lineno
        self.col_offset = orig.col_offset
        self.parent: ast.Expr = orig.parent  # type: ignore


def _has_callback_as_arg_or_keyword(node: ast.Call) -> bool:
    if len(node.args) > 9 and isinstance(node.args[9], ast.Name):
        return True

    for keyword in node.keywords:
        if keyword.arg == 'callback':
            return True

    return False


def _get_callback(node: Call) -> List[Tuple[int, int, str]]:
    """
    Find places where http-method() is called with a callback.

    self.get_url(host, data, callback=asd)

    Example AST
    -----------
    Call(
        func=Attribute(
            value=Name(id='self', ctx=Load()),
            attr='get_url',
            ctx=Load(),
        ),
        args=[],
        keywords=[
            keyword(
                arg='callback',
                value=Name(id='asd', ctx=Load()),
            ),
        ]
    )
    """
    errors: List[Tuple[int, int, str]] = []
    if (
        isinstance(node.func, ast.Attribute)
        and node.func.attr in METHODS
        and _has_callback_as_arg_or_keyword(node)
    ):
        errors.append((node.lineno, node.col_offset, NOC101))
    return errors


class Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: List[Tuple[int, int, str]] = []

    def visit_Call(self, node: ast.Call) -> Any:
        self.errors += _get_callback(Call(node))
        self.generic_visit(node)


class Plugin:
    name = __name__
    version = VERSION

    def __init__(self, tree: ast.AST):
        self._tree = tree

    def run(self) -> Generator[Tuple[int, int, str, Type[Any]], None, None]:
        visitor = Visitor()

        for node in ast.walk(self._tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        visitor.visit(self._tree)

        for line, col, msg in visitor.errors:
            yield line, col, msg, type(self)
