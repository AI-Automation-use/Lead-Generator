# # import logging
# # import re
# # from datetime import datetime, timedelta
# # from typing import List
# # from utils import normalize_areas_string, markdown_bold_to_html
# # from storage import get_identified_leads_df, add_lead_to_excel
# # from scraping import get_company_website, scrape_website, scrape_google_news
# # from ai import check_potential_lead, extract_lead_details, check_potential_lead_by_area, extract_single_lead_details
# # from docs import create_lead_docx
# # from auth import get_access_token, send_email_app_only, send_lead_data_to_api

# # GNEWS_LOOKBACK_DAYS = 30


# # def process_company_pipeline(company: str, my_account_name: str, my_lead_name: str, pages: int = 1) -> None:
# #     logging.info(f"🕒 Processing pipeline for: {company}")
# #     # 1. GNews Fetch (last 30 days)
# #     today = datetime.utcnow()
# #     frm = (today - timedelta(days=30)).strftime("%Y-%m-%d")
# #     to = today.strftime("%Y-%m-%d")
# #     news_results = []
# #     try:
# #         resp = requests.get(BASE_URL, params={"q": company, "from": frm, "to": to, "lang": "en", "token": GNEWS_API_KEY}, verify=False, timeout=30)
# #         resp.raise_for_status()
# #         for art in resp.json().get("articles", []):
# #             news_results.append({"title": art.get("title", ""), "description": art.get("description", ""), "url": art.get("url", "")})
# #         logging.info(f"✅ GNews API returned {len(news_results)} articles.")
# #     except Exception as e:
# #         logging.error(f"❌ GNews API error: {e}")

# #     # 2. Google News Scrape
# #     try:
# #         google_news_results = scrape_google_news(company, pages)
# #         logging.info(f"✅ Google News scrape found {len(google_news_results)} articles.")
# #     except Exception as e:
# #         logging.error(f"❌ Google News scraping error: {e}")
# #         google_news_results = []

# #     all_news = news_results + google_news_results
# #     if not all_news:
# #         logging.warning("⚠️ No news results found; skipping.")
# #         return
# #     news_content = "\n\n".join(f"**Title:** {n['title']}\n**Description:** {n['description']}\n**URL:** {n['url']}" for n in all_news)

# #     # 3. Website Scraping
# #     website = get_company_website(company, API_KEY, CX)
# #     if not website:
# #         logging.error(f"❌ Could not find website for {company}.")
# #         return
# #     try:
# #         website_content, _ = scrape_website(website)
# #         logging.info("✅ Website scraped successfully.")
# #     except Exception as e:
# #         logging.error(f"❌ Website scraping error: {e}")
# #         return

# #     # 4. LinkedIn Scraping
# #     linkedin_url = get_company_website(company + " LinkedIn", API_KEY, CX)
# #     if not linkedin_url:
# #         logging.error(f"❌ Could not find LinkedIn profile for {company}.")
# #         return
# #     try:
# #         linkedin_content, _ = scrape_website(linkedin_url)
# #         logging.info("✅ LinkedIn scraped successfully.")
# #     except Exception as e:
# #         logging.error(f"❌ LinkedIn scraping error: {e}")
# #         return

# #     # 5. AI Lead Check
# #     try:
# #         lead_analysis, potential_lead_check = check_potential_lead(website_content, linkedin_content, news_content)
# #         logging.info("✅ Lead analysis complete.")
# #     except Exception as e:
# #         logging.error(f"❌ OpenAI analysis error: {e}")
# #         return

# #     logging.info(f"🔍 Is '{company}' a potential lead? → {potential_lead_check}")
# #     if potential_lead_check.strip().lower() != "yes":
# #         logging.info(f"🚫 '{company}' is not identified as a potential lead; skipping all downstream steps.")
# #         return

# #     # Extract lead areas
# #     try:
# #         combined_details = extract_lead_details(lead_analysis, company)
# #         logging.info(f"🔍 Raw AI output for lead areas: \n{combined_details}")
# #     except Exception as e:
# #         logging.error(f"❌ Failed to extract lead details from initial analysis: {e}")
# #         return

# #     all_lead_areas_list = []
# #     m = re.search(r"\*\*Lead Identification Area\*\*: (.+)", combined_details)
# #     if m:
# #         all_lead_areas_str = m.group(1).strip()
# #         if all_lead_areas_str.lower() != "not available":
# #             all_lead_areas_list = [area.strip() for area in all_lead_areas_str.split(',') if area.strip()]
# #     if not all_lead_areas_list:
# #         logging.info("📝 The broad analysis did not identify any specific lead areas.")
# #         return

