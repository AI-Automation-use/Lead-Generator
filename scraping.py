# # import logging
# # import sys
# # from urllib.parse import quote
# # from bs4 import BeautifulSoup
# # from playwright.sync_api import sync_playwright
# # import requests
# # import os
# # from typing import List, Tuple, Optional, Set

# # GNEWS_BASE_URL = "https://gnews.io/api/v4/search"
# # GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
# # GOOGLE_CSE_KEY = os.getenv("API_KEY")
# # GOOGLE_CSE_CX = os.getenv("CX")

# # def get_company_website(company_name: str, api_key: str, cx: str) -> Optional[str]:
# #     query = f"{company_name} company website"
# #     search_url = f"https://www.googleapis.com/customsearch/v1?q={quote(query)}&key={api_key}&cx={cx}"
# #     try:
# #         response = requests.get(search_url, verify=False, timeout=30)
# #         if response.status_code == 200:
# #             results = response.json()
# #             if 'items' in results:
# #                 return results['items'][0]['link']
# #     except Exception as e:
# #         logging.error(f"get_company_website error: {e}")
# #     return None

# # def fetch_full_article_text_with_playwright(page, url: str) -> str:
# #     try:
# #         page.goto(url, wait_until="domcontentloaded", timeout=60000)
# #         page.wait_for_timeout(3000)
# #         content = page.locator("body").inner_text()
# #         clean_text = content.strip().replace('\n', ' ').replace('\r', ' ')
# #         return clean_text[:10000] if clean_text else "⚠️ Full article not available."
# #     except Exception as e:
# #         logging.error(f"Error fetching full article from {url}: {e}")
# #         return "⚠️ Full article not available."


# # def scrape_google_news(company_name, pages=1):
# #     query = quote(str(company_name))
# #     results = []
# #     with sync_playwright() as p:
# #         try:
# #             # First, try to launch without specifying a path (ideal)
# #             browser = p.chromium.launch(headless=True)
# #         except Exception as e:
# #             # If that fails, assume local testing and try a common path
# #             # NOTE: You may need to adjust this path if your installation is different
# #             local_executable_path = "C:\\Users\\Vishnu.Kg\\OneDrive - Sonata Software\\Documents\\GENAI PROJECT\\Lead Generator Deploy\\.venv\\chromium_headless_shell-1181\\chrome-win\\headless_shell.exe"
# #             if sys.platform == "win32":
# #                 browser = p.chromium.launch(headless=True, executable_path=local_executable_path)
# #             else:
# #                 raise e # Re-raise if not on Windows
# #         context = browser.new_context(user_agent=(
# #             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
# #             "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
# #         ))
# #         page = context.new_page()
# #         for i in range(pages):
# #             start = i * 10
# #             url = f"https://www.google.com/search?q={query}&tbm=nws&start={start}"
# #             page.goto(url, wait_until="load", timeout=60000)
# #             soup = BeautifulSoup(page.content(), "html.parser")
# #             for result in soup.select("div.SoaBEf"):
# #                 try:
# #                     a_tag = result.find("a", href=True)
# #                     link = a_tag["href"] if a_tag else ""
# #                     title_el = a_tag.select_one("div.n0jPhd.ynAwRc.MBeuO.nDgy9d")
# #                     description_el = a_tag.select_one("div.GI74Re.nDgy9d")
# #                     publisher_el = a_tag.select_one("span.xQ82C.e8fRJf")
# #                     date_el = result.select_one("span[class]:not([class*='xQ82C'])")
# #                     title = title_el.get_text(strip=True) if title_el else ""
# #                     short_description = description_el.get_text(strip=True) if description_el else ""
# #                     publisher = publisher_el.get_text(strip=True) if publisher_el else ""
# #                     published_on = date_el.get_text(strip=True) if date_el else ""
# #                     full_article = fetch_full_article_text_with_playwright(page, link)
# #                     if title and link and not any(r["url"] == link for r in results):
# #                         results.append({
# #                             "title": title,
# #                             "publisher": publisher,
# #                             "published_on": published_on,
# #                             "description": full_article or short_description,
# #                             "url": link
# #                         })
# #                 except Exception:
# #                     continue
# #         browser.close()
# #     return results


