# src.operations.operation_factory

Operation Factory - Load and Create Operations from YAML

This factory loads operation definitions from cortex-op                    # Convert snake_case to CamelCase, but preserve common acronyms
                    words = module_name.split('_')
                    # Preserve common acronyms in uppercase
                    acronyms = {'api': 'API', 'sql': 'SQL', 'sqlite': 'SQLite', 'html': 'HTML', 'css': 'CSS', 'json': 'JSON', 'yaml': 'YAML', 'mkdocs': 'MkDocs', 'pdf': 'PDF', 'cli': 'CLI'}
                    class_name = ''.join(
                        acronyms.get(word.lower(), word.capitalize()) 
                        for word in words
                    ).yaml and
instantiates orchestrators with the appropriate modules.

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)