# #     df = get_identified_leads_df()
# #     existing_company_row = df[df["Company Name"] == company]
# #     if not existing_company_row.empty:
# #         existing_areas_str = existing_company_row["Lead Identification Areas"].iloc[0]
# #         existing_areas_set = set(normalize_areas_string(existing_areas_str).split(', ') if existing_areas_str else set())
# #         truly_new_areas_to_process = [area for area in all_lead_areas_list if area not in existing_areas_set]
# #         if not truly_new_areas_to_process:
# #             logging.info(f"📝 All identified areas for '{company}' are already in the Excel file. Skipping targeted analysis.")
# #             return
# #     else:
# #         truly_new_areas_to_process = all_lead_areas_list

# #     logging.info(f"✅ Found {len(truly_new_areas_to_process)} truly new areas to process: {truly_new_areas_to_process}")

# #     for lead_area in truly_new_areas_to_process:
# #         logging.info(f"🔄 Re-analyzing content for specific new area: '{lead_area}'")
# #         try:
# #             area_analysis, area_potential_check = check_potential_lead_by_area(lead_area, website_content, linkedin_content, news_content)
# #             if area_potential_check.strip().lower() == "yes":
# #                 area_details = extract_single_lead_details(area_analysis, company)
# #                 email_flag = add_lead_to_excel(company, lead_area)
# #                 if email_flag:
# #                     logging.info("✅ Excel updated successfully.")
# #                     lead_doc_name, lead_doc_stream = create_lead_docx(area_analysis, company)
# #                     lead_doc_bytes = lead_doc_stream.getvalue()
# #                     logging.info("📄 DOCX files generated.")
# #                     try:
# #                         sender_email = "So_App_Support@sonata-software.com"
# #                         email_body = (
# #                             f"<html><body><p>A new potential lead has been identified for <strong>{company}</strong> in the area of <strong>{lead_area}</strong>.</p>"
# #                             + "".join(f"<p>{markdown_bold_to_html(line)}</p>" for line in area_details.splitlines())
# #                             + "<p>See attachments for full reports.</p></body></html>"
# #                         )
# #                         sent = send_email_app_only(
# #                             sender_email,
# #                             ["vishnu.kg@sonata-software.com"],
# #                             f"New Lead: {company} - {lead_area}",
# #                             email_body,
# #                             cc_emails=["vishnu.kg@sonata-software.com"],
# #                             attachments=[(lead_doc_name, lead_doc_stream)],
# #                         )
# #                         # if sent:
# #                         #     logging.info(f"✅ Email sent for area: '{lead_area}'")
# #                         #     send_lead_data_to_api(lead_area, my_account_name, my_lead_name, lead_doc_name, lead_doc_bytes)
# #                         #     logging.info(f"📨 Lead data posted to external API for area: '{lead_area}'")
# #                         # else:
# #                         #     logging.warning(f"⚠️ Email not sent for area: '{lead_area}'")
# #                     except Exception as e:
# #                         logging.error(f"❌ Error when attempting to send email/API for area '{lead_area}': {e}")
# #                 else:
# #                     logging.info(f"🚫 No truly new areas were added to Excel for '{company}' - skipping email/API.")
# #             else:
# #                 logging.info(f"🚫 No lead indication found for area '{lead_area}'; skipping email and API steps.")
# #         except Exception as e:
# #             logging.error(f"❌ Error processing lead area '{lead_area}': {e}")

# #     logging.info("✅ Lead generation cycle completed.")







# import logging
# import re
# import os
# from datetime import datetime, timedelta
# from typing import List

# from utils import normalize_areas_string, markdown_bold_to_html
# from storage import get_identified_leads_df, add_lead_to_excel
# from scraping import get_company_website, scrape_website, scrape_google_news, fetch_gnews_articles
# from ai import check_potential_lead, extract_lead_details, check_potential_lead_by_area, extract_single_lead_details
# from docs import create_lead_docx
# from auth import send_email_app_only, send_lead_data_to_api

# GNEWS_LOOKBACK_DAYS = 30

# def process_company_pipeline(company: str, my_account_name: str, my_lead_name: str, pages: int = 1) -> None:
#     if not company:
#         logging.error("No company specified — skipping.")
#         return

#     logging.info(f"🕒 Processing pipeline for: {company}")

