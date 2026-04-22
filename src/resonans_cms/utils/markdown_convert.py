"""Convert Markdown to sanitized HTML and back for round-trip editing."""

from __future__ import annotations

import logging
import re

import markdown2
from bs4 import BeautifulSoup

from resonans_cms.utils.html_sanitize import sanitize_html

logger = logging.getLogger(__name__)

_MARKDOWN_EXTRAS = (
    "fenced-code-blocks",
    "tables",
    "strike",
    "cuddled-lists",
    "code-friendly",
    "break-on-newline",
)

_SIMPLE_CONTAINER_TAGS = frozenset({"p", "div", "br"})

_MARKDOWN_SOURCE_HINTS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?m)^#{1,6}\s"),
    re.compile(r"(?m)^\s{0,3}>\s"),
    re.compile(r"(?m)^\s*[-*+]\s"),
    re.compile(r"(?m)^\s*\d{1,4}[.)]\s"),
    re.compile(r"```"),
    re.compile(r"\[[^\]]+\]\([^)]+\)"),
    re.compile(r"\*\*[^*\n]+\*\*"),
    re.compile(r"__[^_\n]+__"),
    re.compile(r"(?m)^\s*\|.*\|\s*$"),
)

_MAX_HTML_TO_MARKDOWN_CHARS = 1_500_000


def markdown_to_html(markdown_src: str) -> str:
    """Parse Markdown to sanitized HTML."""
    text = markdown_src or ""
    if not text.strip():
        return ""
    html = markdown2.markdown(text, extras=list(_MARKDOWN_EXTRAS))
    return sanitize_html(html)


def _only_simple_containers(soup: BeautifulSoup) -> bool:
    for el in soup.find_all(True):
        name = (el.name or "").lower()
        if name not in _SIMPLE_CONTAINER_TAGS:
            return False
    return True


def _looks_like_markdown(raw: str) -> bool:
    return any(p.search(raw) for p in _MARKDOWN_SOURCE_HINTS)


def prepare_content_for_storage(raw: str) -> str:
    """Normalize input (Markdown or rich-editor HTML) into sanitized HTML."""
    raw = (raw or "").strip()
    if not raw:
        return ""
    if "<" not in raw:
        return markdown_to_html(raw)
    soup = BeautifulSoup(raw, "html.parser")
    if _looks_like_markdown(raw) and _only_simple_containers(soup):
        text = soup.get_text("\n\n").strip()
        return markdown_to_html(text or raw)
    return sanitize_html(raw)


def html_to_markdown(html: str) -> str:
    """Convert stored HTML back to Markdown for round-trip editing."""
    html = (html or "").strip()
    if not html:
        return ""
    if "<" not in html:
        return html
    if len(html) > _MAX_HTML_TO_MARKDOWN_CHARS:
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text("\n\n").strip()
    try:
        from markdownify import markdownify
    except ImportError:
        logger.warning("markdownify is not installed; returning plain text.")
        return BeautifulSoup(html, "html.parser").get_text("\n\n").strip()
    try:
        return (markdownify(html, heading_style="ATX", bullets="-") or "").strip()
    except Exception:
        logger.exception("html_to_markdown failed; using plain-text fallback.")
        return BeautifulSoup(html, "html.parser").get_text("\n\n").strip()
