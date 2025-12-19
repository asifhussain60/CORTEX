# Quick Reference

## __init__



## documentation_orchestrator

### `DocumentationConfig`




### `DocumentationResult`




### `DocumentationOrchestrator`
 (inherits: BaseOrchestrator)






## api_doc_generator

### `APIDocGenerator`


- `generate_module_docs(self, module_info: ModuleInfo, output_path: Path, include_private: bool) -> Path`
- `generate_multi_module_docs(self, modules: List[ModuleInfo], output_dir: Path, index_name: str) -> Path`
- `generate_quick_reference(self, modules: List[ModuleInfo], output_path: Path) -> Path`




## __init__



## diagram_generator

### `DiagramGenerator`


- `generate_class_hierarchy(self, modules: List[ModuleInfo], output_path: Path, title: str) -> Path`
- `generate_phase_flow_diagram(self, phase_data: List[Dict[str, Any]], output_path: Path, title: str) -> Path`
- `generate_sequence_diagram(self, sequences: List[Dict[str, Any]], output_path: Path, title: str) -> Path`




## __init__



## type_extractor

### `TypeExtractor`


- `extract_type_info(self, annotation: Optional[ast.expr]) -> Dict[str, Any]`
- `format_type_for_docs(self, type_info: Dict[str, Any]) -> str`
- `extract_return_type_description(self, docstring: Optional[str]) -> Optional[str]`
- `extract_param_descriptions(self, docstring: Optional[str]) -> Dict[str, str]`




## code_analyzer

### `MethodInfo`




### `ClassInfo`




### `FunctionInfo`




### `ModuleInfo`




### `CodeAnalyzer`


- `analyze_file(self, file_path: Path) -> ModuleInfo`



