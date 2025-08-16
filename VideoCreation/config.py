import os
from pathlib import Path
from typing import Dict, Any, List

class VideoConfig:
    """Central configuration management for video creation workflows"""
    
    def __init__(self, base_path: str = None, environment: str = "local"):
        """
        Initialize configuration
        
        Args:
            base_path: Base directory path (auto-detected if None)
            environment: "local" or "colab"
        """
        self.environment = environment
        self._setup_base_paths(base_path)
        self._setup_greece_paths()
        self._setup_tt_paths()
    
    def _setup_base_paths(self, base_path: str = None):
        """Setup base directory paths based on environment"""
        if base_path:
            self.BASE_DIRECTORY = base_path
        elif self.environment == "colab":
            self.BASE_DIRECTORY = "/content/drive/My Drive/Automation"
        else:  # local
            self.BASE_DIRECTORY = r"C:\NATALIA\Generative AI\auto_channel\Files for SocialVideoBot"
        
        # Ensure base directory exists
        os.makedirs(self.BASE_DIRECTORY, exist_ok=True)
    
    def _setup_greece_paths(self):
        """Setup all Greece workflow paths"""
        # Base Greece directories
        self.BASE_DIRECTORY_GREECE = os.path.join(self.BASE_DIRECTORY, "Greece_Automation")
        self.BASE_DIRECTORY_GREECE_CURRENT = os.path.join(self.BASE_DIRECTORY_GREECE, "3_Hector")
        self.BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS = os.path.join(self.BASE_DIRECTORY_GREECE, "Common_Artifacts")
        
        # Intro paths
        self.INTRO_BASE = os.path.join(self.BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, "Intro")
        self.intro_paths = {
            "audio_en": os.path.join(self.INTRO_BASE, "Intro_Audio_Output_EN.mp3"),
            "audio_ru": os.path.join(self.INTRO_BASE, "Intro_Audio_Output_RU.mp3"),
            "music": os.path.join(self.INTRO_BASE, "Intro_Music.mp3"),
            "text_audio_en": os.path.join(self.INTRO_BASE, "Welcome_EN_TG.mp3"),
            "text_audio_ru": os.path.join(self.INTRO_BASE, "Welcome_RU_TG.mp3"),
            "text_overlay_csv": os.path.join(self.INTRO_BASE, "Intro_Text_Overlay_EN_RU.csv"),
            "video_paths": [os.path.join(self.INTRO_BASE, f"Intro_{i}.mp4") for i in range(1, 2)],  # Fixed: ensure this is a list
            "output_en_horizontal": os.path.join(self.INTRO_BASE, "Intro_Output_horizontal_1920x1080_EN.mp4"),
            "output_ru_horizontal": os.path.join(self.INTRO_BASE, "Intro_Output_horizontal_1920x1080_RU.mp4"),
            "output_en_vertical": os.path.join(self.INTRO_BASE, "Intro_Output_vertical_1080x1920_EN.mp4"),
            "output_ru_vertical": os.path.join(self.INTRO_BASE, "Intro_Output_vertical_1080x1920_RU.mp4")
        }
        
        # Tail paths
        self.TAIL_BASE = os.path.join(self.BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS, "Tail")
        self.tail_paths = {
            "audio_en": os.path.join(self.TAIL_BASE, "Tail_Audio_Output_EN.mp3"),
            "audio_ru": os.path.join(self.TAIL_BASE, "Tail_Audio_Output_RU.mp3"),
            "music": os.path.join(self.TAIL_BASE, "Tail_Music.mp3"),
            "text_audio_en": os.path.join(self.TAIL_BASE, "Tail_EN_TG.mp3"),
            "text_audio_ru": os.path.join(self.TAIL_BASE, "Tail_RU_TG.mp3"),
            "text_overlay_csv": os.path.join(self.TAIL_BASE, "Tail_Text_Overlay_EN_RU.csv"),
            "video_paths": [os.path.join(self.TAIL_BASE, f"Tail_{i}.mp4") for i in range(1, 3)]  # Fixed: ensure this is a list
        }
        
        # Current project paths
        self.current_artifacts = os.path.join(self.BASE_DIRECTORY_GREECE_CURRENT, "Artifacts")
        self.current_result = os.path.join(self.BASE_DIRECTORY_GREECE_CURRENT, "Result_Automation")
        self.current_final = os.path.join(self.BASE_DIRECTORY_GREECE_CURRENT, "Final")
        
        self.current_paths = {
            "video_paths": [os.path.join(self.current_artifacts, f"Prompt {i}.mp4") for i in range(1, 11)],  # Fixed: ensure this is a list
            "audio_ru": os.path.join(self.current_artifacts, "Voice_Over_RU.mp3"),
            "audio_en": os.path.join(self.current_artifacts, "Voice_Over_EN.mp3"),
            "csv": os.path.join(self.current_artifacts, "Video_Texts.csv"),
            "audio_with_tail_ru": os.path.join(self.current_result, "Voice_Over_RU_With_Tail.mp3"),
            "audio_with_tail_en": os.path.join(self.current_result, "Voice_Over_EN_With_Tail.mp3"),
            "main_plus_tail_en_h": os.path.join(self.current_result, "main_plus_tail_horizontal_1920x1080_EN.mp4"),
            "main_plus_tail_ru_h": os.path.join(self.current_result, "main_plus_tail_horizontal_1920x1080_RU.mp4"),
            "main_plus_tail_en_v": os.path.join(self.current_result, "main_plus_tail_vertical_1080x1920_EN.mp4"),
            "main_plus_tail_ru_v": os.path.join(self.current_result, "main_plus_tail_vertical_1080x1920_RU.mp4"),
            "final_en_h": os.path.join(self.current_final, "final_horizontal_1920x1080_EN.mp4"),
            "final_ru_h": os.path.join(self.current_final, "final_horizontal_1920x1080_RU.mp4"),
            "final_en_v": os.path.join(self.current_final, "final_vertical_1080x1920_EN.mp4"),
            "final_ru_v": os.path.join(self.current_final, "final_vertical_1080x1920_RU.mp4")
        }
    
    def _setup_tt_paths(self):
        """Setup TimelessTales paths"""
        self.TT_DIRECTORY = os.path.join(self.BASE_DIRECTORY, "TT")
        self.tt_paths = {
            "tracker_excel": os.path.join(self.TT_DIRECTORY, "TimelessTales_Video_Tracker.xlsx"),
            "intro_video": os.path.join(self.TT_DIRECTORY, "assets/intro/TT_INTRO.mp4"),
            "intro_voice": os.path.join(self.TT_DIRECTORY, "assets/intro/Welcome_RU_TT.mp3"),
            "intro_final": os.path.join(self.TT_DIRECTORY, "assets/intro/TT_INTRO_FINAL.mp4"),
            "tail_video": os.path.join(self.TT_DIRECTORY, "assets/tail/TT_TAIL.mp4"),
            "tail_voice": os.path.join(self.TT_DIRECTORY, "assets/tail/Tail_RU_TT.mp3"),
            "tail_final": os.path.join(self.TT_DIRECTORY, "assets/tail/TT_TAIL_FINAL.mp4")
        }
    
    def get_greece_paths_for_language_orientation(self, language: str, orientation: str) -> Dict[str, str]:
        """Get specific paths for Greece workflow based on language and orientation"""
        lang_suffix = language.upper()
        orient_suffix = "h" if orientation == "horizontal" else "v"
        
        return {
            "intro_audio": self.intro_paths[f"audio_{language.lower()}"],
            "intro_text_audio": self.intro_paths[f"text_audio_{language.lower()}"],
            "intro_video": self.intro_paths[f"output_{language.lower()}_{orientation}"],
            "tail_audio": self.tail_paths[f"audio_{language.lower()}"],
            "tail_text_audio": self.tail_paths[f"text_audio_{language.lower()}"],
            "main_audio": self.current_paths[f"audio_{language.lower()}"],
            "audio_with_tail": self.current_paths[f"audio_with_tail_{language.lower()}"],
            "main_tail_video": self.current_paths[f"main_plus_tail_{language.lower()}_{orient_suffix}"],
            "final_video": self.current_paths[f"final_{language.lower()}_{orient_suffix}"],
            "text_column": "english_text" if language.upper() == "EN" else "russian_text"
        }
    
    def get_video_paths_for_workflow(self, workflow_part: str) -> List[str]:
        """Get video paths for specific workflow parts to ensure proper list format"""
        if workflow_part == "intro":
            return list(self.intro_paths["video_paths"])  # Ensure it's a list
        elif workflow_part == "tail":
            return list(self.tail_paths["video_paths"])   # Ensure it's a list
        elif workflow_part == "current":
            return list(self.current_paths["video_paths"]) # Ensure it's a list
        elif workflow_part == "combined":
            # Return combined list for main + tail workflow
            return list(self.current_paths["video_paths"]) + list(self.tail_paths["video_paths"])
        else:
            return []
    
    def get_required_directories(self) -> list:
        """Get list of all required directories for validation"""
        return [
            self.BASE_DIRECTORY_GREECE_COMMON_ARTIFACTS,
            self.INTRO_BASE,
            self.TAIL_BASE,
            self.current_artifacts,
            self.current_result,
            self.current_final,
            self.TT_DIRECTORY
        ]
    
    def create_all_directories(self):
        """Create all required directories"""
        for directory in self.get_required_directories():
            os.makedirs(directory, exist_ok=True)
        print("✅ All directories created/verified")
    
    def validate_directories(self) -> bool:
        """Validate that all required directories exist"""
        missing = []
        for directory in self.get_required_directories():
            if not os.path.exists(directory):
                missing.append(directory)
        
        if missing:
            print("❌ Missing directories:")
            for dir_path in missing:
                friendly_name = dir_path.replace(self.BASE_DIRECTORY, "Files for SocialVideoBot")
                print(f"   📂 {friendly_name}")
            return False
        
        print("✅ All required directories found!")
        return True

# Factory functions for easy initialization
def get_local_config() -> VideoConfig:
    """Get configuration for local development"""
    return VideoConfig(environment="local")

def get_colab_config(base_path: str = None) -> VideoConfig:
    """Get configuration for Google Colab"""
    return VideoConfig(base_path=base_path, environment="colab")