# # ai.py
# import os
# from typing import Tuple
# from openai import AzureOpenAI

# AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
# AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
# AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# client = AzureOpenAI(
#     api_key=AZURE_API_KEY,
#     api_version="2024-12-01-preview",
#     azure_endpoint=AZURE_ENDPOINT,
# )

# def run_openai_chat(prompt: str) -> str:
#     response = client.chat.completions.create(
#         model=AZURE_DEPLOYMENT,
#         messages=[{"role": "user", "content": prompt}],
#     )
#     return response.choices[0].message.content

# def check_potential_lead(website_content: str, linkedin_content: str, news_content: str) -> Tuple[str, str]:
#     combined_content = f"""
# You are a market-intelligence assistant.
# Analyze the following source materials (Website, LinkedIn, News) and produce a text report with these three sections. 
# Decision rules (strict):
# - For each area, answer “Yes” ONLY if there is CLEAR, COMPANY-SPECIFIC evidence of current interest or activity of that area within the last 3 days found in the Sources below.
# - Use ONLY the provided Sources block. Do NOT invent links or content.
# 1. Interest...
# Sources
# Website Content:
# {website_content}
# LinkedIn Profile Content:
# {linkedin_content}
# Recent News Articles:
# {news_content}
# """
#     lead_analysis = run_openai_chat(combined_content)
#     potential_lead_check = classify_lead(lead_analysis)
#     return lead_analysis, potential_lead_check

# def classify_lead(lead_analysis: str) -> str:
#     prompt = f"""
# You are a proactive lead generation expert.
# Given the following lead analysis, determine if this company shows any sign—direct or indirect—of being a potential lead. Answer strictly with "Yes" or "No".
# Lead Analysis:
# {lead_analysis}
# """
#     response = run_openai_chat(prompt)
#     return response.strip()

# def extract_lead_details(lead_analysis: str, company: str) -> str:
#     prompt = f"""
# Given the following lead analysis for the company "{company}", extract and return:
# 1. Customer Name
# 2. Lead Identification Area(s)
# Format:
# **Customer Name**: <value>
# **Lead Identification Area**: <value>
# Lead Analysis:
# {lead_analysis}
# """
#     return run_openai_chat(prompt)

# def check_potential_lead_by_area(single_lead_area: str, website_content: str, linkedin_content: str, news_content: str) -> Tuple[str, str]:
#     combined_content = f"""
# You are a market-intelligence assistant. Your task is to analyze the following source materials and determine if there is any evidence of **{single_lead_area}**.
# Decision rules (strict):
# - Answer “Yes” ONLY if there is CLEAR, COMPANY-SPECIFIC evidence in the Sources below within the LAST 3 DAYS showing real interest or activity in **{single_lead_area}**.
# Provide a text report with the following sections...
# Website Content:
# {website_content}
# LinkedIn Profile Content:
# {linkedin_content}
# Recent News Articles:
# {news_content}
# """
#     analysis = run_openai_chat(combined_content)
#     potential_lead_check = "Yes" if ("Yes" in analysis or "yes" in analysis) else "No"
#     return analysis, potential_lead_check

# def extract_single_lead_details(lead_analysis: str, company: str) -> str:
#     prompt = f"""
# Given the following lead analysis for the company "{company}", extract and return only one Lead Identification Area in the format:
# **Customer Name**: <value>
# **Lead Identification Area**: <value>
# Lead Analysis:
# {lead_analysis}
# """
#     return run_openai_chat(prompt)


import os
from typing import Tuple, List
from openai import AzureOpenAI
from dotenv import load_dotenv
import logging

load_dotenv()

AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

client = AzureOpenAI(
    api_key=AZURE_API_KEY,
    api_version="2024-12-01-preview",
    azure_endpoint=AZURE_ENDPOINT,
)

