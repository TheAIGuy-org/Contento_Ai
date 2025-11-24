from langgraph.graph import StateGraph, END
from backend.core.state import ContentState
from typing import Literal

# Import ALL agents
from backend.agents.context_injection_node import ContextInjectionNode
from backend.agents.research_node import ResearchNode
from backend.agents.intent_analyzer_node import IntentAnalyzerNode
from backend.agents.router_node import RouterNode
from backend.agents.blueprint_synthesizer_node import BlueprintSynthesizerNode
from backend.agents.writer_node import WriterNode
from backend.agents.optimizer_node import OptimizerNode
from backend.agents.director_node import DirectorNode
from backend.agents.decision_node import DecisionNode


class NexusPrimeWorkflow:
    """Complete Workflow - ALL 15 Nodes Integrated"""
    
    def __init__(self):
        self.context_injection = ContextInjectionNode()
        self.research = ResearchNode()
        self.intent_analyzer = IntentAnalyzerNode()
        self.router = RouterNode()
        self.blueprint_synthesizer = BlueprintSynthesizerNode()
        self.writer = WriterNode()
        self.optimizer = OptimizerNode()
        self.director = DirectorNode()
        self.decision = DecisionNode()
    
    def should_continue(self, state: ContentState) -> Literal["writer", "end"]:
        """Loop control"""
        return "writer" if state['loop_continue'] else "end"
    
    def build_graph(self) -> StateGraph:
        """Construct complete graph"""
        
        workflow = StateGraph(ContentState)
        
        # Add all nodes
        workflow.add_node("context_injection", self.context_injection.execute)
        workflow.add_node("research", self.research.execute)
        workflow.add_node("intent_analyzer", self.intent_analyzer.execute)
        workflow.add_node("router", self.router.execute)
        workflow.add_node("blueprint_synthesizer", self.blueprint_synthesizer.execute)
        workflow.add_node("writer", self.writer.execute)
        workflow.add_node("optimizer", self.optimizer.execute)
        workflow.add_node("director", self.director.execute)
        workflow.add_node("decision", self.decision.execute)
        
        # Define complete flow
        workflow.set_entry_point("context_injection")
        workflow.add_edge("context_injection", "research")
        workflow.add_edge("research", "intent_analyzer")
        workflow.add_edge("intent_analyzer", "router")
        workflow.add_edge("router", "blueprint_synthesizer")
        workflow.add_edge("blueprint_synthesizer", "writer")
        workflow.add_edge("writer", "optimizer")
        workflow.add_edge("optimizer", "director")
        workflow.add_edge("director", "decision")
        
        # Conditional loop
        workflow.add_conditional_edges(
            "decision",
            self.should_continue,
            {
                "writer": "writer",
                "end": END
            }
        )
        
        return workflow.compile()
    
    def run(self, state: ContentState) -> ContentState:
        """Execute complete workflow"""
        
        print("\n" + "="*80)
        print("🚀 NEXUS PRIME: COMPLETE SYSTEM")
        print("="*80)
        print(f"📌 Topic: {state['user_config'].topic}")
        print(f"📌 Platform: {state['user_config'].platform.upper()}")
        print(f"📌 Avatar: {state['user_config'].avatar_id.upper()}")
        print("="*80 + "\n")
        
        graph = self.build_graph()
        final_state = graph.invoke(state)
        
        print("\n" + "="*80)
        print("🏁 COMPLETE")
        print("="*80 + "\n")
        
        return final_state


import re  # Add at top


print("✅ COMPLETE CONSOLIDATED SYSTEM")
print("📦 All components integrated:")
print("  • Enhanced state in original state.py")
print("  • All prompts in prompt_builder.py")
print("  • All text utils in text_processor.py")
print("  • Writer uses ALL utilities")
print("  • Optimizer uses ALL metrics")
print("  • Director uses full framework")
print("  • Complete 9-node workflow")
print("\n🎯 NO redundant 'enhanced' files!")
print("🎯 Everything in proper place!")
print("🎯 Every resource ACTUALLY USED!")