#     # 1. News (GNews API + Google News scrape)
#     today = datetime.utcnow()
#     frm = (today - timedelta(days=GNEWS_LOOKBACK_DAYS)).strftime("%Y-%m-%d")
#     to = today.strftime("%Y-%m-%d")
#     news_results = []
#     try:
#         news_results = fetch_gnews_articles(company, frm, to)
#         logging.info(f"✅ GNews API returned {len(news_results)} articles.")
#     except Exception as e:
#         logging.debug(f"GNews fetch failed or not configured: {e}")

#     google_news_results = []
#     try:
#         google_news_results = scrape_google_news(company, pages)
#         logging.info(f"✅ Google News scrape found {len(google_news_results)} articles.")
#     except Exception as e:
#         logging.warning(f"Google News scraping failed — continuing with available results: {e}")

#     all_news = news_results + google_news_results
#     if not all_news:
#         logging.warning("No news results found; skipping.")
#         return

#     news_content = "\n\n".join(
#         f"**Title:** {n.get('title','')}\n**Description:** {n.get('description','')}\n**URL:** {n.get('url','')}"
#         for n in all_news
#     )

#     # 2. Website scraping
#     website = get_company_website(company)
#     if not website:
#         logging.error(f"Could not find website for {company}.")
#         return
#     try:
#         website_content, _ = scrape_website(website)
#         logging.info("✅ Website scraped successfully.")
#     except Exception as e:
#         logging.error(f"Website scraping error: {e}")
#         return

#     # 3. LinkedIn scraping (search via company + "LinkedIn")
#     linkedin_url = get_company_website(company + " LinkedIn")
#     if not linkedin_url:
#         logging.error(f"Could not find LinkedIn profile for {company}.")
#         return
#     try:
#         linkedin_content, _ = scrape_website(linkedin_url)
#         logging.info("✅ LinkedIn scraped successfully.")
#     except Exception as e:
#         logging.error(f"LinkedIn scraping error: {e}")
#         return

#     # 4. AI lead check
#     try:
#         lead_analysis, potential_lead_check = check_potential_lead(website_content, linkedin_content, news_content)
#         logging.info("✅ Lead analysis complete.")
#     except Exception as e:
#         logging.error(f"OpenAI analysis error: {e}")
#         return

#     logging.info(f"🔍 Is '{company}' a potential lead? → {potential_lead_check}")
#     if potential_lead_check.strip().lower() != "yes":
#         logging.info(f"'{company}' is not a potential lead; skipping.")
#         return

#     # Extract lead areas
#     try:
#         combined_details = extract_lead_details(lead_analysis, company)
#         logging.info(f"🔍 Raw AI output for lead areas: \n{combined_details}")
#     except Exception as e:
#         logging.error(f"Failed to extract lead details: {e}")
#         return

#     all_lead_areas_list: List[str] = []
#     m = re.search(r"\*\*Lead Identification Area\*\*: (.+)", combined_details)
#     if m:
#         all_lead_areas_str = m.group(1).strip()
#         if all_lead_areas_str.lower() != "not available":
#             all_lead_areas_list = [area.strip() for area in all_lead_areas_str.split(',') if area.strip()]

#     if not all_lead_areas_list:
#         logging.info("No specific lead areas identified.")
#         return

#     logging.info(f"✅ Initially identified lead areas: {all_lead_areas_list}")

#     # Filter duplicates before processing
#     df = get_identified_leads_df()
#     existing_company_row = df[df["Company Name"] == company]
#     if not existing_company_row.empty:
#         existing_areas_str = existing_company_row["Lead Identification Areas"].iloc[0]
#         existing_areas_set = set(normalize_areas_string(existing_areas_str).split(', ') if existing_areas_str else set())
#         truly_new_areas_to_process = [area for area in all_lead_areas_list if area not in existing_areas_set]
#         if not truly_new_areas_to_process:
#             logging.info("All identified areas are already tracked — skipping.")
#             return
#     else:
#         truly_new_areas_to_process = all_lead_areas_list

#     logging.info(f"✅ Found {len(truly_new_areas_to_process)} truly new areas to process: {truly_new_areas_to_process}")

#     # Loop and process new areas
#     sender_email = os.getenv("SENDER_USER_ID", "So_App_Support@sonata-software.com")
#     notify_email = os.getenv("NOTIFY_EMAIL", "vishnu.kg@sonata-software.com")

