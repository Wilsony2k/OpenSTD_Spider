"""Parser for std.samr.gov.cn JS-rendered standard detail pages.

Extracts the adoption relation field (采标关系) that is only available
on this portal and not on openstd.samr.gov.cn.
"""

import re


def parse_adoption_relation(page_text: str) -> str | None:
    """Extract 采标关系 (adoption relation) from the full page text.

    The page is JS-rendered, so we search the visible text content
    for the pattern. Examples:
        '采标关系   修改  IEC 61133:1992'
        '采标关系   等同  ISO 9001:2015'
    """
    # Pattern 1: "采标关系" followed by text in the same td/row
    m = re.search(r'采标关系[：:]\s*([^\n]{1,80})', page_text)
    if m:
        return m.group(1).strip()

    # Pattern 2: row label and value in separate elements
    m = re.search(r'采标关系\s*\n\s*([^\n]{1,80})', page_text)
    if m:
        return m.group(1).strip()

    # Pattern 3: find "采标关系" then grab the next significant text
    idx = page_text.find("采标关系")
    if idx >= 0:
        after = page_text[idx + 4:idx + 120]
        # Remove HTML tags
        after = re.sub(r'<[^>]+>', '', after)
        # Clean up whitespace
        after = re.sub(r'\s+', ' ', after).strip()
        # Extract the first meaningful segment (before the next field label)
        for sep in ['废止', '现行', '即将实施', '发布', '实施', '国际标准']:
            sep_idx = after.find(sep)
            if sep_idx > 5:
                after = after[:sep_idx]
                break
        return after.strip() if after else None

    return None


def extract_details_from_rendered_page(page_text: str) -> dict:
    """Extract all available detail fields from rendered page text.

    Returns a dict with fields found, for merging into StdMetaFull.
    """
    result = {}

    adoption_relation = parse_adoption_relation(page_text)
    if adoption_relation:
        result["adoption_relation"] = adoption_relation

    return result
