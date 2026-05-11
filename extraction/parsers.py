import re
from typing import Dict, List, Optional
from extraction.utils import extract_date_from_snippet, human_delay, process_url


class SerpParser:
    """Parses Google SERP elements into Serper-compatible format."""

    @staticmethod
    def extract_search_information(page) -> Dict:
        """Extract search metadata like 'Showing results for'."""
        info = {}
        # "Showing results for" link
        fprsl = page.locator("#fprsl")
        if fprsl.count() > 0:
            info["showingResultsFor"] = fprsl.inner_text()
        return info

    @staticmethod
    def extract_ai_overview(page) -> Optional[Dict]:
        """Extract Google AI Overview content."""
        # Container - search by text content first as ARIA labels vary
        container = page.locator('div.pWvJNd > div.mZJni.Dn7Fzd').first
        
            
        try:
            # Main text content
            # Expanded text container is often div.V_8y0c or div[jsname="Wv56cd"]
            text_selectors = ["div.V_8y0c", "div[jsname='Wv56cd']", ".C93uN", ".P6O19b"]
            full_text = ""
            
            # for sel in text_selectors:
            #     el = container.locator(sel).first
            #     if el.count() > 0:
            #         full_text = el.inner_text(timeout=1000).strip()
            #         if full_text: break
            human_delay(1.3,2.4)
            full_text = container.inner_text(timeout=3000).strip()
            
            pattern = r'\n[^\n]{1,60}(?:\n[^\n]{1,60})?\n\s*\+\d+(?=\n|$)'
            full_text = re.sub(pattern, '', full_text).strip()
            
            # Extract links/sources
            links = []
            seen_links = set()
            
            try:
                page.evaluate("document.querySelector('div[aria-label=\"Show all related links\"]').click()")
                human_delay(0.5, 1.0)
            except Exception as e:
                print("DEBUG: error clicking show all related links:", e)
            
            containers = page.locator('li.CyMdWb').all()
            # links = page.locator("a.NDNGvf").all()
            # els = page.locator("div.T5ny9d").all()
            for container in containers:
                try:
                    href = container.locator("a.NDNGvf").get_attribute("href", timeout=500)
                    if not href or href.startswith("/search") or href in seen_links:
                        continue
                        
                    # Extract title from the card
                    title = container.locator(".Nn35F.Kv3dbb").inner_text(timeout=500).strip()
                    if not title:
                        title = href.inner_text(timeout=2000).strip().split('\n')[0] or href.get_attribute("aria-label") or ""
                        
                    link_details_section = container.locator('.T5ny9d').locator('span')
                    date = link_details_section.nth(1).inner_text(timeout=500)
                    description = link_details_section.last.inner_text(timeout=500).strip('\n')
                    link = {
                        "title": title,
                        "link": process_url(href),
                        "description": description
                    }
                    if date[:5] != description[:5]:
                        link["date"] = date
                    links.append(link)
                    seen_links.add(href)
                except Exception as e:
                    print("DEBUG: error from ai overview : ",e)
            
            if not full_text and not links:
                return None
                
            return {
                "text": full_text,
                "links": links
            }
        except Exception as e:
            print("DEBUG: error from ai overview : ",e) 
            return None

    @staticmethod
    def extract_answer_box(page) -> Optional[Dict]:
        """Extract featured snippet (answer box)."""
        # Common containers for answer boxes:
        # .hp_v-c (Knowledge Graph / Featured Snippet)
        # .g.mnr-c.kp-blk (Knowledge Panel)
        # .xpdopen (Snippet expansion)
        # [data-attrid="wa:/description"] (Specific answer text)
        selectors = [".hp_v-c", ".g.mnr-c.kp-blk", ".xpdopen", "[data-attrid='wa:/description']"]
        container = None
        for sel in selectors:
            el = page.locator(sel).first
            if el.count() > 0:
                container = el
                break
        
        if not container:
            return None
            
        try:
            # Title & Link
            title_el = container.locator("h3").first
            link_el = container.locator("a").first
            
            # Snippet text
            # Often .VwiC3b or specific answer classes
            snippet_selectors = [".VwiC3b", ".hgKElc", ".Z0LcW", ".LGOO1", ".dDoNo"]
            snippet_text = ""
            for sel in snippet_selectors:
                el = container.locator(sel).first
                if el.count() > 0:
                    snippet_text = el.inner_text(timeout=1000)
                    break
            
            if not snippet_text and title_el.count() == 0:
                return None

            res = {
                "snippet": snippet_text,
                "title": title_el.inner_text(timeout=1000) if title_el.count() > 0 else "",
                "link": process_url(link_el.get_attribute("href", timeout=1000)) if link_el.count() > 0 else ""
            }
            
            # Highlighted text
            highlights = container.locator("b, em, strong").all()
            if highlights:
                # Deduplicate and clean
                h_texts = sorted(list(set([h.inner_text().strip() for h in highlights if len(h.inner_text()) > 2])))
                if h_texts:
                    res["snippetHighlighted"] = h_texts
                
            return res
        except:
            return None

    @staticmethod
    def extract_organic_result(element) -> Optional[Dict]:
        """Extract a single organic result. Returns Serper-format dict or None."""
        try:
            # Filter unwanted elements
            is_unwanted = element.evaluate("""element => {
                return !!element.closest('[data-initq]') ||
                    element.closest('[data-text-ad="1"]') ||
                    element.closest('.related-question-pair')
            }""")
            if is_unwanted:
                return None

            # Title
            h3 = element.locator("h3")
            if h3.count() == 0:
                return None
            title = h3.first.inner_text(timeout=2000)
            
            # Link
            link_el = element.locator("a").first
            if link_el.count() == 0:
                return None
            href = link_el.get_attribute("href", timeout=2000)
            if not href or href.startswith("/search"):
                return None
            link = process_url(href)

            # Snippet
            snippet_selectors = [".VwiC3b", ".hgKElc", ".yD70Yd", ".L5699c", ".MUwY0b", ".s3v9rd"]
            raw_snippet = ""
            for selector in snippet_selectors:
                el = element.locator(selector).first
                if el.count() > 0:
                    raw_snippet = el.inner_text(timeout=1000)
                    break
            
            date, snippet = extract_date_from_snippet(raw_snippet)

            result = {
                "title": title,
                "link": link,
                "snippet": snippet,
                "position": None,
            }
            if date:
                result["date"] = date

            # Sitelinks
            try:
                sitelinks = SerpParser._extract_sitelinks(element)
                if sitelinks:
                    result["sitelinks"] = sitelinks
            except:
                pass
                
            # Attributes (e.g. "Missing: practices")
            try:
                # Search for "Missing: " text directly in the element
                # Often in a span or div with specific styling
                attr_text = element.evaluate("""el => {
                    const spans = Array.from(el.querySelectorAll('span, div, a'));
                    const missing = spans.find(s => s.innerText.includes('Missing:'));
                    if (missing) {
                        // Extract just the part after 'Missing:' or the specific line
                        const lines = missing.innerText.split('\\n');
                        const targetLine = lines.find(l => l.includes('Missing:'));
                        return targetLine ? targetLine.replace('Missing:', '').trim() : missing.innerText.replace('Missing:', '').trim();
                    }
                    return null;
                }""")
                if attr_text:
                    result["attributes"] = {"Missing": attr_text}
            except:
                pass

            return result
        except Exception:
            return None

    @staticmethod
    def _extract_sitelinks(element) -> Optional[List[Dict]]:
        """Extract sitelinks in Serper format: {title, link}."""
        # Sitelinks are usually in a specific grid or list
        # Check for inline sitelinks (.OSu99) or expanded ones
        links = element.locator("a").all()
        if len(links) <= 1:
            return None
            
        sitelinks = []
        seen_links = {process_url(links[0].get_attribute("href"))} # skip main link
        
        for link_el in links[1:]:
            try:
                href = process_url(link_el.get_attribute("href", timeout=500))
                text = link_el.inner_text().strip()
                if href and text and href not in seen_links and not href.startswith("/search"):
                    # Basic filter to ensure it's a sitelink and not a random UI link
                    if len(text) > 2 and len(text) < 100:
                        sitelinks.append({"title": text, "link": href})
                        seen_links.add(href)
            except:
                continue
                
        return sitelinks[:4] if sitelinks else None # Serper usually shows 4 max

    @staticmethod
    def extract_people_also_ask(page) -> List[Dict]:
        """Extract PAA questions. Returns Serper-format list."""
        questions = []
        container = page.locator(".LQCGqc")
        if container.count() == 0:
            return questions

        for q_el in page.locator('[jsname="yEVEwb"]').all():
            try:
                question_text = q_el.inner_text()
                q_el.scroll_into_view_if_needed()
                # human_delay(0.05, 0.3)
                q_el.click()
                # human_delay(0.1, 1.0)

                # Use a specific timeout for the answer snippet
                answer = page.wait_for_selector(".hgKElc", timeout=5000)
                answer_container = q_el.locator(".related-question-pair")

                questions.append({
                    "question": question_text,
                    "snippet": answer.inner_text(),
                    "title": answer_container.locator("h3").inner_text(),
                    "link": process_url(
                        answer_container.locator("a").get_attribute("href")
                    ),
                })
                q_el.click()  # Collapse
                human_delay(0.05, 0.5)
            except Exception:
                # If one fails, we just skip it or log it
                continue

        return questions

    @staticmethod
    def extract_related_searches(page) -> List[Dict]:
        """Extract related searches. Returns Serper-format: [{query: "..."}]."""
        results = []
        container = page.locator(".EIaa9b")
        if container.count() == 0:
            return results
        for link in container.locator("a").all():
            text = link.inner_text().strip().lower()
            if text:
                results.append({"query": text})
        return results
