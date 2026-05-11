import json
import sys
from urllib.parse import quote_plus
from typing import Dict, Optional, List

# Ensure UTF-8 output on Windows terminals
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Fallback for older python versions
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

from browser.manager import BrowserManager
from extraction.parsers import SerpParser
from extraction.utils import human_delay
from config.settings import (
    RESULTS_PER_PAGE, DEFAULT_TIMEOUT, SELECTOR_TIMEOUT,
    MIN_PAGE_DELAY, MAX_PAGE_DELAY, DEPERSONALIZATION_PARAMS
)


def search(query: str, num_results: int = 10, *, headless: bool = True,
           proxy: Optional[Dict] = None) -> Dict:
    """
    Scrape Google search results.

    Returns a Serper-compatible JSON dict:
    {
        "organic": [...],
        "peopleAlsoAsk": [...],
        "relatedSearches": [...]
    }
    """
    organic = []
    people_also_ask = []
    related_searches = []
    
    # Using 20 results per request is more stable than 100
    results_per_request = 20

    with BrowserManager(headless=headless, proxy=proxy) as manager:
        try:
            start_index = 0
            consecutive_empty_pages = 0
            
            while len(organic) < num_results and consecutive_empty_pages < 2:
                encoded_query = quote_plus(query)
                # Build URL - AI Overview often needs a "clean" or personalized URL
                url = f"https://www.google.com/search?q={encoded_query}"
                if num_results > 10 or start_index > 0:
                    url += f"&num={results_per_request}&start={start_index}"
                
                print(f"Navigating to: {url}...")
                manager.page.goto(url, timeout=DEFAULT_TIMEOUT)
                
                # Check for CAPTCHA
                captcha_selectors = "iframe[src*='recaptcha'], #captcha-form, #recaptcha, form[action*='sorry']"
                if manager.page.locator(captcha_selectors).count() > 0:
                    print("⚠  CAPTCHA detected — please solve it in the browser window...")
                    manager.page.wait_for_selector(".g, div.MjjYud", state="attached", timeout=120_000)
                    print("✓  CAPTCHA solved, continuing...")
                
                try:
                    manager.page.wait_for_selector(".g, div.MjjYud", state="attached", timeout=SELECTOR_TIMEOUT)
                except Exception as e:
                    # If we already have results, we might just be at the end of the SERP
                    if organic:
                        print("No more results found or timeout reached.")
                        break
                    
                    with open("debug_google_fail.html", "w", encoding="utf-8") as f:
                        f.write(manager.page.content())
                    
                    if manager.page.locator("text='No results found'").count() > 0:
                        print("Google says: No results found.")
                        break
                    raise Exception(f"Failed to find results on first page. Error: {e}")

                # Scroll to load lazy results
                print(f"Scrolling page {start_index // results_per_request + 1}...")
                prev_height = 0
                for i in range(3): 
                    manager.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    human_delay(0.5, 1.0)
                    new_height = manager.page.evaluate("document.body.scrollHeight")
                    if new_height == prev_height:
                        break
                    prev_height = new_height
                
                manager.page.evaluate("window.scrollTo(0, 0)")

                # Extract supplementary data (Top of first page only)
                if start_index == 0:
                    # AI Overview expansion
                    try:
                        # Try to click "Show more" for AI Overview
                        show_more = manager.page.locator('div[aria-label="Show more AI Overview"]').first
                        if show_more.count() > 0 and show_more.is_visible():
                            print("Expanding AI Overview...")
                            show_more.click(timeout=5000)
                            # Wait for expansion to animate and load content
                            human_delay(2.5, 3.5)
                        
                        # # Try to click "Show all" for links
                        # show_all = manager.page.locator('div[aria-label="Show all related links"], div:text("Show all")').first
                        # if show_all.count() > 0 and show_all.is_visible():
                        #     show_all.click(timeout=2000)
                        #     human_delay(0.3, 0.6)
                    except:
                        pass

                    search_info = SerpParser.extract_search_information(manager.page)

                    ai_overview = SerpParser.extract_ai_overview(manager.page)
                    answer_box = SerpParser.extract_answer_box(manager.page)

                # Extract organic results
                elements = manager.page.locator(".g, div.MjjYud").all()
                before_count = len(organic)
                
                for element in elements:
                    if len(organic) >= num_results:
                        break
                    result = SerpParser.extract_organic_result(element)
                    if result:
                        # Deduplicate by link
                        if any(o['link'] == result['link'] for o in organic):
                            continue
                        result["position"] = len(organic) + 1
                        organic.append(result)

                if len(organic) == before_count:
                    consecutive_empty_pages += 1
                else:
                    consecutive_empty_pages = 0

                # Extract bottom-page data
                people_also_ask.extend(
                    SerpParser.extract_people_also_ask(manager.page)
                )
                related_searches.extend(
                    SerpParser.extract_related_searches(manager.page)
                )

                if len(organic) < num_results:
                    start_index += results_per_request
                    human_delay(MIN_PAGE_DELAY, MAX_PAGE_DELAY)
                else:
                    break

        except Exception as e:
            print(f"Scraping interrupted: {e}")
            import traceback
            traceback.print_exc()

    # Build Serper-compatible response
    response = {}
    
    if 'search_info' in locals() and search_info:
        response["searchInformation"] = search_info
        
    if 'ai_overview' in locals() and ai_overview:
        response["aiOverview"] = ai_overview
    
    if 'answer_box' in locals() and answer_box:
        response["answerBox"] = answer_box
        
    response["organic"] = organic[:num_results]
    
    if people_also_ask:
        paa_seen = set()
        unique_paa = []
        for paa in people_also_ask:
            if paa["question"] not in paa_seen:
                paa_seen.add(paa["question"])
                unique_paa.append(paa)
        response["peopleAlsoAsk"] = unique_paa
        
    if related_searches:
        seen = set()
        unique = []
        for rs in related_searches:
            if rs["query"] not in seen:
                seen.add(rs["query"])
                unique.append(rs)
        response["relatedSearches"] = unique
    return response

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Google SERP Scraper (Serper compatible)")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--num", type=int, default=10, help="Number of results needed (default: 10)")
    parser.add_argument("--headful", action="store_true", help="Run in headful mode (visible)")
    parser.add_argument("--output-file", type=str, default="data.json", help="Output file to save the results to (default: data.json in the current directory)")
    args = parser.parse_args()
    
    print(f"Searching for: {args.query} (Target: {args.num} results)...")
    result = search(args.query, num_results=args.num, headless=not args.headful)
    
    output_file = args.output_file
    print(f"DEBUG: output file : {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully scraped {len(result.get('organic', []))} organic results.")
    print(f"Results saved to {output_file}")
