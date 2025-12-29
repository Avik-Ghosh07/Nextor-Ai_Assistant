"""
Web Search Service - Handles web searching operations
"""

import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

# Import BeautifulSoup (optional dependency for web scraping)
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


def search_web(query: str) -> Optional[str]:
    """Search the web using multiple methods: Wikipedia API, DuckDuckGo Instant Answer, and Google scraping."""
    try:
        logger.info(f"🔍 Searching web for: {query}")
        
        # Method 1: Try Wikipedia API
        result = _search_wikipedia(query)
        if result:
            return result
        
        # Method 2: Try DuckDuckGo Instant Answer API
        result = _search_duckduckgo(query)
        if result:
            return result
        
        # Method 3: Try Google search scraping
        result = _search_google(query)
        if result:
            return result
        
        logger.error(f"❌ All web search methods failed for: {query}")
        return None
        
    except Exception as e:
        logger.error(f"❌ Web search error: {e}")
        return None


def _search_wikipedia(query: str) -> Optional[str]:
    """Search Wikipedia for information"""
    try:
        search_term = query.lower()
        search_term = search_term.replace('who is ', '').replace('who are ', '')
        search_term = search_term.replace('what is ', '').replace('what are ', '')
        search_term = search_term.replace('where is ', '').replace('where are ', '')
        search_term = search_term.replace('when was ', '').replace('when is ', '')
        search_term = search_term.replace('tell me about ', '').replace('explain ', '')
        search_term = search_term.strip()
        
        # Common name mappings
        name_mappings = {
            'amazon forest': 'Amazon rainforest',
            'amazon jungle': 'Amazon rainforest',
            'jensen wang': 'Jensen Huang',
        }
        
        wiki_title = name_mappings.get(search_term, search_term)
        wiki_url = "https://en.wikipedia.org/w/api.php"
        headers = {'User-Agent': 'NextorAI/1.0 (Educational Project; Python/requests)'}
        
        # Try direct lookup
        result = _wikipedia_lookup(wiki_url, wiki_title, headers, query)
        if result:
            return result
        
        # Try OpenSearch if direct lookup failed
        result = _wikipedia_search(wiki_url, search_term, headers, query)
        if result:
            return result
        
        logger.warning(f"⚠️ Wikipedia had no article for: {wiki_title}")
        return None
        
    except Exception as wiki_error:
        logger.warning(f"⚠️ Wikipedia search failed: {wiki_error}")
        return None


def _wikipedia_lookup(wiki_url: str, wiki_title: str, headers: dict, query: str) -> Optional[str]:
    """Perform Wikipedia direct lookup"""
    wiki_params = {
        'action': 'query',
        'format': 'json',
        'prop': 'extracts',
        'exintro': True,
        'explaintext': True,
        'redirects': 1,
        'titles': wiki_title
    }
    
    wiki_response = requests.get(wiki_url, params=wiki_params, headers=headers, timeout=8)
    wiki_response.raise_for_status()
    wiki_data = wiki_response.json()
    
    pages = wiki_data.get('query', {}).get('pages', {})
    for page_id, page in pages.items():
        if page_id != '-1' and 'extract' in page:
            extract = page['extract'].strip()
            if extract and len(extract) > 50:
                answer = _format_answer(extract, query)
                if answer:
                    logger.info(f"✅ Found Wikipedia answer for: {wiki_title}")
                    return answer
    return None


def _wikipedia_search(wiki_url: str, search_term: str, headers: dict, query: str) -> Optional[str]:
    """Search Wikipedia using OpenSearch"""
    logger.info(f"⚠️ Direct lookup failed, trying Wikipedia search...")
    search_params = {
        'action': 'opensearch',
        'search': search_term,
        'limit': 1,
        'namespace': 0,
        'format': 'json'
    }
    
    search_resp = requests.get(wiki_url, params=search_params, headers=headers, timeout=5)
    search_data = search_resp.json()
    
    if search_data and len(search_data) > 1 and search_data[1]:
        best_title = search_data[1][0]
        logger.info(f"🔍 Found better Wikipedia title: '{best_title}'")
        return _wikipedia_lookup(wiki_url, best_title, headers, query)
    
    return None


def _search_duckduckgo(query: str) -> Optional[str]:
    """Search DuckDuckGo Instant Answer API"""
    try:
        logger.info(f"🔍 Trying DuckDuckGo Instant Answer API...")
        ddg_url = "https://api.duckduckgo.com/"
        ddg_params = {
            'q': query,
            'format': 'json',
            'no_html': 1,
            'skip_disambig': 1
        }
        
        ddg_response = requests.get(ddg_url, params=ddg_params, timeout=5)
        ddg_response.raise_for_status()
        ddg_data = ddg_response.json()
        
        answer = None
        if ddg_data.get('AbstractText'):
            answer = ddg_data['AbstractText']
        elif ddg_data.get('Answer'):
            answer = ddg_data['Answer']
        elif ddg_data.get('Definition'):
            answer = ddg_data['Definition']
        
        if answer and len(answer) > 50:
            formatted = _format_answer(answer, query)
            if formatted:
                logger.info(f"✅ Found DuckDuckGo answer")
                return formatted
        
        logger.warning(f"⚠️ DuckDuckGo returned no useful answer")
        return None
        
    except Exception as ddg_error:
        logger.warning(f"⚠️ DuckDuckGo search failed: {ddg_error}")
        return None


def _search_google(query: str) -> Optional[str]:
    """Search Google using web scraping"""
    try:
        if not BS4_AVAILABLE:
            logger.warning("⚠️ BeautifulSoup not installed, skipping Google search scraping")
            return None
        
        logger.info(f"🔍 Trying Google search scraping...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}&hl=en"
        response = requests.get(search_url, headers=headers, timeout=8)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Featured snippet selectors
        selectors = [
            'div.hgKElc', 'span.hgKElc', 'div.IZ6rdc', 'span.aCOpRe',
            'div.kno-rdesc span', 'div.V3FYCf', 'div.ayRjaf', 'div.Z0LcW',
            'div.LGOjhe', 'div.VwiC3b', 'div.BNeawe',
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and len(text) > 30:
                    answer = text.strip().replace('Wikipedia', '').strip()
                    formatted = _format_answer(answer, query)
                    if formatted:
                        logger.info(f"✅ Found Google answer with selector: {selector}")
                        return formatted
        
        logger.warning(f"⚠️ Google scraping found no answers")
        return None
        
    except Exception as google_error:
        logger.warning(f"⚠️ Google search scraping failed: {google_error}")
        return None


def _format_answer(answer: str, query: str) -> Optional[str]:
    """Format and validate answer"""
    # Limit to first 3 sentences
    sentences = answer.split('. ')[:3]
    formatted = '. '.join(sentences)
    if not formatted.endswith('.'):
        formatted += '.'
    if len(formatted) > 500:
        formatted = formatted[:497] + "..."
    
    # Filter out joke-like responses for factual queries
    joke_indicators = ['why did', 'why do', 'why don\'t', 'because they', 'walk into a bar', 'knock knock']
    is_joke = any(indicator in formatted.lower() for indicator in joke_indicators)
    query_lower = query.lower()
    is_factual_query = any(query_lower.startswith(q) for q in 
        ['what is', 'what are', 'who is', 'who are', 'where is', 'where are', 
         'when was', 'when is', 'define', 'explain'])
    
    if is_factual_query and is_joke:
        logger.warning(f"⚠️ Filtered out joke-like response for factual query")
        return None
    
    return formatted
