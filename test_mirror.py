import json
from scraper import search

query = 'python web scraping "nonexistentkeyword_999_xyz_123"'
print(f"Testing query: {query}")
result = search(query, num_results=10, headless=False)

with open("test_result.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

attr_found = any('attributes' in o for o in result.get('organic', []))
print(f"Test complete. Attributes found: {attr_found}")
if attr_found:
    print("Example attribute:", [o.get('attributes') for o in result.get('organic', []) if 'attributes' in o][0])
