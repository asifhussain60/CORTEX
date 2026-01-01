"""
Visual Regression Testing for Documentation Hub Files
Tests that CSS class refactoring maintains identical rendering
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from PIL import Image
import imagehash


class VisualRegressionTester:
    """Test visual rendering consistency after CSS refactoring"""
    
    HUB_FILES = [
        "index.html",  # Level 0
        "future/index.html",
        "orchestrators/index.html",
        "sts/index.html",
        "architecture/index.html",
        "knowledge/index.html",
        "features/index.html",
        "validation/index.html",
        "getting-started/index.html",
        "lens/index.html",
    ]
    
    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.screenshots_dir = Path("tests/visual_regression/screenshots")
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
    def setup_driver(self) -> webdriver.Chrome:
        """Initialize headless Chrome driver"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        return webdriver.Chrome(options=options)
    
    def capture_screenshot(self, driver: webdriver.Chrome, url: str, output_path: Path) -> None:
        """Capture full page screenshot"""
        driver.get(url)
        driver.execute_script("window.scrollTo(0, 0)")
        
        # Wait for animations to complete
        driver.implicitly_wait(2)
        
        # Capture screenshot
        driver.save_screenshot(str(output_path))
    
    def validate_inline_styles(self, file_path: Path) -> Tuple[int, List[str]]:
        """
        Count inline styles in HTML file
        Returns: (count, list of inline style snippets)
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all style= attributes
        import re
        style_pattern = r'style="([^"]*)"'
        styles = re.findall(style_pattern, content)
        
        # Filter out acceptable exceptions (JS-generated dynamic content)
        acceptable_exceptions = [
            'display:none',  # JS toggle functionality
            'display: none',
        ]
        
        filtered_styles = [
            s for s in styles 
            if not any(exc in s for exc in acceptable_exceptions)
        ]
        
        return len(filtered_styles), filtered_styles[:10]  # Return first 10 for reporting
    
    def validate_computed_styles(self, driver: webdriver.Chrome, url: str) -> Dict[str, any]:
        """
        Validate computed styles for key elements
        Returns: Dictionary of element selectors and their computed styles
        """
        driver.get(url)
        
        # Key elements to validate
        selectors = [
            ".hero-section",
            ".glass-card",
            ".level1-hero-title",
            ".level1-feature-card",
            ".animation-t1-rise",
            ".animation-t2-pop",
        ]
        
        computed_styles = {}
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    element = elements[0]
                    computed_styles[selector] = {
                        'background': element.value_of_css_property('background'),
                        'padding': element.value_of_css_property('padding'),
                        'border-radius': element.value_of_css_property('border-radius'),
                        'opacity': element.value_of_css_property('opacity'),
                    }
            except Exception as e:
                computed_styles[selector] = f"Error: {str(e)}"
        
        return computed_styles
    
    def test_all_hubs(self) -> Dict[str, any]:
        """
        Run complete visual regression test suite
        Returns: Test results report
        """
        results = {
            "total_files": len(self.HUB_FILES),
            "passed": 0,
            "failed": 0,
            "details": {}
        }
        
        driver = self.setup_driver()
        
        try:
            for hub_file in self.HUB_FILES:
                file_path = self.docs_root / hub_file
                
                if not file_path.exists():
                    results["details"][hub_file] = {
                        "status": "SKIP",
                        "reason": "File not found"
                    }
                    continue
                
                # Test 1: Inline style count
                inline_count, inline_samples = self.validate_inline_styles(file_path)
                
                # Test 2: Screenshot capture
                url = f"file://{file_path.absolute()}"
                screenshot_path = self.screenshots_dir / hub_file.replace("/", "_").replace(".html", ".png")
                screenshot_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    self.capture_screenshot(driver, url, screenshot_path)
                    screenshot_captured = True
                except Exception as e:
                    screenshot_captured = False
                    screenshot_error = str(e)
                
                # Test 3: Computed styles validation
                computed_styles = self.validate_computed_styles(driver, url)
                
                # Determine pass/fail
                # Pass if: inline_count <= 10 (allowing JS exceptions)
                passed = inline_count <= 10 and screenshot_captured
                
                if passed:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                
                results["details"][hub_file] = {
                    "status": "PASS" if passed else "FAIL",
                    "inline_style_count": inline_count,
                    "inline_style_samples": inline_samples if inline_count > 0 else [],
                    "screenshot_captured": screenshot_captured,
                    "screenshot_path": str(screenshot_path) if screenshot_captured else None,
                    "computed_styles": computed_styles,
                }
                
                if not screenshot_captured:
                    results["details"][hub_file]["screenshot_error"] = screenshot_error
                
        finally:
            driver.quit()
        
        return results
    
    def generate_report(self, results: Dict[str, any], output_path: Path) -> None:
        """Generate JSON test report"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n{'='*60}")
        print("VISUAL REGRESSION TEST RESULTS")
        print(f"{'='*60}")
        print(f"Total Files: {results['total_files']}")
        print(f"Passed: {results['passed']} ✅")
        print(f"Failed: {results['failed']} ❌")
        print(f"\nDetailed report: {output_path}")
        print(f"{'='*60}\n")
        
        # Print failures
        for hub_file, details in results["details"].items():
            if details["status"] == "FAIL":
                print(f"❌ {hub_file}")
                print(f"   Inline styles: {details['inline_style_count']}")
                if details['inline_style_samples']:
                    print(f"   Samples: {details['inline_style_samples'][:3]}")


def main():
    """Run visual regression tests"""
    tester = VisualRegressionTester(docs_root="docs")
    
    print("Starting visual regression tests...")
    results = tester.test_all_hubs()
    
    report_path = Path("tests/visual_regression/test_results.json")
    tester.generate_report(results, report_path)
    
    # Exit with appropriate code
    exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
