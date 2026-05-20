"""
Export & Rendering Service
Implements FFmpeg integration for video rendering with effects, resolution options, and audio sync
"""

import subprocess
import os
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum
import json


class Resolution(str, Enum):
    """Supported video resolutions"""
    HD_720P = "720p"
    FULL_HD_1080P = "1080p"
    UHD_4K = "4K"


class VideoFormat(str, Enum):
    """Supported export formats"""
    MP4 = "mp4"
    MOV = "mov"
    WEBM = "webm"


RESOLUTION_SPECS = {
    Resolution.HD_720P: {"width": 1280, "height": 720, "bitrate": "4000k"},
    Resolution.FULL_HD_1080P: {"width": 1920, "height": 1080, "bitrate": "8000k"},
    Resolution.UHD_4K: {"width": 3840, "height": 2160, "bitrate": "16000k"},
}

CODEC_SPECS = {
    VideoFormat.MP4: {
        "video_codec": "libx264",
        "audio_codec": "aac",
        "extension": ".mp4",
    },
    VideoFormat.MOV: {
        "video_codec": "libx264",
        "audio_codec": "aac",
        "extension": ".mov",
    },
    VideoFormat.WEBM: {
        "video_codec": "libvpx-vp9",
        "audio_codec": "libopus",
        "extension": ".webm",
    },
}


class FFmpegExporter:
    """Handles FFmpeg-based video rendering and export"""

    def __init__(self, output_dir: str = "./exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_zoom_effect(
        self,
        clip_path: str,
        start_time: float,
        duration: float,
        intensity: float = 0.5,
    ) -> str:
        """
        Build FFmpeg zoom-in effect (e.g., for kicks/beats)

        Args:
            clip_path: Path to input video
            start_time: When to start effect (seconds)
            duration: Effect duration (seconds)
            intensity: Zoom intensity (0-1)

        Returns:
            FFmpeg filter string
        """
        # Scale intensity to zoom factor (1.0 = no zoom, 1.2 = 20% zoom)
        zoom_factor = 1.0 + (intensity * 0.2)

        # Create zoompan filter
        # zoompan=z='min(zoom+0.015,1.12)':d=43:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':fps=30
        filter_str = (
            f"zoompan=z='min(zoom+{intensity*0.015:.4f},{zoom_factor})'"
            f":d={int(duration*30)}"
            f":x='iw/2-(iw/zoom/2)'"
            f":y='ih/2-(ih/zoom/2)'"
            f":fps=30"
        )

        return filter_str

    def build_crossfade_transition(
        self,
        clip1_path: str,
        clip2_path: str,
        duration: float = 0.5,
    ) -> str:
        """
        Build FFmpeg crossfade/cut transition

        Args:
            clip1_path: Path to first video
            clip2_path: Path to second video
            duration: Transition duration (seconds)

        Returns:
            FFmpeg filter string
        """
        # xfade=transition=fade:duration=0.5:offset=8
        filter_str = (
            f"xfade=transition=fade"
            f":duration={duration}"
            f":offset={duration}"
        )

        return filter_str

    def build_color_shift_effect(
        self,
        clip_path: str,
        start_time: float,
        duration: float,
        intensity: float = 0.5,
    ) -> str:
        """
        Build FFmpeg color shift effect (mood-based coloring)

        Args:
            clip_path: Path to input video
            start_time: When to start effect
            duration: Effect duration
            intensity: Effect intensity (0-1)

        Returns:
            FFmpeg filter string
        """
        # Using colorize or hue shift
        # hue='H + 30' for hue shift
        # Using eq filter for color adjustment
        filter_str = (
            f"eq=saturation={0.5 + intensity}:"
            f"contrast=1.0:"
            f"brightness={-0.1 * intensity}"
        )

        return filter_str

    def build_brightness_effect(
        self,
        clip_path: str,
        start_time: float,
        duration: float,
        intensity: float = 0.5,
    ) -> str:
        """
        Build FFmpeg brightness/contrast effect

        Args:
            clip_path: Path to input video
            start_time: When to start effect
            duration: Effect duration
            intensity: Effect intensity (0-1)

        Returns:
            FFmpeg filter string
        """
        brightness_adjustment = -0.5 + intensity  # Range: -0.5 to 0.5
        contrast_adjustment = 1.0 + (intensity * 0.5)

        filter_str = (
            f"eq=brightness={brightness_adjustment}"
            f":contrast={contrast_adjustment}"
        )

        return filter_str

    def build_beat_sync_zoom(
        self,
        duration_seconds: float,
        bpm: int,
    ) -> str:
        """
        Build FFmpeg pulsing zoom synchronized to BPM

        Args:
            duration_seconds: Clip duration
            bpm: Beats per minute

        Returns:
            FFmpeg filter string
        """
        # Beat duration in seconds
        beat_duration = 60 / bpm

        # Create sinusoidal zoom following beat
        # zoompan=z='1+0.01*sin(2*PI*t/beat_duration)'
        filter_str = (
            f"zoompan=z='1+0.02*sin(2*PI*t/{beat_duration:.3f})'"
            f":d=1"
            f":x='iw/2-(iw/zoom/2)'"
            f":y='ih/2-(ih/zoom/2)'"
            f":fps=30"
        )

        return filter_str

    def render_video(
        self,
        timeline_clips: List[Dict],
        audio_path: str,
        bpm: int,
        resolution: Resolution = Resolution.FULL_HD_1080P,
        format: VideoFormat = VideoFormat.MP4,
        quality: str = "high",
        include_effects: bool = True,
        output_filename: str = "output",
    ) -> Dict:
        """
        Render final video with all clips, effects, and audio

        Args:
            timeline_clips: List of clip dictionaries with effects
            audio_path: Path to audio file
            bpm: BPM for sync effects
            resolution: Output resolution
            format: Output format
            quality: Quality level (high/medium/low)
            include_effects: Whether to apply effects
            output_filename: Output filename (without extension)

        Returns:
            Dictionary with export info and file path
        """
        try:
            # Get resolution specs
            res_spec = RESOLUTION_SPECS[resolution]
            codec_spec = CODEC_SPECS[format]

            # Build output path
            output_path = (
                self.output_dir
                / f"{output_filename}{codec_spec['extension']}"
            )

            # Quality presets for libx264
            quality_presets = {
                "high": "slow",      # Slower encoding, better quality
                "medium": "medium",  # Balanced
                "low": "fast",       # Faster encoding, lower quality
            }

            preset = quality_presets.get(quality, "medium")

            # Build concat demuxer file for multiple clips
            concat_file = self.output_dir / "concat.txt"
            self._create_concat_file(
                concat_file,
                [c.get("path", "") for c in timeline_clips]
            )

            # Build FFmpeg command
            ffmpeg_cmd = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file),
                "-i", audio_path,
                "-c:v", codec_spec["video_codec"],
                "-preset", preset,
                "-b:v", res_spec["bitrate"],
                "-s", f"{res_spec['width']}x{res_spec['height']}",
                "-c:a", codec_spec["audio_codec"],
                "-b:a", "128k",
                "-pix_fmt", "yuv420p",  # Compatibility
                "-y",  # Overwrite output
                str(output_path),
            ]

            # Add effects if enabled
            if include_effects:
                filter_chain = self._build_filter_chain(
                    timeline_clips, bpm
                )
                if filter_chain:
                    ffmpeg_cmd.insert(-1, "-filter_complex")
                    ffmpeg_cmd.insert(-1, filter_chain)

            # Execute FFmpeg
            result = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True,
                check=True,
            )

            # Get file size
            file_size_mb = output_path.stat().st_size / (1024 * 1024)

            return {
                "status": "success",
                "output_path": str(output_path),
                "filename": output_path.name,
                "file_size_mb": round(file_size_mb, 2),
                "resolution": resolution,
                "format": format,
                "duration_seconds": sum(
                    c.get("duration", 0) for c in timeline_clips
                ),
            }

        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "error": str(e.stderr),
                "message": "FFmpeg rendering failed",
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Export failed",
            }

    def _create_concat_file(
        self,
        concat_file: Path,
        video_paths: List[str],
    ) -> None:
        """Create FFmpeg concat demuxer file"""
        with open(concat_file, "w") as f:
            for path in video_paths:
                f.write(f"file '{path}'\n")

    def _build_filter_chain(
        self,
        timeline_clips: List[Dict],
        bpm: int,
    ) -> Optional[str]:
        """
        Build complete FFmpeg filter chain with all effects

        Args:
            timeline_clips: Clips with effect metadata
            bpm: BPM for beat-sync effects

        Returns:
            Filter chain string or None
        """
        filters = []

        for clip in timeline_clips:
            effects = clip.get("effects", [])
            for effect in effects:
                effect_type = effect.get("type")
                intensity = effect.get("intensity", 0.5)

                if effect_type == "zoom":
                    filter_str = self.build_beat_sync_zoom(
                        clip.get("duration", 5),
                        bpm,
                    )
                elif effect_type == "color_shift":
                    filter_str = self.build_color_shift_effect(
                        "",
                        effect.get("startTime", 0),
                        effect.get("duration", 0.5),
                        intensity,
                    )
                elif effect_type == "brightness":
                    filter_str = self.build_brightness_effect(
                        "",
                        effect.get("startTime", 0),
                        effect.get("duration", 0.5),
                        intensity,
                    )
                else:
                    continue

                filters.append(filter_str)

        return ",".join(filters) if filters else None


def create_export_service() -> FFmpegExporter:
    """Factory function to create export service"""
    return FFmpegExporter()


# Example usage
if __name__ == "__main__":
    exporter = FFmpegExporter()

    # Mock timeline clips
    timeline_clips = [
        {
            "path": "clip1.mp4",
            "duration": 5.0,
            "effects": [
                {
                    "type": "zoom",
                    "startTime": 0,
                    "duration": 0.5,
                    "intensity": 0.7,
                }
            ],
        },
        {
            "path": "clip2.mp4",
            "duration": 4.5,
            "effects": [
                {
                    "type": "brightness",
                    "startTime": 2,
                    "duration": 0.5,
                    "intensity": 0.5,
                }
            ],
        },
    ]

    print("📊 FFmpeg Export Service Demo\n")
    print("Supported Resolutions:", list(Resolution))
    print("Supported Formats:", list(VideoFormat))
    print("Supported Effects: zoom, cut, crossfade, color_shift, brightness")
    print("\nExample Filters:")
    print(
        "Zoom:",
        exporter.build_beat_sync_zoom(5.0, 140),
    )
    print(
        "Color Shift:",
        exporter.build_color_shift_effect("", 0, 0.5, 0.7),
    )
    print(
        "Brightness:",
        exporter.build_brightness_effect("", 0, 0.5, 0.6),
    )
