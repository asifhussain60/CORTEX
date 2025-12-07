"""
Test Intelligence Module for CORTEX Planning System

Detects test requirements from feature descriptions and recommends
appropriate testing strategies without prescribing specific frameworks.

Features:
- Test type detection (unit, integration, e2e, visual regression)
- Headed vs headless recommendations
- Framework-agnostic guidance
- Integration with user profile for framework preferences

Author: Asif Hussain
Version: 3.8.4
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


class TestType(Enum):
    """Test type classifications."""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E_BROWSER = "e2e_browser"
    E2E_API = "e2e_api"
    VISUAL_REGRESSION = "visual_regression"
    PERFORMANCE = "performance"
    SECURITY = "security"


class ExecutionMode(Enum):
    """Test execution mode recommendations."""
    HEADLESS = "headless"
    HEADED = "headed"
    HEADLESS_PREFERRED = "headless_preferred"
    HEADED_REQUIRED = "headed_required"


@dataclass
class TestRequirement:
    """Detected test requirement."""
    test_type: TestType
    execution_mode: ExecutionMode
    confidence: float  # 0.0 to 1.0
    reasoning: str
    framework_hints: List[str]  # Suggested frameworks, not prescriptive
    headed_recommended: bool


class TestIntelligence:
    """
    Intelligent test requirement detection for planning.
    
    Analyzes feature descriptions to determine:
    - What types of tests are needed
    - Whether browser automation is required
    - Headed vs headless execution recommendations
    - Framework options (without prescribing)
    """
    
    # Detection patterns for different test types
    E2E_BROWSER_PATTERNS = [
        r'\b(user|users)\s+(clicks?|navigates?|fills?|sees?|views?|enters?|selects?|submits?)\b',
        r'\b(login|signup|register|checkout|cart|form submission)\b',
        r'\b(UI|user interface|frontend|webpage|web page|browser)\b',
        r'\b(button|input|dropdown|modal|dialog|popup)\b',
        r'\b(workflow|user journey|user flow|user experience)\b',
    ]
    
    VISUAL_REGRESSION_PATTERNS = [
        r'\b(visual|appearance|styling|layout|responsive|design)\b',
        r'\b(screenshot|snapshot|pixel-perfect|visual regression)\b',
        r'\b(CSS|theme|color|font|typography)\b',
        r'\b(mobile view|desktop view|tablet view|responsive design)\b',
    ]
    
    E2E_API_PATTERNS = [
        r'\b(API|endpoint|REST|GraphQL|microservice)\b',
        r'\b(request|response|HTTP|status code)\b',
        r'\b(authentication|authorization|token|JWT)\b',
        r'\b(integration|end-to-end API|service integration)\b',
    ]
    
    PERFORMANCE_PATTERNS = [
        r'\b(performance|speed|latency|throughput|load time)\b',
        r'\b(scalability|concurrent users|stress test|load test)\b',
        r'\b(optimization|caching|bottleneck)\b',
    ]
    
    SECURITY_PATTERNS = [
        r'\b(security|vulnerability|XSS|CSRF|SQL injection)\b',
        r'\b(authentication|authorization|access control|permissions)\b',
        r'\b(encryption|hashing|secure|OWASP)\b',
    ]
    
    def __init__(self):
        """Initialize test intelligence engine."""
        self.logger = logging.getLogger(__name__)
    
    def analyze_requirements(self, feature_description: str) -> List[TestRequirement]:
        """
        Analyze feature description to detect test requirements.
        
        Args:
            feature_description: User's feature description or user story
            
        Returns:
            List of detected test requirements with recommendations
        """
        requirements = []
        description_lower = feature_description.lower()
        
        # Always recommend unit tests for any feature
        requirements.append(TestRequirement(
            test_type=TestType.UNIT,
            execution_mode=ExecutionMode.HEADLESS,
            confidence=1.0,
            reasoning="Unit tests are fundamental for all features",
            framework_hints=["pytest", "unittest", "Jest", "xUnit", "JUnit"],
            headed_recommended=False
        ))
        
        # Check for E2E browser automation needs
        if self._matches_patterns(description_lower, self.E2E_BROWSER_PATTERNS):
            requirements.append(TestRequirement(
                test_type=TestType.E2E_BROWSER,
                execution_mode=ExecutionMode.HEADED_REQUIRED,
                confidence=0.9,
                reasoning="User interactions detected - browser automation required",
                framework_hints=["Playwright", "Cypress", "Selenium", "Puppeteer"],
                headed_recommended=True
            ))
        
        # Check for visual regression testing
        if self._matches_patterns(description_lower, self.VISUAL_REGRESSION_PATTERNS):
            requirements.append(TestRequirement(
                test_type=TestType.VISUAL_REGRESSION,
                execution_mode=ExecutionMode.HEADED_REQUIRED,
                confidence=0.85,
                reasoning="Visual/styling requirements detected",
                framework_hints=["Percy", "Chromatic", "BackstopJS", "Playwright (screenshots)"],
                headed_recommended=True
            ))
        
        # Check for API integration tests
        if self._matches_patterns(description_lower, self.E2E_API_PATTERNS):
            requirements.append(TestRequirement(
                test_type=TestType.E2E_API,
                execution_mode=ExecutionMode.HEADLESS,
                confidence=0.8,
                reasoning="API/service integration detected",
                framework_hints=["requests", "httpx", "supertest", "RestAssured"],
                headed_recommended=False
            ))
        
        # Check for performance testing
        if self._matches_patterns(description_lower, self.PERFORMANCE_PATTERNS):
            requirements.append(TestRequirement(
                test_type=TestType.PERFORMANCE,
                execution_mode=ExecutionMode.HEADLESS_PREFERRED,
                confidence=0.75,
                reasoning="Performance requirements detected",
                framework_hints=["Locust", "K6", "JMeter", "Artillery"],
                headed_recommended=False
            ))
        
        # Check for security testing
        if self._matches_patterns(description_lower, self.SECURITY_PATTERNS):
            requirements.append(TestRequirement(
                test_type=TestType.SECURITY,
                execution_mode=ExecutionMode.HEADLESS,
                confidence=0.7,
                reasoning="Security requirements detected",
                framework_hints=["OWASP ZAP", "Bandit", "Safety", "Snyk"],
                headed_recommended=False
            ))
        
        # If no specific test types detected beyond unit, add integration
        if len(requirements) == 1:
            requirements.append(TestRequirement(
                test_type=TestType.INTEGRATION,
                execution_mode=ExecutionMode.HEADLESS,
                confidence=0.6,
                reasoning="Standard integration tests recommended",
                framework_hints=["pytest", "Jest", "TestNG"],
                headed_recommended=False
            ))
        
        return requirements
    
    def _matches_patterns(self, text: str, patterns: List[str]) -> bool:
        """
        Check if text matches any of the given regex patterns.
        
        Args:
            text: Text to check (should be lowercased)
            patterns: List of regex patterns
            
        Returns:
            True if any pattern matches
        """
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def generate_test_strategy_summary(
        self, 
        requirements: List[TestRequirement]
    ) -> Dict[str, Any]:
        """
        Generate human-readable test strategy summary.
        
        Args:
            requirements: List of detected test requirements
            
        Returns:
            Dictionary with formatted strategy information
        """
        summary = {
            "test_types": [],
            "automation_required": False,
            "headed_mode_recommended": False,
            "framework_suggestions": {},
            "execution_strategy": {}
        }
        
        for req in requirements:
            summary["test_types"].append({
                "type": req.test_type.value,
                "confidence": req.confidence,
                "reasoning": req.reasoning
            })
            
            if req.test_type in [TestType.E2E_BROWSER, TestType.VISUAL_REGRESSION]:
                summary["automation_required"] = True
            
            if req.headed_recommended:
                summary["headed_mode_recommended"] = True
            
            # Group frameworks by test type
            summary["framework_suggestions"][req.test_type.value] = req.framework_hints
            
            # Execution strategy
            summary["execution_strategy"][req.test_type.value] = {
                "development": "headed" if req.headed_recommended else "headless",
                "ci_cd": "headless" if req.execution_mode != ExecutionMode.HEADED_REQUIRED else "headed"
            }
        
        return summary
    
    def format_for_planning_template(
        self,
        requirements: List[TestRequirement],
        user_preferences: Optional[Dict[str, str]] = None,
        include_selenium_template: bool = False
    ) -> str:
        """
        Format test requirements for planning template.
        
        Args:
            requirements: Detected test requirements
            user_preferences: User's preferred frameworks from profile
            include_selenium_template: Whether to include generated Selenium template
            
        Returns:
            Formatted string for template insertion
        """
        lines = ["🧪 **Test Strategy:**", ""]
        
        # Group by test type
        for req in requirements:
            icon = self._get_test_type_icon(req.test_type)
            lines.append(f"{icon} **{req.test_type.value.replace('_', ' ').title()}**")
            lines.append(f"   - {req.reasoning}")
            
            # Add framework preference if available
            if user_preferences and req.test_type.value in user_preferences:
                preferred = user_preferences[req.test_type.value]
                lines.append(f"   - Framework: {preferred} (from your profile)")
            else:
                hints = ", ".join(req.framework_hints[:3])  # Show top 3
                lines.append(f"   - Suggested frameworks: {hints}")
            
            # Add execution mode guidance
            if req.headed_recommended:
                lines.append(f"   - Development: Headed mode (visual debugging)")
                lines.append(f"   - CI/CD: {'Headless' if req.execution_mode != ExecutionMode.HEADED_REQUIRED else 'Headed'}")
            else:
                lines.append(f"   - Execution: Headless (faster, no GUI)")
            
            lines.append("")
        
        # Add Selenium template if requested and E2E browser tests detected
        if include_selenium_template:
            has_e2e_browser = any(req.test_type == TestType.E2E_BROWSER for req in requirements)
            if has_e2e_browser:
                lines.append("---")
                lines.append("")
                lines.append("### 🌐 Selenium Test Template (pytest-selenium)")
                lines.append("")
                lines.append("```python")
                # Generate simple template for planning purposes
                template_patterns = {
                    'feature_name': 'UI Workflow',
                    'actions': ['click', 'fill', 'wait'],
                    'elements': ['button', 'input']
                }
                template_code = self.generate_selenium_test_template(template_patterns)
                lines.append(template_code)
                lines.append("```")
                lines.append("")
                lines.append("**Note:** Update selectors (By.ID, By.CSS_SELECTOR) to match your application.")
        
        return "\n".join(lines)
    
    def _get_test_type_icon(self, test_type: TestType) -> str:
        """Get emoji icon for test type."""
        icons = {
            TestType.UNIT: "🔬",
            TestType.INTEGRATION: "🔗",
            TestType.E2E_BROWSER: "🌐",
            TestType.E2E_API: "📡",
            TestType.VISUAL_REGRESSION: "👁️",
            TestType.PERFORMANCE: "⚡",
            TestType.SECURITY: "🔒"
        }
        return icons.get(test_type, "🧪")
    
    def detect_ui_patterns(self, description: str) -> Dict[str, Any]:
        """
        Detect UI patterns from feature description for Selenium template generation.
        
        Args:
            description: Feature description text
            
        Returns:
            Dictionary with detected patterns (actions, elements, feature_name)
        """
        description_lower = description.lower()
        
        # Extract actions from description
        actions = []
        action_keywords = {
            'click': ['click', 'clicks', 'clicking'],
            'fill': ['fill', 'fills', 'enter', 'enters', 'type', 'types'],
            'navigate': ['navigate', 'navigates', 'go to', 'goes to', 'visit'],
            'select': ['select', 'selects', 'choose', 'chooses'],
            'submit': ['submit', 'submits'],
            'wait': ['wait', 'waits for', 'see', 'sees'],
            'login': ['log in', 'logs in', 'login', 'logins', 'sign in']
        }
        
        for action_type, keywords in action_keywords.items():
            for keyword in keywords:
                if keyword in description_lower:
                    actions.append(action_type)
                    break
        
        # Extract common UI elements
        elements = []
        element_patterns = {
            'button': r'\b(button|btn)\b',
            'input': r'\b(input|field|textbox)\b',
            'email': r'\b(email)\b',
            'password': r'\b(password|pwd|credentials)\b',
            'form': r'\b(form|registration|signup)\b',
            'link': r'\b(link)\b',
            'dropdown': r'\b(dropdown|select menu)\b',
            'checkbox': r'\b(checkbox|check box)\b',
            'page': r'\b(page|settings)\b'
        }
        
        for element_name, pattern in element_patterns.items():
            if re.search(pattern, description_lower):
                elements.append(element_name)
        
        # Extract feature name (first few words or common patterns)
        feature_name = "UI Test"
        if 'login' in description_lower or 'log in' in description_lower:
            feature_name = "User Login"
        elif 'registration' in description_lower or 'register' in description_lower:
            feature_name = "User Registration"
        elif 'form' in description_lower:
            feature_name = "Form Submission"
        elif 'navigation' in description_lower or 'navigate' in description_lower:
            feature_name = "Navigation"
        
        return {
            'feature_name': feature_name,
            'actions': list(set(actions)),  # Remove duplicates
            'elements': list(set(elements))
        }
    
    def generate_selenium_test_template(self, ui_patterns: Dict[str, Any]) -> str:
        """
        Generate pytest-selenium test template for UI testing.
        
        Args:
            ui_patterns: Dictionary with feature_name, actions, elements, headless_mode (optional)
            
        Returns:
            Python code string with pytest-selenium test template
        """
        feature_name = ui_patterns.get('feature_name', 'UI Test')
        actions = ui_patterns.get('actions', [])
        elements = ui_patterns.get('elements', [])
        headless_mode = ui_patterns.get('headless_mode', True)  # Default to headless
        
        # Sanitize feature name for function name
        test_name = feature_name.lower().replace(' ', '_').replace('-', '_')
        
        template = f'''"""
