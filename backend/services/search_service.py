# ============================================================================
# FILE: backend/services/search_service.py
# ============================================================================

from tavily import TavilyClient
from typing import List, Dict
from backend.core.config import settings
import asyncio


class SearchService:
    """Tavily search with async support (ENHANCED)"""
    
    def __init__(self):
        self.client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    
    def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "advanced"
    ) -> List[Dict[str, str]]:
        """Execute web search (sync version)"""
        
        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                include_raw_content=False
            )
            
            results = []
            for result in response.get('results', []):
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'content': result.get('content', ''),
                    'score': result.get('score', 0.0)
                })
            
            return results
        
        except Exception as e:
            print(f"  ⚠️ Search failed for '{query}': {str(e)}")
            return []
    
    async def search_async(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "advanced"
    ) -> List[Dict[str, str]]:
        """FIX: Async web search for parallel execution"""
        
        # Run sync search in executor to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.search(query, max_results, search_depth)
        )
    
    async def search_parallel(
        self,
        queries: List[str],
        max_results: int = 5
    ) -> List[List[Dict[str, str]]]:
        """FIX: Execute multiple searches in parallel"""
        
        print(f"  🚀 Executing {len(queries)} searches in parallel...")
        
        # Create tasks for all queries
        tasks = [
            self.search_async(query, max_results)
            for query in queries
        ]
        
        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"  ✗ Query {idx+1} failed: {result}")
                processed_results.append([])
            else:
                print(f"  ✓ Query {idx+1} completed")
                processed_results.append(result)
        
        return processed_results
    
    def extract_facts(self, results: List[Dict[str, str]]) -> List[str]:
        """Extract structured facts with citations"""
        facts = []
        
        for idx, result in enumerate(results, 1):
            content = result['content']
            url = result['url']
            fact = f"{content} [Source: {url}]"
            facts.append(fact)
        
        return facts


search_service = SearchService()