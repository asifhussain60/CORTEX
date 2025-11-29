"""
Visual Test Script for CORTEX MkDocs Site
Compares the mockup design with the actual site using screenshots
"""
import os
import sys
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import anthropic

def capture_screenshot(url, output_path, width=1920, height=1080):
    """Capture screenshot of a webpage"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument(f'--window-size={width},{height}')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(url)
        time.sleep(2)  # Wait for page to fully load
        driver.save_screenshot(output_path)
        print(f"✅ Screenshot saved to {output_path}")
        return True
    except Exception as e:
        print(f"❌ Error capturing screenshot: {e}")
        return False
    finally:
        driver.quit()

def compare_designs_with_vision_api(mockup_path, actual_path):
    """Use Claude Vision API to compare mockup with actual site"""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    # Read images
    with open(mockup_path, 'rb') as f:
        mockup_data = f.read()
    
    with open(actual_path, 'rb') as f:
        actual_data = f.read()
    
    # Create comparison prompt
    prompt = """
    Compare these two designs for the CORTEX documentation site:
    
    Image 1: The target mockup design (Tales-inspired)
    Image 2: The actual deployed site
    
    Analyze and report:
    1. **Visual Match**: How closely does the actual site match the mockup? (0-100%)
    2. **Color Scheme**: Are the colors matching? (dark background, purple/indigo gradients)
    3. **Typography**: Font styles and sizes matching?
    4. **Layout**: Header, navigation, content structure matching?
    5. **Components**: Cards, badges, buttons styling matching?
    6. **Issues Found**: List any visual differences or problems
    7. **Recommendations**: What needs to be fixed?
    
    Be specific and detailed in your analysis.
    """
    
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": mockup_data.hex()
                            }
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": actual_data.hex()
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        
        return message.content[0].text
    except Exception as e:
        print(f"❌ Error calling Vision API: {e}")
        return None

def main():
    """Main test execution"""
    print("🧪 CORTEX Visual Test - Tales Design Verification")
    print("=" * 60)
    
    # Paths
    project_root = Path(__file__).parent
    screenshots_dir = project_root / "workspace" / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    mockup_html = project_root / "docs" / "mockup-tales-styling.html"
    actual_url = "http://127.0.0.1:8000/"
    
    mockup_screenshot = screenshots_dir / "mockup-design.png"
    actual_screenshot = screenshots_dir / "actual-site.png"
    
    # Step 1: Capture mockup screenshot
    print("\n📸 Step 1: Capturing mockup screenshot...")
    if not capture_screenshot(f"file:///{mockup_html}", str(mockup_screenshot)):
        print("❌ Failed to capture mockup screenshot")
        return 1
    
    # Step 2: Capture actual site screenshot
    print("\n📸 Step 2: Capturing actual site screenshot...")
    if not capture_screenshot(actual_url, str(actual_screenshot)):
        print("❌ Failed to capture actual site screenshot")
        return 1
    
    # Step 3: Compare with Vision API
    print("\n🔍 Step 3: Comparing designs with Claude Vision API...")
    comparison_result = compare_designs_with_vision_api(
        str(mockup_screenshot),
        str(actual_screenshot)
    )
    
    if comparison_result:
        print("\n" + "=" * 60)
        print("📊 VISION API ANALYSIS RESULTS")
        print("=" * 60)
        print(comparison_result)
        print("=" * 60)
        
        # Save results
        results_file = screenshots_dir / "comparison-results.txt"
        with open(results_file, 'w') as f:
            f.write(comparison_result)
        print(f"\n✅ Results saved to {results_file}")
        return 0
    else:
        print("❌ Failed to get Vision API comparison")
        return 1

if __name__ == "__main__":
    sys.exit(main())