#     for lead_area in truly_new_areas_to_process:
#         logging.info(f"🔄 Re-analyzing content for specific new area: '{lead_area}'")
#         try:
#             area_analysis, area_potential_check = check_potential_lead_by_area(lead_area, website_content, linkedin_content, news_content)
#             if area_potential_check.strip().lower() != "yes":
#                 logging.info(f"No lead indication for area '{lead_area}'.")
#                 continue

#             area_details = extract_single_lead_details(area_analysis, company)
#             new_areas = add_lead_to_excel(company, lead_area)
#             if not new_areas:
#                 logging.info("No new areas were added to Excel; skipping notification.")
#                 continue

#             lead_doc_name, lead_doc_stream = create_lead_docx(area_analysis, company)
#             lead_doc_bytes = lead_doc_stream.getvalue()

#             email_body = (
#                 f"<html><body><p>A new potential lead has been identified for <strong>{company}</strong> in the area of <strong>{lead_area}</strong>.</p>"
#                 + "".join(f"<p>{markdown_bold_to_html(line)}</p>" for line in area_details.splitlines())
#                 + "<p>See attachments for full reports.</p></body></html>"
#             )

#             sent = send_email_app_only(
#                 sender_email,
#                 [notify_email],
#                 f"New Lead: {company} - {lead_area}",
#                 email_body,
#                 cc_emails=[notify_email],
#                 attachments=[(lead_doc_name, lead_doc_stream)]
#             )

#             # if sent:
#             #     logging.info(f"✅ Email sent for area: '{lead_area}'")
#             #     send_lead_data_to_api(lead_area, my_account_name, my_lead_name, lead_doc_name, lead_doc_bytes)
#             #     logging.info(f"📨 Lead data posted for area: '{lead_area}'")
#             # else:
#                 # logging.warning(f"Email not sent for area: '{lead_area}'")
#         except Exception as e:
#             logging.error(f"Error processing lead area '{lead_area}': {e}")

#     logging.info("Lead generation cycle completed.")





#pipeline working
# import logging
# from datetime import datetime, timedelta
# import requests
# import os
# import re

# from utils import normalize_areas_string, markdown_bold_to_html
# from storage import get_identified_leads_df, add_lead_to_excel
# from scraping import get_company_website, scrape_website, scrape_google_news
# from ai import check_potential_lead, extract_lead_details, check_potential_lead_by_area, extract_single_lead_details
# from docs import create_lead_docx, send_email_app_only
# from dotenv import load_dotenv

# load_dotenv()

# BASE_URL = "https://gnews.io/api/v4/search"
# GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
# API_KEY = os.getenv("API_KEY")
# CX = os.getenv("CX")

# def process_company_pipeline(company: str, my_account_name: str, my_lead_name: str, pages: int = 1) -> None:
#     logging.info(f"🕒 Processing pipeline for: {company}")
#     # 1. GNews Fetch (last 30 days)
#     today = datetime.utcnow()
#     frm = (today - timedelta(days=30)).strftime("%Y-%m-%d")
#     to = today.strftime("%Y-%m-%d")
#     news_results = []
#     try:
#         resp = requests.get(BASE_URL, params={"q": company, "from": frm, "to": to, "lang": "en", "token": GNEWS_API_KEY}, verify=False, timeout=30)
#         resp.raise_for_status()
#         for art in resp.json().get("articles", []):
#             news_results.append({"title": art.get("title", ""), "description": art.get("description", ""), "url": art.get("url", "")})
#         logging.info(f"✅ GNews API returned {len(news_results)} articles.")
#     except Exception as e:
#         logging.error(f"❌ GNews API error: {e}")

#     # 2. Google News Scrape
#     try:
#         google_news_results = scrape_google_news(company, pages)
#         logging.info(f"✅ Google News scrape found {len(google_news_results)} articles.")
#     except Exception as e:
#         logging.error(f"❌ Google News scraping error: {e}")
#         google_news_results = []

#     all_news = news_results + google_news_results
#     if not all_news:
#         logging.warning("⚠️ No news results found; skipping.")
#         return
#     news_content = "\n\n".join(f"**Title:** {n['title']}\n**Description:** {n['description']}\n**URL:** {n['url']}" for n in all_news)

#     # 3. Website Scraping
#     website = get_company_website(company, API_KEY, CX)
#     if not website:
#         logging.error(f"❌ Could not find website for {company}.")
#         return
#     try:
#         website_content, _ = scrape_website(website)
#         logging.info("✅ Website scraped successfully.")
#     except Exception as e:
#         logging.error(f"❌ Website scraping error: {e}")
#         return

