from backend.core.state import UserConfig, create_initial_state
from backend.graph.workflow import NexusPrimeWorkflow
from backend.utils.validators import InputValidator
import json
import time


def display_results(result: dict, execution_time: float):
    """Display complete results using ALL metadata"""
    
    print("\n" + "="*80)
    print("📄 FINAL OUTPUT")
    print("="*80 + "\n")
    print(result['final_output'])
    
    print("\n" + "="*80)
    print("📊 COMPLETE PERFORMANCE METRICS")
    print("="*80)
    
    # Core scores
    diagnostic = result['diagnostic_vector']
    print(f"\n🎯 QUALITY SCORES:")
    print(f"  • Creative Score: {diagnostic.creative_score}/10")
    print(f"  • Compliance Score: {diagnostic.compliance_score}%")
    print(f"  • Engagement Prediction: {diagnostic.engagement_score}/10")
    
    # Metadata metrics
    if diagnostic.metadata:
        print(f"\n📖 READABILITY METRICS:")
        print(f"  • Grade Level: {diagnostic.metadata.get('grade_level', 'N/A')}")
        print(f"  • Avg Sentence Length: {diagnostic.metadata.get('avg_sentence_length', 'N/A')} words")
        print(f"  • Difficult Words: {diagnostic.metadata.get('difficult_words', 'N/A')}")
        
        print(f"\n🎣 HOOK ANALYSIS:")
        print(f"  • Hook Score: {result['draft_artifact'].metadata.get('hook_score', 'N/A')}/10")
        
        print(f"\n📈 ENGAGEMENT TRIGGERS:")
        triggers = result['draft_artifact'].metadata.get('engagement_triggers', [])
        for trigger in triggers:
            print(f"  • {trigger}")
        
        print(f"\n✅ FACT USAGE:")
        print(f"  • Facts Collected: {len(result['ground_truth'])}")
        print(f"  • Usage Rate: {diagnostic.metadata.get('facts_usage_rate', 0):.0f}%")
    
    # Process metrics
    print(f"\n⚙️ PROCESS METRICS:")
    print(f"  • Iterations: {diagnostic.attempt_count}")
    print(f"  • Execution Time: {execution_time:.2f}s")
    print(f"  • Content Length: {len(result['final_output'])} characters")
    
    # Issues
    if diagnostic.flags:
        print(f"\n⚠️ ISSUES IDENTIFIED:")
        for flag in diagnostic.flags:
            print(f"  • {flag}")
    
    # Context used
    print(f"\n🎭 CONTEXT APPLIED:")
    print(f"  • Intent: {result['draft_artifact'].metadata.get('intent', 'N/A')}")
    print(f"  • Platform: {result['user_config'].platform}")
    print(f"  • Avatar: {result['user_config'].avatar_id}")
    
    print("="*80 + "\n")


def save_complete_output(result: dict, execution_time: float, filename: str = "output.json"):
    """Save complete output with ALL metadata"""
    
    output_data = {
        'request_id': result['request_id'],
        'config': {
            'topic': result['user_config'].topic,
            'platform': result['user_config'].platform,
            'avatar_id': result['user_config'].avatar_id
        },
        'content': result['final_output'],
        'metrics': {
            'creative_score': result['diagnostic_vector'].creative_score,
            'compliance_score': result['diagnostic_vector'].compliance_score,
            'engagement_score': result['diagnostic_vector'].engagement_score,
            'iterations': result['diagnostic_vector'].attempt_count,
            'execution_time': execution_time,
            'facts_collected': len(result['ground_truth']),
            'content_length': len(result['final_output'])
        },
        'detailed_metrics': result['diagnostic_vector'].metadata,
        'draft_metadata': result['draft_artifact'].metadata,
        'ground_truth': result['ground_truth'],
        'context_layer': {
            'persona_voice': result['context_layer'].persona_voice[:200] + "...",
            'platform_rules': result['context_layer'].platform_rules[:200] + "..."
        }
    }
    
    with open(filename, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"✅ Complete output saved to {filename}\n")


def run_example(topic: str, platform: str, avatar_id: str, example_name: str):
    """Run a complete example"""
    
    print("\n" + "="*80)
    print(f"🎯 EXAMPLE: {example_name}")
    print("="*80 + "\n")
    
    # Create config
    config = UserConfig(
        topic=topic,
        platform=platform,
        avatar_id=avatar_id
    )
    
    # Validate
    is_valid, message = InputValidator.validate_user_config(config)
    if not is_valid:
        print(f"❌ Validation Error: {message}")
        return
    
    # Run workflow
    workflow = NexusPrimeWorkflow()
    state = create_initial_state(config)
    
    start_time = time.time()
    result = workflow.run(state)
    execution_time = time.time() - start_time
    
    # Display results
    display_results(result, execution_time)
    
    # Save output
    filename = f"output_{example_name.replace(' ', '_').lower()}.json"
    save_complete_output(result, execution_time, filename)


def main():
    """Main entry point - Demonstrates COMPLETE system"""
    
    print("\n" + "🌟"*40)
    print("🚀 NEXUS PRIME: COMPLETE APEX-IMPACT SYSTEM 🚀")
    print("🌟"*40 + "\n")
    
    # Example 1: LinkedIn with Stark
    run_example(
        topic="Why 90% of AI Startups Will Fail in 2025 (And How to Be in the 10%)",
        platform="linkedin",
        avatar_id="stark",
        example_name="LinkedIn_Stark"
    )
    
    # Example 2: Twitter with Viral Bro
    run_example(
        topic="I made $50k in 60 days using AI agents. Here's the exact system",
        platform="twitter",
        avatar_id="viral_bro",
        example_name="Twitter_ViralBro"
    )
    
    # Example 3: Blog with Jobs
    run_example(
        topic="The Future of Human-AI Collaboration",
        platform="blog",
        avatar_id="jobs",
        example_name="Blog_Jobs"
    )
    
    print("\n" + "="*80)
    print("✅ ALL EXAMPLES COMPLETE")
    print("="*80)
    print("\nGenerated outputs:")
    print("  • output_linkedin_stark.json")
    print("  • output_twitter_viralbro.json")
    print("  • output_blog_jobs.json")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()