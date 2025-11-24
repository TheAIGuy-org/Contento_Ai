import json
import asyncio
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Import complete workflow components
from backend.core.state import create_initial_state, UserConfig
from backend.graph.workflow import NexusPrimeWorkflow
from backend.utils.validators import InputValidator
from backend.utils.logger import get_logger

# Configure logging
logger = get_logger("NexusAPI")

app = FastAPI(title="Nexus Prime API", version="2.0.0")

# CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")
    return {
        "system": "Nexus Prime",
        "version": "2.0.0",
        "status": "online",
        "websocket_endpoint": "/ws/generate"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.debug("Health check requested")
    return {
        "status": "active",
        "system": "Nexus Prime Core",
        "version": "2.0.0",
        "nodes": 9
    }

@app.websocket("/ws/generate")
async def websocket_generate(websocket: WebSocket):
    """WebSocket endpoint for content generation"""
    
    await websocket.accept()
    client_id = str(websocket.client.host)
    logger.info(f"⚡ Client Connected: {client_id}")
    
    try:
        # 1. Receive Configuration Payload
        data = await websocket.receive_text()
        config_data = json.loads(data)
        
        logger.info(f"📥 Received Config: {json.dumps(config_data, indent=2)}")
        
        # 2. Build UserConfig
        user_config = UserConfig(
            topic=config_data.get('topic'),
            platform=config_data.get('platform', 'linkedin').lower(),
            avatar_id=config_data.get('avatar', 'stark').lower(),
            custom_avatar_params=config_data.get('custom_params')
        )
        logger.debug(f"UserConfig Built: {user_config}")
        
        # Validate input
        is_valid, message = InputValidator.validate_user_config(user_config)
        if not is_valid:
            logger.warning(f"Validation Failed: {message}")
            await websocket.send_json({
                "type": "error",
                "message": f"Validation Error: {message}"
            })
            return
        
        # 3. Initialize Workflow
        state = create_initial_state(user_config)
        workflow = NexusPrimeWorkflow()
        app_graph = workflow.build_graph()
        
        logger.info(f"🚀 Starting Complete 9-Node Workflow for: '{user_config.topic}'")
        
        start_time = time.time()
        
        # 4. Stream Events with ALL nodes
        async for event in app_graph.astream(state):
            for node_name, node_state in event.items():
                logger.debug(f"Node '{node_name}' completed. State update received.")
                
                payload = {
                    "type": "state_update",
                    "node": node_name,
                    "timestamp": time.time(),
                    "data": {}
                }
                
                # Handle ALL nodes from complete workflow
                
                if node_name == "context_injection":
                    payload["data"] = {
                        "status": "Injecting Persona DNA...",
                        "avatar_loaded": node_state['user_config'].avatar_id,
                        "platform_loaded": node_state['user_config'].platform,
                        "message": f"Avatar: {node_state['user_config'].avatar_id.upper()}"
                    }
                
                elif node_name == "research":
                    facts = node_state.get('ground_truth', [])
                    metadata = node_state['diagnostic_vector'].metadata
                    
                    payload["data"] = {
                        "status": "Deep Diving...",
                        "facts_count": len(facts),
                        "latest_fact": facts[-1][:100] if facts else "Searching...",
                        "search_queries": metadata.get('search_queries', 0),
                        "search_time": metadata.get('search_time', 0),
                        "search_results": metadata.get('search_results', 0),
                        "message": f"Extracted {len(facts)} verified facts in {metadata.get('search_time', 0):.1f}s"
                    }
                
                elif node_name == "intent_analyzer":
                    meta = node_state['draft_artifact'].metadata
                    
                    payload["data"] = {
                        "status": "Analyzing Intent...",
                        "intent": meta.get('intent', 'analyzing...'),
                        "confidence": meta.get('confidence', 'low'),
                        "primary_keyword": meta.get('primary_keyword', 'extracting...'),
                        "secondary_keywords": meta.get('secondary_keywords', []),
                        "message": f"Intent: {meta.get('intent', 'unknown')} | Keyword: {meta.get('primary_keyword', 'none')}"
                    }
                
                elif node_name == "router":
                    meta = node_state['draft_artifact'].metadata
                    
                    payload["data"] = {
                        "status": "Routing DNA...",
                        "skeleton_name": meta.get('skeleton_name', 'Universal'),
                        "needs_synthesis": meta.get('needs_synthesis', False),
                        "message": f"DNA: {meta.get('skeleton_name', 'Unknown')} | Synthesis: {'YES' if meta.get('needs_synthesis') else 'NO'}"
                    }
                
                elif node_name == "blueprint_synthesizer":
                    meta = node_state['draft_artifact'].metadata
                    
                    payload["data"] = {
                        "status": "Synthesizing...",
                        "custom_blueprint": meta.get('custom_blueprint', False),
                        "reasoning": meta.get('blueprint_reasoning', ''),
                        "message": "Custom structure created" if meta.get('custom_blueprint') else "Using standard DNA"
                    }
                
                elif node_name == "writer":
                    draft = node_state['draft_artifact']
                    meta = draft.metadata
                    
                    payload["data"] = {
                        "status": "Generating Content...",
                        "draft_preview": draft.full_text[:200] + "..." if draft.full_text else "Drafting...",
                        "full_text": draft.full_text,
                        "hook": draft.hook,
                        "body": draft.body,
                        "revision": node_state['diagnostic_vector'].attempt_count,
                        "visuals": draft.visuals,
                        "hook_score": meta.get('hook_score', 0),
                        "engagement_triggers": meta.get('engagement_triggers', []),
                        "message": f"Revision #{node_state['diagnostic_vector'].attempt_count} | Hook: {meta.get('hook_score', 0):.1f}/10"
                    }
                
                elif node_name == "optimizer":
                    diag = node_state['diagnostic_vector']
                    meta = diag.metadata
                    
                    payload["data"] = {
                        "status": "Optimizing...",
                        "compliance_score": diag.compliance_score,
                        "engagement_score": diag.engagement_score,
                        "flags": diag.flags,
                        "grade_level": meta.get('grade_level', 0),
                        "keyword_density": meta.get('keyword_density', 0),
                        "facts_usage_rate": meta.get('facts_usage_rate', 0),
                        "message": f"Compliance: {diag.compliance_score}% | Engagement: {diag.engagement_score:.1f}/10"
                    }
                
                elif node_name == "director":
                    diag = node_state['diagnostic_vector']
                    meta = diag.metadata
                    
                    payload["data"] = {
                        "status": "Creative Review...",
                        "creative_score": diag.creative_score,
                        "feedback": diag.reasoning,
                        "flagged_words_evaluated": meta.get('flagged_words_evaluated', False),
                        "decision": "APPROVED" if not node_state.get('loop_continue') else "REVISION REQUESTED",
                        "message": f"Score: {diag.creative_score}/10 | {'APPROVED' if not node_state.get('loop_continue') else 'NEEDS WORK'}"
                    }
                
                elif node_name == "decision":
                    payload["data"] = {
                        "status": "Decision Engine...",
                        "loop_continue": node_state.get('loop_continue', False),
                        "message": "Triggering revision..." if node_state.get('loop_continue') else "Publishing..."
                    }
                
                # Send to client
                await websocket.send_json(payload)
                await asyncio.sleep(0.15)
        
        # 5. Final Complete Payload
        execution_time = time.time() - start_time
        diag = node_state['diagnostic_vector']
        meta = diag.metadata
        draft_meta = node_state['draft_artifact'].metadata
        
        final_payload = {
            "type": "complete",
            "final_output": node_state['final_output'],
            "metrics": {
                "creative": diag.creative_score,
                "compliance": diag.compliance_score,
                "engagement": diag.engagement_score,
                "iterations": diag.attempt_count,
                "time": round(execution_time, 2),
                "facts_used": len(node_state['ground_truth']),
                "facts_usage_rate": meta.get('facts_usage_rate', 0),
                "grade_level": meta.get('grade_level', 0),
                "keyword_density": meta.get('keyword_density', 0),
                "hook_score": draft_meta.get('hook_score', 0),
                "search_time": meta.get('search_time', 0)
            },
            "artifacts": {
                "hook": node_state['draft_artifact'].hook,
                "body": node_state['draft_artifact'].body,
                "visuals": node_state['draft_artifact'].visuals,
                "engagement_triggers": draft_meta.get('engagement_triggers', []),
                "primary_keyword": draft_meta.get('primary_keyword', '')
            },
            "context": {
                "intent": draft_meta.get('intent', 'unknown'),
                "skeleton_used": draft_meta.get('skeleton_name', 'Universal'),
                "custom_blueprint": draft_meta.get('custom_blueprint', False)
            }
        }
        
        await websocket.send_json(final_payload)
        logger.info(f"🏁 Complete in {execution_time:.2f}s | Score: {diag.creative_score}/10")
        logger.debug(f"Final Payload Sent: {json.dumps(final_payload, indent=2)}")
        
    except WebSocketDisconnect:
        logger.warning(f"🔌 Client Disconnected: {client_id}")
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}", exc_info=True)
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"System Error: {str(e)}"
            })
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    
    # Run server
    logger.info("🚀 Starting Nexus Prime Server...")
    logger.info("📡 WebSocket endpoint: ws://localhost:8000/ws/generate")
    logger.info("🌐 Health check: http://localhost:8000/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )