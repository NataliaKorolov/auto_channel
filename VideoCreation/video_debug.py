import os
import cv2
from typing import Optional, List

def GetVideoInfo(video_path: str) -> Optional[dict]:
    """
    Get basic information about a video file.
    Args:
        video_path: Path to the video file
    Returns:
        dict: Video information including size, duration, fps
        None: If video cannot be read
    """
    if not os.path.exists(video_path):
        return None
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        cap.release()
        return {
            'width': width,
            'height': height,
            'size': (width, height),
            'fps': fps,
            'frame_count': frame_count,
            'duration': duration,
            'filename': os.path.basename(video_path)
        }
    except Exception as e:
        print(f"Error getting video info for {video_path}: {str(e)}")
        return None

def dump_clip_info(clip, clip_name: str = "Clip") -> dict:
    """
    Dump comprehensive information about a MoviePy clip for debugging purposes.
    Args:
        clip: MoviePy clip object (VideoClip, AudioClip, CompositeVideoClip, etc.)
        clip_name: Name/identifier for the clip (for logging purposes)
    Returns:
        dict: Dictionary containing all available clip information
    """
    info = {
        "clip_name": clip_name,
        "clip_type": type(clip).__name__,
        "is_none": clip is None
    }
    if clip is None:
        print(f"{clip_name}: CLIP IS NONE!")
        return info
    try:
        info["has_duration"] = hasattr(clip, 'duration')
        if hasattr(clip, 'duration'):
            try:
                info["duration"] = clip.duration
                info["duration_valid"] = info["duration"] is not None and info["duration"] > 0
            except Exception as e:
                info["duration_error"] = str(e)
        if hasattr(clip, 'size'):
            try:
                info["size"] = clip.size
                info["width"] = clip.w if hasattr(clip, 'w') else None
                info["height"] = clip.h if hasattr(clip, 'h') else None
            except Exception as e:
                info["size_error"] = str(e)
        if hasattr(clip, 'fps'):
            try:
                info["fps"] = clip.fps
            except Exception as e:
                info["fps_error"] = str(e)
        if hasattr(clip, 'audio'):
            try:
                info["has_audio"] = clip.audio is not None
                if clip.audio:
                    info["audio_duration"] = getattr(clip.audio, 'duration', None)
            except Exception as e:
                info["audio_error"] = str(e)
        if hasattr(clip, 'start'):
            try:
                info["start"] = clip.start
            except Exception as e:
                info["start_error"] = str(e)
        if hasattr(clip, 'end'):
            try:
                info["end"] = clip.end
            except Exception as e:
                info["end_error"] = str(e)
        if hasattr(clip, 'mask'):
            try:
                info["has_mask"] = clip.mask is not None
            except Exception as e:
                info["mask_error"] = str(e)
        if hasattr(clip, 'clips'):
            try:
                info["num_clips"] = len(clip.clips) if clip.clips else 0
                info["clips_info"] = []
                if clip.clips:
                    for i, subclip in enumerate(clip.clips):
                        subinfo = {
                            "index": i,
                            "type": type(subclip).__name__,
                            "duration": getattr(subclip, 'duration', None),
                            "size": getattr(subclip, 'size', None),
                            "start": getattr(subclip, 'start', None)
                        }
                        info["clips_info"].append(subinfo)
            except Exception as e:
                info["clips_error"] = str(e)
        if hasattr(clip, 'get_frame'):
            try:
                test_frame = clip.get_frame(0)
                info["can_get_frame"] = True
                info["frame_shape"] = test_frame.shape if hasattr(test_frame, 'shape') else None
            except Exception as e:
                info["can_get_frame"] = False
                info["get_frame_error"] = str(e)
        if hasattr(clip, 'filename'):
            info["filename"] = getattr(clip, 'filename', None)
        print(f"\n=== {clip_name} Information ===")
        print(f"Type: {info['clip_type']}")
        if info.get('duration'):
            print(f"Duration: {info['duration']:.2f}s")
        elif 'duration_error' in info:
            print(f"Duration Error: {info['duration_error']}")
        if info.get('size'):
            print(f"Size: {info['size']} (W:{info.get('width')}, H:{info.get('height')})")
        elif 'size_error' in info:
            print(f"Size Error: {info['size_error']}")
        if info.get('fps'):
            print(f"FPS: {info['fps']}")
        if 'has_audio' in info:
            print(f"Has Audio: {info['has_audio']}")
            if info.get('audio_duration'):
                print(f"Audio Duration: {info['audio_duration']:.2f}s")
        if 'num_clips' in info:
            print(f"Number of subclips: {info['num_clips']}")
        if 'can_get_frame' in info:
            print(f"Can get frame: {info['can_get_frame']}")
            if info.get('frame_shape'):
                print(f"Frame shape: {info['frame_shape']}")
            elif 'get_frame_error' in info:
                print(f"Get frame error: {info['get_frame_error']}")
        errors = [k for k in info.keys() if k.endswith('_error')]
        if errors:
            print("Errors found:")
            for error_key in errors:
                print(f"  {error_key}: {info[error_key]}")
        print("=" * (len(clip_name) + 20))
    except Exception as e:
        info["general_error"] = str(e)
        print(f"Error analyzing {clip_name}: {str(e)}")
    return info

