"""Example usage of CQRS infrastructure with pipeline behaviors"""
import asyncio
import logging
from src.application.common.mediator import Mediator
from src.application.behaviors import (
    BrainProtectionBehavior,
    ValidationBehavior,
    PerformanceBehavior,
    LoggingBehavior
)
from src.application.commands.conversation_commands import (
    CaptureConversationCommand,
    LearnPatternCommand
)
from src.application.commands.conversation_handlers import (
    CaptureConversationHandler,
    LearnPatternHandler
)
from src.application.queries.conversation_queries import (
    SearchContextQuery,
    GetConversationQualityQuery
)
from src.application.queries.conversation_handlers import (
    SearchContextHandler,
    GetConversationQualityHandler
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def setup_mediator() -> Mediator:
    """Setup mediator with handlers and behaviors
    
    Pipeline order (behaviors execute in registration order):
    1. LoggingBehavior - Log request/response
    2. PerformanceBehavior - Monitor performance
    3. ValidationBehavior - Validate input
    4. BrainProtectionBehavior - Enforce SKULL rules
    5. Handler - Execute business logic
    
    Returns:
        Configured mediator instance
    """
    mediator = Mediator()
    
    # Register behaviors (order matters!)
    mediator.register_behavior(LoggingBehavior(log_request_data=True))
    mediator.register_behavior(PerformanceBehavior(slow_threshold_ms=500.0))
    mediator.register_behavior(ValidationBehavior())
    mediator.register_behavior(BrainProtectionBehavior())
    
    # Register command handlers
    mediator.register_handler(CaptureConversationCommand, CaptureConversationHandler())
    mediator.register_handler(LearnPatternCommand, LearnPatternHandler())
    
    # Register query handlers
    mediator.register_handler(SearchContextQuery, SearchContextHandler())
    mediator.register_handler(GetConversationQualityQuery, GetConversationQualityHandler())
    
    logger.info("✅ Mediator configured with 4 behaviors and 4 handlers")
    return mediator


async def example_capture_conversation(mediator: Mediator):
    """Example: Capture a conversation"""
    logger.info("\n" + "="*80)
    logger.info("Example 1: Capture Conversation")
    logger.info("="*80)
    
    # Create command
    command = CaptureConversationCommand(
        conversation_id="conv-example-001",
        title="CQRS Implementation Discussion",
        content="This is a detailed conversation about implementing Clean Architecture "
                "with CQRS pattern. We discussed commands, queries, handlers, and "
                "pipeline behaviors. The conversation covered validation, logging, "
                "performance monitoring, and brain protection rules.",
        file_path="/conversations/cqrs-implementation.json",
        quality_score=0.85,
        entity_count=25
    )
    
    # Send through mediator (will execute pipeline)
    result = await mediator.send(command)
    
    if result.is_success:
        logger.info(f"✅ Conversation captured: {result.value}")
    else:
        logger.error(f"❌ Failed to capture: {', '.join(result.errors)}")


async def example_learn_pattern(mediator: Mediator):
    """Example: Learn a pattern"""
    logger.info("\n" + "="*80)
    logger.info("Example 2: Learn Pattern")
    logger.info("="*80)
    
    # Create command
    command = LearnPatternCommand(
        pattern_id="pat-example-001",
        pattern_name="CQRS Pipeline Pattern",
        pattern_type="architecture",
        pattern_content="""
        # CQRS Pipeline Pattern
        
        ## Structure
        1. Logging Behavior - Log all requests
        2. Performance Behavior - Monitor timing
        3. Validation Behavior - Validate input
        4. Brain Protection - Enforce SKULL rules
        5. Handler - Execute business logic
        
        ## Benefits
        - Separation of concerns
        - Centralized cross-cutting logic
        - Testable components
        - Scalable architecture
        """,
        source_conversation_id="conv-example-001",
        namespace="cortex.architecture",
        confidence_score=0.90,
        tags=["cqrs", "clean-architecture", "pipeline"]
    )
    
    # Send through mediator
    result = await mediator.send(command)
    
    if result.is_success:
        logger.info(f"✅ Pattern learned: {result.value}")
    else:
        logger.error(f"❌ Failed to learn: {', '.join(result.errors)}")


async def example_search_context(mediator: Mediator):
    """Example: Search conversations"""
    logger.info("\n" + "="*80)
    logger.info("Example 3: Search Context")
    logger.info("="*80)
    
    # Create query
    query = SearchContextQuery(
        search_text="CQRS implementation",
        namespace_filter="cortex.architecture",
        min_relevance=0.70,
        max_results=10
    )
    
    # Send through mediator
    result = await mediator.send(query)
    
    if result.is_success:
        conversations = result.value
        logger.info(f"✅ Found {len(conversations)} conversations")
        for conv in conversations:
            logger.info(f"   - {conv.title} (quality: {conv.quality_score:.2f})")
    else:
        logger.error(f"❌ Search failed: {', '.join(result.errors)}")


async def example_get_quality(mediator: Mediator):
    """Example: Get conversation quality"""
    logger.info("\n" + "="*80)
    logger.info("Example 4: Get Conversation Quality")
    logger.info("="*80)
    
    # Create query
    query = GetConversationQualityQuery(
        conversation_id="conv-example-001"
    )
    
    # Send through mediator
    result = await mediator.send(query)
    
    if result.is_success:
        quality = result.value
        logger.info(f"✅ Quality Assessment:")
        logger.info(f"   Score: {quality.score:.2f}")
        logger.info(f"   Level: {quality.quality_level}")
        logger.info(f"   Turn Count: {quality.turn_count}")
        logger.info(f"   Entity Count: {quality.entity_count}")
        logger.info(f"   Should Capture: {quality.should_capture}")
        logger.info(f"   Richness Factor: {quality.richness_factor:.2f}")
    else:
        logger.error(f"❌ Failed to get quality: {', '.join(result.errors)}")


async def example_validation_failure(mediator: Mediator):
    """Example: Validation failure"""
    logger.info("\n" + "="*80)
    logger.info("Example 5: Validation Failure (Empty Title)")
    logger.info("="*80)
    
    # Create invalid command
    command = CaptureConversationCommand(
        conversation_id="conv-invalid-001",
        title="",  # Empty title - will fail validation
        content="Content is fine",
        file_path="/conversations/invalid.json"
    )
    
    # Send through mediator (will fail at validation behavior)
    result = await mediator.send(command)
    
    if result.is_success:
        logger.error("❌ Should have failed validation!")
    else:
        logger.info(f"✅ Validation caught error: {', '.join(result.errors)}")


async def example_brain_protection(mediator: Mediator):
    """Example: Brain protection warning"""
    logger.info("\n" + "="*80)
    logger.info("Example 6: Brain Protection (Protected Namespace)")
    logger.info("="*80)
    
    # Create command targeting protected namespace
    command = LearnPatternCommand(
        pattern_id="pat-protected-001",
        pattern_name="System Pattern",
        pattern_type="architecture",
        pattern_content="System-level pattern",
        source_conversation_id="conv-example-001",
        namespace="cortex.system",  # Protected namespace
        confidence_score=0.85
    )
    
    # Send through mediator (will log SKULL warning)
    result = await mediator.send(command)
    
    if result.is_success:
        logger.info(f"✅ Pattern learned (with SKULL warning logged): {result.value}")
    else:
        logger.error(f"❌ Failed: {', '.join(result.errors)}")


async def show_performance_metrics(mediator: Mediator):
    """Show performance metrics summary"""
    logger.info("\n" + "="*80)
    logger.info("Performance Metrics Summary")
    logger.info("="*80)
    
    # Get performance behavior
    for behavior in mediator._behaviors:
        if isinstance(behavior, PerformanceBehavior):
            metrics = behavior.get_metrics_summary()
            for request_type, stats in metrics.items():
                logger.info(f"\n{request_type}:")
                logger.info(f"  Count: {stats['count']}")
                logger.info(f"  Avg Duration: {stats['avg_duration_ms']:.2f}ms")
                logger.info(f"  Min Duration: {stats['min_duration_ms']:.2f}ms")
                logger.info(f"  Max Duration: {stats['max_duration_ms']:.2f}ms")
                logger.info(f"  Success Rate: {stats['success_rate']:.2f}%")
                logger.info(f"  Success Count: {stats['success_count']}")
                logger.info(f"  Failure Count: {stats['failure_count']}")


async def main():
    """Run all examples"""
    logger.info("Starting CQRS Pipeline Examples")
    logger.info("="*80)
    
    # Setup mediator with behaviors and handlers
    mediator = await setup_mediator()
    
    # Run examples
    await example_capture_conversation(mediator)
    await example_learn_pattern(mediator)
    await example_search_context(mediator)
    await example_get_quality(mediator)
    await example_validation_failure(mediator)
    await example_brain_protection(mediator)
    
    # Show performance metrics
    await show_performance_metrics(mediator)
    
    logger.info("\n" + "="*80)
    logger.info("✅ All examples completed!")
    logger.info("="*80)


if __name__ == "__main__":
    asyncio.run(main())
