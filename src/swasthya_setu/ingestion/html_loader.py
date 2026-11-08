"""Clean, dependency-free extractor for official HTML health pages."""

from __future__ import annotations

import html
import re
from pathlib import Path

from langchain_core.documents import Document

FORBIDDEN_BOILERPLATE = [
    "newsroom",
    "select language",
    "emergencies",
    "disease outbreak news",
    "member states",
    "cookie",
]


def _clean_plain_lines(text: str) -> list[str]:
    lines = []
    for raw in text.splitlines():
        line = re.sub(r"\s+", " ", raw).strip()
        if not line:
            continue
        lower_line = line.lower()
        if any(noise in lower_line for noise in FORBIDDEN_BOILERPLATE):
            continue
        if any(lower_line.startswith(p) for p in ["reading time:", "credits:", "credits", "share", "print", "©"]):
            continue
        lines.append(line)
    return lines


def extract_html_sections(raw_html: str) -> list[tuple[str, str]]:
    """Extract section-level chunks with (section_heading, section_text) from official HTML."""
    h1_m = re.search(r"<h1[^>]*>(.*?)</h1>", raw_html, re.DOTALL | re.IGNORECASE)
    if h1_m:
        title = html.unescape(re.sub(r"<[^>]+>", " ", h1_m.group(1))).strip()
    else:
        t_m = re.search(r"<title[^>]*>(.*?)</title>", raw_html, re.DOTALL | re.IGNORECASE)
        title = html.unescape(re.sub(r"<[^>]+>", " ", t_m.group(1))).strip() if t_m else "Web page"
    title = re.sub(r"\s+", " ", title).strip() or "Web page"

    art_m = re.search(
        r'<article[^>]*class=["\'][^"\']*sf-detail-body-wrapper[^"\']*["\'][^>]*>(.*?)</article>',
        raw_html,
        re.DOTALL | re.IGNORECASE,
    )
    if art_m:
        body = art_m.group(1)
    else:
        main_m = re.search(r"<main[^>]*>(.*?)</main>", raw_html, re.DOTALL | re.IGNORECASE)
        if main_m:
            body = main_m.group(1)
        else:
            art2_m = re.search(r"<article[^>]*>(.*?)</article>", raw_html, re.DOTALL | re.IGNORECASE)
            body = art2_m.group(1) if art2_m else raw_html

    # Truncate institutional and reference sections
    body = re.split(r"(?:<[^>]+>\s*)*WHO\s+[Rr]esponse", body, flags=re.IGNORECASE)[0]
    body = re.split(
        r"(?:<[^>]+>\s*)*(?:<strong>)?\s*(?:References|Related\s+links|Further\s+information)",
        body,
        flags=re.IGNORECASE,
    )[0]

    # Strip layout and boilerplate elements
    body = re.sub(
        r"<(?:script|style|nav|header|footer|aside|form|noscript|svg|button|select|option)[^>]*>.*?</(?:script|style|nav|header|footer|aside|form|noscript|svg|button|select|option)>",
        " ",
        body,
        flags=re.DOTALL | re.IGNORECASE,
    )
    body = re.sub(
        r'<[^>]+class=["\'][^"\']*(?:credit|share|social|author|date|cookie|language-selector|menu|breadcrumb)[^"\']*["\'][^>]*>.*?</[^>]+>',
        " ",
        body,
        flags=re.DOTALL | re.IGNORECASE,
    )

    heading_pattern = re.compile(r"(<h[2-3][^>]*>.*?</h[2-3]>)", re.IGNORECASE | re.DOTALL)
    parts = heading_pattern.split(body)

    sections: list[tuple[str, str]] = []
    current_heading = "Overview"

    for part in parts:
        part_clean = part.strip()
        if not part_clean:
            continue
        h_match = re.match(r"<h[2-3][^>]*>(.*?)</h[2-3]>", part_clean, re.IGNORECASE | re.DOTALL)
        if h_match:
            current_heading = html.unescape(re.sub(r"<[^>]+>", " ", h_match.group(1))).strip()
            current_heading = re.sub(r"\s+", " ", current_heading)
        else:
            b_text = re.sub(r"<(?:p|div|li|tr|section|article)[^>]*>", "\n", part_clean, flags=re.IGNORECASE)
            plain = html.unescape(re.sub(r"<[^>]+>", " ", b_text))
            lines = _clean_plain_lines(plain)
            if lines:
                sec_text = "\n\n".join(lines)
                heading_label = f"{title} > {current_heading}" if current_heading.lower() != title.lower() else title
                content = f"{title}\n\n{current_heading}\n\n{sec_text}"
                sections.append((heading_label, content))

    if not sections:
        b_text = re.sub(r"<(?:p|div|li|tr|section|article)[^>]*>", "\n", body, flags=re.IGNORECASE)
        plain = html.unescape(re.sub(r"<[^>]+>", " ", b_text))
        lines = _clean_plain_lines(plain)
        if lines:
            sections.append((title, f"{title}\n\n" + "\n\n".join(lines)))

    return sections


def extract_html_text(text: str) -> tuple[str, str]:
    """Backward-compatible whole-page extractor returning (title, full_content)."""
    sections = extract_html_sections(text)
    if not sections:
        return "Web page", ""
    title = sections[0][0].split(" > ")[0]
    full_body = "\n\n".join(c for _, c in sections)
    return title, full_body


def load_html_paths(paths: list[Path]) -> list[Document]:
    """Load HTML paths and produce section-level Document objects with section headings in page_label."""
    documents: list[Document] = []
    for path in sorted(paths):
        raw_text = path.read_text(encoding="utf-8")
        sections = extract_html_sections(raw_text)
        for idx, (section_label, section_content) in enumerate(sections):
            documents.append(
                Document(
                    page_content=section_content,
                    metadata={
                        "source": str(path),
                        "page": idx,
                        "page_label": section_label,
                    },
                )
            )
    return documents
