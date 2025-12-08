from ast import AST, AnnAssign, BinOp, Constant, Index, Name, Sub, Subscript, Tuple
from ast import parse as ast_parse
from dataclasses import dataclass
from typing import Generator, List, Optional, Union

# TODO: delete this catch block and "type: ignore" if minimum supported version of Python is > 3.9.
try:
    from types import EllipsisType  # type: ignore[attr-defined, unused-ignore]
except ImportError:  # pragma: no cover
    EllipsisType = type(...)  # type: ignore[misc, unused-ignore]

from libcst import SimpleStatementLine
from libcst import parse_module as cst_parse

from metacode.errors import UnknownArgumentTypeError


@dataclass
class ParsedComment:
    key: str
    command: str
    arguments: List[Optional[Union[str, int, float, complex, bool, EllipsisType, AST]]]


def get_right_part(comment: str) -> str:
    return '#'.join(comment.split('#')[1:])


def get_commment_from_cst(comment: str) -> Optional[str]:
    comment = comment.lstrip()

    if not comment:
        return None

    module = cst_parse(comment)

    try:
        statement = next(s for s in module.body if isinstance(s, SimpleStatementLine))
    except StopIteration:
        return get_right_part(comment)

    trailing_whitespace = statement.trailing_whitespace
    comment_of_comment = trailing_whitespace.comment.value if trailing_whitespace.comment is not None else None

    if comment_of_comment is None:
        return get_right_part(comment)

    return comment_of_comment.lstrip("#").lstrip()


def get_candidates(comment: str) -> Generator[ParsedComment, None, None]:
    comment = comment.lstrip()
    try:
        parsed_ast = ast_parse(comment)
        if not (len(parsed_ast.body) != 1 or not isinstance(parsed_ast.body[0], AnnAssign) or not isinstance(parsed_ast.body[0].target, Name) or not isinstance(parsed_ast.body[0].annotation, (Name, Subscript))):

            assign = parsed_ast.body[0]
            key = assign.target.id  # type: ignore[union-attr]

            arguments: List[Optional[Union[str, int, float, complex, bool, EllipsisType, AST]]] = []
            if isinstance(assign.annotation, Name):
                command = assign.annotation.id

            else:

                command = assign.annotation.value.id  # type: ignore[attr-defined]

                if isinstance(assign.annotation.slice, Tuple):  # type: ignore[attr-defined]
                    slice_content = assign.annotation.slice.elts  # type: ignore[attr-defined]  # pragma: no cover
                # TODO: delete this branch if minimum supported version of Python is > 3.8 (we have the Index node only in old Pythons).
                # TODO: also delete this the pragmas here.
                elif isinstance(assign.annotation.slice, Index) and isinstance(assign.annotation.slice.value, Tuple):  # type: ignore[attr-defined]
                    slice_content = assign.annotation.slice.value.elts  # type: ignore[attr-defined]  # pragma: no cover
                else:
                    slice_content = [assign.annotation.slice]  # type: ignore[attr-defined]

                for argument in slice_content:
                    # TODO: delete this branch if minimum supported version of Python is > 3.8 (we have the Index node only in old Pythons).
                    if isinstance(argument, Index):  # pragma: no cover
                        argument = argument.value  # noqa: PLW2901
                    if isinstance(argument, Name):
                        arguments.append(argument.id)
                    elif isinstance(argument, Constant):
                        arguments.append(argument.value)
                    elif isinstance(argument, BinOp) and isinstance(argument.left, Name) and isinstance(argument.right, Name) and isinstance(argument.op, Sub):
                        arguments.append(f'{argument.left.id}-{argument.right.id}')
                    else:
                        arguments.append(argument)

            yield ParsedComment(
                key=key,
                command=command,
                arguments=arguments,
            )

        sub_comment = get_commment_from_cst(comment)
        if sub_comment is not None:
            yield from get_candidates(sub_comment)

    except SyntaxError:
        splitted_comment = comment.split('#')
        if len(splitted_comment) > 1:
            yield from get_candidates(get_right_part(comment))


def parse(comment: str, key: str, allow_ast: bool = False, ignore_case: bool = False) -> List[ParsedComment]:
    if not key.isidentifier():
        raise ValueError('The key must be valid Python identifier.')

    result: List[ParsedComment] = []

    comment = comment.lstrip()

    if not comment:
        return result

    for candidate in get_candidates(comment):
        if candidate.key == key or (candidate.key.lower() == key.lower() and ignore_case):
            for argument in candidate.arguments:
                if isinstance(argument, AST) and not allow_ast:
                    raise UnknownArgumentTypeError(f'An argument of unknown type was found in the comment {comment!r}. If you want to process arbitrary code variants, not just constants, pass allow_ast=True.')
            result.append(candidate)

    return result
