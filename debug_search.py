import requests
from bs4 import BeautifulSoup

def debug_search(query):
    print(f"Testing query: {query}")
    
    # 1. Wikipedia Test
    print("\n--- Wikipedia Test ---")
    search_term = query.lower().replace('who is ', '').strip()
    print(f"Cleaned term: {search_term}")
    
    wiki_url = "https://en.wikipedia.org/w/api.php"
    
    # Current implementation (direct title lookup)
    params_direct = {
        'action': 'query',
        'format': 'json',
        'prop': 'extracts',
        'exintro': True,
        'explaintext': True,
        'redirects': 1,
        'titles': search_term
    }
    try:
        resp = requests.get(wiki_url, params=params_direct, timeout=5)
        data = resp.json()
        pages = data.get('query', {}).get('pages', {})
        print(f"Direct lookup result keys: {list(pages.keys())}")
        if '-1' in pages:
            print("Direct lookup failed (Page -1)")
        else:
            print("Direct lookup SUCCESS")
    except Exception as e:
        print(f"Direct lookup error: {e}")

    # Proposed implementation (Search first)
    print("\n--- Wikipedia Search First Test ---")
    params_search = {
        'action': 'opensearch',
        'search': search_term,
        'limit': 1,
        'namespace': 0,
        'format': 'json'
    }
    try:
        resp = requests.get(wiki_url, params=params_search, timeout=5)
        data = resp.json()
        print(f"Search result: {data}")
        if data and len(data) > 1 and data[1]:
            best_title = data[1][0]
            print(f"Found best title: {best_title}")
        else:
            print("Search found nothing")
    except Exception as e:
        print(f"Search error: {e}")

    # 2. DuckDuckGo Test
    print("\n--- DuckDuckGo Test ---")
    ddg_url = "https://api.duckduckgo.com/"
    ddg_params = {
        'q': query,
        'format': 'json',
        'no_html': 1,
        'skip_disambig': 1
    }
    try:
        resp = requests.get(ddg_url, params=ddg_params, timeout=5)
        data = resp.json()
        print(f"AbstractText: {data.get('AbstractText')}")
        print(f"Answer: {data.get('Answer')}")
    except Exception as e:
        print(f"DDG error: {e}")

    # 3. Google Test
    print("\n--- Google Test ---")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}&hl=en"
    try:
        resp = requests.get(search_url, headers=headers, timeout=8)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        selectors = [
            'div.hgKElc', 'span.hgKElc', 'div.IZ6rdc', 'span.aCOpRe', 
            'div.kno-rdesc span', 'div.V3FYCf', 'div.ayRjaf',
            'div.Z0LcW', # Added new one for direct answers
            'div.LGOjhe' # Another common one
        ]
        
        found = False
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                print(f"✅ Found selector: {selector} -> {elements[0].get_text(strip=True)[:50]}...")
                found = True
        
        if not found:
            print("❌ No selectors matched")
            # Print some classes to debug
            print("Top classes found:")
            divs = soup.find_all('div', class_=True)
            classes = [c for div in divs for c in div.get('class', [])]
            from collections import Counter
            print(Counter(classes).most_common(10))
            
    except Exception as e:
        print(f"Google error: {e}")

if __name__ == "__main__":
    debug_search("who is the greatest footballer in India")
