# from fastapi import APIRouter, HTTPException
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel, ConfigDict 
# from typing import List, Dict, Any
# import os
# import shutil
# import subprocess
# import sys
# import pandas as pd
# import requests

# from common.logs import logger
# from common.s3_operations import S3Helper
# from scripts.dolphin_html_table_to_excel import dolphin_html_table_to_excel
# from scripts.split_dolphin_table import extract_tables_from_entity_list

# TMP_DIR = '/tmp'
# if not os.path.exists(TMP_DIR):
#     os.makedirs(TMP_DIR)

# class EntityRequest(BaseModel):
#     # Added model_config to resolve the Pydantic namespace warning
#     model_config = ConfigDict(protected_namespaces=())

#     file_list: List[str]
#     entity_list: List[Dict[str, Any]]
#     model_name: str = "gpt-4-turbo"

# router = APIRouter()

# @router.post("/extract_entity")
# async def extract_entities(request: EntityRequest):
#     doc_extractor_url = os.getenv("DOC_EXTRACTOR_URL")
#     if not doc_extractor_url:
#         raise HTTPException(status_code=500, detail="DOC_EXTRACTOR_URL is not set in environment.")

#     final_results = []
#     token_dict = {"input": 0, "output": 0, "total": 0}

#     if len(request.file_list) != 1:
#         raise HTTPException(status_code=400, detail="Please provide exactly one S3 path in file_list.")
    
#     s3_path = request.file_list[0]
#     local_file_path = None
    
#     try:
#         logger.info(f"--- Starting Hybrid Extraction for {s3_path} ---")

#         table_entities_config = []
#         non_table_entities_config = []
#         for entity in request.entity_list:
#             if entity.get('entity_type', '').lower() == 'table':
#                 table_entities_config.append(entity)
#             else:
#                 non_table_entities_config.append(entity)
        
#         if table_entities_config:
#             logger.info(f"Processing {len(table_entities_config)} table entities with local Dolphin pipeline...")
            
#             if s3_path.startswith('s3://'):
#                 s3_bucket = s3_path.split('/')[2]
#                 s3_helper = S3Helper(s3_bucket)
#                 s3_key = '/'.join(s3_path.split('/')[3:])
#                 local_file_path = os.path.join(TMP_DIR, os.path.basename(s3_key))
#                 s3_helper.download_file_from_s3(s3_key, local_file_path)
                
#             output_dir = "/opt/Dolphin/Statement_Extraction_and_Reconciliation/results"
#             dolphin_script = os.path.abspath("demo_page.py")
#             config_path = os.path.abspath("config/Dolphin.yaml")
#             cmd = [sys.executable, dolphin_script, "--input_path", local_file_path, "--save_dir", output_dir, "--config", config_path]
#             subprocess.run(cmd, check=True)

#             json_name = os.path.basename(local_file_path).replace('.pdf', '.json')
#             excel_path = os.path.join(output_dir, f"{os.path.basename(local_file_path)}_tables.xlsx")
#             dolphin_html_table_to_excel(os.path.join(output_dir, "recognition_json", json_name), excel_path)
            
#             df = pd.read_excel(excel_path, sheet_name=0, header=None)
#             extracted_tables = extract_tables_from_entity_list(df, table_entities_config)
            
#             for name, table_df in extracted_tables:
#                 headers = table_df.columns.tolist()
#                 rows = table_df.values.tolist()
                
#                 table_data = [headers] + rows
                
#                 table_object = {
#                     "entity_name": name,
#                     "table_data": table_data,
#                     "entity_type": "Table"
#                 }
#                 final_results.append(table_object)

#             logger.info("Dolphin table processing finished.")
            
#         if non_table_entities_config:
#             logger.info(f"Processing {len(non_table_entities_config)} non-table entities via external API...")
            
#             formatted_entity_list = []
#             for entity in non_table_entities_config:
#                 name = entity.get("entity_name")
#                 if not name:
#                     continue
                
#                 # Handle both a single alias string or a list of aliases
#                 aliases = entity.get("entity_alias", [])
#                 if isinstance(aliases, str) and aliases:
#                     aliases = [aliases]
#                 elif not isinstance(aliases, list):
#                     aliases = []
                    
#                 all_parts = [name] + [alias for alias in aliases if alias]
                
#                 # The external API expects the format (Name/Alias1/Alias2)
#                 formatted_string = f"({'/'.join(all_parts)})"
#                 formatted_entity_list.append(formatted_string)

