from ast import AST, BinOp, Index, Name, Subscript

import pytest
from full_match import match

from metacode import ParsedComment, UnknownArgumentTypeError, parse


def test_wrong_key():
    with pytest.raises(ValueError, match=match('The key must be valid Python identifier.')):
        parse('abc', '123')


def test_empty_string():
    assert parse('', 'kek') == []


def test_only_not_python_code():
    assert parse('run, Forest, run!', 'lol') == []
    assert parse('run, Forest, run! # kek!', 'lol') == []


def test_one_simplest_expression():
    assert parse('lol: kek', 'lol') == [ParsedComment(key='lol', command='kek', arguments=[])]
    assert parse('lol: kek', 'kek') == []


def test_expressions_with_not_python_code():
    assert parse('lol: kek # run, Forest, run!', 'lol') == [ParsedComment(key='lol', command='kek', arguments=[])]
    assert parse('run, Forest, run! #lol: kek', 'lol') == [ParsedComment(key='lol', command='kek', arguments=[])]
    assert parse('run, Forest, run! # lol: kek', 'lol') == [ParsedComment(key='lol', command='kek', arguments=[])]
    assert parse('run, Forest, run! # lol: kek # run, Forest, run!', 'lol') == [ParsedComment(key='lol', command='kek', arguments=[])]
    assert parse('run, Forest, run! #lol: kek# run, Forest, run!', 'lol') == [ParsedComment(key='lol', command='kek', arguments=[])]
    assert parse('run, Forest, run! #lol: kek[1, 2, 3]# run, Forest, run!', 'lol') == [ParsedComment(key='lol', command='kek', arguments=[1, 2, 3])]
    assert parse('run, Forest, run! #lol: kek[1, 2, 3]# run, Forest, run!#lol: kek', 'lol') == [ParsedComment(key='lol', command='kek', arguments=[1, 2, 3]), ParsedComment(key='lol', command='kek', arguments=[])]


def test_two_simplest_expressions_with_same_keys():
    assert parse('lol: kek # lol: kekokek', 'lol') == [ParsedComment(key='lol', command='kek', arguments=[]), ParsedComment(key='lol', command='kekokek', arguments=[])]
    assert parse('lol: kek # lol: kekokek', 'kek') == []


def test_one_difficult_expression():
    assert parse('lol: kek[a]', 'lol') == [ParsedComment(key='lol', command='kek', arguments=['a'])]
    assert parse('lol: kek[a, b, c]', 'lol') == [ParsedComment(key='lol', command='kek', arguments=['a', 'b', 'c'])]
    assert parse('lol: kek[a, b, "c"]', 'lol') == [ParsedComment(key='lol', command='kek', arguments=['a', 'b', 'c'])]
    assert parse('lol: kek["a", "b", "c"]', 'lol') == [ParsedComment(key='lol', command='kek', arguments=['a', 'b', 'c'])]
    assert parse('lol: kek["a", False, 111]', 'lol') == [ParsedComment(key='lol', command='kek', arguments=['a', False, 111])]
    assert parse('lol: kek[True, None, 111.5, 5j]', 'lol') == [ParsedComment(key='lol', command='kek', arguments=[True, None, 111.5, 5j])]
    assert parse('lol: kek[...]', 'lol') == [ParsedComment(key='lol', command='kek', arguments=[Ellipsis])]

    assert parse('lol: kek[a]', 'kek') == []


def test_parse_ast_complex_sum_argument_when_its_allowed():
    parsed_comments = parse('lol: kek[3 + 5j]', 'lol', allow_ast=True)

    assert len(parsed_comments) == 1

    parsed_comment = parsed_comments[0]

    assert parsed_comment.key == 'lol'
    assert parsed_comment.command == 'kek'
    assert len(parsed_comment.arguments) == 1

    ast_argument = parsed_comment.arguments[0]

    assert isinstance(ast_argument, AST)
    assert isinstance(ast_argument, BinOp)
    assert ast_argument.left.value == 3
    assert ast_argument.right.value == 5j


