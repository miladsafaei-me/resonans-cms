"""Sanitize Markdown-derived and rich-editor HTML with nh3."""

from __future__ import annotations

import re
from copy import deepcopy
from functools import lru_cache

import nh3

_STYLE_PROPERTIES = frozenset(
    {
        "color",
        "background-color",
        "font-size",
        "font-family",
        "font-weight",
        "font-style",
        "text-align",
        "text-decoration",
        "width",
        "max-width",
        "height",
        "max-height",
        "line-height",
        "letter-spacing",
        "direction",
    }
)

_ALLOWED_A_REL = frozenset(
    {"nofollow", "noopener", "noreferrer", "sponsored", "ugc", "external"}
)

_LANG_CLASS = re.compile(r"^language-[a-z0-9#.+\-_]+$", re.IGNORECASE)
_HEADING_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{1,120}$")


def _class_token_allowed(token: str) -> bool:
    if token == "intent-target":
        return True
    if _LANG_CLASS.fullmatch(token):
        return True
    return False


@lru_cache(maxsize=1)
def _nh3_attributes() -> dict[str, set[str]]:
    attrs = deepcopy(nh3.ALLOWED_ATTRIBUTES)
    class_tags = (
        "p", "span", "div", "h1", "h2", "h3", "h4", "h5", "h6",
        "li", "ol", "ul", "blockquote", "pre", "code", "strong", "em",
        "b", "i", "u", "s", "a", "table", "td", "th",
    )
    for tag in class_tags:
        bucket = attrs.setdefault(tag, set())
        bucket.add("class")
    attrs.setdefault("a", set()).update({"class", "target", "rel"})
    attrs.setdefault("img", set()).update({"class"})
    for htag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        attrs.setdefault(htag, set()).add("id")
    return attrs


def _attribute_filter(tag: str, attr: str, value: str) -> str | None:
    if attr == "class" and value:
        parts = value.split()
        safe = [c for c in parts if _class_token_allowed(c)]
        return " ".join(safe) if safe else None
    if tag == "a" and attr == "target":
        return value if value in ("_blank", "_self") else None
    if tag == "a" and attr == "rel" and value:
        parts = [p.strip().lower() for p in value.split() if p.strip()]
        safe_rel = [p for p in parts if p in _ALLOWED_A_REL]
        return " ".join(safe_rel) if safe_rel else None
    if tag == "img" and attr == "src" and value.lower().startswith("data:"):
        head = value.split(",", 1)[0].lower()
        if "svg" in head:
            return None
        if any(m in head for m in ("image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp")):
            return value
        return None
    if tag in ("h1", "h2", "h3", "h4", "h5", "h6") and attr == "id" and value:
        vid = value.strip()
        if _HEADING_ID_RE.fullmatch(vid):
            return vid[:120]
        return None
    return value


def sanitize_html(html: str) -> str:
    """Return safe HTML fragment for storage and display."""
    if not html or not isinstance(html, str):
        return ""
    return nh3.clean(
        html,
        attributes=_nh3_attributes(),
        attribute_filter=_attribute_filter,
        link_rel=None,
        url_schemes={"http", "https", "mailto", "tel", "data"},
        filter_style_properties=_STYLE_PROPERTIES,
    )
