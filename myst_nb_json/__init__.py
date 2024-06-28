"""
MimeRenderPlugin for MyST-NB for rendering IPython JSON display type to HTML
"""

__all__ = ["JsonMimeRenderPlugin"]
__version__ = "0.1.1"

import json
from collections.abc import Generator, Mapping, Sequence
from functools import cached_property
from importlib.resources import files
from typing import Union, cast

from docutils import nodes
from myst_nb.core.render import MimeData, MimeRenderPlugin, NbElementRenderer

JAVASCRIPT_FILE_NAME = "myst-nb-json.js"
CSS_FILE_NAME = "myst-nb-json.css"
CLS_COLLAPSIBLE = "myst-nb-json-collapsible"
CLS_COLLAPSED = "myst-nb-json-collapsed"
CLS_HIDDEN = "myst-nb-json-hidden"
CLS_KEY = "myst-nb-json-key"
CLS_UNSELECTABLE = "myst-nb-json-unselectable"
CLS_VALUE = "myst-nb-json-value"

ScalarJsonType = Union[str, int, float, bool, None]

JsonType = Union[Mapping[str, "JsonType"], Sequence["JsonType"], ScalarJsonType]


class JsonMimeRenderPlugin(MimeRenderPlugin):
    mime_priority_overrides = [("*", "application/json", 1)]

    @staticmethod
    def handle_mime(
        renderer: NbElementRenderer, data: MimeData, inline: bool
    ) -> Union[None, list[nodes.Element]]:
        """
        A function that renders a mime type to docutils nodes, or returns None to reject

        Args:
            renderer: A class for rendering notebook elements
            data: The Notebook output data
            inline: Whether the MIME type is displayed inline, e.g. in an interactive Jupyter
                notebook. In the context of MyST-NB, content is rendered to a file, so the renderer
                should not accept inline content.

        Returns:
            A list of docutils nodes, or None if this renderer cannot handle the data
        """
        try:
            if not inline and data.mime_type == "application/json":
                root = data.output_metadata.get(data.mime_type, {}).get("root", "root")
                expanded = data.output_metadata.get(data.mime_type, {}).get("expanded", True)
                plugin = JsonMimeRenderPlugin()
                html = plugin.html(data.content, root=root, expanded=expanded)
                return [nodes.raw(text=html, format="html", classes=["output", "text_html"])]
        except Exception as e:
            import traceback

            print(e)
            traceback.print_exc()
        return None

    def html(self, jsonable: JsonType, root: str = "root", expanded: bool = False) -> str:
        """
        Generate an HTML string for a JSON object

        Args:
            jsonable: A JSON-like Python object
            root: Optional name to display as key for the JSON value
            expanded: Whether to initialize the JSON tree collapsed or expanded

        Returns:
            The component's HTML as string
        """
        return "".join(self.component(jsonable, root=root, expanded=expanded))

    def component(
        self, jsonable: JsonType, root: str = "root", expanded: bool = False
    ) -> Generator[str, None, None]:
        """
        Yield HTML fragment strings for a JSON object

        Args:
            jsonable: A JSON-like Python object
            root: Optional name to display as key for the JSON value
            expanded: Whether to initialize the JSON tree collapsed or expanded

        Yields:
            HTML strings
        """
        yield "<div>"
        yield f"""<div class="{CLS_VALUE}"><ul><li>"""
        yield from self.key(root, collapsible=is_nested(jsonable), selectable=False)
        yield from self.value(jsonable, expanded=expanded)
        yield "</li></ul></div>"
        yield self.style
        yield self.script
        yield "</div>"

    @cached_property
    def script(self) -> str:
        script_str = (files(__package__) / "resources" / JAVASCRIPT_FILE_NAME).read_text()
        return f"<script defer>{script_str}</script>"

    @cached_property
    def style(self) -> str:
        css_str = (files(__package__) / "resources" / CSS_FILE_NAME).read_text()
        return f"""<style>{css_str}</style>"""

    def value(
        self, value: JsonType, expanded: bool = False, with_comma: bool = False
    ) -> Generator[str, None, None]:
        if isinstance(value, Sequence) and not isinstance(value, str) and len(value) > 0:
            yield from self.list_value(value, expanded=expanded, with_comma=with_comma)
        elif isinstance(value, Mapping) and len(value) > 0:
            yield from self.dict_value(value, expanded=expanded, with_comma=with_comma)
        else:
            yield from self.scalar_value(cast(ScalarJsonType, value), with_comma=with_comma)

    def key(
        self, key: Union[str, int], collapsible: bool = False, selectable: bool = True
    ) -> Generator[str, None, None]:
        classes = CLS_KEY
        if collapsible:
            classes += " " + CLS_COLLAPSIBLE
        if not selectable:
            classes += " " + CLS_UNSELECTABLE
        yield f"""<span class="{classes}" tabindex=0>{self.quote}{key}{self.quote}{self.colon}</span>"""

    def list_value(
        self, value: Sequence, expanded: bool = False, with_comma: bool = False
    ) -> Generator[str, None, None]:
        yield f"""<div class="{CLS_VALUE}">{self.bracket_open}<ul>"""
        last_index = len(value) - 1
        for index, val in enumerate(value):
            is_last = index == last_index
            yield f"""<li class="{CLS_COLLAPSED if is_nested(val) and not expanded else ''}">"""
            # yield from self.key(index, collapsible=is_nested(val), selectable=False)
            yield from self.value(val, with_comma=not is_last)
            # It would be nicer to add the comma here, but if value yields a block element,
            # the comma would be an orphan in the next line below the value. To have it in the same
            # line, it needs to be inside the value's block.
            yield "</li>"
        yield f"</ul>{self.bracket_close}{self.comma if with_comma else ''}</div>"

    def dict_value(
        self, value: Mapping, expanded: bool = False, with_comma: bool = False
    ) -> Generator[str, None, None]:
        yield f"""<div class="{CLS_VALUE}">{self.curly_open}<ul>"""
        last_index = len(value.items()) - 1
        for index, (key, val) in enumerate(value.items()):
            is_last = index == last_index
            yield f"""<li class="{CLS_COLLAPSED if is_nested(val) and not expanded else ''}">"""
            yield from self.key(key, collapsible=is_nested(val))
            yield from self.value(val, with_comma=not is_last)
            # It would be nicer to add the comma here.
            yield "</li>"
        yield f"</ul>{self.curly_close}{self.comma if with_comma else ''}</div>"

    def scalar_value(
        self, value: ScalarJsonType, with_comma: bool = False
    ) -> Generator[str, None, None]:
        value_str = json.dumps(value)
        yield f"""<span class="{CLS_VALUE}">{value_str}</span>{self.comma if with_comma else ''}"""

    @cached_property
    def quote(self):
        return f"""<span class="{CLS_HIDDEN}">"</span>"""

    @cached_property
    def colon(self):
        return f"""<span class="{CLS_HIDDEN}">: </span>"""

    @cached_property
    def comma(self):
        return f"""<span class="{CLS_HIDDEN}">, </span>"""

    @cached_property
    def curly_open(self):
        return f"""<span class="{CLS_HIDDEN}">&lbrace;</span>"""

    @cached_property
    def curly_close(self):
        return f"""<span class="{CLS_HIDDEN}">&rbrace;</span>"""

    @cached_property
    def bracket_open(self):
        return f"""<span class="{CLS_HIDDEN}">&lbrack;</span>"""

    @cached_property
    def bracket_close(self):
        return f"""<span class="{CLS_HIDDEN}">&rbrack;</span>"""


def is_nested(jsonable: JsonType) -> bool:
    return (
        (isinstance(jsonable, Sequence) and not isinstance(jsonable, str))
        or isinstance(jsonable, Mapping)
    ) and len(jsonable) > 0
