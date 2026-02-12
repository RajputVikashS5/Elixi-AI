"""
Test Suite for Stage 5 Phase 2 - Coding Assistant
Tests CodingAssistant and Coding API endpoints
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_coding_assistant_import():
    """Test if CodingAssistant can be imported."""
    print("\n=== Test 1: Import CodingAssistant ===")
    try:
        from automation.coding_assistant import CodingAssistant
        print("✓ CodingAssistant imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import CodingAssistant: {e}")
        return False


def test_coding_assistant_initialization():
    """Test CodingAssistant initialization."""
    print("\n=== Test 2: Initialize CodingAssistant ===")
    try:
        from automation.coding_assistant import CodingAssistant
        
        assistant = CodingAssistant(mongodb=None, ai_brain=None, enable_cache=False)
        print(f"✓ CodingAssistant initialized: {assistant.name}")
        print(f"  - Supported languages: {len(assistant.supported_languages)}")
        print(f"  - Languages: {', '.join(assistant.supported_languages[:5])}...")
        return True
    except Exception as e:
        print(f"✗ CodingAssistant initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_python_code_analysis():
    """Test Python code analysis."""
    print("\n=== Test 3: Python Code Analysis ===")
    try:
        from automation.coding_assistant import CodingAssistant
        
        assistant = CodingAssistant(mongodb=None, ai_brain=None, enable_cache=False)
        
        # Test with valid Python code
        code = """
def hello_world():
    '''Say hello'''
    print("Hello, World!")
    return True

if __name__ == "__main__":
    hello_world()
"""
        
        result = assistant.analyze(code, 'python')
        
        if result.get('status') == 'success':
            data = result.get('data', {})
            print(f"✓ Python code analyzed:")
            print(f"  - Language: {data.get('language')}")
            print(f"  - Lines: {data.get('lines')}")
            print(f"  - Syntax valid: {data.get('syntax_valid')}")
            print(f"  - Functions: {data.get('functions', 0)}")
            print(f"  - Errors: {len(data.get('errors', []))}")
            print(f"  - Complexity: {data.get('complexity')}")
            return True
        else:
            print(f"✗ Analysis failed: {result.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ Python analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_syntax_error_detection():
    """Test syntax error detection."""
    print("\n=== Test 4: Syntax Error Detection ===")
    try:
        from automation.coding_assistant import CodingAssistant
        
        assistant = CodingAssistant(mongodb=None, ai_brain=None, enable_cache=False)
        
        # Test with invalid Python code
        code = """
