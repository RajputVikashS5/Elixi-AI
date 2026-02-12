import json
import os
import platform
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import base64

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv

from voice_system.wake_word import WakeWordDetector
from voice_system.google_cloud import GoogleCloudVoice
from voice_system.elevenlabs_voice import ElevenLabsVoice
from ai_brain.ollama import OllamaAIBrain
from system_control.applications import ApplicationManager
from system_control.hardware import HardwareController
from system_control.power import PowerManager
from system_control.screenshot import ScreenshotManager
from system_control.monitoring import SystemMonitor

# Stage 4: Automation & Memory
from automation.custom_commands import CustomCommandManager
from automation.workflows import WorkflowManager
from automation.habit_learning import HabitLearningEngine
from automation.suggestion_engine import SuggestionEngine
from memory.memory_manager import MemoryManager
from memory.preference_manager import PreferenceManager

# Stage 4 Phase 4: Database Optimization & Data Retention
from database_optimization import DatabaseOptimizer
from data_retention import DataRetentionManager

# Stage 5: Advanced AI Features (Foundation)
try:
    from stage5_utils import CacheManager, Logger, ConfigLoader, ResourceMonitor, APIResponseFormatter
    from stage5_base import BaseAnalyzer, BaseDataProcessor, PerformanceMonitor, AnalysisResult
    STAGE5_AVAILABLE = True
except ImportError:
    STAGE5_AVAILABLE = False
    print("[Warning] Stage 5 modules not yet available")

load_dotenv()

STARTED_AT = time.time()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MONGODB_URI = os.environ.get("MONGODB_URI")
MONGODB_DB = os.environ.get("MONGODB_DB", "ELIXIDB")
MONGODB_COLLECTION_MEMORIES = os.environ.get("MONGODB_COLLECTION_MEMORIES", "memories")
MONGODB_COLLECTION_EVENTS = os.environ.get("MONGODB_COLLECTION_EVENTS", "events")

_mongo_client = None
_wake_word_detector = None
_google_voice = None
_elevenlabs_voice = None
_ollama_brain = None
_app_manager = None
_hardware_controller = None
_power_manager = None
_screenshot_manager = None
_system_monitor = None

# Stage 4: Automation & Memory
_custom_command_manager = None
_workflow_manager = None
_habit_learning_engine = None
_suggestion_engine = None
_memory_manager = None
_preference_manager = None

# Stage 4 Phase 4: Database Optimization
_database_optimizer = None
_data_retention_manager = None

# Stage 5: Advanced AI Features (Lazy-loaded)
_stage5_cache_manager = None
_screen_analyzer = None
_coding_assistant = None
_news_weather_service = None
_model_manager = None
_performance_monitor = None


def get_db():
    global _mongo_client
    if not MONGODB_URI:
        return None
    if _mongo_client is None:
        _mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
    return _mongo_client[MONGODB_DB]


def get_collection(name):
    db = get_db()
    if db is None:
        return None
    return db[name]


def get_wake_word_detector():
    global _wake_word_detector
    if _wake_word_detector is None:
        _wake_word_detector = WakeWordDetector()
    return _wake_word_detector


def get_google_voice():
    global _google_voice
    if _google_voice is None:
        _google_voice = GoogleCloudVoice()
    return _google_voice


def get_elevenlabs_voice():
    global _elevenlabs_voice
    if _elevenlabs_voice is None:
        _elevenlabs_voice = ElevenLabsVoice()
    return _elevenlabs_voice




def get_app_manager():
    global _app_manager
    if _app_manager is None:
        _app_manager = ApplicationManager()
    return _app_manager


def get_hardware_controller():
    global _hardware_controller
    if _hardware_controller is None:
        _hardware_controller = HardwareController()
    return _hardware_controller


def get_power_manager():
    global _power_manager
    if _power_manager is None:
        _power_manager = PowerManager()
    return _power_manager


def get_screenshot_manager():
    global _screenshot_manager
    if _screenshot_manager is None:
        _screenshot_manager = ScreenshotManager()
    return _screenshot_manager


def get_system_monitor():
    global _system_monitor
    if _system_monitor is None:
        _system_monitor = SystemMonitor()
    return _system_monitor
def get_ollama_brain():
    global _ollama_brain
    if _ollama_brain is None:
        _ollama_brain = OllamaAIBrain()
    return _ollama_brain


# Stage 4: Automation & Memory Managers
def get_custom_command_manager():
    global _custom_command_manager
    if _custom_command_manager is None:
        _custom_command_manager = CustomCommandManager(get_db())
    return _custom_command_manager


def get_workflow_manager():
    global _workflow_manager
    if _workflow_manager is None:
        _workflow_manager = WorkflowManager(get_db())
    return _workflow_manager


def get_habit_learning_engine():
    global _habit_learning_engine
    if _habit_learning_engine is None:
        _habit_learning_engine = HabitLearningEngine(get_db())
    return _habit_learning_engine


def get_suggestion_engine():
    global _suggestion_engine
    if _suggestion_engine is None:
        _suggestion_engine = SuggestionEngine(get_db())
    return _suggestion_engine


# Phase 2: Memory Managers
def get_memory_manager():
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager(get_db())
    return _memory_manager


def get_preference_manager():
    global _preference_manager
    if _preference_manager is None:
        _preference_manager = PreferenceManager(get_db())
    return _preference_manager


# Stage 4 Phase 4: Database & Data Management
def get_database_optimizer():
    global _database_optimizer
    if _database_optimizer is None:
        _database_optimizer = DatabaseOptimizer(get_db())
    return _database_optimizer


def get_data_retention_manager():
    global _data_retention_manager
    if _data_retention_manager is None:
        _data_retention_manager = DataRetentionManager(get_db())
    return _data_retention_manager


# ============ STAGE 5: Advanced AI Features ============

