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


def extract_html_text(text: str) -> tuple[str, str]:
    """Extract clean article title and body from official health pages.
    
    Drops navigation, headers, footers, language pickers, cookie banners,
    institutional sections (WHO response, References, Related links), and social widgets.
    """
    # 1. Title from <h1> or <title>
    h1_m = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.DOTALL | re.IGNORECASE)
    if h1_m:
        title = html.unescape(re.sub(r"<[^>]+>", " ", h1_m.group(1))).strip()
    else:
        t_m = re.search(r"<title[^>]*>(.*?)</title>", text, re.DOTALL | re.IGNORECASE)
        title = html.unescape(re.sub(r"<[^>]+>", " ", t_m.group(1))).strip() if t_m else "Web page"
    title = re.sub(r"\s+", " ", title).strip() or "Web page"

    # 2. Extract article / main body container
    art_m = re.search(
        r'<article[^>]*class=["\'][^"\']*sf-detail-body-wrapper[^"\']*["\'][^>]*>(.*?)</article>',
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if art_m:
        body = art_m.group(1)
    else:
        main_m = re.search(r"<main[^>]*>(.*?)</main>", text, re.DOTALL | re.IGNORECASE)
        if main_m:
            body = main_m.group(1)
        else:
            art2_m = re.search(r"<article[^>]*>(.*?)</article>", text, re.DOTALL | re.IGNORECASE)
            body = art2_m.group(1) if art2_m else text

    # 3. Truncate at institutional response, References, or Related links
    body = re.split(r"(?:<[^>]+>\s*)*WHO\s+[Rr]esponse", body, flags=re.IGNORECASE)[0]
    body = re.split(
        r"(?:<[^>]+>\s*)*(?:<strong>)?\s*(?:References|Related\s+links|Further\s+information)",
        body,
        flags=re.IGNORECASE,
    )[0]

    # 4. Strip non-content and layout tags
    body = re.sub(
        r"<(?:script|style|nav|header|footer|aside|form|noscript|svg|button|select|option)[^>]*>.*?</(?:script|style|nav|header|footer|aside|form|noscript|svg|button|select|option)>",
        " ",
        body,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # 5. Strip divs/spans with noise classes
    body = re.sub(
        r'<[^>]+class=["\'][^"\']*(?:credit|share|social|author|date|cookie|language-selector|menu|breadcrumb)[^"\']*["\'][^>]*>.*?</[^>]+>',
        " ",
        body,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # 6. Convert block tags to newlines and unescape HTML
    body = re.sub(r"<(?:p|div|h[1-6]|li|tr|section|article)[^>]*>", "\n", body, flags=re.IGNORECASE)
    plain_text = html.unescape(re.sub(r"<[^>]+>", " ", body))

    # 7. Collect clean paragraphs, filtering out boilerplate phrases
    paragraphs = []
    for line in plain_text.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if not line:
            continue
        lower_line = line.lower()
        if any(noise in lower_line for noise in FORBIDDEN_BOILERPLATE):
            continue
        if any(lower_line.startswith(prefix) for prefix in ["reading time:", "credits:", "credits", "share", "print", "©"]):
            continue
        paragraphs.append(line)

    content = f"{title}\n\n" + "\n\n".join(paragraphs) if paragraphs else title
    return title, content


def load_html_paths(paths: list[Path]) -> list[Document]:
    documents: list[Document] = []
    for path in sorted(paths):
        heading, content = extract_html_text(path.read_text(encoding="utf-8"))
        if content:
            documents.append(
                Document(
                    page_content=content,
                    metadata={
                        "source": str(path),
                        "page": 0,
                        "page_label": heading,
                    },
                )
            )
    return documents
