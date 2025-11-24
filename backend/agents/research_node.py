from backend.core.state import ContentState
from backend.core.avatars import get_avatar
from backend.services.llm_service import llm_service
from backend.services.search_service import search_service
from backend.utils.prompt_builder import PromptBuilder
from backend.utils.text_processor import TextProcessor
from backend.utils.logger import get_logger
from typing import List, Dict
import asyncio
import time

logger = get_logger(__name__)

class ResearchNode:
    """Phase 1: Deep Diver with Parallel Search (ENHANCED)"""
    
    def __init__(self):
        self.prompt_builder = PromptBuilder()
        self.text_processor = TextProcessor()
    
    def execute(self, state: ContentState) -> ContentState:
        """Execute research phase with parallel searches"""
        
        logger.info("🔍 [Phase 1] Research Node: Gathering ground truth...")
        
        avatar = get_avatar(
            state['user_config'].avatar_id,
            state['user_config'].custom_avatar_params
        )
        logger.debug(f"Avatar Loaded: {avatar.name}")
        
        # Step 1: Generate search queries
        query_prompt = self.prompt_builder.build_research_prompt(
            topic=state['user_config'].topic,
            avatar=avatar
        )
        logger.debug(f"Research Query Prompt: {query_prompt[:500]}...")
        
        query_response = llm_service.generate_research(query_prompt)
        search_queries = self.text_processor.extract_queries_from_response(query_response)
        
        logger.info(f"  Generated {len(search_queries)} search queries")
        for i, query in enumerate(search_queries, 1):
            logger.info(f"    Query {i}: {query}")
        
        # Step 2: Execute searches (parallel or sequential based on availability)
        logger.info(f"  🚀 Executing {len(search_queries)} searches in parallel...")
        start_time = time.time()
        
        try:
            # FIX: Try parallel execution first
            # Note: asyncio.run cannot be called when an event loop is already running
            # We should check if we are in an event loop
            try:
                loop = asyncio.get_running_loop()
                # If we are in a loop, we should await it, but execute is sync.
                # This design pattern (sync execute calling async) is tricky.
                # For now, we'll assume this is called from a sync context or handle it carefully.
                # If called from sync context (like server.py's threadpool), asyncio.run works.
                all_results = asyncio.run(self._execute_parallel_search(search_queries))
            except RuntimeError:
                # If we are already in a loop, we can't use asyncio.run.
                # We might need to use the existing loop or run in a separate thread.
                # For simplicity in this sync method, we'll fallback to sequential or use a new loop in a thread.
                # But let's try sequential fallback for safety if parallel fails due to loop issues.
                logger.warning("  ⚠️ Event loop detected, falling back to sequential search to avoid nesting.")
                all_results = self._execute_sequential_search(search_queries)

            execution_time = time.time() - start_time
            logger.info(f"  ⚡ Parallel/Sequential search completed in {execution_time:.2f}s")
            
        except Exception as e:
            # Fallback to sequential execution
            logger.warning(f"  ⚠️ Parallel search failed, using sequential fallback: {e}")
            all_results = self._execute_sequential_search(search_queries)
            execution_time = time.time() - start_time
            logger.info(f"  ✓ Sequential search completed in {execution_time:.2f}s")
        
        # Step 3: Flatten results
        flat_results = []
        for result_list in all_results:
            flat_results.extend(result_list)
        
        logger.debug(f"Total Search Results: {len(flat_results)}")
        
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
            
            logger.info(f"  📊 Extracted {len(facts)} verified facts")
            for i, fact in enumerate(facts, 1):
                logger.info(f"    Fact {i}: {fact}")
        else:
            state['ground_truth'] = []
            logger.warning("  ⚠️ No search results obtained")
        
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
        logger.debug("Starting parallel search...")
        results = await search_service.search_parallel(queries, max_results=3)
        for i, res in enumerate(results):
            logger.info(f"  ✓ Query {i+1} completed")
        return results
    
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
                logger.info(f"  ✓ Searched: {query}")
            except Exception as e:
                logger.error(f"  ✗ Search failed for '{query}': {e}")
                all_results.append([])
        
        return all_results