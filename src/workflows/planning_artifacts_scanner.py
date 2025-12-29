"""
Planning Artifacts Scanner

Scans cortex-brain/planning/ directory to discover all planning artifacts
and classify them by type.

Part of Phase 2: Migration System
"""

import json
import yaml
from pathlib import Path
from typing import List, Dict, Optional, Set
from enum import Enum
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


class ArtifactType(Enum):
    """Classification of planning artifacts"""
    MASTER_PLAN = "master_plan"
    SUB_PLAN = "sub_plan"
    TRACKER = "tracker"
    REPORT = "report"
    UNKNOWN = "unknown"


@dataclass
class PlanMetadata:
    """Metadata extracted from a planning artifact"""
    file_path: Path
    artifact_type: ArtifactType
    plan_id: Optional[str] = None
    title: Optional[str] = None
    created_date: Optional[str] = None
    status: Optional[str] = None
    parent_plan_id: Optional[str] = None
    is_yaml: bool = False
    is_markdown: bool = False
    raw_metadata: Dict = field(default_factory=dict)


@dataclass
class PlanDiscovery:
    """Results of scanning planning directory"""
    all_artifacts: List[PlanMetadata] = field(default_factory=list)
    master_plans: List[PlanMetadata] = field(default_factory=list)
    sub_plans: List[PlanMetadata] = field(default_factory=list)
    trackers: List[PlanMetadata] = field(default_factory=list)
    reports: List[PlanMetadata] = field(default_factory=list)
    unknown: List[PlanMetadata] = field(default_factory=list)
    plan_relationships: Dict[str, List[PlanMetadata]] = field(default_factory=dict)
    orphaned_artifacts: List[PlanMetadata] = field(default_factory=list)


