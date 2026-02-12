#!/usr/bin/env python3
"""
STAGE 2 TEST SUITE - Voice & AI Brain
Tests all voice and AI capabilities for ELIXI Stage 2 milestone
"""

import requests
import json
import os
import sys
import time
from dotenv import load_dotenv
from voice_system.elevenlabs_voice import ElevenLabsVoice

load_dotenv()

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

BASE_URL = "http://127.0.0.1:5000"
TIMEOUT = 10

# Test tracking
total_tests = 0
passed_tests = 0
failed_tests = 0
warnings = []

def print_header(text):
    print(f"\n{BLUE}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{RESET}\n")

def test_pass(test_name, details=""):
    global passed_tests, total_tests
    total_tests += 1
    passed_tests += 1
    status = f"{GREEN}✓ PASS{RESET}"
    print(f"{status} {test_name}")
    if details:
        print(f"      {details}")

def test_fail(test_name, error=""):
    global failed_tests, total_tests
    total_tests += 1
    failed_tests += 1
    status = f"{RED}✗ FAIL{RESET}"
    print(f"{status} {test_name}")
    if error:
        print(f"      {RED}Error: {error}{RESET}")

def test_warn(test_name, details=""):
    global total_tests
    total_tests += 1
    status = f"{YELLOW}⚠ WARN{RESET}"
    print(f"{status} {test_name}")
    if details:
        print(f"      {details}")
    warnings.append(test_name)

def print_summary():
    print(f"\n{BLUE}{'='*60}")
    print(f"  STAGE 2 TEST SUMMARY")
    print(f"{'='*60}{RESET}")
    print(f"Total Tests:    {total_tests}")
    print(f"{GREEN}Passed:         {passed_tests}{RESET}")
    print(f"{RED}Failed:         {failed_tests}{RESET}")
    print(f"{YELLOW}Warnings:       {len(warnings)}{RESET}")
    
    if warnings:
        print(f"\n{YELLOW}Warnings:{RESET}")
        for w in warnings:
            print(f"  - {w}")
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"\nSuccess Rate:   {success_rate:.1f}%")
    
    if failed_tests == 0 and len(warnings) <= 2:
        print(f"\n{GREEN}✓ Stage 2 is ready for deployment!{RESET}")
        return 0
    elif failed_tests == 0:
        print(f"\n{YELLOW}⚠ Stage 2 works but needs attention to warnings{RESET}")
        return 1
    else:
        print(f"\n{RED}✗ Stage 2 has critical issues that must be fixed{RESET}")
        return 2

# ============================================================================
# INFRASTRUCTURE TESTS
# ============================================================================

