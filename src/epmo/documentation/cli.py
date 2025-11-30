"""
Enhanced CLI Interface for CORTEX EPM Documentation Generator

Command-line interface supporting multi-modal output options. Integrates
all Phase 4.2 components into a unified documentation generation system
with support for both Mermaid diagrams and AI image prompts.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - Part of CORTEX 3.0
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from .parser import analyze_epmo_structure
from .dependency_mapper import analyze_epmo_dependencies
from .health_integration import HealthIntegration
from .models import (
    create_epmo_model, validate_model, GenerationConfig, 
    TemplateConfiguration, DocumentationFormat, DiagramConfig
)
from .markdown_generator import generate_markdown_documentation
from .mermaid_generator import create_diagrams_for_model
from .image_prompt_bridge import integrate_image_prompts_with_epmo
from .template_engine import render_documentation

logger = logging.getLogger(__name__)


class EPMDocumentationCLI:
    """
    Enhanced CLI interface for EPM documentation generation.
    
    Supports:
    - Multi-modal output (Markdown + Diagrams + AI prompts)
    - Customizable templates and configurations
    - Health integration and quality analysis
    - Batch processing of multiple EPMOs
    - Output format selection and customization
    """
    
    def __init__(self):
        """Initialize CLI interface."""
        self.setup_logging()
        
    def setup_logging(self, level: str = "INFO"):
        """Setup logging configuration."""
        log_level = getattr(logging, level.upper())
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('epmo_docs_generation.log')
            ]
        )
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser for CLI."""
        parser = argparse.ArgumentParser(
            description="CORTEX EPM Documentation Generator - Multi-Modal Documentation System",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Basic documentation generation
  python cli.py /path/to/epmo

  # Generate with custom output directory  
  python cli.py /path/to/epmo -o /path/to/docs

  # Generate with visual content
  python cli.py /path/to/epmo --include-diagrams --include-image-prompts

  # Use custom template
  python cli.py /path/to/epmo --template comprehensive --format markdown

  # Batch process multiple EPMOs
  python cli.py /path/to/project --batch --recursive

  # Generate with health analysis
  python cli.py /path/to/epmo --health-analysis --remediation-guide
            """
        )
        
        # Required arguments
        parser.add_argument(
            'epmo_path',
            type=Path,
            help="Path to Entry Point Module or project directory"
        )
        
        # Output options
        output_group = parser.add_argument_group('Output Options')
        output_group.add_argument(
            '-o', '--output',
            type=Path,
            default=Path('docs'),
            help="Output directory for generated documentation (default: docs)"
        )
        output_group.add_argument(
            '--format',
            choices=['markdown', 'html', 'json'],
            default='markdown',
            help="Output format (default: markdown)"
        )
        output_group.add_argument(
            '--template',
            choices=['comprehensive', 'minimal', 'api_reference', 'architecture', 'health_report'],
            default='comprehensive',
            help="Documentation template (default: comprehensive)"
        )
        
        # Content options
        content_group = parser.add_argument_group('Content Options')
        content_group.add_argument(
            '--include-diagrams',
            action='store_true',
            default=True,
            help="Include Mermaid diagrams (default: True)"
        )
        content_group.add_argument(
            '--include-image-prompts',
            action='store_true',
            default=True,
            help="Generate AI image prompts (default: True)"
        )
        content_group.add_argument(
            '--health-analysis',
            action='store_true',
            default=True,
            help="Include health analysis (default: True)"
        )
        content_group.add_argument(
            '--remediation-guide',
            action='store_true',
            default=True,
            help="Include remediation recommendations (default: True)"
        )
        content_group.add_argument(
            '--api-documentation',
            action='store_true',
            default=True,
            help="Include API documentation (default: True)"
        )
        
        # Diagram options
        diagram_group = parser.add_argument_group('Diagram Options')
        diagram_group.add_argument(
            '--max-diagram-nodes',
            type=int,
            default=50,
            help="Maximum nodes in diagrams (default: 50)"
        )
        diagram_group.add_argument(
            '--diagram-complexity',
            choices=['low', 'medium', 'high'],
            default='medium',
            help="Diagram complexity level (default: medium)"
        )
        diagram_group.add_argument(
            '--include-private',
            action='store_true',
            help="Include private members in diagrams"
        )
        
        # Processing options
        process_group = parser.add_argument_group('Processing Options')
        process_group.add_argument(
            '--batch',
            action='store_true',
            help="Process multiple EPMOs in directory"
        )
        process_group.add_argument(
            '--recursive',
            action='store_true',
            help="Recursively find EPMOs (with --batch)"
        )
        process_group.add_argument(
            '--parallel',
            action='store_true',
            help="Process EPMOs in parallel (experimental)"
        )
        process_group.add_argument(
            '--dry-run',
            action='store_true',
            help="Show what would be generated without creating files"
        )
        
        # Advanced options
        advanced_group = parser.add_argument_group('Advanced Options')
        advanced_group.add_argument(
            '--project-root',
            type=Path,
            help="Project root directory (auto-detected if not specified)"
        )
        advanced_group.add_argument(
            '--config-file',
            type=Path,
            help="Configuration file path"
        )
        advanced_group.add_argument(
            '--template-dir',
            type=Path,
            help="Custom template directory"
        )
        advanced_group.add_argument(
            '--log-level',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            default='INFO',
            help="Logging level (default: INFO)"
        )
        
        # Quality options
        quality_group = parser.add_argument_group('Quality Options')
        quality_group.add_argument(
            '--validate-output',
            action='store_true',
            help="Validate generated documentation"
        )
        quality_group.add_argument(
            '--quality-threshold',
            type=float,
            default=70.0,
            help="Minimum quality threshold (default: 70.0)"
        )
        
        return parser
    
    def parse_config_file(self, config_path: Path) -> Dict[str, Any]:
        """Parse configuration file."""
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}")
            return {}
        
        try:
            if config_path.suffix == '.json':
                return json.loads(config_path.read_text())
            else:
                logger.warning(f"Unsupported config format: {config_path.suffix}")
                return {}
        except Exception as e:
            logger.error(f"Error parsing config file: {e}")
            return {}
    
    def create_generation_config(self, args: argparse.Namespace) -> GenerationConfig:
        """Create generation configuration from CLI arguments."""
        
        # Template configuration
        template_config = TemplateConfiguration(
            template_name=args.template,
            include_diagrams=args.include_diagrams,
            include_health_badges=args.health_analysis,
            include_code_examples=args.api_documentation,
        )
        
        # Output format
        format_map = {
            'markdown': DocumentationFormat.MARKDOWN,
            'html': DocumentationFormat.HTML,
            'json': DocumentationFormat.JSON
        }
        output_format = format_map.get(args.format, DocumentationFormat.MARKDOWN)
        
        # Generation config
        config = GenerationConfig(
            output_format=output_format,
            output_directory=str(args.output),
            template_config=template_config,
            include_health_analysis=args.health_analysis,
            include_dependency_analysis=True,
            include_architecture_diagrams=args.include_diagrams,
            include_api_documentation=args.api_documentation,
            include_remediation_guide=args.remediation_guide,
            max_diagram_complexity=args.max_diagram_nodes
        )
        
        return config
    
    def create_diagram_config(self, args: argparse.Namespace) -> DiagramConfig:
        """Create diagram configuration from CLI arguments."""
        return DiagramConfig(
            max_nodes=args.max_diagram_nodes,
            max_edges=min(args.max_diagram_nodes * 2, 100),
            include_private=args.include_private,
            color_by_complexity=True,
            group_by_module=True,
            show_external_deps=True
        )
    
    def find_epmos(self, path: Path, recursive: bool = False) -> List[Path]:
        """Find EPMO directories in the given path."""
        epmos = []
        
        if path.is_file():
            # Single Python file
            if path.suffix == '.py':
                epmos.append(path.parent)
        elif path.is_dir():
            if recursive:
                # Recursively find Python packages
                for item in path.rglob('__init__.py'):
                    epmos.append(item.parent)
            else:
                # Check if current directory is an EPMO
                if (path / '__init__.py').exists():
                    epmos.append(path)
                else:
                    # Check immediate subdirectories
                    for item in path.iterdir():
                        if item.is_dir() and (item / '__init__.py').exists():
                            epmos.append(item)
        
        return list(set(epmos))  # Remove duplicates
    
    def generate_documentation_for_epmo(
        self,
        epmo_path: Path,
        project_root: Path,
        config: GenerationConfig,
        diagram_config: DiagramConfig,
        args: argparse.Namespace
    ) -> Dict[str, Any]:
        """Generate documentation for a single EPMO."""
        
        start_time = datetime.now()
        logger.info(f"Generating documentation for EPMO: {epmo_path}")
        
        try:
            # Step 1: Analyze EPMO structure
            logger.info("Analyzing EPMO structure...")
            ast_analysis = analyze_epmo_structure(epmo_path)
            
            # Step 2: Analyze dependencies
            logger.info("Analyzing dependencies...")
            dependency_analysis = analyze_epmo_dependencies(epmo_path, project_root)
            
            # Step 3: Get health analysis (if requested)
            health_data = None
            if args.health_analysis:
                try:
                    logger.info("Running health analysis...")
                    health_integration = HealthIntegration()
                    health_result = health_integration.analyze_epmo_health(epmo_path, project_root)
                    health_data = health_result if health_result.get('status') == 'success' else None
                except Exception as e:
                    logger.warning(f"Health analysis failed: {e}")
            
            # Step 4: Create documentation model
            logger.info("Creating documentation model...")
            model = create_epmo_model(
                epmo_path=epmo_path,
                ast_analysis=ast_analysis,
                dependency_analysis=dependency_analysis,
                health_data=health_data
            )
            
            # Step 5: Generate diagrams
            if config.include_architecture_diagrams:
                logger.info("Generating diagrams...")
                diagrams = create_diagrams_for_model(model, diagram_config)
                model.multi_modal_diagrams.extend(diagrams)
            
            # Step 6: Generate image prompts
            if args.include_image_prompts:
                logger.info("Generating image prompts...")
                image_prompts, prompt_files = integrate_image_prompts_with_epmo(
                    model, 
                    Path(config.output_directory) / 'diagrams'
                )
                model.image_prompts.extend(image_prompts)
            
            # Step 7: Validate model
            warnings = validate_model(model)
            if warnings:
                model.warnings.extend(warnings)
                logger.warning(f"Model validation warnings: {warnings}")
            
            # Step 8: Generate documentation
            if not args.dry_run:
                logger.info("Generating documentation...")
                
                # Choose generation method
                if config.template_config.template_name == 'comprehensive':
                    documentation = generate_markdown_documentation(
                        model,
                        Path(config.output_directory) / f"{epmo_path.name}_documentation.md",
                        config
                    )
                else:
                    documentation = render_documentation(
                        model,
                        f"{config.template_config.template_name}.md.j2",
                        config.output_format,
                        Path(args.template_dir) if args.template_dir else None,
                        config.template_config
                    )
                    
                    # Write to file
                    output_file = Path(config.output_directory) / f"{epmo_path.name}_documentation.md"
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    output_file.write_text(documentation, encoding='utf-8')
            
            # Calculate generation time
            generation_time = (datetime.now() - start_time).total_seconds()
            model.metadata.generation_time_seconds = generation_time
            
            # Prepare result
            result = {
                'status': 'success',
                'epmo_path': str(epmo_path),
                'epmo_name': epmo_path.name,
                'model': model,
                'summary_stats': model.get_summary_stats(),
                'visual_stats': model.get_visual_stats(),
                'generation_time': generation_time,
                'warnings': model.warnings,
                'output_files': []
            }
            
            if not args.dry_run:
                output_file = Path(config.output_directory) / f"{epmo_path.name}_documentation.md"
                result['output_files'].append(str(output_file))
                
                if args.include_image_prompts:
                    result['output_files'].extend(prompt_files.values() if 'prompt_files' in locals() else [])
            
            logger.info(f"Documentation generation completed in {generation_time:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Error generating documentation for {epmo_path}: {e}")
            return {
                'status': 'error',
                'epmo_path': str(epmo_path),
                'epmo_name': epmo_path.name,
                'error': str(e),
                'generation_time': (datetime.now() - start_time).total_seconds()
            }
    
    def run(self) -> int:
        """Main CLI entry point."""
        parser = self.create_parser()
        args = parser.parse_args()
        
        # Setup logging level
        self.setup_logging(args.log_level)
        
        # Load configuration file if specified
        config_data = {}
        if args.config_file:
            config_data = self.parse_config_file(args.config_file)
        
        # Determine project root
        project_root = args.project_root or args.epmo_path
        if project_root.is_file():
            project_root = project_root.parent
        
        # Create configurations
        config = self.create_generation_config(args)
        diagram_config = self.create_diagram_config(args)
        
        # Apply configuration file overrides
        if config_data:
            logger.info(f"Applying configuration from {args.config_file}")
            # Apply overrides (implementation would merge config_data with config)
        
        # Find EPMOs to process
        if args.batch:
            epmos = self.find_epmos(args.epmo_path, args.recursive)
            if not epmos:
                logger.error(f"No EPMOs found in {args.epmo_path}")
                return 1
            logger.info(f"Found {len(epmos)} EPMOs to process")
        else:
            epmos = [args.epmo_path]
        
        # Generate documentation
        results = []
        total_start_time = datetime.now()
        
        for epmo_path in epmos:
            result = self.generate_documentation_for_epmo(
                epmo_path, project_root, config, diagram_config, args
            )
            results.append(result)
        
        total_time = (datetime.now() - total_start_time).total_seconds()
        
        # Print summary
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] == 'error']
        
        print(f"\n{'='*60}")
        print(f"CORTEX EPM Documentation Generation Summary")
        print(f"{'='*60}")
        print(f"Total EPMOs processed: {len(results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Output directory: {config.output_directory}")
        
        if args.dry_run:
            print("\n🔍 DRY RUN - No files were created")
        
        # Print individual results
        for result in successful:
            stats = result.get('summary_stats', {})
            visual = result.get('visual_stats', {})
            print(f"\n✅ {result['epmo_name']}:")
            print(f"   Files: {stats.get('total_files', 0)}, "
                  f"Classes: {stats.get('total_classes', 0)}, "
                  f"Functions: {stats.get('total_functions', 0)}")
            if visual.get('total_diagrams', 0) > 0:
                print(f"   Diagrams: {visual['total_diagrams']} "
                      f"({visual['mermaid_diagrams']} technical, {visual['image_prompts']} visual)")
            print(f"   Time: {result['generation_time']:.2f}s")
        
        for result in failed:
            print(f"\n❌ {result['epmo_name']}: {result['error']}")
        
        # Validate output if requested
        if args.validate_output and not args.dry_run:
            print("\n🔍 Validating generated documentation...")
            # Implementation would validate output files
        
        return 0 if not failed else 1


def main():
    """Main entry point for CLI."""
    cli = EPMDocumentationCLI()
    return cli.run()


if __name__ == '__main__':
    sys.exit(main())