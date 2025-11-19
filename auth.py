# import logging
# import os
# import base64
# from io import BytesIO
# import requests
# from msal import ConfidentialClientApplication
# from azure.storage.blob import BlobServiceClient

# GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
# TOKEN_CONTAINER_NAME = "potentiallist"
# TOKEN_BLOB_NAME = "token.json"
# AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

# def _require_env():
#     missing = [k for k in ("TENANT_ID","CLIENT_ID","CLIENT_SECRET") if not os.getenv(k)]
#     if missing:
#         raise RuntimeError(f"Missing envs: {missing}")

# def _get_app_token() -> str:
#     _require_env()
#     app = ConfidentialClientApplication(
#         client_id=os.getenv("CLIENT_ID"),
#         client_credential=os.getenv("CLIENT_SECRET"),
#         authority=f"https://login.microsoftonline.com/{os.getenv('TENANT_ID')}"
#     )
#     res = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
#     if "access_token" not in res:
#         logging.error(f"Token acquisition failed: {res}")
#         raise RuntimeError("Token acquisition failed")
#     return res["access_token"]

# def send_email_app_only(sender_user_id: str, to_emails: list, subject: str, html_body: str, cc_emails: list | None = None, bcc_emails: list | None = None, attachments: list | None = None) -> bool:
#     try:
#         token = _get_app_token()
#         message = {
#             "message": {
#                 "subject": subject,
#                 "importance": "Normal",
#                 "body": {"contentType": "HTML", "content": html_body},
#                 "toRecipients": [{"emailAddress": {"address": e}} for e in to_emails],
#                 "attachments": [],
#             },
#             "saveToSentItems": "true"
#         }
#         if cc_emails:
#             message["message"]["ccRecipients"] = [{"emailAddress": {"address": e}} for e in cc_emails]
#         if bcc_emails:
#             message["message"]["bccRecipients"] = [{"emailAddress": {"address": e}} for e in bcc_emails]
#         if attachments:
#             for name, data_stream in attachments:
#                 data_stream.seek(0)
#                 encoded_content = base64.b64encode(data_stream.read()).decode("utf-8")
#                 message["message"]["attachments"].append({
#                     "@odata.type": "#microsoft.graph.fileAttachment",
#                     "name": name,
#                     "contentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
#                     "contentBytes": encoded_content
#                 })
#         url = f"{GRAPH_API_ENDPOINT}/users/{sender_user_id}/sendMail"
#         r = requests.post(url, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, json=message, timeout=30)
#         if r.status_code == 202:
#             logging.info(f"Email sent to {to_emails}")
#             return True
#         else:
#             logging.error(f"Send failed [{r.status_code}]: {r.text}")
#             return False
#     except Exception as e:
#         logging.error(f"Error sending email: {e}")
#         return False

# def send_lead_data_to_api(lead_areas: str, account_name: str, lead_name: str, file_name: str | None = None, file_bytes: bytes | None = None) -> bool:
#     api_url = os.getenv("LEAD_API_URL")
#     if not api_url:
#         logging.error("LEAD_API_URL not set")
#         return False
#     try:
#         if file_name and file_bytes is not None:
#             files = [
#                 ('new_leadidentificationarea', (None, lead_areas)),
#                 ('new_name', (None, lead_name)),
#                 ('new_accountname', (None, account_name)),
#                 ('new_supportingdocuments', (file_name, BytesIO(file_bytes), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')),
#             ]
#             resp = requests.post(api_url, files=files, timeout=60)
#         else:
#             data = {
#                 "new_leadidentificationarea": lead_areas,
#                 "new_name": lead_name,
#                 "new_accountname": account_name
#             }
#             resp = requests.post(api_url, json=data, timeout=60)
#         resp.raise_for_status()
#         logging.info("Lead data posted to API")
#         return True
#     except Exception as e:
#         logging.error(f"Failed to send lead data: {e}")
#         return False

import os
from msal import ConfidentialClientApplication
import logging
from dotenv import load_dotenv


load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"

def _require_env():
    missing = [k for k, v in {"TENANT_ID": TENANT_ID, "CLIENT_ID": CLIENT_ID, "CLIENT_SECRET": CLIENT_SECRET}.items() if not v]
    if missing:
        raise RuntimeError(f"Missing required env vars for App-only flow: {', '.join(missing)}")


def _get_app_token() -> str:
    _require_env()
    app = ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential=CLIENT_SECRET,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
    )
    res = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"]) 
    if "access_token" not in res:
        logging.error(f"Token acquisition failed: {res.get('error_description', res)}")
        raise RuntimeError(f"Token acquisition failed: {res}")
    logging.info("🔐 Acquired App-only access token.")
    return res["access_token"]