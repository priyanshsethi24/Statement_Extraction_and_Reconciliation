import os
import requests
import json
from typing import List, Dict, Any
from litellm import completion

from prompts.table_extraction_prompt import TABLE_EXTRACTION_PROMPT 

async def extract_table_with_llm(
    table_config: Dict[str, Any], 
    raw_html_text: str, 

    model_name: str
) -> List[List[Any]]:
    """
    Uses litellm to extract and structure a single table from raw text.
    """
    final_prompt = TABLE_EXTRACTION_PROMPT.format(
        user_config_json=json.dumps(table_config, indent=2),
        raw_table_text=raw_html_text
    )

    messages = [
        {"role": "system", "content": "You are an expert data extraction system that only responds with valid JSON."},
        {"role": "user", "content": final_prompt}
    ]
    
    try:
        response = completion(
            model=model_name,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=2048
        )
        
        llm_output_str = response.choices[0].message.content
        parsed_data = json.loads(llm_output_str)
        
        return parsed_data.get("table_data", [])

    except Exception as e:
        print(f"CRITICAL ERROR during LLM table extraction: {e}")
        return []