#     # 4. LinkedIn Scraping
#     linkedin_url = get_company_website(company + " LinkedIn", API_KEY, CX)
#     if not linkedin_url:
#         logging.error(f"❌ Could not find LinkedIn profile for {company}.")
#         return
#     try:
#         linkedin_content, _ = scrape_website(linkedin_url)
#         logging.info("✅ LinkedIn scraped successfully.")
#     except Exception as e:
#         logging.error(f"❌ LinkedIn scraping error: {e}")
#         return

#     # 5. AI Lead Check
#     try:
#         lead_analysis, potential_lead_check = check_potential_lead(website_content, linkedin_content, news_content)
#         logging.info("✅ Lead analysis complete.")
#     except Exception as e:
#         logging.error(f"❌ OpenAI analysis error: {e}")
#         return

#     logging.info(f"🔍 Is '{company}' a potential lead? → {potential_lead_check}")
#     if potential_lead_check.strip().lower() != "yes":
#         logging.info(f"🚫 '{company}' is not identified as a potential lead; skipping all downstream steps.")
#         return

#     # Extract lead areas
#     try:
#         combined_details = extract_lead_details(lead_analysis, company)
#         logging.info(f"🔍 Raw AI output for lead areas: \n{combined_details}")
#     except Exception as e:
#         logging.error(f"❌ Failed to extract lead details from initial analysis: {e}")
#         return

#     all_lead_areas_list = []
#     m = re.search(r"\*\*Lead Identification Area\*\*: (.+)", combined_details)
#     if m:
#         all_lead_areas_str = m.group(1).strip()
#         if all_lead_areas_str.lower() != "not available":
#             all_lead_areas_list = [area.strip() for area in all_lead_areas_str.split(',') if area.strip()]
#     if not all_lead_areas_list:
#         logging.info("📝 The broad analysis did not identify any specific lead areas.")
#         return

#     df = get_identified_leads_df()
#     existing_company_row = df[df["Company Name"] == company]
#     if not existing_company_row.empty:
#         existing_areas_str = existing_company_row["Lead Identification Areas"].iloc[0]
#         existing_areas_set = set(normalize_areas_string(existing_areas_str).split(', ') if existing_areas_str else set())
#         truly_new_areas_to_process = [area for area in all_lead_areas_list if area not in existing_areas_set]
#         if not truly_new_areas_to_process:
#             logging.info(f"📝 All identified areas for '{company}' are already in the Excel file. Skipping targeted analysis.")
#             return
#     else:
#         truly_new_areas_to_process = all_lead_areas_list

#     logging.info(f"✅ Found {len(truly_new_areas_to_process)} truly new areas to process: {truly_new_areas_to_process}")

#     for lead_area in truly_new_areas_to_process:
#         logging.info(f"🔄 Re-analyzing content for specific new area: '{lead_area}'")
#         try:
#             area_analysis, area_potential_check = check_potential_lead_by_area(lead_area, website_content, linkedin_content, news_content)
#             if area_potential_check.strip().lower() == "yes":
#                 area_details = extract_single_lead_details(area_analysis, company)
#                 email_flag = add_lead_to_excel(company, lead_area)
#                 if email_flag:
#                     logging.info("✅ Excel updated successfully.")
#                     lead_doc_name, lead_doc_stream = create_lead_docx(area_analysis, company)
#                     lead_doc_bytes = lead_doc_stream.getvalue()
#                     logging.info("📄 DOCX files generated.")
#                     try:
#                         sender_email = "So_App_Support@sonata-software.com"
#                         email_body = (
#                             f"<html><body><p>A new potential lead has been identified for <strong>{company}</strong> in the area of <strong>{lead_area}</strong>.</p>"
#                             + "".join(f"<p>{markdown_bold_to_html(line)}</p>" for line in area_details.splitlines())
#                             + "<p>See attachments for full reports.</p></body></html>"
#                         )
#                         sent = send_email_app_only(
#                             sender_email,
#                             ["vishnu.kg@sonata-software.com"],
#                             f"New Lead: {company} - {lead_area}",
#                             email_body,
#                             cc_emails=["vishnu.kg@sonata-software.com"],
#                             attachments=[(lead_doc_name, lead_doc_stream)],
#                         )
#                         # if sent:
#                         #     logging.info(f"✅ Email sent for area: '{lead_area}'")
#                         #     send_lead_data_to_api(lead_area, my_account_name, my_lead_name, lead_doc_name, lead_doc_bytes)
#                         #     logging.info(f"📨 Lead data posted to external API for area: '{lead_area}'")
#                         # else:
#                         #     logging.warning(f"⚠️ Email not sent for area: '{lead_area}'")
#                     except Exception as e:
#                         logging.error(f"❌ Error when attempting to send email/API for area '{lead_area}': {e}")
#                 else:
#                     logging.info(f"🚫 No truly new areas were added to Excel for '{company}' - skipping email/API.")
#             else:
#                 logging.info(f"🚫 No lead indication found for area '{lead_area}'; skipping email and API steps.")
#         except Exception as e:
#             logging.error(f"❌ Error processing lead area '{lead_area}': {e}")

