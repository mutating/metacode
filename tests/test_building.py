from ast import Name

import pytest
from full_match import match

from metacode import ParsedComment, build, insert


def test_run_build_with_wrong_key_or_action():
    """build(ParsedComment(...)) rejects invalid key and command identifiers as distinct validation failures."""
    with pytest.raises(ValueError, match=match('The key must be valid Python identifier.')):
        build(ParsedComment(
            key='123',
            command='action',
            arguments=[],
        ))

    with pytest.raises(ValueError, match=match('The command must be valid Python identifier.')):
        build(ParsedComment(
            key='key',
            command='123',
            arguments=[],
        ))


def test_build_ast():
    """build() rejects AST arguments instead of serializing arbitrary AST nodes."""
    with pytest.raises(TypeError, match=match('AST nodes are read-only and cannot be written to.')):
        build(ParsedComment(
            key='key',
            command='command',
            arguments=[Name()],
        ))


def test_create_simple_comment():
    """build() renders an empty-argument ParsedComment as '# key: command', omitting [] and using canonical spacing."""
    assert build(ParsedComment(
        key='key',
        command='command',
        arguments=[],
    )) == '# key: command'


def test_create_difficult_comment():
    """build() formats supported arguments in brackets, leaving identifier strings bare and quoting other strings."""
    assert build(ParsedComment(
        key='key',
        command='command',
        arguments=[1],
    )) == '# key: command[1]'

    assert build(ParsedComment(
        key='key',
        command='command',
        arguments=[1, 2, 3],
    )) == '# key: command[1, 2, 3]'

    assert build(ParsedComment(
        key='key',
        command='command',
        arguments=['build'],
    )) == '# key: command[build]'

    assert build(ParsedComment(
        key='key',
        command='command',
        arguments=['build', 'build'],
    )) == '# key: command[build, build]'

    assert build(ParsedComment(
        key='key',
        command='command',
        arguments=['lol-kek'],
    )) == "# key: command['lol-kek']"

    assert build(ParsedComment(
        key='key',
        command='command',
        arguments=['lol-kek', 'lol-kek-chedurek'],
    )) == "# key: command['lol-kek', 'lol-kek-chedurek']"

    assert build(ParsedComment(
        key='key',
        command='command',
        arguments=[...],
    )) == "# key: command[...]"

    assert build(ParsedComment(
        key='key',
        command='command',
        arguments=[..., ...],
    )) == "# key: command[..., ...]"

    assert build(ParsedComment(
        key='key',
        command='command',
        arguments=[1.5],
    )) == "# key: command[1.5]"

    assert build(ParsedComment(
        key='key',
        command='command',
        arguments=[1.5, 3.0],
    )) == "# key: command[1.5, 3.0]"

    assert build(ParsedComment(
        key='key',
        command='command',
        arguments=[5j],
    )) == "# key: command[5j]"

    assert build(ParsedComment(
        key='key',
        command='command',
        arguments=[None],
    )) == "# key: command[None]"

    assert build(ParsedComment(
        key='key',
        command='command',
        arguments=[True],
    )) == "# key: command[True]"

    assert build(ParsedComment(
        key='key',
        command='command',
        arguments=[False],
    )) == "# key: command[False]"

    assert build(ParsedComment(
        key='key',
        command='command',
        arguments=[1, 2, 3, 1.5, 3.0, 5j, 1000j, 'build', 'build2', 'lol-kek', 'lol-kek-chedurek', None, True, False, ...],
    )) == "# key: command[1, 2, 3, 1.5, 3.0, 5j, 1000j, build, build2, 'lol-kek', 'lol-kek-chedurek', None, True, False, ...]"


def test_insert_to_strange_comment():
    """insert() rejects existing text that does not start with '#', even when the new comment is invalid."""
    with pytest.raises(ValueError, match=match('The existing part of the comment should start with a #.')):
        insert(ParsedComment(key='key', command='command', arguments=[]), 'kek', at_end=True)

    with pytest.raises(ValueError, match=match('The existing part of the comment should start with a #.')):
        insert(ParsedComment(key=' key', command='command', arguments=[]), 'kek', at_end=True)

    with pytest.raises(ValueError, match=match('The existing part of the comment should start with a #.')):
        insert(ParsedComment(key=' key', command='command', arguments=[]), 'kek')

    with pytest.raises(ValueError, match=match('The existing part of the comment should start with a #.')):
        insert(ParsedComment(key='key', command='command', arguments=[]), 'kek')


def test_insert_at_begin_to_empty():
    """Default insert into empty input returns build(comment) directly."""
    comment = ParsedComment(
        key='key',
        command='command',
        arguments=['build'],
    )

    assert insert(comment, '') == build(comment)


def test_insert_at_end_to_empty():
    """Inserting with at_end=True into empty input returns build(comment) directly."""
    comment = ParsedComment(
        key='key',
        command='command',
        arguments=['build'],
    )

    assert insert(comment, '', at_end=True) == build(comment)


def test_insert_at_begin_to_not_empty():
    """Default insert prepends the built comment, trims leading whitespace, uses one separator, and does not deduplicate."""
    comment = ParsedComment(
        key='key',
        command='command',
        arguments=['build'],
    )

    assert insert(comment, '# kek') == build(comment) + ' # kek'
    assert insert(comment, ' # kek') == build(comment) + ' # kek'
    assert insert(comment, build(comment)) == build(comment) + ' ' + build(comment)


def test_insert_at_end_to_not_empty():
    """at_end=True appends metacode after existing comment text with one separator space and no deduplication."""
    comment = ParsedComment(
        key='key',
        command='command',
        arguments=['build'],
    )

    assert insert(comment, '# kek', at_end=True) == '# kek ' + build(comment)
    assert insert(comment, '# kek ', at_end=True) == '# kek ' + build(comment)
    assert insert(comment, build(comment), at_end=True) == build(comment) + ' ' + build(comment)
