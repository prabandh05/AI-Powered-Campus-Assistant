import argparse
from collections import deque
from typing import List, Set

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urldefrag, urlparse


def _normalize_url(url: str) -> str:
    """Remove URL fragments for consistent comparison."""
    clean, _ = urldefrag(url)
    return clean


def _is_same_domain(url: str, base_netloc: str) -> bool:
    parsed = urlparse(url)
    if not parsed.netloc:
        return True
    return parsed.netloc == base_netloc


def extract_visible_text(html: str) -> str:
    """Extract cleaned visible text from an HTML document."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove non-content elements
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    # Drop empty lines and very short noise lines
    lines = [line for line in lines if len(line) > 0]
    return "\n".join(lines)


def crawl_website(
    base_url: str,
    max_pages: int = 50,
    timeout: int = 10,
) -> List[str]:
    """
    Crawl a website starting from base_url, limited to internal links.

    Returns a list of cleaned page texts.
    """
    visited: Set[str] = set()
    queue: deque[str] = deque()
    queue.append(base_url)

    base_netloc = urlparse(base_url).netloc
    pages_text: List[str] = []

    while queue and len(visited) < max_pages:
        url = _normalize_url(queue.popleft())
        if url in visited:
            continue
        visited.add(url)

        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
        except requests.RequestException:
            # Skip pages that error out
            continue

        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            # Ignore non-HTML content (PDFs, images, etc.) for this MVP
            continue

        pages_text.append(extract_visible_text(response.text))

        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            absolute_url = urljoin(url, href)
            absolute_url = _normalize_url(absolute_url)

            if absolute_url.startswith(("mailto:", "tel:")):
                continue
            if not absolute_url.startswith("http"):
                continue
            if not _is_same_domain(absolute_url, base_netloc):
                continue
            if absolute_url not in visited:
                queue.append(absolute_url)

    return pages_text


def save_crawled_text(pages_text: List[str], output_path: str) -> None:
    """Save all crawled page texts into a single text file."""
    from pathlib import Path

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as f:
        for i, page in enumerate(pages_text):
            f.write(page)
            if i != len(pages_text) - 1:
                f.write("\n\n" + "=" * 80 + "\n\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Crawl an official college website and save cleaned text for the RAG pipeline."
    )
    parser.add_argument(
        "--base-url",
        required=True,
        help="Base URL of the college website to crawl (e.g., https://www.examplecollege.edu)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=50,
        help="Maximum number of pages to crawl (default: 50)",
    )
    parser.add_argument(
        "--output",
        default="data/website_text.txt",
        help="Path to output text file (default: data/website_text.txt)",
    )

    args = parser.parse_args()

    pages_text = crawl_website(args.base_url, max_pages=args.max_pages)
    save_crawled_text(pages_text, args.output)


if __name__ == "__main__":
    main()

