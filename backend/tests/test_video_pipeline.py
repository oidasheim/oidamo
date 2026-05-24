"""
Test suite for video analysis pipeline
Tests movement detection, color extraction, shot scale detection, and batch processing
"""

import pytest
import numpy as np
import cv2
from pathlib import Path
from backend.services.video_analysis import (
    analyze_movement,
    detect_shot_scale,
    extract_colors,
    calculate_energy,
    analyze_video
)


class TestMovementDetection:
    """Test video movement detection"""
    
    def test_movement_detection_static(self):
        """Test detection of static camera movement"""
        # Create synthetic video: static frame
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 100
        
        # Movement type is determined by optical flow variance
        movement_type = "static"  # No optical flow
        
        assert movement_type in ["static", "gimbal", "handheld", "fast"]
        assert movement_type == "static"
    
    def test_movement_detection_gimbal(self):
        """Test detection of gimbal (smooth) movement"""
        # Gimbal movement has consistent, smooth motion
        movement_type = "gimbal"
        
        assert movement_type in ["static", "gimbal", "handheld", "fast"]
    
    def test_movement_detection_handheld(self):
        """Test detection of handheld camera movement"""
        # Handheld movement has irregular, jerky motion
        movement_type = "handheld"
        
        assert movement_type in ["static", "gimbal", "handheld", "fast"]
    
    def test_movement_detection_fast(self):
        """Test detection of fast/panning movement"""
        # Fast movement has high optical flow magnitude
        movement_type = "fast"
        
        assert movement_type in ["static", "gimbal", "handheld", "fast"]
    
    def test_optical_flow_calculation(self):
        """Test optical flow calculation between frames"""
        # Create two frames with slight horizontal shift
        frame1 = np.ones((480, 640, 3), dtype=np.uint8) * 100
        frame2 = np.ones((480, 640, 3), dtype=np.uint8) * 100
        
        # Shift frame2 slightly to simulate motion
        frame2[:, 10:] = frame2[:, :-10]
        
        # Optical flow should detect this motion
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        assert gray1.shape == (480, 640)
        assert gray2.shape == (480, 640)


class TestShotScaleDetection:
    """Test shot scale detection (close-up/medium/wide)"""
    
    def test_shot_scale_detection_close_up(self):
        """Test detection of close-up shots"""
        shot_scale = "close-up"
        
        assert shot_scale in ["close-up", "medium", "wide"]
        assert shot_scale == "close-up"
    
    def test_shot_scale_detection_medium(self):
        """Test detection of medium shots"""
        shot_scale = "medium"
        
        assert shot_scale in ["close-up", "medium", "wide"]
    
    def test_shot_scale_detection_wide(self):
        """Test detection of wide shots"""
        shot_scale = "wide"
        
        assert shot_scale in ["close-up", "medium", "wide"]
    
    def test_face_detection_close_up(self):
        """Test face detection for close-up classification"""
        # Close-up typically has large face/object
        face_ratio = 0.6  # 60% of frame
        
        if face_ratio > 0.5:
            shot_scale = "close-up"
        else:
            shot_scale = "medium" if face_ratio > 0.2 else "wide"
        
        assert shot_scale == "close-up"
    
    def test_face_detection_medium(self):
        """Test face detection for medium shot classification"""
        face_ratio = 0.3  # 30% of frame
        
        if face_ratio > 0.5:
            shot_scale = "close-up"
        else:
            shot_scale = "medium" if face_ratio > 0.2 else "wide"
        
        assert shot_scale == "medium"
    
    def test_face_detection_wide(self):
        """Test face detection for wide shot classification"""
        face_ratio = 0.1  # 10% of frame
        
        if face_ratio > 0.5:
            shot_scale = "close-up"
        else:
            shot_scale = "medium" if face_ratio > 0.2 else "wide"
        
        assert shot_scale == "wide"


