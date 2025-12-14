"""
CORTEX 3.0 Smart Hint System - Integration Example

This demonstrates how to integrate smart hints into CORTEX responses.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from src.tier1.smart_hint_integration import (
    get_smart_hint_system,
    analyze_response_for_hint,
    capture_current_conversation
)


def example_response_with_smart_hint():
    """Example of generating a CORTEX response with smart hint."""
    
    # Simulated user request and CORTEX response
    user_prompt = "Let's plan the authentication system for the dashboard"
    
    assistant_response = """
🧠 **CORTEX Feature Planning**
Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX

🎯 **My Understanding Of Your Request:** 
   You want to design and implement an authentication system that secures dashboard access

⚠️ **Challenge:** ✓ **Accept**
   This approach is sound. Authentication is critical and the multi-phase plan ensures proper implementation.

💬 **Response:** I'll design a token-based authentication system with JWT for stateless auth, implement user login/signup flows, add route guards for dashboard protection, and ensure secure password hashing with bcrypt.

📝 **Your Request:** Plan authentication system for dashboard

🔍 Next Steps:
   ☐ Phase 1: Authentication Core (JWT service, password hashing, user model)
   ☐ Phase 2: API Endpoints (Login, signup, logout, token refresh)
   ☐ Phase 3: Frontend Integration (Login UI, route guards, session management)
   ☐ Phase 4: Security & Testing (Security audit, integration tests, penetration testing)
   
   Ready to proceed with all phases, or would you like to focus on a specific phase first?
"""
    
    # Analyze conversation and generate hint
    hint_text = analyze_response_for_hint(user_prompt, assistant_response)
    
    # Build complete response
    complete_response = assistant_response
    
    if hint_text:
        complete_response += "\n\n" + hint_text
    
    return complete_response


def example_capture_workflow():
    """Example of the capture workflow."""
    
    user_prompt = "Let's plan the authentication system"
    assistant_response = """
🧠 **CORTEX Feature Planning**

⚠️ **Challenge:** ✓ **Accept**

💬 **Response:** I'll design a token-based auth system with JWT.

🔍 Next Steps:
   ☐ Phase 1: Core implementation
   ☐ Phase 2: API endpoints
   ☐ Phase 3: Frontend integration
"""
    
    # User says "capture conversation"
    print("User: capture conversation\n")
    
    # Capture using smart hint system
    confirmation = capture_current_conversation(user_prompt, assistant_response)
    
    print("CORTEX:")
    print(confirmation)


def example_vault_management():
    """Example of vault management operations."""
    
    system = get_smart_hint_system()
    
    # Get vault statistics
    stats = system.get_vault_stats()
    
    print("📊 Conversation Vault Statistics\n")
    print(f"Total conversations: {stats.get('total_conversations', 0)}")
    print(f"Average quality: {stats.get('average_quality_score', 0)}")
    print(f"\nQuality distribution:")
    for level, count in stats.get('quality_distribution', {}).items():
        print(f"  {level}: {count}")
    
    # List recent conversations
    recent = system.list_recent_conversations(limit=5)
    
    print(f"\n📝 Recent Conversations ({len(recent)})\n")
    for conv in recent:
        print(f"  • {conv['topic']}")
        print(f"    Quality: {conv['quality_level']} ({conv['quality_score']}/10)")
        print(f"    ID: {conv['conversation_id']}")
        print()


def example_quality_analysis():
    """Example of manual quality analysis."""
    
    from src.tier1.conversation_quality import create_analyzer
    
    # Create analyzer
    analyzer = create_analyzer({'hint_threshold': 'GOOD'})
    
    # Test conversation
    user_prompt = "How do we implement caching?"
    assistant_response = """
    We have several caching strategies:
    1. In-memory caching (Redis)
    2. CDN caching
    3. Database query caching
    
    The trade-off is between speed and consistency.
    
    Files involved: `src/cache/redis_cache.py`, `src/cache/cdn_cache.py`
    """
    
    # Analyze
    quality = analyzer.analyze_conversation(user_prompt, assistant_response)
    
    print("🔍 Quality Analysis\n")
    print(f"Score: {quality.total_score}/10")
    print(f"Level: {quality.level}")
    print(f"Reasoning: {quality.reasoning}")
    print(f"Show hint: {quality.should_show_hint}")
    
    print("\n📊 Semantic Elements Detected:\n")
    elements = quality.elements
    if elements.multi_phase_planning:
        print(f"  ✓ Multi-phase planning: {elements.phase_count} phases")
    if elements.challenge_accept_flow:
        print("  ✓ Challenge/Accept reasoning")
    if elements.design_decisions:
        print("  ✓ Design decisions")
    if elements.file_references > 0:
        print(f"  ✓ File references: {elements.file_references}")
    if elements.next_steps_provided:
        print("  ✓ Next steps provided")
    if elements.code_implementation:
        print("  ✓ Code implementation")
    if elements.architectural_discussion:
        print("  ✓ Architectural discussion")


if __name__ == '__main__':
    print("=" * 70)
    print("CORTEX 3.0 Smart Hint System - Integration Examples")
    print("=" * 70)
    print()
    
    print("EXAMPLE 1: Response with Smart Hint")
    print("-" * 70)
    response = example_response_with_smart_hint()
    print(response)
    print()
    
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Capture Workflow")
    print("-" * 70)
    example_capture_workflow()
    print()
    
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Quality Analysis")
    print("-" * 70)
    example_quality_analysis()
    print()
    
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Vault Management")
    print("-" * 70)
    example_vault_management()
    print()
