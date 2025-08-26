# import json
# import pandas as pd
# import html
# import os

# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))


# def dolphin_html_table_to_excel(json_path, excel_path):
#     with open(json_path, 'r', encoding='utf-8') as f:
#         dolphin_json = json.load(f)

#     all_tables = []
#     for page_idx, page in enumerate(dolphin_json.get('pages', [])):
#         elements = page.get('elements', [])
#         for elem_idx, elem in enumerate(elements):
#             if elem.get('label') == 'tab':
#                 html_table = elem.get('text', '')
#                 if not html_table:
#                     continue
#                 html_table_unescaped = html.unescape(html_table)
#                 try:
#                     dfs = pd.read_html(html_table_unescaped)
#                     for i, df in enumerate(dfs):
#                         sheet_name = f"Page{page_idx+1}_Table{elem_idx+1}_{i+1}"
#                         all_tables.append((sheet_name, df))
#                 except Exception as e:
#                     print(f"Error parsing HTML table on page {page_idx+1}, element {elem_idx+1}: {e}")

#     if all_tables:
#         with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
#             for sheet_name, df in all_tables:
#                 df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
#         print(f"Exported {len(all_tables)} tables to {excel_path}")
#     else:
#         print("No tables found in Dolphin JSON output.")
#     return

# if __name__ == "__main__":
#     json_path = os.path.join(PROJECT_ROOT, 'results', 'recognition_json', 'sample_statement3.json')
#     excel_path = os.path.join(PROJECT_ROOT, 'dolphin_extracted_tables3.xlsx')
#     dolphin_html_table_to_excel(json_path, excel_path)
