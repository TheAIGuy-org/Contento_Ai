from backend.core.state import ContentState
from backend.core.avatars import get_avatar
from backend.services.llm_service import llm_service
from backend.services.search_service import search_service
from backend.utils.prompt_builder import PromptBuilder
from backend.utils.text_processor import TextProcessor
from typing import List, Dict
import asyncio
import time


class ResearchNode:
    """Phase 1: Deep Diver with Parallel Search (ENHANCED)"""
    
    def __init__(self):
        self.prompt_builder = PromptBuilder()
        self.text_processor = TextProcessor()
    
    def execute(self, state: ContentState) -> ContentState:
        """Execute research phase with parallel searches"""
        
        print("🔍 [Phase 1] Research Node: Gathering ground truth...")
        
        avatar = get_avatar(
            state['user_config'].avatar_id,
            state['user_config'].custom_avatar_params
        )
        
        # Step 1: Generate search queries
        query_prompt = self.prompt_builder.build_research_prompt(
            topic=state['user_config'].topic,
            avatar=avatar
        )
        
        query_response = llm_service.generate_research(query_prompt)
        search_queries = self.text_processor.extract_queries_from_response(query_response)
        
        print(f"  Generated {len(search_queries)} search queries")
        
        # Step 2: Execute searches (parallel or sequential based on availability)
        start_time = time.time()
        
        try:
            # FIX: Try parallel execution first
            all_results = asyncio.run(self._execute_parallel_search(search_queries))
            execution_time = time.time() - start_time
            print(f"  ⚡ Parallel search completed in {execution_time:.2f}s")
            
        except Exception as e:
            # Fallback to sequential execution
            print(f"  ⚠️ Parallel search failed, using sequential fallback: {e}")
            all_results = self._execute_sequential_search(search_queries)
            execution_time = time.time() - start_time
            print(f"  ✓ Sequential search completed in {execution_time:.2f}s")
        
        # Step 3: Flatten results
        flat_results = []
        for result_list in all_results:
            flat_results.extend(result_list)
        
        # Step 4: Synthesize facts
        if flat_results:
            results_text = [
                f"{r['title']}: {r['content']} [Source: {r['url']}]" 
                for r in flat_results
            ]
            
            synthesis_prompt = self.prompt_builder.build_synthesis_prompt(results_text)
            synthesis_response = llm_service.generate_research(synthesis_prompt)
            
            facts = self.text_processor.extract_facts_from_response(synthesis_response)
            state['ground_truth'] = facts
            
            print(f"  📊 Extracted {len(facts)} verified facts")
        else:
            state['ground_truth'] = []
            print("  ⚠️ No search results obtained")
        
        # Store search metrics
        state['diagnostic_vector'].metadata['search_time'] = execution_time
        state['diagnostic_vector'].metadata['search_queries'] = len(search_queries)
        state['diagnostic_vector'].metadata['search_results'] = len(flat_results)
        
        return state
    
    async def _execute_parallel_search(
        self,
        queries: List[str]
    ) -> List[List[Dict[str, str]]]:
        """FIX: Execute searches in parallel"""
        return await search_service.search_parallel(queries, max_results=3)
    
    def _execute_sequential_search(
        self,
        queries: List[str]
    ) -> List[List[Dict[str, str]]]:
        """Fallback: Execute searches sequentially"""
        all_results = []
        
        for query in queries:
            try:
                results = search_service.search(query, max_results=3)
                all_results.append(results)
                print(f"  ✓ Searched: {query}")
            except Exception as e:
                print(f"  ✗ Search failed for '{query}': {e}")
                all_results.append([])
        
        return all_results