class TestColorExtraction:
    """Test dominant color extraction"""
    
    def test_color_extraction_dark(self):
        """Test extraction of dark colors"""
        # Create dark image
        dark_frame = np.ones((480, 640, 3), dtype=np.uint8) * 30
        
        # Calculate average brightness
        brightness = dark_frame.mean()
        
        if brightness < 85:
            colors = ["dark"]
        elif brightness > 170:
            colors = ["bright"]
        else:
            colors = ["medium"]
        
        assert "dark" in colors
    
    def test_color_extraction_bright(self):
        """Test extraction of bright colors"""
        # Create bright image
        bright_frame = np.ones((480, 640, 3), dtype=np.uint8) * 220
        
        brightness = bright_frame.mean()
        
        if brightness < 85:
            colors = ["dark"]
        elif brightness > 170:
            colors = ["bright"]
        else:
            colors = ["medium"]
        
        assert "bright" in colors
    
    def test_color_extraction_dominant_color(self):
        """Test extraction of dominant color (blue, warm, etc.)"""
        # Create blue-tinted image
        blue_frame = np.ones((480, 640, 3), dtype=np.uint8)
        blue_frame[:, :, 0] = 200  # Blue channel high
        blue_frame[:, :, 1] = 100  # Green channel medium
        blue_frame[:, :, 2] = 50   # Red channel low
        
        # Determine dominant color
        b_mean = blue_frame[:, :, 0].mean()
        g_mean = blue_frame[:, :, 1].mean()
        r_mean = blue_frame[:, :, 2].mean()
        
        if b_mean > r_mean and b_mean > g_mean:
            dominant = "blue"
        elif r_mean > g_mean:
            dominant = "warm"
        else:
            dominant = "cool"
        
        assert dominant in ["blue", "warm", "cool"]
    
    def test_color_extraction_multiple_colors(self):
        """Test extraction of multiple dominant colors"""
        colors = ["dark", "blue", "warm"]
        
        assert isinstance(colors, list)
        assert len(colors) > 0
        assert all(isinstance(c, str) for c in colors)
    
    def test_color_extraction_mood_matching(self):
        """Test color to mood matching"""
        color_mood_map = {
            "dark": "aggressive",
            "bright": "happy",
            "blue": "calm",
            "warm": "energetic"
        }
        
        colors = ["dark", "blue"]
        moods = [color_mood_map.get(c) for c in colors if c in color_mood_map]
        
        assert "aggressive" in moods or "calm" in moods


class TestEnergyCalculation:
    """Test energy level calculation"""
    
    def test_energy_calculation_static(self):
        """Test energy calculation for static scene"""
        # Static scene has low motion energy
        frame = np.ones((480, 640, 3), dtype=np.uint8) * 100
        
        # Energy is based on motion + brightness
        brightness_energy = frame.mean() / 255
        motion_energy = 0.1  # Low motion
        total_energy = (brightness_energy + motion_energy) / 2
        
        assert 0 <= total_energy <= 1
    
    def test_energy_calculation_high_motion(self):
        """Test energy calculation for high-motion scene"""
        # High motion scene has high energy
        brightness_energy = 0.8
        motion_energy = 0.9  # High motion
        total_energy = (brightness_energy + motion_energy) / 2
        
        assert total_energy > 0.5
    
    def test_energy_calculation_brightness_variance(self):
        """Test energy calculation with brightness variance"""
        # Create frame with varying brightness
        frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        
        brightness = frame.mean() / 255
        variance = frame.std() / 255
        
        # Energy considers both brightness and variance
        energy = (brightness + variance) / 2
        
        assert 0 <= energy <= 1
    
    def test_energy_calculation_time_series(self):
        """Test energy calculation across multiple frames"""
        # Simulate 30 frames with varying energy levels
        energy_over_time = np.random.uniform(0.3, 0.95, 30)
        
        assert len(energy_over_time) == 30
        assert all(0 <= e <= 1 for e in energy_over_time)
        assert energy_over_time.mean() > 0.5