Selenium UI Tests for {feature_name}

Generated by CORTEX Planning System 3.0
Framework: pytest-selenium
Mode: {'Headless' if headless_mode else 'Headed'}
"""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


@pytest.fixture
def driver():
    """Selenium WebDriver fixture with headless Chrome configuration."""
    options = Options()
    {'options.add_argument("--headless")' if headless_mode else '# Headed mode - GUI visible'}
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    
    yield driver
    
    driver.quit()


def test_{test_name}(driver):
    """
    Test {feature_name} functionality.
    
    Actions: {', '.join(actions) if actions else 'UI interactions'}
    Elements: {', '.join(elements) if elements else 'UI elements'}
    """
    # Navigate to application
    driver.get("http://localhost:8080")  # Update with your app URL
    
    try:
'''
        
        # Add action-specific code
        if 'click' in actions and 'button' in elements:
            template += '''        # Wait for and click button
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "button_id"))  # Update selector
        )
        button.click()
        
'''
        
        if 'fill' in actions and ('email' in elements or 'input' in elements):
            template += '''        # Fill input fields
        email_input = driver.find_element(By.ID, "email")  # Update selector
        email_input.send_keys("test@example.com")
        
'''
        
        if 'fill' in actions and 'password' in elements:
            template += '''        password_input = driver.find_element(By.ID, "password")  # Update selector
        password_input.send_keys("testpassword123")
        
'''
        
        if 'submit' in actions or ('click' in actions and 'form' in elements):
            template += '''        # Submit form
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
'''
        
        if 'wait' in actions:
            template += '''        # Wait for expected result
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "success_message"))  # Update selector
        )
        
'''
        
        # Add assertions
        template += '''        # Verify expected outcome
        assert driver.current_url  # Add specific URL check
        # assert "expected text" in driver.page_source
        
    except TimeoutException:
        pytest.fail("Element not found within timeout period")
    except Exception as e:
        pytest.fail(f"Test failed with error: {{e}}")
'''
        
        return template


def detect_test_requirements(feature_description: str) -> List[TestRequirement]:
    """
    Convenience function for test requirement detection.
    
    Args:
        feature_description: Feature description to analyze
        
    Returns:
        List of detected test requirements
    """
    intelligence = TestIntelligence()
    return intelligence.analyze_requirements(feature_description)