def run_openai_chat(prompt: str) -> str:
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def check_potential_lead(website_content: str, linkedin_content: str, news_content: str) -> Tuple[str, str]:
    combined_content = f"""
    You are a market-intelligence assistant.
    Analyze the following source materials (Website, LinkedIn, News) and produce a text report with these three sections. 
    Decision rules (strict):
    - For each area, answer “Yes” ONLY if there is CLEAR, COMPANY-SPECIFIC evidence of current interest or activity in that area within the last 3 days found in the Sources below. Examples: official announcements, press releases, case studies, product/initiative pages tied to THIS company, exec statements, RFPs/tenders, partnerships, hiring/posts explicitly for that area, migration/adoption milestones.
    - Generic capability pages, vague marketing language, industry articles not tied to THIS company, or historical items older than 3 days → “No”.
    - Use ONLY the provided Sources block. Do NOT invent links or content.
    - For every “Yes”, include at least one exact excerpt in the Evidence section PLUS the source URL and (if available) the date. If you cannot provide an excerpt + URL from the Sources block, answer “No”.
    1. **Interest**
       For each area below, state “Yes” or “No”. If “Yes”, add a one-sentence why with an inline source tag like (Website), (LinkedIn), or (News).
       New Business Development Areas:
         - SFR150
         - Zones
         - DYN365
         - AI
         - AWS  
       Large Deal Areas:
         - Cost Takeout
         - Cloud Migration
         - Data Migration
         - Platform Migration
         - SaaS
         - GCC
         - Partner with IT 
    2. **Contacts**
       List each contact found, with type (email/phone/name+title) and the source (Website, LinkedIn, or News). Use only items present in Sources. 
    3. **Evidence**
       Under sub-headings for Website, LinkedIn, and News, give the exact excerpt(s) that support each “Yes” or any contacts found. For each excerpt include the source URL and (if present) the date. If no supporting excerpts exist for a given area, do not fabricate; that area must be “No”.
    **Sources**
    Website Content:
    {website_content} 
    LinkedIn Profile Content:
    {linkedin_content}
    Recent News Articles:
    {news_content}
    """.format(website_content=website_content, linkedin_content=linkedin_content, news_content=news_content)

    lead_analysis = run_openai_chat(combined_content)
    potential_lead_check = classify_lead(lead_analysis)
    return lead_analysis, potential_lead_check


def classify_lead(lead_analysis: str) -> str:
    prompt = f"""
    You are a proactive lead generation expert.
    Given the following lead analysis, determine if this company shows any sign—direct or indirect—of being a potential lead. Even a slight indication of interest, relevance, or alignment should result in "Yes".
    **Lead Analysis:**
    {lead_analysis}
    Answer strictly with "Yes" or "No".
    """
    response = run_openai_chat(prompt)
    return response.strip()


def extract_lead_details(lead_analysis: str, company: str) -> str:
    prompt = f"""
    Given the following lead analysis for the company "{company}", extract and return the following in plain text format:
    1. Customer Name
    2. Lead Identification Area(s) (e.g., SFR150, Zones, DYN365, AI, AWS, Cost Takeout, Cloud Migration, Data Migration, Platform Migration, SaaS, GCC, Partner with IT)
    Format the output like this:
    **Customer Name**: <value>
    **Lead Identification Area**: <value>
    If a field is not found, just leave it like.
    Lead Analysis:
    {lead_analysis}
    """
    return run_openai_chat(prompt)


def extract_single_lead_details(lead_analysis, company):
    prompt = f"""
    Given the following lead analysis for the company "{company}", extract and return the following in plain text format:
    1. Customer Name
    2. Lead Identification Area (e.g., SFR150, Zones, DYN365, AI, AWS, Cost Takeout, Cloud Migration, Data Migration, Platform Migration, SaaS, GCC, Partner with IT) Mention any one. do not give more than one and no details.
    Format the output like this:
    **Customer Name**: <value>
    **Lead Identification Area**: <value>
    If a field is not found, just leave it like.
    Lead Analysis:
    {lead_analysis}
    """
    return run_openai_chat(prompt)

def check_potential_lead_by_area(single_lead_area: str, website_content: str, linkedin_content: str, news_content: str) -> Tuple[str, str]:
    """
    Analyzes content for a single, specific lead identification area.
    Returns the detailed analysis and a 'Yes' or 'No' based on that area.
    """
    combined_content = f"""
    You are a market-intelligence assistant. Your task is to analyze the following source materials and determine if there is any evidence of **{single_lead_area}**.
    Decision rules (strict):
    - Answer “Yes” ONLY if there is CLEAR, COMPANY-SPECIFIC evidence in the Sources below within the LAST 3 DAYS showing real interest or activity in **{single_lead_area}** (e.g., official announcements, press releases, case studies naming this company, exec statements, RFPs/tenders, partnerships, live projects, product/initiative pages tied to this company, or hiring/posts explicitly for this area).
    - Generic capability/marketing pages, industry articles not tied to this company, vague mentions, or items older than 3 days → “No”.
    - Use ONLY the provided Sources block. Do NOT invent or add outside links.
    - Every “Yes” MUST include at least one exact excerpt and a URL from the Sources. If you cannot provide an excerpt + URL, answer “No”.
    Provide a text report with the following sections:
    1. **{single_lead_area}**
       State "Yes" or "No". If "Yes", explain concisely why it is a potential lead and include an inline source link or supporting content if present. Do not add unrelated commentary.
    2. **Contacts**
       List all contacts found (email/phone/name+title) and the source source URL. Use only items present in Sources.
       - If no contacts are found, OMIT the **Contacts** section entirely. Do not write placeholders like "Not available".
    3. **Evidence**
       Under sub-headings **Website**, **LinkedIn**, and **News**, include ONLY those sub-headings that have at least one supporting excerpt. For each excerpt, include the source URL and, if present, the date.
       - If a source has no supporting excerpts, OMIT that sub-heading.
       - If there are zero excerpts across all sources, OMIT the entire **Evidence** section.
       - Never write placeholder lines like "No evidence found", "N/A", or similar.
    **Sources**
    Website Content:
    {website_content}
    LinkedIn Profile Content:
    {linkedin_content}
    Recent News Articles:
    {news_content}
    """ .format(single_lead_area=single_lead_area, website_content=website_content, linkedin_content=linkedin_content, news_content=news_content)
    analysis = run_openai_chat(combined_content)
    potential_lead_check = "Yes" if ("Yes" in analysis or "yes" in analysis) else "No"
    return analysis, potential_lead_check