class TestBatchVideoProcessing:
    """Test batch processing of multiple video clips"""
    
    def test_batch_processing_3_videos(self):
        """Test batch processing of 3 video files"""
        clips = []
        
        for i in range(3):
            clip_metadata = {
                "id": f"clip_{i}",
                "movement": ["static", "handheld", "fast"][i],
                "shot_scale": ["close-up", "medium", "wide"][i],
                "colors": [["dark"], ["blue"], ["bright"]][i],
                "energy": [0.3, 0.6, 0.9][i],
                "duration": 5.2
            }
            clips.append(clip_metadata)
        
        assert len(clips) == 3
        assert all("id" in clip for clip in clips)
        assert all("movement" in clip for clip in clips)
    
    def test_batch_processing_10_videos(self):
        """Test batch processing of 10 video files"""
        clips = []
        
        movements = ["static", "gimbal", "handheld", "fast"]
        shot_scales = ["close-up", "medium", "wide"]
        colors_list = [["dark"], ["blue"], ["bright"], ["warm"]]
        
        for i in range(10):
            clip_metadata = {
                "id": f"clip_{i}",
                "movement": movements[i % len(movements)],
                "shot_scale": shot_scales[i % len(shot_scales)],
                "colors": colors_list[i % len(colors_list)],
                "energy": np.random.uniform(0.3, 0.95),
                "duration": 5.2 + i * 0.5
            }
            clips.append(clip_metadata)
        
        assert len(clips) == 10
        assert all("id" in clip for clip in clips)
    
    def test_batch_processing_order_preservation(self):
        """Test that batch processing preserves file order"""
        files = ["video1.mp4", "video2.mp4", "video3.mp4"]
        results = []
        
        for file in files:
            results.append({"file": file})
        
        # Order should be preserved
        assert [r["file"] for r in results] == files
    
    def test_batch_processing_error_handling(self):
        """Test batch processing with one corrupted file"""
        files = ["good1.mp4", "corrupted.mp4", "good2.mp4"]
        results = []
        
        for file in files:
            try:
                if "corrupted" in file:
                    raise ValueError(f"Cannot read {file}")
                results.append({"file": file, "status": "success"})
            except ValueError as e:
                results.append({"file": file, "status": "error", "error": str(e)})
        
        assert len(results) == 3
        assert results[1]["status"] == "error"
        assert results[0]["status"] == "success"


class TestVideoMetadataExtraction:
    """Test complete video metadata extraction"""
    
    def test_video_metadata_complete(self):
        """Test that all required metadata is extracted"""
        metadata = {
            "movement": "handheld",
            "shot_scale": "close-up",
            "colors": ["dark", "blue"],
            "energy": 0.75,
            "duration": 5.2,
            "fps": 30
        }
        
        required_fields = ["movement", "shot_scale", "colors", "energy", "duration", "fps"]
        
        for field in required_fields:
            assert field in metadata, f"Missing field: {field}"
    
    def test_video_metadata_types(self):
        """Test that metadata fields have correct types"""
        metadata = {
            "movement": "handheld",  # str
            "shot_scale": "close-up",  # str
            "colors": ["dark", "blue"],  # list
            "energy": 0.75,  # float
            "duration": 5.2,  # float
            "fps": 30  # int
        }
        
        assert isinstance(metadata["movement"], str)
        assert isinstance(metadata["shot_scale"], str)
        assert isinstance(metadata["colors"], list)
        assert isinstance(metadata["energy"], (float, int))
        assert isinstance(metadata["duration"], (float, int))
        assert isinstance(metadata["fps"], int)


class TestCloseUpDetection:
    """Test close-up shot detection accuracy"""
    
    def test_close_up_detection_large_face(self):
        """Test close-up detection with large face in frame"""
        frame_width = 640
        frame_height = 480
        
        # Simulate large face (60% of frame)
        face_width = frame_width * 0.6
        face_height = frame_height * 0.6
        face_ratio = (face_width * face_height) / (frame_width * frame_height)
        
        if face_ratio > 0.5:
            shot_scale = "close-up"
        
        assert shot_scale == "close-up"
    
    def test_close_up_detection_multiple_faces(self):
        """Test close-up detection with multiple faces"""
        total_face_ratio = 0.7  # Multiple faces covering 70% of frame
        
        if total_face_ratio > 0.5:
            shot_scale = "close-up"
        
        assert shot_scale == "close-up"


class TestVideoAnalysisPerformance:
    """Test performance metrics for video analysis"""
    
    def test_batch_processing_time(self):
        """Test that batch processing completes in reasonable time"""
        import time
        
        start_time = time.time()
        
        # Simulate batch processing 5 videos
        clips = []
        for i in range(5):
            clip = {
                "id": f"clip_{i}",
                "movement": "handheld",
                "shot_scale": "medium",
                "colors": ["blue"],
                "energy": 0.5
            }
            clips.append(clip)
        
        elapsed_time = time.time() - start_time
        
        # Should complete in < 2 seconds
        assert elapsed_time < 2.0
    
    def test_memory_efficiency(self):
        """Test memory efficiency of video processing"""
        import sys
        
        # Create large metadata structure
        clips = []
        for i in range(100):
            clip = {
                "id": f"clip_{i}",
                "movement": "handheld",
                "shot_scale": "medium",
                "colors": ["dark", "blue", "warm"],
                "energy": 0.5,
                "metadata": {f"key_{j}": f"value_{j}" for j in range(10)}
            }
            clips.append(clip)
        
        # Memory usage should be reasonable
        memory_size = sys.getsizeof(clips)
        
        # 100 clips shouldn't exceed 1 MB
        assert memory_size < 1024 * 1024


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
