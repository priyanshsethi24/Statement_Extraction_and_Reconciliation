# This file holds the master prompt for GPT-4.
TABLE_EXTRACTION_PROMPT = """
Your task is to act as an expert data extraction system. You will be given a user's configuration and a block of messy text containing one or more tables. Your job is to extract data ONLY for the table specified by the `entity_name` in the user's configuration.

**Your Instructions:**

1.  **Identify the Target Table:** Find the section in the messy text that corresponds to the `entity_name` from the user's configuration.
2.  **Extract Specific Columns:** From that table section, extract the data for the columns listed in the user's configuration. Ensure the output columns are in the exact same order as specified.
3.  **Include Summary Lines:** After the main data rows, identify and include any summary or "total" lines that belong to that specific table.
4.  **Format the Output:** Return your response as a single, valid JSON object with one key: "table_data". The value must be a list of lists.
    *   The first inner list MUST be the header row, using the exact column names from the user's configuration.
    *   All subsequent inner lists are the data rows.
    *   If the requested table is not found in the text, return an empty list: `{{"table_data": []}}`.  # --- THIS IS THE FIX ---

---
**User Configuration (What to extract):**

{user_config_json}


---
**Messy Table Text (Where to extract from):**


{raw_table_text}



---
**Your JSON Output:**
"""

