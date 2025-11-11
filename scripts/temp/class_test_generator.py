"""Class test generation."""

from typing import Dict, Any


class ClassTestGenerator:
    """Generates test code for classes."""
    
    def generate(self, class_info: Dict[str, Any]) -> str:
        """Generate tests for a class."""
        class_name = class_info["name"]
        test_class_name = f"Test{class_name}"
        
        tests = [f'class {test_class_name}:']
        tests.append(f'    """Tests for {class_name} class."""')
        tests.append('')
        
        # Initialization test
        if class_info["has_init"]:
            tests.append(f'    def test_{class_name.lower()}_initialization(self):')
            tests.append(f'        """Test {class_name} initialization."""')
            tests.append(f'        instance = {class_name}()')
            tests.append(f'        assert instance is not None')
        
        # Method tests
        for method in class_info.get("methods", []):
            if method["name"].startswith("_") and method["name"] != "__init__":
                continue  # Skip private methods
            
            if method["name"] != "__init__":
                tests.append('')
                tests.append(f'    def test_{method["name"]}(self):')
                tests.append(f'        """Test {method["name"]} method."""')
                tests.append(f'        instance = {class_name}()')
                
                # Generate basic call
                if method["args"]:
                    # Filter out 'self'
                    args = [a for a in method["args"] if a != "self"]
                    if args:
                        args_str = ", ".join(f"mock_{a}" for a in args)
                        tests.append(f'        result = instance.{method["name"]}({args_str})')
                    else:
                        tests.append(f'        result = instance.{method["name"]}()')
                else:
                    tests.append(f'        result = instance.{method["name"]}()')
                
                if method.get("has_return"):
                    tests.append(f'        assert result is not None')
        
        return '\n'.join(tests)