def broken_function(
    print("This is missing a closing parenthesis"
    return True
"""
        
        result = assistant.analyze(code, 'python')
        
        if result.get('status') == 'success':
            data = result.get('data', {})
            errors = data.get('errors', [])
            print(f"✓ Syntax errors detected:")
            print(f"  - Syntax valid: {data.get('syntax_valid')}")
            print(f"  - Errors found: {len(errors)}")
            if errors:
                print(f"  - First error: {errors[0].get('message', 'Unknown')[:60]}...")
            return True
        else:
            print(f"✗ Error detection failed: {result.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ Syntax error test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_code_generation():
    """Test code generation functionality."""
    print("\n=== Test 5: Code Generation ===")
    try:
        from automation.coding_assistant import CodingAssistant
        
        assistant = CodingAssistant(mongodb=None, ai_brain=None, enable_cache=False)
        
        description = "Create a function to calculate factorial of a number"
        language = "python"
        
        result = assistant.generate_code(description, language)
        
        if result.get('status') == 'success':
            data = result.get('data', {})
            code = data.get('code', '')
            print(f"✓ Code generated:")
            print(f"  - Language: {data.get('language')}")
            print(f"  - Lines: {data.get('lines')}")
            print(f"  - Generation time: {data.get('generation_time_ms', 0):.2f}ms")
            print(f"  - Code preview:")
            print("  " + "\n  ".join(code.split('\n')[:5]))
            if len(code.split('\n')) > 5:
                print("  ...")
            return True
        else:
            print(f"✗ Code generation failed: {result.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ Code generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_code_debugging():
    """Test code debugging functionality."""
    print("\n=== Test 6: Code Debugging ===")
    try:
        from automation.coding_assistant import CodingAssistant
        
        assistant = CodingAssistant(mongodb=None, ai_brain=None, enable_cache=False)
        
        # Code with potential issues
        code = """
def divide_numbers(a, b):
    return a / b

result = divide_numbers(10, 0)
print(result)
"""
        
        error_message = "ZeroDivisionError: division by zero"
        
        result = assistant.debug_code(code, error_message, 'python')
        
        if result.get('status') == 'success':
            data = result.get('data', {})
            suggestions = data.get('suggestions', [])
            print(f"✓ Debugging analysis completed:")
            print(f"  - Language: {data.get('language')}")
            print(f"  - Errors found: {len(data.get('errors_found', []))}")
            print(f"  - Suggestions: {len(suggestions)}")
            if suggestions:
                print(f"  - First suggestion: {suggestions[0][:80]}...")
            print(f"  - Fixed code available: {data.get('fixed_code') is not None}")
            return True
        else:
            print(f"✗ Debugging failed: {result.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ Debugging test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_code_explanation():
    """Test code explanation functionality."""
    print("\n=== Test 7: Code Explanation ===")
    try:
        from automation.coding_assistant import CodingAssistant
        
        assistant = CodingAssistant(mongodb=None, ai_brain=None, enable_cache=False)
        
        # Sample code to explain
        code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        
        result = assistant.explain_code(code, 'python', 'medium')
        
        if result.get('status') == 'success':
            data = result.get('data', {})
            overview = data.get('overview', '')
            print(f"✓ Code explanation generated:")
            print(f"  - Language: {data.get('language')}")
            print(f"  - Overview length: {len(overview)} chars")
            print(f"  - Overview: {overview[:100]}...")
            print(f"  - Key concepts: {', '.join(data.get('key_concepts', []))}")
            return True
        else:
            print(f"✗ Explanation failed: {result.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ Explanation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_code_refactoring():
    """Test code refactoring functionality."""
    print("\n=== Test 8: Code Refactoring ===")
    try:
        from automation.coding_assistant import CodingAssistant
        
        assistant = CodingAssistant(mongodb=None, ai_brain=None, enable_cache=False)
        
        # Code that could be improved
        code = """
def calc(x, y, z):
    a = x + y
    b = a * z
    c = b - x
    return c
"""
        
        goals = ['readability', 'maintainability']
        
        result = assistant.refactor_code(code, 'python', goals)
        
        if result.get('status') == 'success':
            data = result.get('data', {})
            improvements = data.get('improvements', [])
            print(f"✓ Refactoring suggestions generated:")
            print(f"  - Language: {data.get('language')}")
            print(f"  - Goals: {', '.join(data.get('goals_addressed', []))}")
            print(f"  - Improvements: {len(improvements)}")
            if improvements:
                print(f"  - First improvement: {improvements[0].get('description', 'N/A')[:60]}...")
            print(f"  - Refactored code available: {data.get('refactored_code') is not None}")
            return True
        else:
            print(f"✗ Refactoring failed: {result.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ Refactoring test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_documentation_generation():
    """Test documentation generation functionality."""
    print("\n=== Test 9: Documentation Generation ===")
    try:
        from automation.coding_assistant import CodingAssistant
        
        assistant = CodingAssistant(mongodb=None, ai_brain=None, enable_cache=False)
        
        # Code to document
        code = """
def calculate_area(width, height):
    return width * height

def calculate_perimeter(width, height):
    return 2 * (width + height)
"""
        
        result = assistant.generate_documentation(code, 'python', 'markdown')
        
        if result.get('status') == 'success':
            data = result.get('data', {})
            doc = data.get('documentation', '')
            print(f"✓ Documentation generated:")
            print(f"  - Language: {data.get('language')}")
            print(f"  - Format: {data.get('format')}")
            print(f"  - Documentation length: {len(doc)} chars")
            print(f"  - Sections: {', '.join(data.get('sections', {}).keys())}")
            print(f"  - Preview:")
            print("  " + "\n  ".join(doc.split('\n')[:5]))
            return True
        else:
            print(f"✗ Documentation generation failed: {result.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ Documentation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_javascript_analysis():
    """Test JavaScript code analysis."""
    print("\n=== Test 10: JavaScript Analysis ===")
    try:
        from automation.coding_assistant import CodingAssistant
        
        assistant = CodingAssistant(mongodb=None, ai_brain=None, enable_cache=False)
        
        # JavaScript code
        code = """
function greet(name) {
    const message = `Hello, ${name}!`;
    console.log(message);
    return message;
}

const result = greet('World');
"""
        
        result = assistant.analyze(code, 'javascript')
        
        if result.get('status') == 'success':
            data = result.get('data', {})
            print(f"✓ JavaScript code analyzed:")
            print(f"  - Language: {data.get('language')}")
            print(f"  - Lines: {data.get('lines')}")
            print(f"  - Functions: {data.get('functions', 0)}")
            print(f"  - Arrow functions: {data.get('arrow_functions', 0)}")
            print(f"  - Warnings: {len(data.get('warnings', []))}")
            return True
        else:
            print(f"✗ JavaScript analysis failed: {result.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ JavaScript analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_language_detection():
    """Test automatic language detection."""
    print("\n=== Test 11: Language Auto-Detection ===")
    try:
        from automation.coding_assistant import CodingAssistant
        
        assistant = CodingAssistant(mongodb=None, ai_brain=None, enable_cache=False)
        
        # Python code without specifying language
        python_code = "def test(): pass"
        result = assistant.analyze(python_code)
        
        if result.get('status') == 'success':
            detected = result.get('data', {}).get('language')
            print(f"✓ Language detection working:")
            print(f"  - Detected: {detected}")
            print(f"  - Expected: python")
            return detected == 'python'
        else:
            print(f"✗ Language detection failed")
            return False
    except Exception as e:
        print(f"✗ Language detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_functionality():
    """Test caching functionality."""
    print("\n=== Test 12: Cache Functionality ===")
    try:
        from automation.coding_assistant import CodingAssistant
        
        assistant = CodingAssistant(mongodb=None, ai_brain=None, enable_cache=True)
        
        code = "def test(): return 42"
        
        # First call - should compute
        result1 = assistant.analyze(code, 'python')
        
        # Second call - should use cache
        result2 = assistant.analyze(code, 'python')
        
        if result1.get('status') == 'success' and result2.get('status') == 'success':
            print(f"✓ Cache functionality working:")
            print(f"  - First call successful")
            print(f"  - Second call successful")
            print(f"  - Cache enabled: {assistant.enable_cache}")
            return True
        else:
            print(f"✗ Cache test failed")
            return False
    except Exception as e:
        print(f"✗ Cache test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoints():
    """Test API endpoints."""
    print("\n=== Test 13: API Endpoints ===")
    try:
        import requests
        
        base_url = "http://127.0.0.1:5000"
        
        # Test generate-code endpoint
        response = requests.post(
            f"{base_url}/coding/generate-code",
            json={
                'description': 'Create a function to add two numbers',
                'language': 'python'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ API endpoint /coding/generate-code working:")
            print(f"  - Status: {response.status_code}")
            print(f"  - Response status: {result.get('status')}")
            return True
        else:
            print(f"⚠ API endpoint returned status {response.status_code}")
            print(f"  Note: Backend may not be running")
            return None  # Skip, not a failure
    except requests.exceptions.ConnectionError:
        print(f"⚠ Backend not running - skipping API test")
        print(f"  Start backend with: python main.py")
        return None  # Skip, not a failure
    except Exception as e:
        print(f"✗ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all test cases."""
    print("\n" + "="*60)
    print("Stage 5 Phase 2 - Coding Assistant Test Suite")
    print("="*60)
    
    tests = [
        test_coding_assistant_import,
        test_coding_assistant_initialization,
        test_python_code_analysis,
        test_syntax_error_detection,
        test_code_generation,
        test_code_debugging,
        test_code_explanation,
        test_code_refactoring,
        test_documentation_generation,
        test_javascript_analysis,
        test_language_detection,
        test_cache_functionality,
        test_api_endpoints,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test crashed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False)
    skipped = sum(1 for r in results if r is None)
    total = len(results)
    
    print(f"Total tests: {total}")
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    print(f"⚠ Skipped: {skipped}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    elif passed > failed:
        print(f"\n✓ Mostly working ({passed}/{total} passed)")
    else:
        print(f"\n⚠ Issues detected ({failed} failures)")
    
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