#             payload = {
#                 "file_list": [s3_path],
#                 "entity_list": formatted_entity_list,
#                 "model_name": request.model_name 
#             }
            
#             response = requests.post(doc_extractor_url, json=payload)
#             response.raise_for_status()
            
#             api_data = response.json().get('data', {})
#             token_dict.update(api_data.get('token_dict', {}))
            
#             external_results = api_data.get('entity_table_list', [])
#             if external_results:
#                 entity_table = external_results[0].get('entity_table', [])
#                 for item in entity_table:
#                     entity_name_formatted = item.get('entity_type')
#                     entity_values = item.get('values')

#                     if entity_name_formatted and entity_values:
#                         # Reformat non-table entity output
#                         entity_name_clean = entity_name_formatted.strip('()').split('/')[0]
#                         entity_value = entity_values[0]

#                         # Find the original entity_type from the request config for this entity
#                         original_entity = next((e for e in non_table_entities_config if e['entity_name'] == entity_name_clean), None)
#                         entity_type = original_entity.get('entity_type', 'Unknown') if original_entity else 'Unknown'

#                         # Create the final non-table object
#                         non_table_object = {
#                             "entity_name": entity_name_clean,
#                             "entity_value": entity_value,
#                             "entity_type": entity_type
#                         }
#                         final_results.append(non_table_object)
#                     else:
#                         logger.warning(f"Received malformed item from external API, skipping: {item}")

            
#         return JSONResponse({
#             "message": "Entity Extraction successful",
#             "data": {
#                 "file_name": os.path.basename(s3_path),
#                 "token_dict": token_dict,
#                 "entity_table_list": final_results
#             }
#         }, status_code=200)

#     except requests.exceptions.RequestException as e:
#         logger.error(f"External API call failed: {e}")
#         return JSONResponse({"message": f"External API call failed: {e}"}, status_code=502)
        
#     except Exception as e:
#         logger.error(f"An unexpected error occurred during extraction: {e}", exc_info=True)
#         return JSONResponse({"message": f"Entity Extraction failed: {e}"}, status_code=500)

#     finally:
#         if local_file_path and os.path.exists(local_file_path):
#             os.remove(local_file_path)
#             logger.info(f"Cleaned up temporary file: {local_file_path}")



from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict 
from typing import List, Union, Dict, Any
import os
import shutil
import subprocess
import sys
import requests
import json
import html
from urllib.parse import urljoin

from common.logs import logger
from common.s3_new_operations import S3HelperNew
from common.s3_operations import S3Helper
from scripts.llm_utils import extract_table_with_llm

TMP_DIR = '/tmp'
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)

class EntityRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    file_list: List[Union[str,dict]]
    entity_list: List[Dict[str, Any]]
    model_name: str = "gpt-4-turbo"

router = APIRouter()

