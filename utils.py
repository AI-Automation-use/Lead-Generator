# import re
# from datetime import datetime

# def normalize_areas_string(areas_str: str) -> str:
#     if not isinstance(areas_str, str):
#         return ""
#     parts = areas_str.replace(';', ',').split(',')
#     cleaned = sorted(list(set(a.strip() for a in parts if a.strip())))
#     return ', '.join(cleaned)

# def markdown_bold_to_html(text: str) -> str:
#     return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

import re
from typing import List, Optional

def normalize_areas_string(areas_str: str) -> str:
    if not isinstance(areas_str, str):
        return ""
    parts = areas_str.replace(";", ",").split(",")
    cleaned_parts = sorted(list(set(area.strip() for area in parts if area.strip())))
    return ", ".join(cleaned_parts)


def _addr_list(emails: Optional[List[str]]) -> List[dict]:
    if not emails:
        return []
    return [{"emailAddress": {"address": e}} for e in emails]


def markdown_bold_to_html(text: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)