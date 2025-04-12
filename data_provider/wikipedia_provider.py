import wikipediaapi
from typing import Dict

wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent='PerplexityProject/1.0 (https://github.com/saerom/perplexity_project; saerom@example.com)'
)

def get_info(query: str, override_query: str = None) -> Dict:
    """Get artist or topic information from Wikipedia using wikipediaapi with fallback search."""
    search_term = override_query or query

    try:
        # Try direct page lookup first
        page = wiki.page(search_term)

        if not page.exists():
            # Fallback to search if direct page not found
            search_results = wiki.search(search_term)
            if search_results:
                page = wiki.page(search_results[0])

        if page.exists():
            # Filter out irrelevant sections
            sections_data = []
            for section in page.sections:
                if section.title and section.title.lower() not in ['references', 'external links', 'see also', 'notes']:
                    sections_data.append({
                        "title": section.title,
                        "content": section.text
                    })

            return {
                "source": "wikipedia",
                "query": query,
                "used_term": page.title,
                "summary": page.summary,
                "url": page.fullurl,
                "categories": list(page.categories.keys()),
                "sections": sections_data,
                "content_snippet": page.text[:1000],
            }

        else:
            return {
                "error": f"No Wikipedia page found for '{search_term}'",
                "source": "wikipedia",
                "query": query
            }

    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}",
            "source": "wikipedia",
            "query": query
        }