def get_stage5_cache_manager():
    """Get Stage 5 cache manager (CacheManager)."""
    global _stage5_cache_manager
    if not STAGE5_AVAILABLE:
        return None
    if _stage5_cache_manager is None:
        _stage5_cache_manager = CacheManager(get_db())
    return _stage5_cache_manager


def get_screen_analyzer():
    """Get Stage 5 screen analyzer (ScreenAnalyzer)."""
    global _screen_analyzer
    if not STAGE5_AVAILABLE:
        return None
    if _screen_analyzer is None:
        try:
            from vision.screen_analyzer import get_screen_analyzer as get_analyzer
            _screen_analyzer = get_analyzer(
                mongodb=get_db(),
                ai_brain=get_ollama_brain()
            )
        except ImportError as e:
            print(f"[Warning] ScreenAnalyzer not available: {e}")
            return None
    return _screen_analyzer


def get_coding_assistant():
    """Get Stage 5 coding assistant (CodingAssistant)."""
    global _coding_assistant
    if not STAGE5_AVAILABLE:
        return None
    if _coding_assistant is None:
        try:
            from automation.coding_assistant import CodingAssistant
            _coding_assistant = CodingAssistant(
                mongodb=get_db(),
                ai_brain=get_ollama_brain(),
                enable_cache=True
            )
        except ImportError as e:
            print(f"[Warning] CodingAssistant not available: {e}")
            return None
    return _coding_assistant


def get_news_weather_service():
    """Get Stage 5 news & weather service (NewsWeatherManager)."""
    global _news_weather_service
    if not STAGE5_AVAILABLE:
        return None
    if _news_weather_service is None:
        try:
            from news_weather import NewsWeatherManager
            _news_weather_service = NewsWeatherManager(
                mongodb=get_db(),
                enable_cache=True
            )
        except ImportError as e:
            print(f"[Warning] NewsWeatherManager not available: {e}")
            return None
    return _news_weather_service


def get_model_manager():
    """Get Stage 5 model manager (ModelManager)."""
    # Will be implemented in Phase 4
    # Placeholder for future implementation
    return None


def get_performance_monitor():
    """Get Stage 5 performance monitor."""
    global _performance_monitor
    if not STAGE5_AVAILABLE:
        return None
    if _performance_monitor is None:
        from stage5_base import get_performance_monitor as get_monitor
        _performance_monitor = get_monitor()
    return _performance_monitor


def generate_reply(prompt):
    text = prompt.lower()
    words = text.split()

    if ("hello" in text or "hi" in text) and len(words) <= 4:
        return "Hello. ELIXI is online and ready."
    if "time" in text and len(words) <= 4:
        return time.strftime("Local time is %H:%M.")
    if "status" in text and len(words) <= 4:
        return "All systems nominal."
    if "help" in text and len(words) <= 5:
        return "Try asking about system status or tell me a task to automate."

    # Try Ollama if available, otherwise fall back to a default reply.
    ollama = get_ollama_brain()
    if ollama.is_available():
        reply = ollama.generate_reply(prompt)
        if reply:
            return reply

    return "Understood. I will route that to the automation brain once it is connected."



class ElixiHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def do_GET(self):
        if self.path == "/system-status":
            uptime = int(time.time() - STARTED_AT)
            db_connected = False
            if MONGODB_URI:
                try:
                    client = get_db().client
                    client.admin.command("ping")
                    db_connected = True
                except PyMongoError:
                    db_connected = False
            self._send_json(
                {
                    "success": True,
                    "platform": platform.platform(),
                    "python_version": platform.python_version(),
                    "uptime_sec": uptime,
                    "db_connected": db_connected,
                }
            )
            return

        if self.path == "/memory/load":
            collection = get_collection(MONGODB_COLLECTION_MEMORIES)
            if collection is None:
                self._send_json({"success": False, "error": "MongoDB not configured"}, status=500)
                return
            try:
                items = list(collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(100))
                self._send_json({"success": True, "items": items})
                return
            except PyMongoError as error:
                self._send_json({"success": False, "error": str(error)}, status=500)
                return

        # ==================== STAGE 5: VISION ENDPOINTS (GET) ====================
        if self.path == "/vision/identify-window":
            if not STAGE5_AVAILABLE:
                self._send_json({"success": False, "error": "Stage 5 not available"}, status=503)
                return
            
            analyzer = get_screen_analyzer()
            if not analyzer:
                self._send_json({"success": False, "error": "Screen analyzer not available"}, status=503)
                return
            
            result = analyzer.identify_window()
            self._send_json(result)
            return
        
        if self.path == "/vision/screen-cache":
            if not STAGE5_AVAILABLE:
                self._send_json({"success": False, "error": "Stage 5 not available"}, status=503)
                return
            
            analyzer = get_screen_analyzer()
            if not analyzer:
                self._send_json({"success": False, "error": "Screen analyzer not available"}, status=503)
                return
            
            result = analyzer.get_screen_cache()
            self._send_json(result)
            return
        
        # ==================== STAGE 5: NEWS & WEATHER ENDPOINTS (GET) ====================
        if self.path == "/info/cached-news":
            if not STAGE5_AVAILABLE:
                self._send_json({"success": False, "error": "Stage 5 not available"}, status=503)
                return
            
            news_service = get_news_weather_service()
            if not news_service:
                self._send_json({"success": False, "error": "News & Weather service not available"}, status=503)
                return
            
            result = news_service.get_cached_news()
            self._send_json(result)
            return

        self._send_json({"success": False, "error": "Not found"}, status=404)

    def do_POST(self):
        if self.path == "/execute":
            payload = self._read_json()
            command = payload.get("command")
            args = payload.get("args") or {}

            if command == "chat":
                prompt = args.get("prompt", "")
                reply = generate_reply(prompt)
                events = get_collection(MONGODB_COLLECTION_EVENTS)
                if events is not None:
                    try:
                        events.insert_one(
                            {
                                "timestamp": time.time(),
                                "type": "chat",
                                "prompt": prompt,
                                "reply": reply,
                            }
                        )
                    except PyMongoError:
                        pass
                self._send_json({"success": True, "reply": reply})
                return

            if command == "wake_word_detect":
                text = args.get("text", "")
                detector = get_wake_word_detector()
                detected = detector.detect(text)
                self._send_json({"success": True, "detected": detected})
                return

            if command == "tts":
                text = args.get("text", "")
                elevenlabs_voice = get_elevenlabs_voice()
                try:
                    audio = elevenlabs_voice.generate_speech(text)
                    if audio:
                        self._send_json({"success": True, "audio": audio})
                    else:
                        self._send_json({"success": False, "error": "Failed to generate audio"}, status=500)
                except Exception as e:
                    self._send_json({"success": False, "error": str(e)}, status=500)
                return

            self._send_json(
                {
                    "success": True,
                    "reply": "Command queued. Automation engine not yet wired.",
                    "command": command,
                }
            )
            return

        if self.path == "/memory/save":
            payload = self._read_json()
            collection = get_collection(MONGODB_COLLECTION_MEMORIES)
            if collection is None:
                self._send_json({"success": False, "error": "MongoDB not configured"}, status=500)
                return
            try:
                collection.insert_one({"timestamp": time.time(), "data": payload})
                self._send_json({"success": True})
                return
            except PyMongoError as error:
                self._send_json({"success": False, "error": str(error)}, status=500)
                return

        if self.path == "/voice/transcribe":
            payload = self._read_json()
            audio_base64 = payload.get("audio", "")
            
            if not audio_base64:
                self._send_json({"success": False, "error": "No audio data"}, status=400)
                return
            
            try:
                audio_bytes = base64.b64decode(audio_base64)
                google_voice = get_google_voice()
                
                if not google_voice.is_configured():
                    self._send_json({"success": False, "error": "Google Cloud not configured"}, status=503)
                    return
                
                transcript = google_voice.speech_to_text(audio_bytes)
                if transcript:
                    self._send_json({"success": True, "transcript": transcript})
                else:
                    self._send_json({"success": False, "error": "STT conversion failed"}, status=400)
            except Exception as e:
                self._send_json({"success": False, "error": str(e)}, status=500)
            return

        if self.path == "/voice/synthesize":
            payload = self._read_json()
            text = payload.get("text", "")
            
            if not text:
                self._send_json({"success": False, "error": "No text provided"}, status=400)
                return
            
            try:
                # Try ElevenLabs first (preferred)
                elevenlabs_voice = get_elevenlabs_voice()
                if elevenlabs_voice.is_configured():
                    audio_base64 = elevenlabs_voice.text_to_speech(text)
                    if audio_base64:
                        self._send_json({"success": True, "audio": audio_base64, "provider": "elevenlabs"})
                        return
                
                # Fallback to Google Cloud
                google_voice = get_google_voice()
                if google_voice.is_configured():
                    audio_base64 = google_voice.text_to_speech(text)
                    if audio_base64:
                        self._send_json({"success": True, "audio": audio_base64, "provider": "google"})
                        return
                
                self._send_json({"success": False, "error": "No TTS service configured"}, status=503)
            except Exception as e:
                self._send_json({"success": False, "error": str(e)}, status=500)
            return

        if self.path == "/voice/wake-word-check":
            payload = self._read_json()
            text = payload.get("text", "")
            
            detector = get_wake_word_detector()
            is_wake_word = detector.detect(text)
            command = detector.extract_command(text) if is_wake_word else ""
            
            self._send_json({
                "success": True,
                "is_wake_word": is_wake_word,
                "command": command
            })
            return

        if self.path == "/voice/status":
            google_voice = get_google_voice()
            elevenlabs_voice = get_elevenlabs_voice()
            
            self._send_json({
                "success": True,
                "providers": {
                    "google_cloud": {
                        "configured": google_voice.is_configured(),
                        "priority": 2
                    },
                    "elevenlabs": {
                        "configured": elevenlabs_voice.is_configured(),
                        "priority": 1,
                        "voice_id": elevenlabs_voice.voice_id if elevenlabs_voice.is_configured() else None
                    }
                }
            })
            return

        # ========== SYSTEM CONTROL ENDPOINTS (STAGE 3) ==========
        
        # Application Management
        if self.path == "/system/app/open":
            payload = self._read_json()
            app_name = payload.get("app_name", "")
            args = payload.get("args", [])
            
            app_manager = get_app_manager()
            result = app_manager.open_application(app_name, args)
            self._send_json(result)
            return

        if self.path == "/system/app/close":
            payload = self._read_json()
            app_name = payload.get("app_name", "")
            force = payload.get("force", False)
            
            app_manager = get_app_manager()
            result = app_manager.close_application(app_name, force)
            self._send_json(result)
            return

        if self.path == "/system/app/list":
            app_manager = get_app_manager()
            result = app_manager.list_running_applications()
            self._send_json(result)
            return

        if self.path == "/system/app/info":
            payload = self._read_json()
            app_name = payload.get("app_name", "")
            
            app_manager = get_app_manager()
            result = app_manager.get_application_info(app_name)
            self._send_json(result)
            return

        # Hardware Control - Volume
        if self.path == "/system/hardware/volume/get":
            hardware = get_hardware_controller()
            result = hardware.get_volume()
            self._send_json(result)
            return

        if self.path == "/system/hardware/volume/set":
            payload = self._read_json()
            level = payload.get("level", 50)
            
            hardware = get_hardware_controller()
            result = hardware.set_volume(level)
            self._send_json(result)
            return

        if self.path == "/system/hardware/volume/mute":
            hardware = get_hardware_controller()
            result = hardware.mute_volume()
            self._send_json(result)
            return

        if self.path == "/system/hardware/volume/unmute":
            hardware = get_hardware_controller()
            result = hardware.unmute_volume()
            self._send_json(result)
            return

        if self.path == "/system/hardware/volume/up":
            payload = self._read_json()
            increment = payload.get("increment", 10)
            
            hardware = get_hardware_controller()
            result = hardware.volume_up(increment)
            self._send_json(result)
            return

        if self.path == "/system/hardware/volume/down":
            payload = self._read_json()
            decrement = payload.get("decrement", 10)
            
            hardware = get_hardware_controller()
            result = hardware.volume_down(decrement)
            self._send_json(result)
            return

        # Hardware Control - Brightness
        if self.path == "/system/hardware/brightness/get":
            hardware = get_hardware_controller()
            result = hardware.get_brightness()
            self._send_json(result)
            return

        if self.path == "/system/hardware/brightness/set":
            payload = self._read_json()
            level = payload.get("level", 50)
            
            hardware = get_hardware_controller()
            result = hardware.set_brightness(level)
            self._send_json(result)
            return

        if self.path == "/system/hardware/brightness/up":
            payload = self._read_json()
            increment = payload.get("increment", 10)
            
            hardware = get_hardware_controller()
            result = hardware.brightness_up(increment)
            self._send_json(result)
            return

        if self.path == "/system/hardware/brightness/down":
            payload = self._read_json()
            decrement = payload.get("decrement", 10)
            
            hardware = get_hardware_controller()
            result = hardware.brightness_down(decrement)
            self._send_json(result)
            return

        # Hardware Control - WiFi
        if self.path == "/system/hardware/wifi/status":
            hardware = get_hardware_controller()
            result = hardware.get_wifi_status()
            self._send_json(result)
            return

        if self.path == "/system/hardware/wifi/enable":
            hardware = get_hardware_controller()
            result = hardware.enable_wifi()
            self._send_json(result)
            return

        if self.path == "/system/hardware/wifi/disable":
            hardware = get_hardware_controller()
            result = hardware.disable_wifi()
            self._send_json(result)
            return

        if self.path == "/system/hardware/wifi/list":
            hardware = get_hardware_controller()
            result = hardware.list_wifi_networks()
            self._send_json(result)
            return

        # Power Management
        if self.path == "/system/power/shutdown":
            payload = self._read_json()
            delay = payload.get("delay", 0)
            force = payload.get("force", False)
            
            power = get_power_manager()
            result = power.shutdown(delay, force)
            self._send_json(result)
            return

        if self.path == "/system/power/restart":
            payload = self._read_json()
            delay = payload.get("delay", 0)
            force = payload.get("force", False)
            
            power = get_power_manager()
            result = power.restart(delay, force)
            self._send_json(result)
            return

        if self.path == "/system/power/sleep":
            power = get_power_manager()
            result = power.sleep()
            self._send_json(result)
            return

        if self.path == "/system/power/hibernate":
            power = get_power_manager()
            result = power.hibernate()
            self._send_json(result)
            return

        if self.path == "/system/power/lock":
            power = get_power_manager()
            result = power.lock_screen()
            self._send_json(result)
            return

        if self.path == "/system/power/cancel-shutdown":
            power = get_power_manager()
            result = power.cancel_shutdown()
            self._send_json(result)
            return

        if self.path == "/system/power/logoff":
            power = get_power_manager()
            result = power.log_off()
            self._send_json(result)
            return

        # Screenshot & File Operations
        if self.path == "/system/screenshot/capture":
            payload = self._read_json()
            save_path = payload.get("save_path", None)
            
            screenshot = get_screenshot_manager()
            result = screenshot.capture_screenshot(save_path)
            self._send_json(result)
            return

        if self.path == "/system/screenshot/capture-region":
            payload = self._read_json()
            x = payload.get("x", 0)
            y = payload.get("y", 0)
            width = payload.get("width", 800)
            height = payload.get("height", 600)
            save_path = payload.get("save_path", None)
            
            screenshot = get_screenshot_manager()
            result = screenshot.capture_region(x, y, width, height, save_path)
            self._send_json(result)
            return

        if self.path == "/system/screenshot/auto-save":
            payload = self._read_json()
            prefix = payload.get("prefix", "screenshot")
            
            screenshot = get_screenshot_manager()
            result = screenshot.auto_save_screenshot(prefix)
            self._send_json(result)
            return

        if self.path == "/system/files/search":
            payload = self._read_json()
            query = payload.get("query", "")
            search_dirs = payload.get("search_dirs", None)
            max_results = payload.get("max_results", 50)
            file_types = payload.get("file_types", None)
            
            screenshot = get_screenshot_manager()
            result = screenshot.search_files(query, search_dirs, max_results, file_types)
            self._send_json(result)
            return

        if self.path == "/system/files/recent":
            payload = self._read_json()
            days = payload.get("days", 7)
            search_dirs = payload.get("search_dirs", None)
            max_results = payload.get("max_results", 50)
            
            screenshot = get_screenshot_manager()
            result = screenshot.get_recent_files(days, search_dirs, max_results)
            self._send_json(result)
            return

        if self.path == "/system/files/open-location":
            payload = self._read_json()
            filepath = payload.get("filepath", "")
            
            screenshot = get_screenshot_manager()
            result = screenshot.open_file_location(filepath)
            self._send_json(result)
            return

        # System Monitoring
        if self.path == "/system/monitor/overview":
            monitor = get_system_monitor()
            result = monitor.get_system_overview()
            self._send_json(result)
            return

        if self.path == "/system/monitor/cpu":
            payload = self._read_json()
            interval = payload.get("interval", 1.0)
            per_cpu = payload.get("per_cpu", False)
            
            monitor = get_system_monitor()
            result = monitor.get_cpu_usage(interval, per_cpu)
            self._send_json(result)
            return

        if self.path == "/system/monitor/cpu/info":
            monitor = get_system_monitor()
            result = monitor.get_cpu_info()
            self._send_json(result)
            return

        if self.path == "/system/monitor/memory":
            monitor = get_system_monitor()
            result = monitor.get_memory_usage()
            self._send_json(result)
            return

        if self.path == "/system/monitor/memory/top-processes":
            payload = self._read_json()
            count = payload.get("count", 10)
            
            monitor = get_system_monitor()
            result = monitor.get_top_memory_processes(count)
            self._send_json(result)
            return

        if self.path == "/system/monitor/disk":
            payload = self._read_json()
            path = payload.get("path", None)
            
            monitor = get_system_monitor()
            result = monitor.get_disk_usage(path)
            self._send_json(result)
            return

        if self.path == "/system/monitor/disk/io":
            monitor = get_system_monitor()
            result = monitor.get_disk_io()
            self._send_json(result)
            return

        if self.path == "/system/monitor/network":
            monitor = get_system_monitor()
            result = monitor.get_network_usage()
            self._send_json(result)
            return

        if self.path == "/system/monitor/network/connections":
            payload = self._read_json()
            kind = payload.get("kind", "inet")
            
            monitor = get_system_monitor()
            result = monitor.get_network_connections(kind)
            self._send_json(result)
            return

        if self.path == "/system/monitor/network/interfaces":
            monitor = get_system_monitor()
            result = monitor.get_network_interfaces()
            self._send_json(result)
            return

        if self.path == "/system/monitor/temperature":
            monitor = get_system_monitor()
            result = monitor.get_temperatures()
            self._send_json(result)
            return

        if self.path == "/system/monitor/battery":
            monitor = get_system_monitor()
            result = monitor.get_battery_status()
            self._send_json(result)
            return

        if self.path == "/system/monitor/processes":
            monitor = get_system_monitor()
            result = monitor.get_process_count()
            self._send_json(result)
            return

        # ==================== STAGE 4: AUTOMATION & MEMORY ====================
        
        # Custom Commands
        if self.path == "/automation/custom-commands/create":
            payload = self._read_json()
            manager = get_custom_command_manager()
            result = manager.create_command(
                payload.get("command_name"),
                payload.get("trigger_words", []),
                payload.get("actions", []),
                payload.get("description", "")
            )
            self._send_json(result)
            return
        
        if self.path == "/automation/custom-commands/list":
            payload = self._read_json()
            manager = get_custom_command_manager()
            result = manager.list_commands(payload.get("enabled_only", False))
            self._send_json(result)
            return
        
        if self.path == "/automation/custom-commands/get":
            payload = self._read_json()
            manager = get_custom_command_manager()
            result = manager.get_command(payload.get("command_id"))
            self._send_json(result)
            return
        
        if self.path == "/automation/custom-commands/update":
            payload = self._read_json()
            manager = get_custom_command_manager()
            command_id = payload.pop("command_id", None)
            if not command_id:
                self._send_json({"success": False, "error": "command_id required"}, status=400)
                return
            result = manager.update_command(command_id, **payload)
            self._send_json(result)
            return
        
        if self.path == "/automation/custom-commands/delete":
            payload = self._read_json()
            manager = get_custom_command_manager()
            result = manager.delete_command(payload.get("command_id"))
            self._send_json(result)
            return
        
        if self.path == "/automation/custom-commands/execute":
            payload = self._read_json()
            manager = get_custom_command_manager()
            result = manager.execute_command(payload.get("command_id"))
            self._send_json(result)
            return
        
        if self.path == "/automation/custom-commands/top":
            payload = self._read_json()
            manager = get_custom_command_manager()
            result = manager.get_top_commands(payload.get("limit", 10))
            self._send_json(result)
            return
        
        # Workflows
        if self.path == "/automation/workflows/create":
            payload = self._read_json()
            manager = get_workflow_manager()
            result = manager.create_workflow(
                payload.get("workflow_name"),
                payload.get("description", ""),
                payload.get("steps", []),
                payload.get("trigger")
            )
            self._send_json(result)
            return
        
        if self.path == "/automation/workflows/list":
            payload = self._read_json()
            manager = get_workflow_manager()
            result = manager.list_workflows(payload.get("enabled_only", False))
            self._send_json(result)
            return
        
        if self.path == "/automation/workflows/get":
            payload = self._read_json()
            manager = get_workflow_manager()
            result = manager.get_workflow(payload.get("workflow_id"))
            self._send_json(result)
            return
        
        if self.path == "/automation/workflows/update":
            payload = self._read_json()
            manager = get_workflow_manager()
            workflow_id = payload.pop("workflow_id", None)
            if not workflow_id:
                self._send_json({"success": False, "error": "workflow_id required"}, status=400)
                return
            result = manager.update_workflow(workflow_id, **payload)
            self._send_json(result)
            return
        
        if self.path == "/automation/workflows/delete":
            payload = self._read_json()
            manager = get_workflow_manager()
            result = manager.delete_workflow(payload.get("workflow_id"))
            self._send_json(result)
            return
        
        if self.path == "/automation/workflows/execute":
            payload = self._read_json()
            manager = get_workflow_manager()
            result = manager.prepare_workflow_execution(payload.get("workflow_id"))
            self._send_json(result)
            return
        
        if self.path == "/automation/workflows/history":
            payload = self._read_json()
            manager = get_workflow_manager()
            result = manager.get_workflow_history(payload.get("workflow_id"), payload.get("limit", 50))
            self._send_json(result)
            return
        
        # Habit Learning
        if self.path == "/automation/habits/analyze":
            payload = self._read_json()
            engine = get_habit_learning_engine()
            result = engine.analyze_recent_events(payload.get("days", 7))
            self._send_json(result)
            return
        
        if self.path == "/automation/habits/list":
            engine = get_habit_learning_engine()
            result = engine.get_detected_habits()
            self._send_json(result)
            return
        
        if self.path == "/automation/habits/feedback":
            payload = self._read_json()
            engine = get_habit_learning_engine()
            result = engine.provide_habit_feedback(
                payload.get("pattern_id"),
                payload.get("feedback")
            )
            self._send_json(result)
            return
        
        if self.path == "/automation/habits/analytics":
            engine = get_habit_learning_engine()
            result = engine.get_habit_analytics()
            self._send_json(result)
            return
        
        # Suggestions
        if self.path == "/suggestions/active":
            payload = self._read_json()
            engine = get_suggestion_engine()
            result = engine.get_active_suggestions(payload.get("limit", 5))
            self._send_json(result)
            return
        
        if self.path == "/suggestions/for-context":
            payload = self._read_json()
            engine = get_suggestion_engine()
            context = payload.get("context", {})
            result = engine.get_suggestions_for_context(context)
            self._send_json(result)
            return
        
        if self.path == "/suggestions/respond":
            payload = self._read_json()
            engine = get_suggestion_engine()
            result = engine.respond_to_suggestion(
                payload.get("suggestion_id"),
                payload.get("response"),
                payload.get("helpful")
            )
            self._send_json(result)
            return
        
        if self.path == "/suggestions/analytics":
            engine = get_suggestion_engine()
            result = engine.get_suggestion_analytics()
            self._send_json(result)
            return
        
        if self.path == "/suggestions/dismiss-type":
            payload = self._read_json()
            engine = get_suggestion_engine()
            result = engine.dismiss_suggestion_type(payload.get("type"))
            self._send_json(result)
            return
        
        # ==================== PHASE 2: MEMORY SYSTEM ====================
        
        # Memory Management
        if self.path == "/memory/save":
            payload = self._read_json()
            manager = get_memory_manager()
            result = manager.save_memory(
                payload.get("type"),
                payload.get("content"),
                payload.get("context"),
                payload.get("tags", []),
                payload.get("importance", 0.5)
            )
            self._send_json(result)
            return
        
        if self.path == "/memory/search":
            payload = self._read_json()
            manager = get_memory_manager()
            result = manager.search_memories(
                payload.get("query"),
                payload.get("type"),
                payload.get("limit", 10)
            )
            self._send_json(result)
            return
        
        if self.path == "/memory/get":
            payload = self._read_json()
            manager = get_memory_manager()
            result = manager.get_memory(payload.get("memory_id"))
            self._send_json(result)
            return
        
        if self.path == "/memory/context":
            payload = self._read_json()
            manager = get_memory_manager()
            result = manager.get_conversation_context(payload.get("conversation_id"))
            self._send_json(result)
            return
        
        if self.path == "/memory/add-to-conversation":
            payload = self._read_json()
            manager = get_memory_manager()
            result = manager.add_to_conversation(
                payload.get("conversation_id"),
                payload.get("role"),
                payload.get("message")
            )
            self._send_json(result)
            return
        
        if self.path == "/memory/delete":
            payload = self._read_json()
            manager = get_memory_manager()
            result = manager.delete_memory(payload.get("memory_id"))
            self._send_json(result)
            return
        
        if self.path == "/memory/recent":
            payload = self._read_json()
            manager = get_memory_manager()
            result = manager.get_recent_memories(payload.get("days", 7), payload.get("limit", 10))
            self._send_json(result)
            return
        
        if self.path == "/memory/by-type":
            payload = self._read_json()
            manager = get_memory_manager()
            result = manager.get_memories_by_type(payload.get("type"), payload.get("limit", 10))
            self._send_json(result)
            return
        
        if self.path == "/memory/update-relevance":
            payload = self._read_json()
            manager = get_memory_manager()
            result = manager.update_memory_relevance(payload.get("memory_id"), payload.get("score"))
            self._send_json(result)
            return
        
        if self.path == "/memory/cleanup":
            payload = self._read_json()
            manager = get_memory_manager()
            result = manager.cleanup_old_memories(payload.get("days_to_keep", 90))
            self._send_json(result)
            return
        
        if self.path == "/memory/statistics":
            manager = get_memory_manager()
            result = manager.get_memory_statistics()
            self._send_json(result)
            return
        
        if self.path == "/memory/semantic-search":
            payload = self._read_json()
            manager = get_memory_manager()
            result = manager.semantic_search(
                payload.get("query"),
                payload.get("type"),
                payload.get("limit", 10),
                payload.get("threshold", 0.3)
            )
            self._send_json(result)
            return
        
        if self.path == "/memory/search-related":
            payload = self._read_json()
            manager = get_memory_manager()
            result = manager.search_related_memories(
                payload.get("conversation_id"),
                payload.get("query"),
                payload.get("limit", 10)
            )
            self._send_json(result)
            return
        
        if self.path == "/memory/set-expiry":
            payload = self._read_json()
            manager = get_memory_manager()
            result = manager.set_memory_expiry(
                payload.get("memory_id"),
                payload.get("days_to_expiry", 30)
            )
            self._send_json(result)
            return
        
        if self.path == "/memory/archive-expired":
            manager = get_memory_manager()
            result = manager.archive_expired_memories()
            self._send_json(result)
            return
        
        if self.path == "/memory/conversation-summary":
            payload = self._read_json()
            manager = get_memory_manager()
            result = manager.get_conversation_summary(payload.get("conversation_id"))
            self._send_json(result)
            return
        
        # Preference Management
        if self.path == "/preferences/set":
            payload = self._read_json()
            manager = get_preference_manager()
            result = manager.set_preference(
                payload.get("category"),
                payload.get("key"),
                payload.get("value"),
                payload.get("source", "manual"),
                payload.get("confidence", 1.0)
            )
            self._send_json(result)
            return
        
        if self.path == "/preferences/get":
            payload = self._read_json()
            manager = get_preference_manager()
            result = manager.get_preference(payload.get("category"), payload.get("key"))
            self._send_json(result)
            return
        
        if self.path == "/preferences/all":
            payload = self._read_json()
            manager = get_preference_manager()
            result = manager.get_all_preferences(payload.get("category"))
            self._send_json(result)
            return
        
        if self.path == "/preferences/delete":
            payload = self._read_json()
            manager = get_preference_manager()
            result = manager.delete_preference(payload.get("category"), payload.get("key"))
            self._send_json(result)
            return
        
        if self.path == "/preferences/recommendations":
            payload = self._read_json()
            manager = get_preference_manager()
            result = manager.get_preference_recommendations(payload.get("category"))
            self._send_json(result)
            return
        
        if self.path == "/preferences/apply":
            payload = self._read_json()
            manager = get_preference_manager()
            result = manager.apply_preference(payload.get("category"), payload.get("key"))
            self._send_json(result)
            return
        
        if self.path == "/preferences/reject":
            payload = self._read_json()
            manager = get_preference_manager()
            result = manager.reject_preference(payload.get("category"), payload.get("key"))
            self._send_json(result)
            return
        
        if self.path == "/preferences/statistics":
            manager = get_preference_manager()
            result = manager.get_preference_statistics()
            self._send_json(result)
            return
        
        if self.path == "/preferences/history":
            payload = self._read_json()
            manager = get_preference_manager()
            result = manager.get_preference_history(
                payload.get("category"),
                payload.get("key"),
                payload.get("limit", 50)
            )
            self._send_json(result)
            return
        
        # ==================== PHASE 3: BEHAVIORAL LEARNING ====================
        
        if self.path == "/preferences/analyze-behavior":
            payload = self._read_json()
            manager = get_preference_manager()
            result = manager.analyze_behavior_for_preferences(payload.get("days", 14))
            self._send_json(result)
            return
        
        if self.path == "/preferences/patterns":
            manager = get_preference_manager()
            result = manager.detect_preference_patterns()
            self._send_json(result)
            return
        
        if self.path == "/preferences/auto-learn":
            payload = self._read_json()
            manager = get_preference_manager()
            result = manager.auto_learn_from_usage(payload.get("enabled", True))
            self._send_json(result)
            return
        
        if self.path == "/preferences/suggest-from-habits":
            payload = self._read_json()
            manager = get_preference_manager()
            result = manager.suggest_preferences_from_habits(payload.get("habit_ids"))
            self._send_json(result)
            return
        
        if self.path == "/preferences/learning-analytics":
            manager = get_preference_manager()
            result = manager.get_learning_analytics()
            self._send_json(result)
            return
        
        # ==================== PHASE 4: DATABASE OPTIMIZATION ====================
        
        if self.path == "/database/create-indexes":
            optimizer = get_database_optimizer()
            result = optimizer.create_all_indexes()
            self._send_json(result)
            return
        
        if self.path == "/database/index-stats":
            optimizer = get_database_optimizer()
            result = optimizer.get_index_stats()
            self._send_json(result)
            return
        
        if self.path == "/database/collection-stats":
            optimizer = get_database_optimizer()
            result = optimizer.get_collection_stats()
            self._send_json(result)
            return
        
        if self.path == "/database/verify-indexes":
            optimizer = get_database_optimizer()
            result = optimizer.verify_indexes_exist()
            self._send_json(result)
            return
        
        if self.path == "/database/optimize-suggestions":
            optimizer = get_database_optimizer()
            result = optimizer.optimize_memory_query()
            self._send_json(result)
            return
        
        # ==================== PHASE 4: DATA RETENTION ====================
        
        if self.path == "/data/set-retention-policy":
            payload = self._read_json()
            manager = get_data_retention_manager()
            result = manager.set_retention_policy(
                payload.get("memory_type"),
                payload.get("retention_days"),
                payload.get("action", "delete")
            )
            self._send_json(result)
            return
        
        if self.path == "/data/get-retention-policy":
            payload = self._read_json()
            manager = get_data_retention_manager()
            result = manager.get_retention_policy(payload.get("memory_type"))
            self._send_json(result)
            return
        
        if self.path == "/data/cleanup-expired":
            payload = self._read_json()
            manager = get_data_retention_manager()
            result = manager.cleanup_expired_data(payload.get("memory_type"))
            self._send_json(result)
            return
        
        if self.path == "/data/retention-stats":
            manager = get_data_retention_manager()
            result = manager.get_retention_stats()
            self._send_json(result)
            return
        
        if self.path == "/data/list-policies":
            manager = get_data_retention_manager()
            result = manager.list_policies()
            self._send_json(result)
            return
        
        if self.path == "/data/restore-from-archive":
            payload = self._read_json()
            manager = get_data_retention_manager()
            result = manager.restore_from_archive(
                payload.get("memory_type"),
                payload.get("archive_collection")
            )
            self._send_json(result)
            return
        
        # ==================== END PHASE 4 ====================
        
        # ==================== STATUS ENDPOINT ====================
        if self.path == "/system-status":
            status = {
                "uptime_seconds": time.time() - STARTED_AT,
                "stage": 4,
                "stage5_available": STAGE5_AVAILABLE,
                "mongodb": "connected" if get_db() else "disconnected",
                "timestamp": time.time()
            }
            self._send_json({"success": True, "status": status})
            return
        
        # ==================== STAGE 5: ADVANCED AI FEATURES ====================
        # Vision/Screen Analysis (Phase 1)
        if self.path == "/vision/analyze-screen":
            if not STAGE5_AVAILABLE:
                self._send_json({"success": False, "error": "Stage 5 not available"})
                return
            
            analyzer = get_screen_analyzer()
            if not analyzer:
                self._send_json({"success": False, "error": "Screen analyzer not available"})
                return
            
            payload = self._read_json()
            result = analyzer.analyze(payload)
            self._send_json(result)
            return
        
        if self.path == "/vision/get-screen-text":
            if not STAGE5_AVAILABLE:
                self._send_json({"success": False, "error": "Stage 5 not available"})
                return
            
            analyzer = get_screen_analyzer()
            if not analyzer:
                self._send_json({"success": False, "error": "Screen analyzer not available"})
                return
            
            payload = self._read_json()
            ocr_threshold = payload.get('ocr_confidence_threshold', 0.7)
            result = analyzer.get_screen_text(ocr_threshold)
            self._send_json(result)
            return
        
        # Note: GET endpoints handled in do_GET
        
        # Coding Assistant (Phase 2)
        if self.path == "/coding/generate-code":
            if not STAGE5_AVAILABLE:
                self._send_json({"success": False, "error": "Stage 5 not available"})
                return
            
            assistant = get_coding_assistant()
            if not assistant:
                self._send_json({"success": False, "error": "Coding assistant not available"})
                return
            
            payload = self._read_json()
            description = payload.get('description', '')
            language = payload.get('language', 'python')
            context = payload.get('context')
            
            result = assistant.generate_code(description, language, context)
            self._send_json(result)
            return
        
        if self.path == "/coding/debug-code":
            if not STAGE5_AVAILABLE:
                self._send_json({"success": False, "error": "Stage 5 not available"})
                return
            
            assistant = get_coding_assistant()
            if not assistant:
                self._send_json({"success": False, "error": "Coding assistant not available"})
                return
            
            payload = self._read_json()
            code = payload.get('code', '')
            error_message = payload.get('error_message')
            language = payload.get('language')
            
            result = assistant.debug_code(code, error_message, language)
            self._send_json(result)
            return
        
        if self.path == "/coding/explain-code":
            if not STAGE5_AVAILABLE:
                self._send_json({"success": False, "error": "Stage 5 not available"})
                return
            
            assistant = get_coding_assistant()
            if not assistant:
                self._send_json({"success": False, "error": "Coding assistant not available"})
                return
            
            payload = self._read_json()
            code = payload.get('code', '')
            language = payload.get('language')
            detail_level = payload.get('detail_level', 'medium')
            
            result = assistant.explain_code(code, language, detail_level)
            self._send_json(result)
            return
        
        if self.path == "/coding/refactor-code":
            if not STAGE5_AVAILABLE:
                self._send_json({"success": False, "error": "Stage 5 not available"})
                return
            
            assistant = get_coding_assistant()
            if not assistant:
                self._send_json({"success": False, "error": "Coding assistant not available"})
                return
            
            payload = self._read_json()
            code = payload.get('code', '')
            language = payload.get('language')
            goals = payload.get('goals', ['readability', 'maintainability'])
            
            result = assistant.refactor_code(code, language, goals)
            self._send_json(result)
            return
        
        if self.path == "/coding/documentation":
            if not STAGE5_AVAILABLE:
                self._send_json({"success": False, "error": "Stage 5 not available"})
                return
            
            assistant = get_coding_assistant()
            if not assistant:
                self._send_json({"success": False, "error": "Coding assistant not available"})
                return
            
            payload = self._read_json()
            code = payload.get('code', '')
            language = payload.get('language')
            doc_format = payload.get('format', 'markdown')
            
            result = assistant.generate_documentation(code, language, doc_format)
            self._send_json(result)
            return
        
        # ==================== STAGE 5: NEWS & WEATHER ENDPOINTS (POST) ====================
        if self.path == "/info/weather":
            if not STAGE5_AVAILABLE:
                self._send_json({"success": False, "error": "Stage 5 not available"})
                return
            
            news_service = get_news_weather_service()
            if not news_service:
                self._send_json({"success": False, "error": "News & Weather service not available"})
                return
            
            payload = self._read_json()
            location = payload.get('location', 'London')
            units = payload.get('units', 'metric')
            
            result = news_service.get_weather(location, units)
            self._send_json(result)
            return
        
        if self.path == "/info/weather-forecast":
            if not STAGE5_AVAILABLE:
                self._send_json({"success": False, "error": "Stage 5 not available"})
                return
            
            news_service = get_news_weather_service()
            if not news_service:
                self._send_json({"success": False, "error": "News & Weather service not available"})
                return
            
            payload = self._read_json()
            location = payload.get('location', 'London')
            days = payload.get('days', 5)
            units = payload.get('units', 'metric')
            
            result = news_service.get_weather_forecast(location, days, units)
            self._send_json(result)
            return
        
        if self.path == "/info/news":
            if not STAGE5_AVAILABLE:
                self._send_json({"success": False, "error": "Stage 5 not available"})
                return
            
            news_service = get_news_weather_service()
            if not news_service:
                self._send_json({"success": False, "error": "News & Weather service not available"})
                return
            
            payload = self._read_json()
            query = payload.get('query', '')
            category = payload.get('category', 'general')
            country = payload.get('country', 'us')
            page_size = payload.get('page_size', 10)
            
            result = news_service.get_news(query, category, country, page_size)
            self._send_json(result)
            return
        
        # Model Management (Phase 4)
        # Coming: /ai/available-models, /ai/switch-model, /ai/model-status
        
        # Background Mode (Phase 5)
        # Coming: /system/background-mode, /system/background-status, /system/auto-start
        
        # ==================== END STAGE 4 ====================

        self._send_json({"success": False, "error": "Not found"}, status=404)


def run():
    server = HTTPServer(("127.0.0.1", 5000), ElixiHandler)
    if not MONGODB_URI:
        print("MongoDB not configured. Set MONGODB_URI to connect to Atlas.")
    print("ELIXI backend listening on http://127.0.0.1:5000")
    server.serve_forever()


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(0)
