"""
Inject internal links into HTML content based on keyword → URL mappings.

Given a list of ``(phrase, url)`` tuples (or dicts with ``keywords`` and ``url`` fields),
replaces the first occurrence of each phrase in visible text with an ``<a>`` tag.
Does not touch text inside ``<a>``, ``<code>``, ``<pre>``, or heading tags.
"""

from __future__ import annotations

import re
from typing import Iterable

from bs4 import BeautifulSoup, NavigableString

_SKIP_PARENTS = frozenset({"a", "code", "pre", "script", "style", "h1", "h2", "h3", "h4", "h5", "h6"})


def apply_auto_links(html: str, intents: Iterable[dict]) -> str:
    """
    Args:
        html: Source HTML fragment.
        intents: Iterable of ``{"url": str, "keywords": [str, ...]}`` dicts.
            Each unique URL gets at most one link injection per document.

    Returns:
        HTML with internal links injected.
    """
    if not html or not html.strip():
        return html or ""

    mapping: list[tuple[re.Pattern, str]] = []
    seen_urls: set[str] = set()
    for intent in intents:
        url = (intent.get("url") or "").strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        for phrase in intent.get("keywords") or []:
            term = (phrase or "").strip()
            if not term:
                continue
            pattern = re.compile(
                r"(?<![\w/>])" + re.escape(term) + r"(?![\w<])",
                re.IGNORECASE,
            )
            mapping.append((pattern, url))

    if not mapping:
        return html

    soup = BeautifulSoup(html, "html.parser")
    linked_urls: set[str] = set()

    for text_node in list(soup.find_all(string=True)):
        parent = text_node.parent
        if parent is None:
            continue
        parent_chain = [p.name for p in parent.parents if p.name]
        if (parent.name or "").lower() in _SKIP_PARENTS:
            continue
        if any(name.lower() in _SKIP_PARENTS for name in parent_chain):
            continue
        text = str(text_node)
        for pattern, url in mapping:
            if url in linked_urls:
                continue
            match = pattern.search(text)
            if not match:
                continue
            before = text[: match.start()]
            after = text[match.end():]
            matched_text = match.group(0)
            new_link = soup.new_tag("a", href=url)
            new_link["class"] = "intent-target"
            new_link.string = matched_text
            fragments: list = []
            if before:
                fragments.append(NavigableString(before))
            fragments.append(new_link)
            if after:
                fragments.append(NavigableString(after))
            text_node.replace_with(*fragments)
            linked_urls.add(url)
            break

    return str(soup)