# # def scrape_website(website):
# #     with sync_playwright() as p:
# #         BROWSER_EXECUTABLE_PATH = r"C:\Users\Vishnu.Kg\OneDrive - Sonata Software\Documents\GENAI PROJECT\Lead Generator Deploy\.venv\chromium_headless_shell-1181\chrome-win\headless_shell.exe"
# #         browser = p.chromium.launch(headless=True, executable_path= BROWSER_EXECUTABLE_PATH)
# #         context = browser.new_context(
# #             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
# #             ignore_https_errors=True
# #         )
# #         page = context.new_page()
# #         page.set_extra_http_headers({
# #             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
# #             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
# #             "Accept-Language": "en-US,en;q=0.9",
# #             "Connection": "keep-alive",
# #         })
# #         page.goto(website, wait_until="load", timeout=60000)
# #         page_content = page.content()
# #         soup = BeautifulSoup(page_content, 'html.parser')
# #         title = soup.title.string if soup.title else "No title found"
# #         paragraphs = soup.find_all('p')
# #         paragraphs_content = '\n'.join([para.get_text() for para in paragraphs])
# #         headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
# #         headings_content = '\n'.join([heading.get_text() for heading in headings])
# #         full_content = f"**Title:** {title}\n\n"
# #         full_content += f"**Headings:**\n{headings_content}\n\n"
# #         full_content += f"**Paragraphs:**\n{paragraphs_content}\n\n"
# #         full_content += f"\n\n**Source:** {website}"
# #         browser.close()
# #         return full_content, website




# import logging
# import sys
# from urllib.parse import quote
# from bs4 import BeautifulSoup
# from playwright.sync_api import sync_playwright
# import requests
# import os
# from typing import List, Tuple

# GNEWS_BASE_URL = "https://gnews.io/api/v4/search"
# GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
# GOOGLE_CSE_KEY = os.getenv("API_KEY")
# GOOGLE_CSE_CX = os.getenv("CX")

# def fetch_gnews_articles(company: str, frm: str, to: str) -> List[dict]:
#     results = []
#     if not GNEWS_API_KEY:
#         raise RuntimeError("GNEWS_API_KEY not configured")
#     try:
#         resp = requests.get(
#             GNEWS_BASE_URL,
#             params={"q": company, "from": frm, "to": to, "lang": "en", "token": GNEWS_API_KEY},
#             verify=False,
#             timeout=30
#         )
#         resp.raise_for_status()
#         for art in resp.json().get("articles", []):
#             results.append({
#                 "title": art.get("title", ""),
#                 "description": art.get("description", ""),
#                 "url": art.get("url", "")
#             })
#     except Exception as e:
#         logging.error(f"GNews API error: {e}")
#         raise
#     return results

# def fetch_full_article_text_with_playwright(page, url: str) -> str:
#     try:
#         page.goto(url, wait_until="domcontentloaded", timeout=60000)
#         page.wait_for_timeout(3000)
#         content = page.locator("body").inner_text()
#         return content.strip().replace('\n', ' ').replace('\r', ' ')[:10000]
#     except Exception as e:
#         logging.debug(f"Error fetching full article {url}: {e}")
#         return "⚠️ Full article not available."