class PlanningArtifactsScanner:
    """
    Scans cortex-brain/planning/ to discover and classify all planning artifacts.
    
    Responsibilities:
    - Recursively scan planning directory
    - Classify artifacts by type (master plan, sub-plan, tracker, report)
    - Extract metadata from YAML frontmatter and markdown headers
    - Detect relationships between plans
    - Identify orphaned artifacts
    """
    
    def __init__(self, planning_directory: Path):
        """
        Initialize scanner with planning directory path.
        
        Args:
            planning_directory: Path to cortex-brain/planning/
        """
        self.planning_directory = Path(planning_directory)
        logger.info(f"Initialized PlanningArtifactsScanner for {self.planning_directory}")
    
    def scan_directory(self) -> PlanDiscovery:
        """
        Scan planning directory and discover all artifacts.
        
        Returns:
            PlanDiscovery object with all discovered artifacts
        """
        logger.info(f"Starting scan of {self.planning_directory}")
        
        if not self.planning_directory.exists():
            logger.warning(f"Planning directory does not exist: {self.planning_directory}")
            return PlanDiscovery()
        
        discovery = PlanDiscovery()
        
        # Scan for all YAML and MD files
        yaml_files = list(self.planning_directory.rglob("*.yaml"))
        md_files = list(self.planning_directory.rglob("*.md"))
        
        all_files = yaml_files + md_files
        logger.info(f"Found {len(all_files)} files ({len(yaml_files)} YAML, {len(md_files)} MD)")
        
        # Process each file
        for file_path in all_files:
            metadata = self._process_file(file_path)
            if metadata:
                discovery.all_artifacts.append(metadata)
                
                # Categorize by type
                if metadata.artifact_type == ArtifactType.MASTER_PLAN:
                    discovery.master_plans.append(metadata)
                elif metadata.artifact_type == ArtifactType.SUB_PLAN:
                    discovery.sub_plans.append(metadata)
                elif metadata.artifact_type == ArtifactType.TRACKER:
                    discovery.trackers.append(metadata)
                elif metadata.artifact_type == ArtifactType.REPORT:
                    discovery.reports.append(metadata)
                else:
                    discovery.unknown.append(metadata)
        
        # Detect relationships
        self._detect_plan_relationships(discovery)
        
        logger.info(
            f"Scan complete: {len(discovery.all_artifacts)} artifacts "
            f"({len(discovery.master_plans)} master, {len(discovery.sub_plans)} sub, "
            f"{len(discovery.trackers)} trackers, {len(discovery.reports)} reports, "
            f"{len(discovery.unknown)} unknown)"
        )
        
        return discovery
    
    def _process_file(self, file_path: Path) -> Optional[PlanMetadata]:
        """
        Process a single file and extract metadata.
        
        Args:
            file_path: Path to file
            
        Returns:
            PlanMetadata if file is valid, None otherwise
        """
        try:
            # Determine file type
            is_yaml = file_path.suffix.lower() == ".yaml"
            is_markdown = file_path.suffix.lower() == ".md"
            
            # Extract metadata
            if is_yaml:
                raw_metadata = self._extract_yaml_metadata(file_path)
            elif is_markdown:
                raw_metadata = self._extract_markdown_metadata(file_path)
            else:
                return None
            
            # Classify artifact type
            artifact_type = self.classify_artifact_type(file_path, raw_metadata)
            
            # Build metadata object
            metadata = PlanMetadata(
                file_path=file_path,
                artifact_type=artifact_type,
                plan_id=raw_metadata.get("plan_id"),
                title=raw_metadata.get("title"),
                created_date=raw_metadata.get("created_date") or raw_metadata.get("created"),
                status=raw_metadata.get("status"),
                parent_plan_id=raw_metadata.get("parent_plan_id") or raw_metadata.get("parent_plan"),
                is_yaml=is_yaml,
                is_markdown=is_markdown,
                raw_metadata=raw_metadata
            )
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return None
    
    def _extract_yaml_metadata(self, file_path: Path) -> Dict:
        """Extract metadata from YAML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict):
                    return data
                return {}
        except Exception as e:
            logger.error(f"Failed to parse YAML {file_path}: {e}")
            return {}
    
    def _extract_markdown_metadata(self, file_path: Path) -> Dict:
        """Extract metadata from Markdown frontmatter and headers"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = {}
            
            # Try to extract YAML frontmatter
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    try:
                        frontmatter = yaml.safe_load(parts[1])
                        if isinstance(frontmatter, dict):
                            metadata.update(frontmatter)
                    except:
                        pass
            
            # Extract title from first H1
            lines = content.split('\n')
            for line in lines:
                if line.startswith("# "):
                    if "title" not in metadata:
                        metadata["title"] = line[2:].strip()
                    break
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to parse Markdown {file_path}: {e}")
            return {}
    
    def classify_artifact_type(self, file_path: Path, metadata: Dict) -> ArtifactType:
        """
        Classify artifact type based on filename and metadata.
        
        Args:
            file_path: Path to file
            metadata: Extracted metadata dict
            
        Returns:
            ArtifactType enum value
        """
        filename = file_path.name.lower()
        
        # Check explicit artifact_type in metadata
        if "artifact_type" in metadata:
            type_str = metadata["artifact_type"].lower()
            try:
                return ArtifactType(type_str)
            except ValueError:
                pass
        
        # Check by filename patterns
        if "master" in filename and "plan" in filename:
            return ArtifactType.MASTER_PLAN
        
        if "sub-plan" in filename or "subplan" in filename:
            return ArtifactType.SUB_PLAN
        
        if "tracker" in filename or "visual-tracker" in filename:
            return ArtifactType.TRACKER
        
        if "report" in filename or "status" in filename:
            return ArtifactType.REPORT
        
        # Check by parent_plan_id (indicates sub-plan)
        if metadata.get("parent_plan_id") or metadata.get("parent_plan"):
            return ArtifactType.SUB_PLAN
        
        # Check by plan_id (indicates master plan if no parent)
        if metadata.get("plan_id") and not metadata.get("parent_plan_id"):
            return ArtifactType.MASTER_PLAN
        
        return ArtifactType.UNKNOWN
    
    def extract_plan_metadata(self, file_path: Path) -> Optional[PlanMetadata]:
        """
        Extract metadata from a specific plan file.
        
        Args:
            file_path: Path to plan file
            
        Returns:
            PlanMetadata or None if extraction fails
        """
        return self._process_file(file_path)
    
    def detect_plan_relationships(self, artifacts: List[PlanMetadata]) -> Dict[str, List[PlanMetadata]]:
        """
        Detect relationships between plans based on plan_id and parent_plan_id.
        
        Args:
            artifacts: List of PlanMetadata objects
            
        Returns:
            Dict mapping plan_id to list of related sub-plans
        """
        discovery = PlanDiscovery(all_artifacts=artifacts)
        self._detect_plan_relationships(discovery)
        return discovery.plan_relationships
    
    def _detect_plan_relationships(self, discovery: PlanDiscovery):
        """
        Internal method to populate plan_relationships and orphaned_artifacts.
        
        Args:
            discovery: PlanDiscovery object to populate
        """
        # Build map of plan_id -> master plan
        master_plan_map = {}
        for master in discovery.master_plans:
            if master.plan_id:
                master_plan_map[master.plan_id] = master
        
        # Group sub-plans by parent_plan_id
        for sub_plan in discovery.sub_plans:
            parent_id = sub_plan.parent_plan_id
            if parent_id:
                if parent_id not in discovery.plan_relationships:
                    discovery.plan_relationships[parent_id] = []
                discovery.plan_relationships[parent_id].append(sub_plan)
                
                # Check if parent exists
                if parent_id not in master_plan_map:
                    if sub_plan not in discovery.orphaned_artifacts:
                        discovery.orphaned_artifacts.append(sub_plan)
            else:
                # Sub-plan without parent_plan_id
                if sub_plan not in discovery.orphaned_artifacts:
                    discovery.orphaned_artifacts.append(sub_plan)
        
        # Add trackers and reports to relationships if they have plan_id or parent_plan_id
        for artifact in discovery.trackers + discovery.reports:
            parent_id = artifact.parent_plan_id or artifact.plan_id
            if parent_id:
                if parent_id not in discovery.plan_relationships:
                    discovery.plan_relationships[parent_id] = []
                discovery.plan_relationships[parent_id].append(artifact)
                
                # Check if parent exists
                if parent_id not in master_plan_map:
                    if artifact not in discovery.orphaned_artifacts:
                        discovery.orphaned_artifacts.append(artifact)
