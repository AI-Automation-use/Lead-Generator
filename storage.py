# # import logging
# # import pandas as pd
# # from azure.storage.blob import BlobServiceClient
# # from io import BytesIO
# # import os
# # import datetime
# # from utils import normalize_areas_string
# # from typing import List, Optional, Set, Tuple

# # AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
# # LEAD_EXCEL_CONTAINER_NAME = "potentiallist"
# # LEAD_EXCEL_BLOB_NAME = "leads_tracking.xlsx"

# # def get_blob_service_client() -> BlobServiceClient:
# #     return BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

# # def download_excel_from_blob(blob_service_client: BlobServiceClient, container_name: str, blob_name: str) -> Optional[BytesIO]:
# #     try:
# #         container_client = blob_service_client.get_container_client(container_name)
# #         blob_client = container_client.get_blob_client(blob_name)
# #         download_stream = blob_client.download_blob()
# #         return BytesIO(download_stream.readall())
# #     except Exception as e:
# #         logging.error(f"Error downloading blob {blob_name}: {e}")
# #         return None


# # def upload_excel_to_blob(blob_service_client: BlobServiceClient, container_name: str, blob_name: str, data_stream: bytes) -> None:
# #     try:
# #         container_client = blob_service_client.get_container_client(container_name)
# #         blob_client = container_client.get_blob_client(blob_name)
# #         blob_client.upload_blob(data_stream, overwrite=True)
# #         logging.info(f"Successfully uploaded {blob_name} to blob storage.")
# #     except Exception as e:
# #         logging.error(f"Error uploading blob {blob_name}: {e}")

# # def get_identified_leads_df() -> pd.DataFrame:
# #     blob_service_client = get_blob_service_client()
# #     excel_data = download_excel_from_blob(blob_service_client, LEAD_EXCEL_CONTAINER_NAME, LEAD_EXCEL_BLOB_NAME)
# #     if excel_data:
# #         try:
# #             df = pd.read_excel(excel_data)
# #             return df
# #         except Exception as e:
# #             logging.error(f"Error reading Excel from blob: {e}")
# #             return pd.DataFrame(columns=["Company Name", "Lead Identification Areas", "Timestamp"])
# #     else:
# #         return pd.DataFrame(columns=["Company Name", "Lead Identification Areas", "Timestamp"])


# # def add_lead_to_excel(company_name: str, lead_areas: str) -> Set[str]:
# #     blob_service_client = get_blob_service_client()
# #     df = get_identified_leads_df()
# #     normalized_incoming_areas_str = normalize_areas_string(lead_areas)
# #     incoming_areas_set = set(normalized_incoming_areas_str.split(', ') if normalized_incoming_areas_str else set())
# #     existing_company_row = df[df["Company Name"] == company_name]
# #     truly_new_areas: Set[str] = set()

# #     if not existing_company_row.empty:
# #         existing_areas_str = existing_company_row["Lead Identification Areas"].iloc[0]
# #         existing_areas_set = set(existing_areas_str.split(', ') if existing_areas_str else set())
# #         truly_new_areas = incoming_areas_set - existing_areas_set
# #         if truly_new_areas:
# #             updated_areas_set = existing_areas_set.union(incoming_areas_set)
# #             updated_areas_list = sorted(list(updated_areas_set))
# #             updated_areas_str = ", ".join(updated_areas_list)
# #             df.loc[df["Company Name"] == company_name, "Lead Identification Areas"] = updated_areas_str
# #             df.loc[df["Company Name"] == company_name, "Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# #             output = BytesIO()
# #             df.to_excel(output, index=False)
# #             output.seek(0)
# #             upload_excel_to_blob(blob_service_client, LEAD_EXCEL_CONTAINER_NAME, LEAD_EXCEL_BLOB_NAME, output.getvalue())
# #             logging.info(f"Company '{company_name}' updated with new lead areas: {', '.join(sorted(list(truly_new_areas)))}.")
# #         else:
# #             logging.info(f"Company '{company_name}' already exists with these lead areas. No update needed.")
# #     else:
# #         new_entry = pd.DataFrame([{
# #             "Company Name": company_name,
# #             "Lead Identification Areas": normalized_incoming_areas_str,
# #             "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# #         }])
# #         df = pd.concat([df, new_entry], ignore_index=True)
# #         output = BytesIO()
# #         df.to_excel(output, index=False)
# #         output.seek(0)
# #         upload_excel_to_blob(blob_service_client, LEAD_EXCEL_CONTAINER_NAME, LEAD_EXCEL_BLOB_NAME, output.getvalue())
# #         logging.info(f"New company '{company_name}' added as a lead with areas: {normalized_incoming_areas_str}.")
# #         truly_new_areas = incoming_areas_set

# #     return truly_new_areas



# import logging
# import os
# from io import BytesIO
# import pandas as pd
# from azure.storage.blob import BlobServiceClient
# from datetime import datetime

# AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
# LEAD_EXCEL_CONTAINER_NAME = "potentiallist"
# LEAD_EXCEL_BLOB_NAME = "leads_tracking.xlsx"

# def get_blob_service_client() -> BlobServiceClient:
#     return BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

# def download_excel_from_blob(blob_service_client: BlobServiceClient, container_name: str, blob_name: str) -> BytesIO | None:
#     try:
#         container_client = blob_service_client.get_container_client(container_name)
#         blob_client = container_client.get_blob_client(blob_name)
#         download_stream = blob_client.download_blob()
#         return BytesIO(download_stream.readall())
#     except Exception as e:
#         logging.debug(f"Unable to download blob: {e}")
#         return None

