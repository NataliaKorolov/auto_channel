from video_common import CreateAudioFile, CreateVideoFile, ConcatenateAudioFiles, ConcatenateVideoFiles
from config import get_local_config, VideoConfig
import os

# Initialize configuration
config = get_local_config()

def create_complete_video_for_greece(language: str, orientation: str, cleanup_intermediate: bool = False, build_all: bool = True, video_config: VideoConfig = None):
    """
    Creates a complete video with intro, main content, and tail for the specified language and orientation.
    
    Args:
        language: Language code ("EN" or "RU")
        orientation: Video orientation ("horizontal" or "vertical")
        cleanup_intermediate: Whether to clean up intermediate files to save storage
        build_all: If False, skips intro/tail creation and uses existing files
        video_config: VideoConfig instance (uses global config if None)
        
    Returns:
        str: Path to final video if successful, None if failed
    """
    
    if video_config is None:
        video_config = config
    
    print(f"\n🎬 Creating {language} {orientation} video")
    print("=" * 50)
    
    # Get paths for this specific language/orientation
    paths = video_config.get_greece_paths_for_language_orientation(language, orientation)
    
    # Track intermediate files for cleanup
    intermediate_files = [
        paths["intro_audio"],
        paths["tail_audio"], 
        paths["audio_with_tail"],
        paths["intro_video"],
        paths["main_tail_video"]
    ]
    
    try:
        # Define dimensions based on orientation
        if orientation == "horizontal":
            size = (1920, 1080)
            resize_dim = "width"
        else:  # vertical
            size = (1080, 1920)
            resize_dim = "height"
        
        if build_all:
            # Step 1: Create intro audio
            print(f"Step 1/6: 🎵 Creating intro audio...")
            try:
                CreateAudioFile(
                    output_file=paths["intro_audio"],
                    music_overlay_path=video_config.intro_paths["music"],
                    text_audio_overlay_path=paths["intro_text_audio"],
                    set_duration_by_text_audio=True,
                    time_of_music_before_voice=0.2,
                    time_of_music_after_voice=1.5
                )
                
                if not os.path.exists(paths["intro_audio"]):
                    raise FileNotFoundError(f"Failed to create intro audio: {paths['intro_audio']}")
                    
                print(f"✅ Step 1 completed: {os.path.basename(paths['intro_audio'])}")
                
            except Exception as e:
                print(f"❌ Step 1 failed: {e}")
                raise RuntimeError(f"Intro audio creation failed: {e}")
            
            # Step 2: Create intro video
            print(f"Step 2/6: 🎬 Creating intro video...")
            try:
                CreateVideoFile(
                    output_file=paths["intro_video"],
                    size=size,
                    resize_dim=resize_dim,
                    audio_path=paths["intro_audio"],
                    csv_path=video_config.intro_paths["text_overlay_csv"],
                    text_column=paths["text_column"],
                    video_paths=video_config.get_video_paths_for_workflow("intro"),  # Fixed: use method to ensure list
                    use_audio_duration=False
                )
                
                if not os.path.exists(paths["intro_video"]):
                    raise FileNotFoundError(f"Failed to create intro video: {paths['intro_video']}")
                    
                print(f"✅ Step 2 completed: {os.path.basename(paths['intro_video'])}")
                
            except Exception as e:
                print(f"❌ Step 2 failed: {e}")
                raise RuntimeError(f"Intro video creation failed: {e}")
            
            # Step 3: Create tail audio
            print(f"Step 3/6: 🎵 Creating tail audio...")
            try:
                CreateAudioFile(
                    output_file=paths["tail_audio"],
                    music_overlay_path=video_config.tail_paths["music"],
                    text_audio_overlay_path=paths["tail_text_audio"],
                    set_duration_by_text_audio=True,
                    time_of_music_before_voice=2,
                    time_of_music_after_voice=2
                )
                
                if not os.path.exists(paths["tail_audio"]):
                    raise FileNotFoundError(f"Failed to create tail audio: {paths['tail_audio']}")
                    
                print(f"✅ Step 3 completed: {os.path.basename(paths['tail_audio'])}")
                
            except Exception as e:
                print(f"❌ Step 3 failed: {e}")
                raise RuntimeError(f"Tail audio creation failed: {e}")
        else:
            # Validate existing files
            print("⏸️ Skipping steps 1-3 (build_all=False). Checking for existing files...")
            
            missing_files = []
            required_files = [
                ("Intro audio", paths["intro_audio"]),
                ("Intro video", paths["intro_video"]),
                ("Tail audio", paths["tail_audio"])
            ]
            
            for name, path in required_files:
                if not os.path.exists(path):
                    missing_files.append(f"{name}: {path}")
                    
            if missing_files:
                print("❌ Missing required files:")
                for missing in missing_files:
                    print(f"   - {missing}")
                raise FileNotFoundError("Cannot proceed without existing intro/tail files when build_all=False")
            else:
                print("✅ All required intro/tail files found")
        
        # Step 4: Combine main and tail audio
        print(f"Step 4/6: 🔗 Combining main and tail audio...")
        try:
            success = ConcatenateAudioFiles(
                audio_paths=[paths["main_audio"], paths["tail_audio"]],
                output_file=paths["audio_with_tail"],
                silence_between=0.5
            )
            
            if not success or not os.path.exists(paths["audio_with_tail"]):
                raise FileNotFoundError(f"Failed to combine audio: {paths['audio_with_tail']}")
                
            print(f"✅ Step 4 completed: {os.path.basename(paths['audio_with_tail'])}")
            
        except Exception as e:
            print(f"❌ Step 4 failed: {e}")
            raise RuntimeError(f"Audio combination failed: {e}")
        
        # Step 5: Create main+tail video
        print(f"Step 5/6: 🎬 Creating main+tail video...")
        try:
            CreateVideoFile(
                output_file=paths["main_tail_video"],
                size=size,
                resize_dim=resize_dim,
                audio_path=paths["audio_with_tail"],
                csv_path=[video_config.current_paths["csv"], video_config.tail_paths["text_overlay_csv"]],
                text_column=paths["text_column"],
                video_paths=video_config.get_video_paths_for_workflow("combined"),  # Fixed: use method to ensure list
                use_audio_duration=True
            )
            
            if not os.path.exists(paths["main_tail_video"]):
                raise FileNotFoundError(f"Failed to create main+tail video: {paths['main_tail_video']}")
                
            print(f"✅ Step 5 completed: {os.path.basename(paths['main_tail_video'])}")
            
        except Exception as e:
            print(f"❌ Step 5 failed: {e}")
            raise RuntimeError(f"Main+tail video creation failed: {e}")
        
        # Step 6: Concatenate intro with main+tail
        print(f"Step 6/6: 🔗 Creating final combined video...")
        try:
            success = ConcatenateVideoFiles(
                video_paths=[paths["intro_video"], paths["main_tail_video"]],
                output_file=paths["final_video"]
            )
            
            if not success or not os.path.exists(paths["final_video"]):
                raise FileNotFoundError(f"Failed to create final video: {paths['final_video']}")
                
            print(f"🎉 SUCCESS: Final video created: {os.path.basename(paths['final_video'])}")
            
        except Exception as e:
            print(f"❌ Step 6 failed: {e}")
            raise RuntimeError(f"Final video creation failed: {e}")
        
        # Optional cleanup for storage management
        if cleanup_intermediate:
            print(f"🧹 Cleaning up intermediate files...")
            cleanup_count = 0
            for file_path in intermediate_files:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        cleanup_count += 1
                        print(f"   ✓ Removed: {os.path.basename(file_path)}")
                except Exception as cleanup_error:
                    print(f"   ⚠️ Failed to remove {os.path.basename(file_path)}: {cleanup_error}")
            
            print(f"✅ Cleanup completed: {cleanup_count} files removed")
        
        print(f"✅ COMPLETED: {language} {orientation} video: {paths['final_video']}")
        return paths["final_video"]
        
    except Exception as e:
        print(f"❌ FAILED: {language} {orientation} video creation failed: {e}")
        
        # Clean up intermediate files on failure
        print(f"🧹 Cleaning up due to failure...")
        cleanup_count = 0
        for file_path in intermediate_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    cleanup_count += 1
            except:
                pass
        
        if cleanup_count > 0:
            print(f"✅ Cleaned up {cleanup_count} intermediate files")
        
        return None

def check_greece_workflow_directories(video_config: VideoConfig = None) -> bool:
    """Check if all required Greece workflow directories exist."""
    if video_config is None:
        video_config = config
    
    return video_config.validate_directories()

if __name__ == "__main__":
    # Check directories before running workflow
    if check_greece_workflow_directories():
        build_all = True 
        
        # Create all four video variants using the centralized config
        create_complete_video_for_greece(language="EN", orientation="horizontal", cleanup_intermediate=False, build_all=build_all, video_config = None) 
        # create_complete_video_for_greece(language="RU", orientation="horizontal", cleanup_intermediate=False, build_all=build_all) 
        # create_complete_video_for_greece(language="EN", orientation="vertical", cleanup_intermediate=False, build_all=build_all) 
        # create_complete_video_for_greece(language="RU", orientation="vertical", cleanup_intermediate=False, build_all=build_all) 
    else:
        print("⏸️  Greece workflow stopped due to missing directories.")