#     logging.info("✅ Lead generation cycle completed.")









import logging
from datetime import datetime, timedelta
import requests
import os
import re

from utils import normalize_areas_string, markdown_bold_to_html
from storage import get_identified_leads_df, add_lead_to_excel
from scraping import get_company_website, scrape_website, scrape_google_news
from ai import check_potential_lead, extract_lead_details, check_potential_lead_by_area, extract_single_lead_details, extract_and_validate_contacts_from_analysis, format_contacts_with_openai
from docs import create_lead_docx, send_email_app_only
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://gnews.io/api/v4/search"
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
API_KEY = os.getenv("API_KEY")
CX = os.getenv("CX")

def process_company_pipeline(company: str, my_account_name: str, my_lead_name: str, pages: int = 1) -> None:
    logging.info(f"🕒 Processing pipeline for: {company}")
    # 1. GNews Fetch (last 30 days)
    today = datetime.utcnow()
    frm = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    to = today.strftime("%Y-%m-%d")
    news_results = []
    try:
        resp = requests.get(BASE_URL, params={"q": company, "from": frm, "to": to, "lang": "en", "token": GNEWS_API_KEY}, verify=False, timeout=30)
        resp.raise_for_status()
        for art in resp.json().get("articles", []):
            news_results.append({"title": art.get("title", ""), "description": art.get("description", ""), "url": art.get("url", "")})
        logging.info(f"✅ GNews API returned {len(news_results)} articles.")
    except Exception as e:
        logging.error(f"❌ GNews API error: {e}")

    # 2. Google News Scrape
    try:
        google_news_results = scrape_google_news(company, pages)
        logging.info(f"✅ Google News scrape found {len(google_news_results)} articles.")
    except Exception as e:
        logging.error(f"❌ Google News scraping error: {e}")
        google_news_results = []

    all_news = news_results + google_news_results
    if not all_news:
        logging.warning("⚠️ No news results found; skipping.")
        return
    news_content = "\n\n".join(f"**Title:** {n['title']}\n**Description:** {n['description']}\n**URL:** {n['url']}" for n in all_news)

    # 3. Website Scraping
    website = get_company_website(company, API_KEY, CX)
    if not website:
        logging.error(f"❌ Could not find website for {company}.")
        return
    try:
        website_content, _ = scrape_website(website)
        logging.info("✅ Website scraped successfully.")
    except Exception as e:
        logging.error(f"❌ Website scraping error: {e}")
        return

    # 4. LinkedIn Scraping
    linkedin_url = get_company_website(company + " LinkedIn", API_KEY, CX)
    if not linkedin_url:
        logging.error(f"❌ Could not find LinkedIn profile for {company}.")
        return
    try:
        linkedin_content, _ = scrape_website(linkedin_url)
        logging.info("✅ LinkedIn scraped successfully.")
    except Exception as e:
        logging.error(f"❌ LinkedIn scraping error: {e}")
        return

    # 5. AI Lead Check
    try:
        lead_analysis, potential_lead_check = check_potential_lead(website_content, linkedin_content, news_content)
        logging.info("✅ Lead analysis complete.")
    except Exception as e:
        logging.error(f"❌ OpenAI analysis error: {e}")
        return

    logging.info(f"🔍 Is '{company}' a potential lead? → {potential_lead_check}")
    if potential_lead_check.strip().lower() != "yes":
        logging.info(f"🚫 '{company}' is not identified as a potential lead; skipping all downstream steps.")
        return

    # Extract lead areas
    try:
        combined_details = extract_lead_details(lead_analysis, company)
        logging.info(f"🔍 Raw AI output for lead areas: \n{combined_details}")
    except Exception as e:
        logging.error(f"❌ Failed to extract lead details from initial analysis: {e}")
        return

    all_lead_areas_list = []
    m = re.search(r"\*\*Lead Identification Area\*\*: (.+)", combined_details)
    if m:
        all_lead_areas_str = m.group(1).strip()
        if all_lead_areas_str.lower() != "not available":
            all_lead_areas_list = [area.strip() for area in all_lead_areas_str.split(',') if area.strip()]
    if not all_lead_areas_list:
        logging.info("📝 The broad analysis did not identify any specific lead areas.")
        return

    df = get_identified_leads_df()
    existing_company_row = df[df["Company Name"] == company]
    if not existing_company_row.empty:
        existing_areas_str = existing_company_row["Lead Identification Areas"].iloc[0]
        existing_areas_set = set(normalize_areas_string(existing_areas_str).split(', ') if existing_areas_str else set())
        truly_new_areas_to_process = [area for area in all_lead_areas_list if area not in existing_areas_set]
        if not truly_new_areas_to_process:
            logging.info(f"📝 All identified areas for '{company}' are already in the Excel file. Skipping targeted analysis.")
            return
    else:
        truly_new_areas_to_process = all_lead_areas_list

    logging.info(f"✅ Found {len(truly_new_areas_to_process)} truly new areas to process: {truly_new_areas_to_process}")

    for lead_area in truly_new_areas_to_process:
        logging.info(f"🔄 Re-analyzing content for specific new area: '{lead_area}'")
        try:
            area_analysis, area_potential_check = check_potential_lead_by_area(lead_area, website_content, linkedin_content, news_content)
            if area_potential_check.strip().lower() == "yes":
                area_details = extract_single_lead_details(area_analysis, company)
                email_flag = add_lead_to_excel(company, lead_area)
                if email_flag:
                    logging.info("✅ Excel updated successfully.")
                    lead_doc_name, lead_doc_stream = create_lead_docx(area_analysis, company)
                    lead_doc_bytes = lead_doc_stream.getvalue()
                    logging.info("📄 DOCX files generated.")
                    try:
                        sender_email = "So_App_Support@sonata-software.com"
                        email_body = (
                            f"<html><body><p>A new potential lead has been identified for <strong>{company}</strong> in the area of <strong>{lead_area}</strong>.</p>"
                            + "".join(f"<p>{markdown_bold_to_html(line)}</p>" for line in area_details.splitlines())
                            + "<p>See attachments for full reports.</p></body></html>"
                        )
                        sent = send_email_app_only(
                            sender_email,
                            ["vishnu.kg@sonata-software.com"],
                            f"New Lead: {company} - {lead_area}",
                            email_body,
                            cc_emails=["vishnu.kg@sonata-software.com"],
                            attachments=[(lead_doc_name, lead_doc_stream)],
                        )
                        # if sent:
                        #     logging.info(f"✅ Email sent for area: '{lead_area}'")
                        #     send_lead_data_to_api(lead_area, my_account_name, my_lead_name, lead_doc_name, lead_doc_bytes)
                        #     logging.info(f"📨 Lead data posted to external API for area: '{lead_area}'")
                        # else:
                        #     logging.warning(f"⚠️ Email not sent for area: '{lead_area}'")
                    except Exception as e:
                        logging.error(f"❌ Error when attempting to send email/API for area '{lead_area}': {e}")
                else:
                    logging.info(f"🚫 No truly new areas were added to Excel for '{company}' - skipping email/API.")
            else:
                logging.info(f"🚫 No lead indication found for area '{lead_area}'; skipping email and API steps.")
            
            # filtered_contacts_text, contact_flag = extract_and_validate_contacts_from_analysis(area_analysis, lead_area)
            # logging.info(f"Contact extraction result for '{lead_area}': flag={contact_flag}")
    
            # if contact_flag.strip().lower() == "yes":
            #     contacts_list = format_contacts_with_openai(filtered_contacts_text)
            #     if contacts_list:
            #         try:
            #             sender_email = "So_App_Support@sonata-software.com"
    
            #             # Build HTML summary table for contacts
            #             contacts_html = "<p><strong>Filtered Contacts (relevant to lead area):</strong></p>"
            #             contacts_html += "<table border='0' cellpadding='4' cellspacing='0'>"
            #             contacts_html += "<tr><th>Name</th><th>Title</th><th>Contact</th><th>Source</th><th>URL</th></tr>"
            #             for c in contacts_list:
            #                 contacts_html += "<tr>"
            #                 contacts_html += f"<td>{c.get('name') or ''}</td>"
            #                 contacts_html += f"<td>{c.get('title') or ''}</td>"
            #                 contacts_html += f"<td>{c.get('contact') or ''}</td>"
            #                 contacts_html += f"<td>{c.get('source') or ''}</td>"
            #                 contacts_html += f"<td>{c.get('source_url') or ''}</td>"
            #                 contacts_html += "</tr>"
            #             contacts_html += "</table>"
    
            #             # Contact-only email (no attachments)
            #             email_body_contacts = (
            #                 f"<html><body><p>Validated contact details extracted for "
            #                 f"<strong>{company}</strong> - <strong>{lead_area}</strong>:</p>"
            #                 + contacts_html
            #                 + "</body></html>"
            #             )
    
            #             sent_contacts = send_email_app_only(
            #                 sender_email,
            #                 ["vishnu.kg@sonata-software.com"],
            #                 f"Contact Details: {company} - {lead_area}",
            #                 email_body_contacts,
            #                 cc_emails=["vishnu.kg@sonata-software.com"],
            #             )
            #             if sent_contacts:
            #                 logging.info(f"✅ Contact email sent for area: '{lead_area}'.")
            #             else:
            #                 logging.warning(f"⚠️ Contact email NOT sent for area: '{lead_area}'.")
    
            #         except Exception as e:
            #             logging.error(f"❌ Error sending contact email for area '{lead_area}': {e}")
            #     else:
            #         logging.info(f"🚫 Contacts formatting/parsing returned empty for area '{lead_area}'. Skipping contacts email.")
            # else:
            #     logging.info(f"🚫 No contact details found for area '{lead_area}'; skipping contacts email.")

            # filtered_contacts_text, contact_flag = extract_and_validate_contacts_from_analysis(area_analysis, lead_area)
            # logging.info(filtered_contacts_text, contact_flag)
            # if contact_flag.strip().lower() == "yes":
            #     contacts_list = format_contacts_with_openai(filtered_contacts_text)
            #     if contacts_list:
            #         try:
            #             sender_email = "So_App_Support@sonata-software.com"
            #             contacts_html = "<p><strong>Filtered Contacts (relevant to lead area):</strong></p>"
            #             contacts_html += "<table border='0' cellpadding='4' cellspacing='0'>"
            #             contacts_html += "<tr><th>Name</th><th>Title</th><th>Contact</th><th>Source</th><th>URL</th></tr>"
            #             for c in contacts_list:
            #                 contacts_html += "<tr>"
            #                 contacts_html += f"<td>{c.get('name') or ''}</td>"
            #                 contacts_html += f"<td>{c.get('title') or ''}</td>"
            #                 contacts_html += f"<td>{c.get('contact') or ''}</td>"
            #                 contacts_html += f"<td>{c.get('source') or ''}</td>"
            #                 contacts_html += f"<td>{c.get('source_url') or ''}</td>"
            #                 contacts_html += "</tr>"
            #             contacts_html += "</table>"

            #             email_body = (
            #                 f"<html><body><p>A new potential lead has been identified for "
            #                 f"<strong>{company}</strong> in the area of <strong>{lead_area}</strong>.</p>"
            #                 + "".join(
            #                     f"<p>{markdown_bold_to_html(line)}</p>"
            #                     for line in area_details.splitlines()
            #                 )
            #                 + contacts_html
            #                 + "<p>Refer to details above.</p></body></html>"
            #             )
            #             sent = send_email_app_only(
            #                 sender_email,
            #                 ["vishnu.kg@sonata-software.com"],
            #                 f"New Lead: {company} - {lead_area}",
            #                 email_body,
            #                 cc_emails=["vishnu.kg@sonata-software.com"],
            #             )
            #         except Exception as e:
            #             logging.error(f"❌ Error when attempting to send email/API for area '{lead_area}': {e}")
            #     else:
            #         logging.info(
            #             f"🚫 Contacts formatting/parsing returned empty for area '{lead_area}'. Skipping email/API."
            #         )
            # else:
            #     logging.info(f"🚫 No Conatact Details Found '{lead_area}'; skipping email and API steps.")
        except Exception as e:
            logging.error(f"❌ Error processing lead area '{lead_area}': {e}")


    logging.info("✅ Lead generation cycle completed.")