def test_parse_ast_subscription_argument_when_its_allowed():
    parsed_comments = parse('lol: kek[jej[ok]]', 'lol', allow_ast=True)

    assert len(parsed_comments) == 1

    parsed_comment = parsed_comments[0]

    assert parsed_comment.key == 'lol'
    assert parsed_comment.command == 'kek'
    assert len(parsed_comment.arguments) == 1

    ast_argument = parsed_comment.arguments[0]

    assert isinstance(ast_argument, AST)
    # TODO: delete this shit about Index if minimum supported version of Python is > 3.8 (we have the Index node only in old Pythons).
    assert isinstance(ast_argument, (Subscript, Index))
    if isinstance(ast_argument, Index):
        ast_argument = ast_argument.value
    assert ast_argument.value.id == 'jej'
    assert isinstance(ast_argument.slice, (Name, Index))
    if isinstance(ast_argument.slice, Index):
        assert ast_argument.slice.value.id == 'ok'
    else:
        assert ast_argument.slice.id == 'ok'


def test_parse_ast_complex_sum_argument_when_its_not_allowed():
    with pytest.raises(UnknownArgumentTypeError, match=match('An argument of unknown type was found in the comment \'lol: kek[3 + 5j]\'. If you want to process arbitrary code variants, not just constants, pass allow_ast=True.')):
        parse('lol: kek[3 + 5j]', 'lol')


def test_multiple_not_simple_expressions():
    assert parse('lol: kek[a] # lol: kek[a, b, c]', 'lol') == [ParsedComment(key='lol', command='kek', arguments=['a']), ParsedComment(key='lol', command='kek', arguments=['a', 'b', 'c'])]
    assert parse('lol: kek[a] # lol: kek', 'lol') == [ParsedComment(key='lol', command='kek', arguments=['a']), ParsedComment(key='lol', command='kek', arguments=[])]
    assert parse('lol: kek[a, b, c] # lol: kek', 'lol') == [ParsedComment(key='lol', command='kek', arguments=['a', 'b', 'c']), ParsedComment(key='lol', command='kek', arguments=[])]


def test_empty_subcomment():
    assert parse('kek! # #c[]: lel', 'lol') == []
    assert parse('kek! ##c[]: lel', 'lol') == []
    assert parse('##c[]: lel', 'lol') == []
    assert parse('#####################', 'lol') == []
    assert parse('# ###### ##### # ## #### ##', 'lol') == []
    assert parse('                                      # ###### ##### # ## #### ##', 'lol') == []
    assert parse('                                      # ###### ##### # ## #### ##lol: kek[a, b, c]', 'lol') == [ParsedComment(key='lol', command='kek', arguments=['a', 'b', 'c'])]


def test_sub_expressions_in_arguments():
    assert parse('lol: kek[a-b]', 'lol') == [ParsedComment(key='lol', command='kek', arguments=['a-b'])]


def test_plus_expressions_in_arguments():
    with pytest.raises(UnknownArgumentTypeError, match=match('An argument of unknown type was found in the comment \'lol: kek[a+b]\'. If you want to process arbitrary code variants, not just constants, pass allow_ast=True.')):
        parse('lol: kek[a+b]', 'lol')

    parsed_comments = parse('lol: kek[a+b]', 'lol', allow_ast=True)
    comment = parsed_comments[0]

    assert comment.key == 'lol'
    assert comment.command == 'kek'

    assert len(comment.arguments) == 1
    assert isinstance(comment.arguments[0], AST)


def test_triple_subs():
    with pytest.raises(UnknownArgumentTypeError, match=match('An argument of unknown type was found in the comment \'lol: kek[a-b-c]\'. If you want to process arbitrary code variants, not just constants, pass allow_ast=True.')):
        parse('lol: kek[a-b-c]', 'lol')

    parsed_comment = parse('lol: kek[a-b-c]', 'lol', allow_ast=True)[0]

    assert len(parsed_comment.arguments) == 1

    argument = parsed_comment.arguments[0]

    assert isinstance(argument, (BinOp, Index))