# def upload_excel_to_blob(blob_service_client: BlobServiceClient, container_name: str, blob_name: str, data: bytes):
#     container_client = blob_service_client.get_container_client(container_name)
#     blob_client = container_client.get_blob_client(blob_name)
#     blob_client.upload_blob(data, overwrite=True)

# def get_identified_leads_df() -> pd.DataFrame:
#     blob_service_client = get_blob_service_client()
#     data = download_excel_from_blob(blob_service_client, LEAD_EXCEL_CONTAINER_NAME, LEAD_EXCEL_BLOB_NAME)
#     if data:
#         try:
#             return pd.read_excel(data)
#         except Exception as e:
#             logging.debug(f"Read Excel error: {e}")
#             return pd.DataFrame(columns=["Company Name","Lead Identification Areas","Timestamp"])
#     return pd.DataFrame(columns=["Company Name","Lead Identification Areas","Timestamp"])

# def add_lead_to_excel(company_name: str, lead_areas: str):
#     df = get_identified_leads_df()
#     normalized = lead_areas
#     now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
#     if df[df["Company Name"] == company_name].empty:
#         new_entry = pd.DataFrame([{"Company Name": company_name, "Lead Identification Areas": normalized, "Timestamp": now_str}])
#         df = pd.concat([df, new_entry], ignore_index=True)
#     else:
#         df.loc[df["Company Name"] == company_name, "Lead Identification Areas"] = normalized
#         df.loc[df["Company Name"] == company_name, "Timestamp"] = now_str
#     output = BytesIO()
#     df.to_excel(output, index=False)
#     output.seek(0)
#     blob_service_client = get_blob_service_client()
#     upload_excel_to_blob(blob_service_client, LEAD_EXCEL_CONTAINER_NAME, LEAD_EXCEL_BLOB_NAME, output.getvalue())
#     return {a.strip() for a in normalized.split(',') if a.strip()}

import logging
import os
import pandas as pd
from datetime import datetime
from typing import Optional, Set
from io import BytesIO
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from utils import normalize_areas_string

# Local env
load_dotenv()

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
LEAD_EXCEL_CONTAINER_NAME = "potentiallist"
LEAD_EXCEL_BLOB_NAME = "leads_tracking.xlsx"
TOKEN_CONTAINER_NAME = "potentiallist"

def get_blob_service_client() -> BlobServiceClient:
    return BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)


def download_excel_from_blob(blob_service_client: BlobServiceClient, container_name: str, blob_name: str) -> Optional[BytesIO]:
    try:
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)
        download_stream = blob_client.download_blob()
        return BytesIO(download_stream.readall())
    except Exception as e:
        logging.error(f"Error downloading blob {blob_name}: {e}")
        return None


def upload_excel_to_blob(blob_service_client: BlobServiceClient, container_name: str, blob_name: str, data_stream: bytes) -> None:
    try:
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(data_stream, overwrite=True)
        logging.info(f"Successfully uploaded {blob_name} to blob storage.")
    except Exception as e:
        logging.error(f"Error uploading blob {blob_name}: {e}")


def get_identified_leads_df() -> pd.DataFrame:
    blob_service_client = get_blob_service_client()
    excel_data = download_excel_from_blob(blob_service_client, LEAD_EXCEL_CONTAINER_NAME, LEAD_EXCEL_BLOB_NAME)
    if excel_data:
        try:
            df = pd.read_excel(excel_data)
            return df
        except Exception as e:
            logging.error(f"Error reading Excel from blob: {e}")
            return pd.DataFrame(columns=["Company Name", "Lead Identification Areas", "Timestamp"])
    else:
        return pd.DataFrame(columns=["Company Name", "Lead Identification Areas", "Timestamp"])


def add_lead_to_excel(company_name: str, lead_areas: str) -> Set[str]:
    blob_service_client = get_blob_service_client()
    df = get_identified_leads_df()
    normalized_incoming_areas_str = normalize_areas_string(lead_areas)
    incoming_areas_set = set(normalized_incoming_areas_str.split(', ') if normalized_incoming_areas_str else set())
    existing_company_row = df[df["Company Name"] == company_name]
    truly_new_areas: Set[str] = set()

    if not existing_company_row.empty:
        existing_areas_str = existing_company_row["Lead Identification Areas"].iloc[0]
        existing_areas_set = set(existing_areas_str.split(', ') if existing_areas_str else set())
        truly_new_areas = incoming_areas_set - existing_areas_set
        if truly_new_areas:
            updated_areas_set = existing_areas_set.union(incoming_areas_set)
            updated_areas_list = sorted(list(updated_areas_set))
            updated_areas_str = ", ".join(updated_areas_list)
            df.loc[df["Company Name"] == company_name, "Lead Identification Areas"] = updated_areas_str
            df.loc[df["Company Name"] == company_name, "Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            output = BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)
            upload_excel_to_blob(blob_service_client, LEAD_EXCEL_CONTAINER_NAME, LEAD_EXCEL_BLOB_NAME, output.getvalue())
            logging.info(f"Company '{company_name}' updated with new lead areas: {', '.join(sorted(list(truly_new_areas)))}.")
        else:
            logging.info(f"Company '{company_name}' already exists with these lead areas. No update needed.")
    else:
        new_entry = pd.DataFrame([{
            "Company Name": company_name,
            "Lead Identification Areas": normalized_incoming_areas_str,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        df = pd.concat([df, new_entry], ignore_index=True)
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        upload_excel_to_blob(blob_service_client, LEAD_EXCEL_CONTAINER_NAME, LEAD_EXCEL_BLOB_NAME, output.getvalue())
        logging.info(f"New company '{company_name}' added as a lead with areas: {normalized_incoming_areas_str}.")
        truly_new_areas = incoming_areas_set

    return truly_new_areas