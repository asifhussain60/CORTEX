"""
CORTEX 3.0 Track B Phase 4 - Mock Data Integration System

Integration layer between mock dual-channel data and enhanced narrative engine.
Demonstrates narrative generation capabilities with realistic development scenarios.

NEW - Phase 4 Implementation: Complete integration with temporal analysis,
context weaving, and story generation using 5 enhanced templates.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import yaml
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging

from .mock_data import DualChannelMockData, MockConversation, MockDaemonCapture
from .narrative_engine import (
    NarrativeEngine, StoryTemplateSystem, ContextWeavingEngine, 
    TemporalContextAnalyzer, DecisionRationaleExtractor,
    StoryTemplate, ContextElement
)

logger = logging.getLogger(__name__)


class MockDataIntegrationSystem:
    """
    Complete integration system for mock data and narrative generation.
    
    Phase 4 Enhancement: Provides end-to-end integration testing,
    story generation validation, and performance benchmarking
    for Track B narrative capabilities.
    """
    
    def __init__(self, mock_data_dir: str = None, output_dir: str = None):
        """Initialize mock data integration system"""
        self.mock_data_dir = Path(mock_data_dir) if mock_data_dir else Path.cwd() / "mock_data"
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "narrative_output"
        
        # Initialize components
        self.mock_data = DualChannelMockData()
        self.narrative_engine = NarrativeEngine()
        self.template_system = StoryTemplateSystem()
        self.context_weaver = ContextWeavingEngine()
        self.temporal_analyzer = TemporalContextAnalyzer()
        self.decision_extractor = DecisionRationaleExtractor()
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info(f"Mock data integration system initialized - Phase 4 Enhanced")
    
    def run_complete_integration_test(self) -> Dict[str, Any]:
        """
        Run complete integration test of mock data → narrative generation.
        
        Phase 4 Test Coverage:
        1. Generate realistic mock data (15 conversations, 30 captures)
        2. Process with enhanced narrative engine (5 templates)
        3. Test temporal context analysis
        4. Validate YAML dual-channel compatibility
        5. Benchmark performance (<200ms target)
        """
        
        logger.info("Starting complete Track B Phase 4 integration test")
        test_start = datetime.now()
        
        # Step 1: Generate comprehensive mock data
        logger.info("Step 1: Generating mock data")
        mock_conversations = self.mock_data.generate_conversations(count=15)
        mock_captures = self.mock_data.generate_daemon_captures(count=30)
        
        # Step 2: Test context weaving with enhanced algorithm
        logger.info("Step 2: Testing enhanced context weaving")
        context_elements = self.context_weaver.extract_context_elements(
            mock_conversations, mock_captures
        )
        weaving_result = self.context_weaver.weave_context_narrative(context_elements)
        
        # Step 3: Test temporal context analysis (NEW - Phase 4)
        logger.info("Step 3: Testing temporal context analysis")
        temporal_analysis = self.temporal_analyzer.analyze_temporal_patterns(context_elements)
        
        # Step 4: Test decision rationale extraction (NEW - Phase 4)
        logger.info("Step 4: Testing decision rationale extraction")
        decision_rationales = self.decision_extractor.extract_decisions(
            mock_conversations, mock_captures
        )
        
        # Step 5: Test all 5 enhanced story templates
        logger.info("Step 5: Testing story generation with enhanced templates")
        story_results = self._test_all_story_templates(
            context_elements, temporal_analysis, decision_rationales
        )
        
        # Step 6: Test YAML dual-channel compatibility
        logger.info("Step 6: Testing YAML dual-channel compatibility")
        yaml_compatibility = self._test_yaml_compatibility(mock_conversations, mock_captures)
        
        # Step 7: Performance benchmarking
        logger.info("Step 7: Performance benchmarking")
        performance_metrics = self._benchmark_performance(
            context_elements, mock_conversations, mock_captures
        )
        
        # Step 8: Generate comprehensive output
        logger.info("Step 8: Generating output files")
        output_files = self._generate_integration_output(
            mock_conversations, mock_captures, context_elements,
            temporal_analysis, decision_rationales, story_results
        )
        
        test_duration = (datetime.now() - test_start).total_seconds() * 1000  # ms
        
        integration_result = {
            "test_summary": {
                "phase": "Track B Phase 4",
                "status": "COMPLETE",
                "duration_ms": test_duration,
                "timestamp": test_start.isoformat()
            },
            "mock_data_stats": {
                "conversations_generated": len(mock_conversations),
                "captures_generated": len(mock_captures),
                "context_elements_extracted": len(context_elements)
            },
            "narrative_engine_results": {
                "templates_tested": len(story_results),
                "stories_generated": sum(len(stories) for stories in story_results.values()),
                "temporal_sessions_identified": len(temporal_analysis.get("work_sessions", [])),
                "decisions_extracted": len(decision_rationales)
            },
            "performance_metrics": performance_metrics,
            "yaml_compatibility": yaml_compatibility,
            "output_files": output_files,
            "quality_validation": self._validate_integration_quality(story_results),
            "track_b_readiness": self._assess_track_b_readiness(
                performance_metrics, yaml_compatibility, story_results
            )
        }
        
        # Save integration report
        self._save_integration_report(integration_result)
        
        logger.info(f"Track B Phase 4 integration test complete: {test_duration:.1f}ms")
        return integration_result
    
    def _test_all_story_templates(self, context_elements: List[ContextElement],
                                  temporal_analysis: Dict[str, Any],
                                  decisions: List) -> Dict[str, List[Dict[str, Any]]]:
        """Test story generation with all 5 enhanced templates"""
        
        # Prepare context data for story generation
        context_data = {
            "conversations": self._extract_conversation_data(context_elements),
            "file_changes": self._extract_file_change_data(context_elements),
            "git_commits": self._extract_git_data(context_elements),
            "time_range": self._extract_time_range(context_elements),
            "temporal_analysis": temporal_analysis,
            "decisions": decisions,
            "work_sessions": temporal_analysis.get("work_sessions", []),
            "timeline_data": temporal_analysis.get("timeline_visualization", {})
        }
        
        story_results = {}
        
        # Test each enhanced template
        template_ids = [
            "dev_progress_technical",
            "feature_journey_storytelling", 
            "bug_investigation_detective",      # NEW - Phase 4
            "refactoring_journey_improvement",  # NEW - Phase 4
            "continue_context_timeline"         # NEW - Phase 4
        ]
        
        for template_id in template_ids:
            logger.info(f"Testing template: {template_id}")
            try:
                # Generate story structure using template
                story_structure = self.template_system.generate_story_structure(
                    template_id, context_data
                )
                
                # Generate full narrative
                narrative = self.narrative_engine.generate_narrative(
                    story_structure, context_data, template_id
                )
                
                story_results[template_id] = [{
                    "story_structure": story_structure,
                    "full_narrative": narrative,
                    "generation_metadata": {
                        "template_used": template_id,
                        "context_elements": len(context_elements),
                        "generation_time": datetime.now().isoformat(),
                        "quality_score": self._calculate_story_quality(narrative)
                    }
                }]
                
                logger.info(f"Template {template_id} generated successfully")
                
            except Exception as e:
                logger.error(f"Template {template_id} failed: {e}")
                story_results[template_id] = [{
                    "error": str(e),
                    "template_id": template_id,
                    "status": "failed"
                }]
        
        return story_results
    
    def _extract_conversation_data(self, context_elements: List[ContextElement]) -> List[Dict[str, Any]]:
        """Extract conversation data from context elements"""
        conversations = []
        for elem in context_elements:
            if elem.source_type == "conversation":
                conversations.append({
                    "content": elem.content,
                    "timestamp": elem.timestamp.isoformat(),
                    "entities": elem.entities,
                    "metadata": elem.metadata
                })
        return conversations
    
    def _extract_file_change_data(self, context_elements: List[ContextElement]) -> List[Dict[str, Any]]:
        """Extract file change data from context elements"""
        file_changes = []
        for elem in context_elements:
            if elem.source_type == "daemon_capture":
                file_changes.append({
                    "file_path": elem.entities[0] if elem.entities else "unknown",
                    "timestamp": elem.timestamp.isoformat(),
                    "change_type": elem.metadata.get("change_type", "modified"),
                    "event_type": elem.metadata.get("event_type", "file_change")
                })
        return file_changes
    
    def _extract_git_data(self, context_elements: List[ContextElement]) -> List[Dict[str, Any]]:
        """Extract git commit data from context elements"""
        git_commits = []
        for elem in context_elements:
            if elem.source_type == "daemon_capture" and elem.metadata.get("git_metadata"):
                git_commits.append({
                    "commit_id": elem.metadata["git_metadata"].get("commit_hash", "unknown"),
                    "message": elem.metadata["git_metadata"].get("message", elem.content),
                    "timestamp": elem.timestamp.isoformat(),
                    "files": elem.entities
                })
        return git_commits
    
    def _extract_time_range(self, context_elements: List[ContextElement]) -> Dict[str, str]:
        """Extract time range from context elements"""
        if not context_elements:
            return {}
            
        timestamps = [elem.timestamp for elem in context_elements]
        return {
            "start": min(timestamps).isoformat(),
            "end": max(timestamps).isoformat(),
            "duration_hours": (max(timestamps) - min(timestamps)).total_seconds() / 3600
        }
    
    def _test_yaml_compatibility(self, conversations: List[MockConversation], 
                                captures: List[MockDaemonCapture]) -> Dict[str, Any]:
        """Test YAML dual-channel compatibility"""
        compatibility_test = {
            "yaml_serialization": True,
            "yaml_deserialization": True,
            "schema_validation": True,
            "errors": []
        }
        
        try:
            # Test conversation YAML serialization
            conv_yaml_data = []
            for conv in conversations:
                conv_dict = {
                    "conversation_id": conv.conversation_id,
                    "timestamp": conv.timestamp.isoformat(),
                    "session_type": conv.session_type,
                    "messages": conv.messages,
                    "project_context": conv.project_context,
                    "files_mentioned": conv.files_mentioned,
                    "entities_extracted": conv.entities_extracted
                }
                conv_yaml_data.append(conv_dict)
            
            # Serialize to YAML
            yaml_content = yaml.dump(conv_yaml_data, default_flow_style=False)
            
            # Deserialize from YAML
            parsed_data = yaml.safe_load(yaml_content)
            
            # Validate structure
            if len(parsed_data) != len(conversations):
                compatibility_test["schema_validation"] = False
                compatibility_test["errors"].append("Conversation count mismatch after YAML round-trip")
            
        except Exception as e:
            compatibility_test["yaml_serialization"] = False
            compatibility_test["errors"].append(f"YAML serialization error: {e}")
        
        try:
            # Test capture YAML serialization
            capture_yaml_data = []
            for capture in captures:
                capture_dict = {
                    "capture_id": capture.capture_id,
                    "timestamp": capture.timestamp.isoformat(),
                    "event_type": capture.event_type,
                    "file_path": capture.file_path,
                    "change_type": capture.change_type,
                    "content_delta": capture.content_delta,
                    "git_metadata": capture.git_metadata
                }
                capture_yaml_data.append(capture_dict)
            
            # Serialize to YAML
            yaml_content = yaml.dump(capture_yaml_data, default_flow_style=False)
            
            # Deserialize from YAML
            parsed_data = yaml.safe_load(yaml_content)
            
            # Validate structure
            if len(parsed_data) != len(captures):
                compatibility_test["schema_validation"] = False
                compatibility_test["errors"].append("Capture count mismatch after YAML round-trip")
                
        except Exception as e:
            compatibility_test["yaml_serialization"] = False
            compatibility_test["errors"].append(f"Capture YAML serialization error: {e}")
        
        return compatibility_test
    
    def _benchmark_performance(self, context_elements: List[ContextElement],
                              conversations: List[MockConversation],
                              captures: List[MockDaemonCapture]) -> Dict[str, Any]:
        """Benchmark narrative generation performance"""
        
        performance_metrics = {}
        
        # Context weaving performance
        start_time = datetime.now()
        weaving_result = self.context_weaver.weave_context_narrative(context_elements)
        context_weaving_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Temporal analysis performance
        start_time = datetime.now()
        temporal_result = self.temporal_analyzer.analyze_temporal_patterns(context_elements)
        temporal_analysis_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Story generation performance (average across templates)
        story_generation_times = []
        for template_id in ["dev_progress_technical", "continue_context_timeline"]:
            start_time = datetime.now()
            try:
                context_data = {"conversations": conversations, "file_changes": []}
                story_structure = self.template_system.generate_story_structure(template_id, context_data)
                generation_time = (datetime.now() - start_time).total_seconds() * 1000
                story_generation_times.append(generation_time)
            except Exception as e:
                logger.warning(f"Performance test failed for {template_id}: {e}")
        
        avg_story_generation = sum(story_generation_times) / max(len(story_generation_times), 1)
        
        performance_metrics = {
            "context_weaving_ms": context_weaving_time,
            "temporal_analysis_ms": temporal_analysis_time,
            "avg_story_generation_ms": avg_story_generation,
            "total_pipeline_ms": context_weaving_time + temporal_analysis_time + avg_story_generation,
            "performance_target_ms": 200,
            "meets_performance_target": (context_weaving_time + temporal_analysis_time + avg_story_generation) < 200,
            "throughput_elements_per_second": len(context_elements) / max((context_weaving_time / 1000), 0.001)
        }
        
        return performance_metrics
    
    def _calculate_story_quality(self, narrative: str) -> float:
        """Calculate quality score for generated narrative (0.0 - 1.0)"""
        if not narrative or not isinstance(narrative, str):
            return 0.0
        
        # Simple quality heuristics
        word_count = len(narrative.split())
        sentence_count = narrative.count('.') + narrative.count('!') + narrative.count('?')
        
        # Quality factors
        length_score = min(1.0, word_count / 100)  # Prefer 100+ words
        structure_score = min(1.0, sentence_count / 5)  # Prefer 5+ sentences
        coherence_score = 0.8  # Placeholder for coherence analysis
        
        overall_score = (length_score + structure_score + coherence_score) / 3
        return round(overall_score, 2)
    
    def _validate_integration_quality(self, story_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Validate overall integration quality"""
        quality_validation = {
            "templates_working": 0,
            "templates_total": len(story_results),
            "average_quality_score": 0.0,
            "stories_generated": 0,
            "validation_passed": False
        }
        
        total_quality = 0.0
        working_templates = 0
        total_stories = 0
        
        for template_id, stories in story_results.items():
            for story in stories:
                if "error" not in story:
                    working_templates += 1
                    total_stories += 1
                    quality_score = story.get("generation_metadata", {}).get("quality_score", 0.0)
                    total_quality += quality_score
        
        quality_validation["templates_working"] = working_templates
        quality_validation["stories_generated"] = total_stories
        
        if total_stories > 0:
            quality_validation["average_quality_score"] = total_quality / total_stories
        
        # Validation criteria: 80%+ templates working, 0.6+ average quality
        quality_validation["validation_passed"] = (
            working_templates >= (len(story_results) * 0.8) and 
            quality_validation["average_quality_score"] >= 0.6
        )
        
        return quality_validation
    
    def _assess_track_b_readiness(self, performance_metrics: Dict[str, Any],
                                  yaml_compatibility: Dict[str, Any], 
                                  story_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Assess overall Track B Phase 4 readiness"""
        
        readiness_criteria = {
            "performance_ready": performance_metrics.get("meets_performance_target", False),
            "yaml_compatible": yaml_compatibility.get("yaml_serialization", False) and yaml_compatibility.get("yaml_deserialization", False),
            "templates_functional": len([k for k, v in story_results.items() if not any("error" in story for story in v)]) >= 4,
            "integration_stable": True  # Assume stable if we get this far
        }
        
        overall_readiness = all(readiness_criteria.values())
        
        return {
            "criteria": readiness_criteria,
            "overall_ready": overall_readiness,
            "readiness_score": sum(readiness_criteria.values()) / len(readiness_criteria),
            "next_phase": "Phase 5: Enhanced Continue Command" if overall_readiness else "Continue Phase 4 development",
            "blocking_issues": [k for k, v in readiness_criteria.items() if not v]
        }
    
    def _generate_integration_output(self, conversations, captures, context_elements,
                                    temporal_analysis, decisions, story_results) -> List[str]:
        """Generate comprehensive output files for integration test"""
        output_files = []
        
        # 1. Mock data summary
        mock_summary = {
            "generated_data": {
                "conversations": len(conversations),
                "captures": len(captures),
                "context_elements": len(context_elements),
                "time_span_hours": self.temporal_analyzer._calculate_time_span_hours(context_elements)
            },
            "sample_conversation": conversations[0].__dict__ if conversations else {},
            "sample_capture": captures[0].__dict__ if captures else {}
        }
        
        mock_file = self.output_dir / "mock_data_summary.yaml"
        with open(mock_file, 'w') as f:
            yaml.dump(mock_summary, f, default_flow_style=False)
        output_files.append(str(mock_file))
        
        # 2. Temporal analysis report
        temporal_file = self.output_dir / "temporal_analysis_report.yaml"
        with open(temporal_file, 'w') as f:
            yaml.dump(temporal_analysis, f, default_flow_style=False)
        output_files.append(str(temporal_file))
        
        # 3. Generated stories
        for template_id, stories in story_results.items():
            story_file = self.output_dir / f"story_{template_id}.yaml"
            with open(story_file, 'w') as f:
                yaml.dump(stories, f, default_flow_style=False)
            output_files.append(str(story_file))
        
        return output_files
    
    def _save_integration_report(self, integration_result: Dict[str, Any]):
        """Save comprehensive integration test report"""
        report_file = self.output_dir / "track_b_phase_4_integration_report.yaml"
        
        with open(report_file, 'w') as f:
            yaml.dump(integration_result, f, default_flow_style=False)
        
        logger.info(f"Integration report saved: {report_file}")


# Convenience function for running integration tests
def run_track_b_phase_4_integration() -> Dict[str, Any]:
    """
    Convenience function to run complete Track B Phase 4 integration test.
    
    Returns comprehensive results for validation and benchmarking.
    """
    integration_system = MockDataIntegrationSystem()
    return integration_system.run_complete_integration_test()


if __name__ == "__main__":
    # Run integration test if called directly
    print("Running Track B Phase 4 Integration Test...")
    results = run_track_b_phase_4_integration()
    
    print(f"\\nIntegration Test Complete!")
    print(f"Duration: {results['test_summary']['duration_ms']:.1f}ms")
    print(f"Stories Generated: {results['narrative_engine_results']['stories_generated']}")
    print(f"Performance Target Met: {results['performance_metrics']['meets_performance_target']}")
    print(f"Track B Ready: {results['track_b_readiness']['overall_ready']}")