def extract_and_validate_contacts_from_analysis(area_analysis: str, lead_area: str) -> Tuple[str, str]:
    """
    Uses Azure OpenAI (via run_openai_chat) to:
      - Extract contact details present in the area_analysis text
      - Filter out top-level execs (CEO, Founder, Chairman, President, Managing Director, CTO, CFO, etc.)
      - Keep only contacts likely responsible for the lead_area (Director, VP, Head, Manager, Lead, Specialist, Principal, Architect, etc.)
    Returns:
      - filtered_contacts_text: plain text listing the filtered contacts (one per line: Name | Title | Contact Info | Source | Source URL)
      - contact_flag: "Yes" if at least one valid contact found, else "No"
    """
    prompt = f"""
You are a strict data-extraction assistant. Given the following analysis text (which may contain a '**Contacts**' section and other content),
extract and RETURN ONLY the contacts that are *directly relevant* to the lead area: "{lead_area}".

Decision rules:
- Do NOT return C-level or top executive contacts: exclude CEO, Founder, Co-Founder, Chair, Chairman, President, Managing Director, CTO, CFO, Chief *, and any similar top-level titles.
- Only include contacts whose title indicates responsibility/ownership or direct relevance to the technical or business area (examples: Director, Sr Director, Head of <area>, VP (if directly tied to the area), Manager, Lead, Principal, Specialist, Architect, Program Manager).
- Only use contact information exactly as it appears in the analysis text. Do NOT invent emails/phones/names.
- For each included contact, produce a single line in this exact format:
  Name | Title | Contact Info (email/phone if present, otherwise "N/A") | Source (Website/LinkedIn/News) | Source URL (if present)
- If there are no qualifying contacts, ONLY output the single line:
  NO_CONTACTS_FOUND

Input:
{area_analysis}

Remember: output nothing else besides either the list of contacts (one per line) or the single token NO_CONTACTS_FOUND.
"""
    try:
        ai_response = run_openai_chat(prompt).strip()
    except Exception as e:
        logging.error(f"❌ Error calling OpenAI to extract contacts: {e}")
        return "", "No"

    if not ai_response or "NO_CONTACTS_FOUND" in ai_response.upper() or ai_response.strip().lower() in ["no_contacts_found", "no contacts found"]:
        return "", "No"

    filtered_contacts_text = ai_response
    return filtered_contacts_text, "Yes"



def format_contacts_with_openai(filtered_contacts_text: str) -> List[dict]:
    """
    Uses Azure OpenAI to normalize and format the extracted contact text
    into a clean JSON list of contact dictionaries.
    """
    if not filtered_contacts_text.strip() or "NO_CONTACTS_FOUND" in filtered_contacts_text.upper():
        return []

    prompt = f"""
You are a precise data formatter.
Given the following extracted contact text, convert it into a clean JSON array of objects.
Each object must contain: name, title, contact_info, source, and source_url.

Ensure:
- Proper capitalization of names and titles.
- If a field is missing, use an empty string ("").
- Do not include commentary or markdown, just valid JSON.

Example:
[
  {{
    "name": "John Doe",
    "title": "Director, Cloud Solutions",
    "contact_info": "john.doe@company.com",
    "source": "LinkedIn",
    "source_url": "https://linkedin.com/in/johndoe"
  }}
]

Input:
{filtered_contacts_text}
"""

    try:
        response = run_openai_chat(prompt)
        # Clean and parse JSON safely
        import json
        cleaned = response.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned)
    except Exception as e:
        logging.error(f"❌ Failed to format contacts with OpenAI: {e}")
        return []