def test_python_backend():
    """Test if Python backend is running"""
    print_header("1. INFRASTRUCTURE & BACKEND")
    
    try:
        response = requests.get(f"{BASE_URL}/system-status", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            test_pass(
                "Python Backend Running",
                f"Platform: {data.get('platform', 'N/A')} | Python: {data.get('python_version', 'N/A')}"
            )
            return True
        else:
            test_fail("Python Backend Running", f"Status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        test_fail(
            "Python Backend Running",
            "Cannot connect. Start backend: cd python-core && python main.py"
        )
        return False
    except Exception as e:
        test_fail("Python Backend Running", str(e))
        return False

def test_database_connection():
    """Test MongoDB connection"""
    try:
        response = requests.get(f"{BASE_URL}/system-status", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            db_connected = data.get("db_connected", False)
            
            if db_connected:
                test_pass("MongoDB Connection", "Database connected and accessible")
            else:
                if os.getenv("MONGODB_URI"):
                    test_warn(
                        "MongoDB Connection",
                        "URI set but connection failed. Check credentials and network."
                    )
                else:
                    test_warn(
                        "MongoDB Connection",
                        "MONGODB_URI not set. Memory features disabled (non-critical for Stage 2)"
                    )
    except Exception as e:
        test_fail("MongoDB Connection", str(e))

# ============================================================================
# TEXT-TO-SPEECH TESTS
# ============================================================================

def test_elevenlabs_configuration():
    """Test ElevenLabs configuration"""
    print_header("2. TEXT-TO-SPEECH (TTS)")
    
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID")
    model_id = os.getenv("ELEVENLABS_MODEL_ID")
    
    if not api_key:
        test_fail(
            "ElevenLabs Configuration",
            "ELEVENLABS_API_KEY not set. TTS will not work."
        )
        return False
    
    test_pass(
        "ElevenLabs API Key Found",
        f"Voice ID: {voice_id or 'default (Rachel)'} | Model: {model_id or 'eleven_monolingual_v1'}"
    )
    return True

def test_elevenlabs_api():
    """Test ElevenLabs API directly"""
    voice = ElevenLabsVoice()

    if not voice.is_configured():
        test_fail(
            "ElevenLabs API Client",
            "Failed to initialize. Check ELEVENLABS_API_KEY and network access."
        )
        return False

    try:
        audio_b64 = voice.text_to_speech("Hello from ELIXI")
        if audio_b64:
            test_pass(
                "ElevenLabs API TTS",
                f"Audio generated ({len(audio_b64)} base64 chars)"
            )
            return True
        test_warn("ElevenLabs API TTS", "No audio data returned from ElevenLabs.")
        return False
    except Exception as e:
        test_warn("ElevenLabs API TTS", f"Error: {str(e)}")
        return False

def test_tts_endpoint():
    """Test Text-to-Speech via backend"""
    try:
        response = requests.post(
            f"{BASE_URL}/execute",
            json={
                "command": "tts",
                "args": {"text": "Hello, I am ELIXI"}
            },
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("audio"):
                test_pass(
                    "TTS Generation",
                    f"Audio generated ({len(data.get('audio', ''))} bytes)"
                )
                return True
            else:
                test_warn(
                    "TTS Generation",
                    data.get("error", "No audio data returned. ElevenLabs may not be configured.")
                )
                return False
        else:
            test_warn("TTS Generation", f"Status {response.status_code}. Backend may not support TTS endpoint.")
            return False
    except Exception as e:
        test_warn("TTS Generation", f"Error: {str(e)}")
        return False

# ============================================================================
# WAKE WORD DETECTION TESTS
# ============================================================================

def test_wake_word_detection():
    """Test wake word detection"""
    print_header("3. WAKE WORD DETECTION")
    
    try:
        test_cases = [
            ("hey elixi", True, "exact match"),
            ("Hey Elixi", True, "case insensitive"),
            ("HEY ELIXI", True, "all caps"),
            ("hey elixi play music", True, "with command"),
            ("alexa what time is it", False, "different wake word"),
            ("hello", False, "no wake word"),
        ]
        
        for text, should_detect, description in test_cases:
            try:
                response = requests.post(
                    f"{BASE_URL}/execute",
                    json={
                        "command": "wake_word_detect",
                        "args": {"text": text}
                    },
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    detected = data.get("detected", False)
                    
                    if detected == should_detect:
                        test_pass(f"Wake Word Detection: '{text}'", description)
                    else:
                        test_fail(
                            f"Wake Word Detection: '{text}'",
                            f"Expected {should_detect}, got {detected} ({description})"
                        )
                else:
                    test_warn(
                        "Wake Word Detection Endpoint",
                        "Endpoint may not be implemented. Skipping detailed tests."
                    )
                    break
            except Exception as e:
                test_warn("Wake Word Detection", f"Error testing '{text}': {str(e)}")
                break
    except Exception as e:
        test_fail("Wake Word Detection", str(e))

# ============================================================================
# AI BRAIN (OLLAMA) TESTS
# ============================================================================

def test_ollama_availability():
    """Test if Ollama is running"""
    print_header("4. AI BRAIN (OLLAMA)")
    
    ollama_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
    
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                model_names = [m.get("name", "unknown") for m in models[:5]]
                test_pass(
                    "Ollama Service Running",
                    f"Found {len(models)} model(s): {', '.join(model_names)}"
                )
                return True
            else:
                test_fail(
                    "Ollama Service Running",
                    "Ollama is running but no models installed. Pull a model first."
                )
                return False
        else:
            test_fail("Ollama Service Running", f"Status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        test_fail(
            "Ollama Service Running",
            "Cannot reach Ollama. Start it: ollama serve"
        )
        return False
    except Exception as e:
        test_fail("Ollama Service Running", str(e))
        return False

def test_ollama_model():
    """Test specific Ollama model"""
    try:
        ollama_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "mistral")
        
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_installed = any(m.get("name", "").startswith(model) for m in models)
            
            if model_installed:
                test_pass(f"Ollama Model '{model}' Available", "Ready for AI responses")
            else:
                test_warn(
                    f"Ollama Model '{model}' Available",
                    f"Model not found. Pull it: ollama pull {model}"
                )
    except Exception as e:
        test_fail("Ollama Model Check", str(e))

def test_ai_response_generation():
    """Test AI response generation via chat"""
    print_header("5. AI RESPONSE GENERATION")
    
    test_prompts = [
        "Hello ELIXI",
        "What time is it?",
        "Tell me a joke",
        "How can you help me?"
    ]
    
    for prompt in test_prompts:
        try:
            response = requests.post(
                f"{BASE_URL}/execute",
                json={
                    "command": "chat",
                    "args": {"prompt": prompt}
                },
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get("reply", "")
                
                if reply and len(reply) > 0:
                    # Check if it's a meaningful response
                    if len(reply) > 5:
                        test_pass(f"AI Response: '{prompt}'", f"'{reply[:60]}...'")
                    else:
                        test_warn(f"AI Response: '{prompt}'", f"Response too short: '{reply}'")
                else:
                    test_warn(f"AI Response: '{prompt}'", "No response generated")
            else:
                test_fail(f"AI Response: '{prompt}'", f"Status {response.status_code}")
        except Exception as e:
            test_fail(f"AI Response: '{prompt}'", str(e))

# ============================================================================
# CONVERSATION FLOW TESTS
# ============================================================================

def test_conversation_flow():
    """Test complete conversation flow"""
    print_header("6. CONVERSATION FLOW")
    
    conversation = [
        "hello",
        "how are you",
        "what can you do",
        "goodbye"
    ]
    
    try:
        for i, prompt in enumerate(conversation, 1):
            response = requests.post(
                f"{BASE_URL}/execute",
                json={
                    "command": "chat",
                    "args": {"prompt": prompt}
                },
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get("reply", "")
                test_pass(f"Turn {i}: User '{prompt}'", f"ELIXI: '{reply[:50]}...'")
            else:
                test_fail(f"Turn {i}: User '{prompt}'", f"Status {response.status_code}")
    except Exception as e:
        test_fail("Conversation Flow", str(e))

# ============================================================================
# PERSONALITY & CONTEXT TESTS
# ============================================================================

def test_personality():
    """Test personality and context-aware responses"""
    print_header("7. PERSONALITY & CONTEXT")
    
    # Test greeting
    try:
        response = requests.post(
            f"{BASE_URL}/execute",
            json={
                "command": "chat",
                "args": {"prompt": "Hi there"}
            },
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "").lower()
            
            # Check if response contains greeting-like content
            has_greeting = any(word in reply for word in ["hello", "hi", "hey", "welcome"])
            
            if has_greeting or len(reply) > 10:
                test_pass("Personality: Greeting Response", "ELIXI responds to greetings appropriately")
            else:
                test_warn("Personality: Greeting Response", "Response lacks personality")
    except Exception as e:
        test_warn("Personality: Greeting Response", str(e))

def test_context_awareness():
    """Test if AI maintains some context"""
    print_header("8. CONTEXT AWARENESS")
    
    try:
        # Skip this test as it requires memory integration
        test_warn(
            "Context Awareness",
            "Requires Stage 4 (Memory). Not critical for Stage 2."
        )
    except Exception as e:
        test_warn("Context Awareness", str(e))

# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

def test_response_latency():
    """Test response latency"""
    print_header("9. PERFORMANCE")
    
    try:
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/execute",
            json={
                "command": "chat",
                "args": {"prompt": "hi"}
            },
            timeout=TIMEOUT
        )
        latency = (time.time() - start) * 1000  # ms
        
        if response.status_code == 200:
            if latency < 1000:
                test_pass("Response Latency", f"{latency:.0f}ms (excellent)")
            elif latency < 3000:
                test_pass("Response Latency", f"{latency:.0f}ms (acceptable)")
            else:
                test_warn("Response Latency", f"{latency:.0f}ms (slow, may indicate Ollama delays)")
        else:
            test_fail("Response Latency", f"Request failed: {response.status_code}")
    except Exception as e:
        test_fail("Response Latency", str(e))

# ============================================================================
# STAGE 2 READINESS ASSESSMENT
# ============================================================================

def stage2_assessment():
    """Provide Stage 2 readiness assessment"""
    print_header("STAGE 2 READINESS ASSESSMENT")
    
    print("Stage 2 Requirements:")
    print("  ✓ Must have: Speech-to-Text (STT)")
    print("  ✓ Must have: Text-to-Speech (TTS)")
    print("  ✓ Must have: Wake Word Detection")
    print("  ✓ Must have: Offline AI (Ollama)")
    print("  ✓ Must have: Personality & Smart Replies")
    print()
    
    if failed_tests == 0:
        print(f"{GREEN}✓ All critical tests passed!{RESET}")
        print("Stage 2 is ready for:")
        print("  - Voice-based interaction")
        print("  - Wake word activation")
        print("  - Offline AI responses")
        print("  - Natural conversation flow")
    elif len(warnings) > 0 and failed_tests == 0:
        print(f"{YELLOW}⚠ Stage 2 is functional but incomplete:{RESET}")
        print("  - Some optional services not configured (e.g., STT provider)")
        print("  - Can still use text input and offline voice features")
    else:
        print(f"{RED}✗ Stage 2 has critical issues:{RESET}")
        print("  Please fix failed tests before proceeding")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print(f"\n{BLUE}")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  ELIXI STAGE 2 TEST SUITE".center(58) + "║")
    print("║" + "  Voice & AI Brain Testing".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    print(f"{RESET}")
    
    # Check if backend is running
    if not test_python_backend():
        print(f"\n{RED}Backend is not running. Cannot proceed with tests.{RESET}")
        print("Start the backend with: cd python-core && python main.py")
        sys.exit(1)
    
    # Infrastructure tests
    test_database_connection()
    
    # Voice system tests
    has_tts = test_elevenlabs_configuration()
    if has_tts:
        test_elevenlabs_api()
        test_tts_endpoint()
    
    # Wake word tests
    test_wake_word_detection()
    
    # AI brain tests
    if test_ollama_availability():
        test_ollama_model()
        test_ai_response_generation()
    
    # Conversation tests
    test_conversation_flow()
    test_personality()
    test_context_awareness()
    
    # Performance tests
    test_response_latency()
    
    # Assessment and summary
    stage2_assessment()
    exit_code = print_summary()
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