@router.post("/extract_entity")
async def extract_entities(request: EntityRequest):
    doc_extractor_url = os.getenv("DOC_EXTRACTOR_URL")
    if not doc_extractor_url:
        raise HTTPException(status_code=500, detail="DOC_EXTRACTOR_URL is not set in environment.")

    final_results = []
    token_dict = {"input": 0, "output": 0, "total": 0}

    if len(request.file_list) != 1:
        raise HTTPException(status_code=400, detail="Please provide exactly one S3 path in file_list.")
    
    s3_path = request.file_list[0]
    local_file_path = None
    
    try:

        logger.info(f"--- Starting LLM-Driven Hybrid Extraction for {s3_path} ---")

        table_entities_config = [e for e in request.entity_list if e.get('entity_type', '').lower() == 'table']
        non_table_entities_config = [e for e in request.entity_list if e.get('entity_type', '').lower() != 'table']

        if type(s3_path) == dict:
            s3_helper = S3HelperNew()
            s3_key = s3_path['s3_key']
            s3_bucket = s3_path['s3_bucket']
            s3_version_id = s3_path['s3_version_id']
            file_name_with_ext = os.path.basename(s3_key)
            name_without_ext, ext = os.path.splitext(file_name_with_ext)
            # ts = str(time.time()).replace('.', '_')
            # local_key = list(s3_key.split('.'))
            # local_key[0] += f'_{ts}'
            # local_key = '.'.join(local_key)
            local_file_path = os.path.join(TMP_DIR, file_name_with_ext)
            s3_helper.download_file_from_s3(s3_bucket, s3_key, s3_version_id ,local_file_path)
        else:
            if s3_path.startswith('s3://'):
                s3_bucket = s3_path.split('/')[2]
                s3_helper = S3Helper(s3_bucket)
                s3_key = '/'.join(s3_path.split('/')[3:])
                local_file_path = os.path.join(TMP_DIR, os.path.basename(s3_key))
                s3_helper.download_file_from_s3(s3_key, local_file_path)

        # TABLE EXTRACTION (LLM-Powered) ---
        if table_entities_config:
            logger.info(f"Processing {len(table_entities_config)} tables with internal LLM pipeline...")
            
            output_dir = "results"
            dolphin_script = os.path.abspath("demo_page.py")
            config_path = os.path.abspath("config/Dolphin.yaml")
            batch_size  = "2"
            cmd = [sys.executable, dolphin_script, "--input_path", local_file_path, "--save_dir", output_dir, "--config", config_path, "--max_batch_size", batch_size]
            subprocess.run(cmd, check=True)

            json_name = os.path.basename(local_file_path).replace('.pdf', '.json')
            json_path = os.path.join(output_dir, "recognition_json", json_name)
            
            with open(json_path, 'r', encoding='utf-8') as f:
                dolphin_data = json.load(f)

            
        
            full_document_text = ""
            for page in dolphin_data.get('pages', []):
                for elem in page.get('elements', []):
                    # Unescape HTML entities like &amp; and add the text
                    full_document_text += html.unescape(elem.get('text', '')) + "\n"
            
            if not full_document_text:
                raise Exception("Could not extract any text from the document using Dolphin.")

            for table_config in table_entities_config:
                logger.info(f"Extracting table '{table_config['entity_name']}' using LLM...")
                # We now pass the full document text to the LLM
                table_data = await extract_table_with_llm(table_config, full_document_text, request.model_name)
                
                if table_data:
                    final_results.append({
                        "entity_name": table_config['entity_name'],
                        "table_data": table_data,
                        "entity_type": "Table"
                    })
                else:
                    logger.warning(f"LLM failed to extract data for table: {table_config['entity_name']}")
            logger.info("LLM table processing finished.")
        
        #  NON-TABLE EXTRACTION (Using the existing external API)
        if non_table_entities_config:
            logger.info(f"Processing {len(non_table_entities_config)} non-table entities via external API...")
            
            formatted_entity_list = []
            for entity in non_table_entities_config:
                name = entity.get("entity_name")
                if not name: continue
                aliases = entity.get("entity_alias", [])
                if isinstance(aliases, str) and aliases: aliases = [aliases]
                elif not isinstance(aliases, list): aliases = []
                all_parts = [name] + [alias for alias in aliases if alias]
                formatted_string = f"({'/'.join(all_parts)})"
                formatted_entity_list.append(formatted_string)

            payload = {"file_list": [s3_path], "entity_list": formatted_entity_list, "model_name": request.model_name}
            
            api_endpoint = urljoin(doc_extractor_url, "extract_entity")
            response = requests.post(api_endpoint, json=payload)
            response.raise_for_status()
            
            api_data = response.json().get('data', {})
            token_dict.update(api_data.get('token_dict', {}))
            
            external_results = api_data.get('entity_table_list', [])
            if external_results:
                entity_table = external_results[0].get('entity_table', [])
                for item in entity_table:
                    entity_name_formatted = item.get('entity_type')
                    entity_values = item.get('values')
                    if entity_name_formatted and entity_values:
                        entity_name_clean = entity_name_formatted.strip('()').split('/')[0]
                        entity_value = entity_values[0]
                        original_entity = next((e for e in non_table_entities_config if e['entity_name'] == entity_name_clean), None)
                        entity_type = original_entity.get('entity_type', 'Unknown') if original_entity else 'Unknown'
                        non_table_object = { "entity_name": entity_name_clean, "entity_value": entity_value, "entity_type": entity_type }
                        final_results.append(non_table_object)
                    else:
                        logger.warning(f"Received malformed item from external API, skipping: {item}")

        return JSONResponse({"message": "Entity Extraction successful", "data": {"file_name": os.path.basename(s3_path), "token_dict": token_dict, "entity_table_list": final_results}}, status_code=200)

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return JSONResponse({"message": f"An unexpected error occurred: {e}"}, status_code=500)

    finally:
        if local_file_path and os.path.exists(local_file_path):
            os.remove(local_file_path)
            logger.info(f"Cleaned up temporary file: {local_file_path}")

