import re

import pytest

from myst_nb_json import JsonMimeRenderPlugin


@pytest.fixture
def plugin() -> JsonMimeRenderPlugin:
    return JsonMimeRenderPlugin()


def _strip_xml_attributes(string: str) -> str:
    return re.sub(pattern=r"<(?P<tag>\w+)(?:\s+[^>]*)>", repl=r"<\g<tag>>", string=string)


def _strip_xml_whitespace(string: str) -> str:
    return re.sub(pattern=r">\s+<", repl="><", string=string)


def _strip_xml_tags(string: str) -> str:
    return re.sub(pattern=r"<\/?\w+[^>]*>", repl="", string=string)


CHAR_to_HTML_ENTITY = {
    ">": "&gt;",
    "<": "&lt;",
    "&": "&amp;",
    # These also cause problems, although they should not strictly need escaping
    "[": "&lbrack;",
    "]": "&rbrack;",
    "{": "&lbrace;",
    "}": "&rbrace;",
    '"': "&quot;",
    # Hash (in CSS color) causes problems for Selenium Chrome webdriver
    "#": "&num;",
}
HTML_ENTITY_TO_CHAR = {v: k for k, v in CHAR_to_HTML_ENTITY.items()}


def _html_unescape(string: str) -> str:
    return re.sub(
        pattern=r"&\w+;",
        repl=lambda m: HTML_ENTITY_TO_CHAR.get(m.group(), m.group()),
        string=string,
    )


@pytest.mark.parametrize(
    ("value", "expected_xml"),
    [
        ("abc", '<span>"abc"</span>'),
        (42, "<span>42</span>"),
        (3.14, "<span>3.14</span>"),
        (True, "<span>true</span>"),
        (False, "<span>false</span>"),
        (None, "<span>null</span>"),
    ],
)
def test_scalar_value(plugin: JsonMimeRenderPlugin, value, expected_xml: str):
    actual = "".join(plugin.scalar_value(value))
    # It should produce the expected HTML structure
    assert _strip_xml_whitespace(_strip_xml_attributes(actual)) == expected_xml


@pytest.mark.parametrize(
    ("value", "expected_xml", "expected_text"),
    [
        ([], "<div><span>&lbrack;</span><ul></ul><span>&rbrack;</span></div>", "[]"),
        (
            ["a", "b"],
            '<div><span>&lbrack;</span><ul><li><span>"a"</span><span>, </span></li><li><span>"b"</span></li></ul><span>&rbrack;</span></div>',
            '["a", "b"]',
        ),
    ],
)
def test_list_value(plugin: JsonMimeRenderPlugin, value, expected_xml: str, expected_text: str):
    actual = "".join(plugin.list_value(value))
    # It should produce the expected HTML structure
    assert _strip_xml_whitespace(_strip_xml_attributes(actual)) == expected_xml
    # It should preserve JSON syntax as user-electable text (even if brackets are not displayed)
    assert _html_unescape(_strip_xml_tags(actual)) == expected_text


@pytest.mark.parametrize(
    ("value", "expected_xml", "expected_text"),
    [
        ({}, "<div><span>&lbrace;</span><ul></ul><span>&rbrace;</span></div>", "{}"),
        (
            {"k1": "v1", "k2": "v2"},
            '<div><span>&lbrace;</span><ul><li><span><span>"</span>k1<span>"</span><span>: </span></span><span>"v1"</span><span>, </span></li><li><span><span>"</span>k2<span>"</span><span>: </span></span><span>"v2"</span></li></ul><span>&rbrace;</span></div>',
            '{"k1": "v1", "k2": "v2"}',
        ),
    ],
)
def test_dict_value(plugin: JsonMimeRenderPlugin, value, expected_xml: str, expected_text: str):
    actual = "".join(plugin.dict_value(value))
    # It should produce the expected HTML structure
    assert _strip_xml_whitespace(_strip_xml_attributes(actual)) == expected_xml
    # It should preserve JSON syntax as user-electable text (even if braces and quotes are not displayed)
    assert _html_unescape(_strip_xml_tags(actual)) == expected_text