# def scrape_google_news(company_name: str, pages: int = 1) -> List[dict]:
#     query = quote(str(company_name))
#     results = []
#     with sync_playwright() as p:
#         try:
#             browser = p.chromium.launch(headless=True)
#         except Exception:
#             # fallback executable path for Windows if necessary
#             if sys.platform == "win32":
#                 local_executable_path = r"C:\chromium_headless_shell\chrome-win\headless_shell.exe"
#                 browser = p.chromium.launch(headless=True, executable_path=local_executable_path)
#             else:
#                 raise
#         context = browser.new_context()
#         page = context.new_page()
#         for i in range(pages):
#             start = i * 10
#             url = f"https://www.google.com/search?q={query}&tbm=nws&start={start}"
#             page.goto(url, wait_until="load", timeout=60000)
#             soup = BeautifulSoup(page.content(), "html.parser")
#             for result in soup.select("div.SoaBEf"):
#                 try:
#                     a_tag = result.find("a", href=True)
#                     link = a_tag["href"] if a_tag else ""
#                     title_el = a_tag.select_one("div.n0jPhd.ynAwRc.MBeuO.nDgy9d") if a_tag else None
#                     description_el = a_tag.select_one("div.GI74Re.nDgy9d") if a_tag else None
#                     title = title_el.get_text(strip=True) if title_el else (a_tag.get_text(strip=True) if a_tag else "")
#                     short_description = description_el.get_text(strip=True) if description_el else ""
#                     full_article = fetch_full_article_text_with_playwright(page, link) if link else short_description
#                     if title and link and not any(r["url"] == link for r in results):
#                         results.append({
#                             "title": title,
#                             "description": full_article or short_description,
#                             "url": link
#                         })
#                 except Exception:
#                     continue
#         browser.close()
#     return results

# def scrape_website(website: str, executable_path: str | None = None) -> Tuple[str, str]:
#     # Uses Playwright to fetch the rendered page and parses text content
#     BROWSER_EXECUTABLE_PATH = executable_path
#     with sync_playwright() as p:
#         if BROWSER_EXECUTABLE_PATH:
#             browser = p.chromium.launch(headless=True, executable_path=BROWSER_EXECUTABLE_PATH)
#         else:
#             browser = p.chromium.launch(headless=True)
#         context = browser.new_context(ignore_https_errors=True)
#         page = context.new_page()
#         page.set_extra_http_headers({
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#         })
#         page.goto(website, wait_until="load", timeout=60000)
#         page_content = page.content()
#         soup = BeautifulSoup(page_content, 'html.parser')
#         title = soup.title.string if soup.title else "No title found"
#         paragraphs = soup.find_all('p')
#         paragraphs_content = '\n'.join([para.get_text() for para in paragraphs])
#         headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
#         headings_content = '\n'.join([h.get_text() for h in headings])
#         full_content = f"**Title:** {title}\n\n**Headings:**\n{headings_content}\n\n**Paragraphs:**\n{paragraphs_content}\n\n**Source:** {website}"
#         browser.close()
#         return full_content, website

# def get_company_website(company_name: str) -> str | None:
#     """
#     Simple fallback:
#     - If the input is already a URL, return it.
#     - Otherwise, try Google Custom Search if API key + cx provided.
#     - If not, return None.
#     """
#     if company_name.startswith("http://") or company_name.startswith("https://"):
#         return company_name
#     if GOOGLE_CSE_KEY and GOOGLE_CSE_CX:
#         try:
#             url = f"https://www.googleapis.com/customsearch/v1?q={quote(company_name + ' company website')}&key={GOOGLE_CSE_KEY}&cx={GOOGLE_CSE_CX}"
#             resp = requests.get(url, timeout=15, verify=False)
#             resp.raise_for_status()
#             j = resp.json()
#             if 'items' in j and j['items']:
#                 return j['items'][0].get('link')
#         except Exception as e:
#             logging.debug(f"Custom Search failed: {e}")
#     # no viable website found
#     return None

import logging
import sys
import requests
from urllib.parse import quote
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from typing import Optional

def fetch_full_article_text_with_playwright(page, url: str) -> str:
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)
        content = page.locator("body").inner_text()
        clean_text = content.strip().replace('\n', ' ').replace('\r', ' ')
        return clean_text[:10000] if clean_text else "⚠️ Full article not available."
    except Exception as e:
        logging.error(f"Error fetching full article from {url}: {e}")
        return "⚠️ Full article not available."