def compare_clips_info(clips: List, clip_names: List[str]) -> dict:
    """
    Compare comprehensive information between multiple MoviePy clips and highlight differences.
    Args:
        clips: List of MoviePy clip objects to compare
        clip_names: List of names/identifiers for the clips (must match length of clips)
    Returns:
        dict: Dictionary containing comparison results and differences
    """
    if len(clips) != len(clip_names):
        raise ValueError(f"Number of clips ({len(clips)}) must match number of names ({len(clip_names)})")
    if len(clips) < 2:
        raise ValueError("At least 2 clips are required for comparison")
    all_info = []
    for clip, name in zip(clips, clip_names):
        info = dump_clip_info(clip, name)
        all_info.append(info)
    comparison = {
        "clip_names": clip_names,
        "individual_info": all_info,
        "differences": {},
        "similarities": {},
        "warnings": []
    }
    properties_to_compare = [
        'clip_type', 'is_none', 'duration', 'duration_valid', 'size', 'width', 'height', 
        'fps', 'has_audio', 'audio_duration', 'start', 'end', 'has_mask', 'num_clips',
        'can_get_frame', 'frame_shape'
    ]
    print(f"\n{'='*80}")
    print(f"COMPARING {len(clips)} CLIPS: {' vs '.join(clip_names)}")
    print(f"{'='*80}")
    for prop in properties_to_compare:
        values = [info.get(prop) for info in all_info]
        if all(val == values[0] for val in values):
            comparison["similarities"][prop] = values[0]
        else:
            comparison["differences"][prop] = dict(zip(clip_names, values))
            print(f"\n🔍 DIFFERENCE in {prop}:")
            for name, val in zip(clip_names, values):
                print(f"  {name}: {val}")
    print(f"\n{'='*50}")
    print("DETAILED ANALYSIS")
    print(f"{'='*50}")
    none_clips = [name for info, name in zip(all_info, clip_names) if info.get('is_none')]
    if none_clips:
        warning = f"⚠️  WARNING: These clips are None: {', '.join(none_clips)}"
        comparison["warnings"].append(warning)
        print(warning)
    durations = []
    for info, name in zip(all_info, clip_names):
        if info.get('duration') is not None:
            durations.append((name, info['duration']))
    if len(durations) > 1:
        print(f"\n📏 Duration Analysis:")
        durations.sort(key=lambda x: x[1])
        shortest = durations[0]
        longest = durations[-1]
        print(f"   Shortest: {shortest[0]} = {shortest[1]:.2f}s")
        print(f"   Longest:  {longest[0]} = {longest[1]:.2f}s")
        if longest[1] - shortest[1] > 0.1:
            warning = f"Duration mismatch: {longest[1] - shortest[1]:.2f}s difference"
            comparison["warnings"].append(warning)
            print(f"   ⚠️  {warning}")
        if len(durations) > 3:
            print(f"   All durations:")
            for name, duration in durations:
                print(f"     {name}: {duration:.2f}s")
    print(f"\n{'='*50}")
    print("COMPARISON SUMMARY")
    print(f"{'='*50}")
    print(f"Clips compared: {len(clips)}")
    print(f"Properties compared: {len(properties_to_compare)}")
    print(f"Similarities found: {len(comparison['similarities'])}")
    print(f"Differences found: {len(comparison['differences'])}")
    print(f"Warnings generated: {len(comparison['warnings'])}")
    return comparison
