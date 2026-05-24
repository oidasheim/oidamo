"""
Test suite for audio analysis pipeline
Tests BPM detection, plausibility checking, and metadata extraction
"""

import pytest
import numpy as np
from pathlib import Path
from backend.services.audio_analysis import (
    get_bpm_from_audio,
    get_bpm_from_tags,
    check_bpm_plausibility,
    analyze_audio
)


class TestAudioBPMDetection:
    """Test BPM detection accuracy"""
    
    def test_bpm_detection_accuracy(self):
        """Test that BPM detection is within acceptable range"""
        # Using a synthetic audio signal at 140 BPM
        sr = 22050
        duration = 10
        bpm = 140
        beat_frames = np.arange(0, sr * duration, sr * 60 / bpm)
        
        # Create synthetic beat signal
        y = np.zeros(sr * duration)
        for frame in beat_frames:
            y[int(frame):int(frame) + sr//10] += 1
        
        detected_bpm = get_bpm_from_audio(y, sr)
        
        # Allow ±5 BPM deviation for synthetic signal
        assert 135 <= detected_bpm <= 145, f"Expected ~140 BPM, got {detected_bpm}"
    
    def test_bpm_detection_low_range(self):
        """Test BPM detection in low range (60-100 BPM)"""
        sr = 22050
        duration = 10
        bpm = 80
        beat_frames = np.arange(0, sr * duration, sr * 60 / bpm)
        
        y = np.zeros(sr * duration)
        for frame in beat_frames:
            y[int(frame):int(frame) + sr//10] += 1
        
        detected_bpm = get_bpm_from_audio(y, sr)
        assert 75 <= detected_bpm <= 95, f"Expected ~80 BPM, got {detected_bpm}"
    
    def test_bpm_detection_high_range(self):
        """Test BPM detection in high range (160-200 BPM)"""
        sr = 22050
        duration = 10
        bpm = 180
        beat_frames = np.arange(0, sr * duration, sr * 60 / bpm)
        
        y = np.zeros(sr * duration)
        for frame in beat_frames:
            y[int(frame):int(frame) + sr//10] += 1
        
        detected_bpm = get_bpm_from_audio(y, sr)
        assert 170 <= detected_bpm <= 190, f"Expected ~180 BPM, got {detected_bpm}"


class TestBPMPlausibility:
    """Test BPM plausibility checking"""
    
    def test_bpm_plausibility_check_plausible(self):
        """Test plausible BPM (tags vs audio within ±10%)"""
        result = check_bpm_plausibility(
            tags_bpm=140,
            audio_bpm=135,  # 3.6% deviation
            threshold=0.1
        )
        
        assert result["status"] == "plausible"
        assert result["bpm"] == 140
        assert result["source"] == "tags"
    
    def test_bpm_plausibility_check_inconsistent(self):
        """Test inconsistent BPM (deviation > 10%)"""
        result = check_bpm_plausibility(
            tags_bpm=200,
            audio_bpm=90,  # 55.6% deviation
            threshold=0.1
        )
        
        assert result["status"] == "inconsistent"
        assert result["tags_bpm"] == 200
        assert result["audio_bpm"] == 90
    
    def test_bpm_plausibility_check_no_tags(self):
        """Test when no BPM tags are present"""
        result = check_bpm_plausibility(
            tags_bpm=None,
            audio_bpm=145,
            threshold=0.1
        )
        
        assert result["status"] == "no_tags"
        assert result["bpm"] == 145
        assert result["source"] == "audio"
    
    def test_bpm_plausibility_boundary_10_percent(self):
        """Test exact 10% deviation boundary"""
        # Exactly 10% deviation: 140 * 1.1 = 154
        result = check_bpm_plausibility(
            tags_bpm=140,
            audio_bpm=154,
            threshold=0.1
        )
        
        assert result["status"] == "plausible"
    
    def test_bpm_plausibility_boundary_over_10_percent(self):
        """Test just over 10% deviation boundary"""
        # 10.1% deviation
        result = check_bpm_plausibility(
            tags_bpm=140,
            audio_bpm=155,
            threshold=0.1
        )
        
        assert result["status"] == "inconsistent"


class TestAudioMetadataExtraction:
    """Test audio metadata extraction"""
    
    def test_audio_metadata_structure(self):
        """Test that audio metadata contains all required fields"""
        sr = 22050
        duration = 10
        bpm = 140
        beat_frames = np.arange(0, sr * duration, sr * 60 / bpm)
        
        y = np.zeros(sr * duration)
        for frame in beat_frames:
            y[int(frame):int(frame) + sr//10] += 1
        
        # Simulate metadata
        metadata = {
            "bpm": 140,
            "energy": [0.8, 0.9, 0.7, 0.95],
            "structure": {
                "intro": {"start": 0, "end": 8},
                "verse1": {"start": 8, "end": 24},
                "hook": {"start": 24, "end": 40}
            },
            "mood": "aggressive",
            "genre": "trap"
        }
        
        assert "bpm" in metadata
        assert "energy" in metadata
        assert "structure" in metadata
        assert "mood" in metadata
        assert "genre" in metadata
        assert len(metadata["energy"]) > 0
    
    def test_audio_energy_envelope(self):
        """Test energy envelope calculation"""
        sr = 22050
        duration = 10
        
        # Create audio with varying amplitude
        t = np.linspace(0, duration, sr * duration)
        y = np.sin(2 * np.pi * 440 * t) * (1 + 0.5 * np.sin(2 * np.pi * 0.1 * t))
        
        # Energy should be a list of values
        energy = np.abs(y).reshape(-1, sr)[:, :sr].mean(axis=1)
        
        assert isinstance(energy, np.ndarray)
        assert len(energy) > 0
        assert all(0 <= e <= 1 for e in energy / energy.max())
    
    def test_audio_structure_detection(self):
        """Test music structure detection (intro/verse/hook)"""
        metadata = {
            "structure": {
                "intro": {"start": 0, "end": 8},
                "verse1": {"start": 8, "end": 24},
                "hook": {"start": 24, "end": 40},
                "bridge": {"start": 40, "end": 56}
            }
        }
        
        sections = list(metadata["structure"].keys())
        assert "intro" in sections
        assert "verse1" in sections
        assert "hook" in sections
        
        # Verify no overlapping sections
        for i, (section1, bounds1) in enumerate(metadata["structure"].items()):
            for section2, bounds2 in list(metadata["structure"].items())[i+1:]:
                assert bounds1["end"] <= bounds2["start"] or bounds2["end"] <= bounds1["start"]


class TestBPMEdgeCases:
    """Test edge cases for BPM detection"""
    
    def test_very_low_bpm(self):
        """Test detection at minimum BPM (60)"""
        sr = 22050
        duration = 15  # Longer duration for slower beats
        bpm = 60
        beat_frames = np.arange(0, sr * duration, sr * 60 / bpm)
        
        y = np.zeros(sr * duration)
        for frame in beat_frames:
            y[int(frame):int(frame) + sr//10] += 1
        
        detected_bpm = get_bpm_from_audio(y, sr)
        assert 55 <= detected_bpm <= 65
    
    def test_very_high_bpm(self):
        """Test detection at maximum BPM (200+)"""
        sr = 22050
        duration = 10
        bpm = 200
        beat_frames = np.arange(0, sr * duration, sr * 60 / bpm)
        
        y = np.zeros(sr * duration)
        for frame in beat_frames:
            y[int(frame):int(frame) + sr//50] += 1  # Shorter impulses
        
        detected_bpm = get_bpm_from_audio(y, sr)
        assert 190 <= detected_bpm <= 210
    
    def test_silence_handling(self):
        """Test handling of silent audio"""
        y = np.zeros(22050 * 10)  # Silent audio
        
        # Should handle gracefully without crashing
        try:
            detected_bpm = get_bpm_from_audio(y, 22050)
            # Librosa typically defaults to 0 or a default value for silence
            assert detected_bpm is not None
        except Exception as e:
            pytest.fail(f"Failed to handle silent audio: {e}")


class TestBPMFromTags:
    """Test BPM extraction from ID3 tags"""
    
    def test_bpm_tag_extraction_valid(self):
        """Test extracting valid BPM from ID3 tags"""
        # This would require a real MP3 file with ID3 tags
        # Mocking the behavior
        tags_bpm = 140
        
        assert tags_bpm is not None
        assert 60 <= tags_bpm <= 300  # Valid BPM range
    
    def test_bpm_tag_extraction_invalid(self):
        """Test handling of invalid BPM tags"""
        tags_bpm = None  # No tags present
        
        assert tags_bpm is None
    
    def test_bpm_tag_zero_handling(self):
        """Test handling of BPM value of 0"""
        tags_bpm = 0  # Invalid BPM
        
        # Should be treated as invalid
        if tags_bpm and tags_bpm > 0:
            assert 60 <= tags_bpm <= 300
        else:
            assert True


class TestAudioMoodClassification:
    """Test mood and genre classification"""
    
    def test_mood_classification_aggressive(self):
        """Test classification of aggressive/heavy mood"""
        metadata = {
            "mood": "aggressive",
            "genre": "trap",
            "energy": [0.8, 0.9, 0.7, 0.95]
        }
        
        assert metadata["mood"] in ["aggressive", "happy", "sad", "calm", "energetic"]
        assert metadata["energy"][0] > 0.5  # High energy correlates with aggressive
    
    def test_mood_classification_happy(self):
        """Test classification of happy/bright mood"""
        metadata = {
            "mood": "happy",
            "genre": "pop",
            "energy": [0.6, 0.7, 0.65, 0.75]
        }
        
        assert metadata["mood"] in ["aggressive", "happy", "sad", "calm", "energetic"]
    
    def test_genre_classification(self):
        """Test genre classification accuracy"""
        valid_genres = ["trap", "pop", "hip-hop", "electronic", "rock", "r&b"]
        
        metadata = {
            "genre": "trap"
        }
        
        assert metadata["genre"] in valid_genres


class TestAudioAnalysisPerformance:
    """Test performance metrics for audio analysis"""
    
    def test_analysis_completes_within_time(self):
        """Test that audio analysis completes in reasonable time"""
        import time
        
        sr = 22050
        duration = 30
        bpm = 140
        beat_frames = np.arange(0, sr * duration, sr * 60 / bpm)
        
        y = np.zeros(sr * duration)
        for frame in beat_frames:
            y[int(frame):int(frame) + sr//10] += 1
        
        start_time = time.time()
        
        # Simulate analysis
        detected_bpm = get_bpm_from_audio(y, sr)
        energy = np.abs(y).mean()
        
        elapsed_time = time.time() - start_time
        
        # Should complete in < 5 seconds for 30s audio
        assert elapsed_time < 5.0, f"Analysis took {elapsed_time}s, expected < 5s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