def scrape_google_news(company_name, pages=1):
    query = quote(str(company_name))
    results = []
    with sync_playwright() as p:
        try:
            # First, try to launch without specifying a path (ideal)
            browser = p.chromium.launch(headless=True)
        except Exception as e:
            # If that fails, assume local testing and try a common path
            # NOTE: You may need to adjust this path if your installation is different
            local_executable_path = "C:\\Users\\Vishnu.Kg\\OneDrive - Sonata Software\\Documents\\GENAI PROJECT\\Lead Generator Deploy\\.venv\\chromium_headless_shell-1181\\chrome-win\\headless_shell.exe"
            if sys.platform == "win32":
                browser = p.chromium.launch(headless=True, executable_path=local_executable_path)
            else:
                raise e # Re-raise if not on Windows
        context = browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        ))
        page = context.new_page()
        for i in range(pages):
            start = i * 10
            url = f"https://www.google.com/search?q={query}&tbm=nws&start={start}"
            page.goto(url, wait_until="load", timeout=60000)
            soup = BeautifulSoup(page.content(), "html.parser")
            for result in soup.select("div.SoaBEf"):
                try:
                    a_tag = result.find("a", href=True)
                    link = a_tag["href"] if a_tag else ""
                    title_el = a_tag.select_one("div.n0jPhd.ynAwRc.MBeuO.nDgy9d")
                    description_el = a_tag.select_one("div.GI74Re.nDgy9d")
                    publisher_el = a_tag.select_one("span.xQ82C.e8fRJf")
                    date_el = result.select_one("span[class]:not([class*='xQ82C'])")
                    title = title_el.get_text(strip=True) if title_el else ""
                    short_description = description_el.get_text(strip=True) if description_el else ""
                    publisher = publisher_el.get_text(strip=True) if publisher_el else ""
                    published_on = date_el.get_text(strip=True) if date_el else ""
                    full_article = fetch_full_article_text_with_playwright(page, link)
                    if title and link and not any(r["url"] == link for r in results):
                        results.append({
                            "title": title,
                            "publisher": publisher,
                            "published_on": published_on,
                            "description": full_article or short_description,
                            "url": link
                        })
                except Exception:
                    continue
        browser.close()
    return results


def scrape_website(website):
    with sync_playwright() as p:
        BROWSER_EXECUTABLE_PATH = r"C:\Users\Vishnu.Kg\OneDrive - Sonata Software\Documents\GENAI PROJECT\Lead Generator Deploy\.venv\chromium_headless_shell-1181\chrome-win\headless_shell.exe"
        browser = p.chromium.launch(headless=True, executable_path= BROWSER_EXECUTABLE_PATH)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            ignore_https_errors=True
        )
        page = context.new_page()
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        })
        page.goto(website, wait_until="load", timeout=60000)
        page_content = page.content()
        soup = BeautifulSoup(page_content, 'html.parser')
        title = soup.title.string if soup.title else "No title found"
        paragraphs = soup.find_all('p')
        paragraphs_content = '\n'.join([para.get_text() for para in paragraphs])
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        headings_content = '\n'.join([heading.get_text() for heading in headings])
        full_content = f"**Title:** {title}\n\n"
        full_content += f"**Headings:**\n{headings_content}\n\n"
        full_content += f"**Paragraphs:**\n{paragraphs_content}\n\n"
        full_content += f"\n\n**Source:** {website}"
        browser.close()
        return full_content, website

# -----------------------------
# Search helpers
# -----------------------------

def get_company_website(company_name: str, api_key: str, cx: str) -> Optional[str]:
    query = f"{company_name} company website"
    search_url = f"https://www.googleapis.com/customsearch/v1?q={quote(query)}&key={api_key}&cx={cx}"
    try:
        response = requests.get(search_url, verify=False, timeout=30)
        if response.status_code == 200:
            results = response.json()
            if 'items' in results:
                return results['items'][0]['link']
    except Exception as e:
        logging.error(f"get_company_website error: {e}")
    return None
