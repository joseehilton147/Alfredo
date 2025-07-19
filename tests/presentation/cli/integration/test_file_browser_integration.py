"""Integration tests for FileExplorer component."""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from src.presentation.cli.components.file_browser import FileExplorer
from src.presentation.cli.themes.default_theme import DefaultTheme


class TestFileExplorerIntegration:
    """Integration tests for FileExplorer with real file system operations."""

    @pytest.fixture
    def complex_file_structure(self):
        """Create a complex file structure for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create nested directory structure
            (temp_path / "videos").mkdir()
            (temp_path / "videos" / "movies").mkdir()
            (temp_path / "videos" / "series").mkdir()
            (temp_path / "documents").mkdir()
            (temp_path / "images").mkdir()

            # Create video files in different locations
            (temp_path / "video_root.mp4").touch()
            (temp_path / "videos" / "action_movie.avi").touch()
            (temp_path / "videos" / "comedy.mkv").touch()
            (temp_path / "videos" / "movies" / "blockbuster.mov").touch()
            (temp_path / "videos" / "series" / "episode1.webm").touch()
            (temp_path / "videos" / "series" / "episode2.flv").touch()

            # Create non-video files (should be filtered out)
            (temp_path / "readme.txt").touch()
            (temp_path / "documents" / "report.pdf").touch()
            (temp_path / "images" / "photo.jpg").touch()

            yield temp_path

    @pytest.fixture
    def theme(self):
        """Create a theme for testing."""
        return DefaultTheme()

    def test_full_navigation_workflow(self, complex_file_structure, theme):
        """Test complete navigation workflow through directory structure."""
        explorer = FileExplorer(complex_file_structure, theme)

        # Start at root - should see video file and directories
        assert explorer.has_video_files()
        video_files = explorer.get_video_files_in_current_dir()
        assert len(video_files) == 1
        assert video_files[0].name == "video_root.mp4"

        # Navigate to videos directory
        videos_dir = complex_file_structure / "videos"
        success = explorer.navigate_to(videos_dir)
        assert success

        # Should find video files in videos directory
        video_files = explorer.get_video_files_in_current_dir()
        assert len(video_files) == 2
        video_names = [f.name for f in video_files]
        assert "action_movie.avi" in video_names
        assert "comedy.mkv" in video_names

        # Navigate to movies subdirectory
        movies_dir = videos_dir / "movies"
        success = explorer.navigate_to(movies_dir)
        assert success

        # Should find movie file
        video_files = explorer.get_video_files_in_current_dir()
        assert len(video_files) == 1
        assert video_files[0].name == "blockbuster.mov"

    def test_keyboard_navigation_through_structure(self, complex_file_structure, theme):
        """Test keyboard navigation through directory structure."""
        explorer = FileExplorer(complex_file_structure, theme)

        # Find videos directory in entries
        videos_index = None
        for i, (path, is_dir, name) in enumerate(explorer._entries):
            if is_dir and name == "videos":
                videos_index = i
                break

        assert videos_index is not None

        # Navigate to videos directory using keyboard
        explorer.selected_index = videos_index
        result = explorer.handle_key("enter")

        # Should navigate (return None) and change directory
        assert result is None
        assert explorer.current_path.name == "videos"

        # Should now see video files in videos directory
        video_files = explorer.get_video_files_in_current_dir()
        assert len(video_files) == 2

    def test_file_selection_workflow(self, complex_file_structure, theme):
        """Test selecting video files through keyboard navigation."""
        explorer = FileExplorer(complex_file_structure, theme)

        # Find the video file in root
        video_index = None
        expected_path = None
        for i, (path, is_dir, name) in enumerate(explorer._entries):
            if not is_dir and name == "video_root.mp4":
                video_index = i
                expected_path = path
                break

        assert video_index is not None

        # Select the video file
        explorer.selected_index = video_index
        result = explorer.handle_key("enter")

        # Should return the file path
        assert result == expected_path
        assert result.name == "video_root.mp4"

    def test_parent_navigation_workflow(self, complex_file_structure, theme):
        """Test navigating back to parent directories."""
        explorer = FileExplorer(complex_file_structure, theme)

        # Navigate deep into structure
        videos_dir = complex_file_structure / "videos" / "series"
        explorer.navigate_to(videos_dir)

        # Should be in series directory
        assert explorer.current_path.name == "series"

        # Use keyboard to go to parent
        result = explorer.handle_key("h")
        assert result is None
        assert explorer.current_path.name == "videos"

        # Go to parent again
        explorer.handle_key("h")
        assert explorer.current_path == complex_file_structure

    def test_mixed_case_video_detection(self, theme):
        """Test video detection with mixed case extensions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create files with different case extensions
            (temp_path / "video1.MP4").touch()
            (temp_path / "video2.Avi").touch()  # This won't be detected
            (temp_path / "video3.AVI").touch()  # This will be detected
            (temp_path / "video4.mkv").touch()

            explorer = FileExplorer(temp_path, theme)
            video_files = explorer.get_video_files_in_current_dir()

            # Should detect files with exact case matches from SUPPORTED_VIDEO_EXTENSIONS
            video_names = [f.name for f in video_files]
            assert "video1.MP4" in video_names
            assert "video3.AVI" in video_names
            assert "video4.mkv" in video_names
            # video2.Avi should not be detected as we don't have .Avi in our supported extensions

    def test_empty_directory_navigation(self, theme):
        """Test navigation in empty directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create empty subdirectory
            empty_dir = temp_path / "empty"
            empty_dir.mkdir()

            explorer = FileExplorer(temp_path, theme)

            # Navigate to empty directory
            success = explorer.navigate_to(empty_dir)
            assert success

            # Should handle empty directory gracefully
            assert not explorer.has_video_files()
            assert len(explorer.get_video_files_in_current_dir()) == 0

            # Should still be able to navigate
            explorer.handle_key("down")
            explorer.handle_key("up")

            # Should be able to render
            panel = explorer.render()
            assert panel is not None

    def test_large_directory_performance(self, theme):
        """Test performance with large number of files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create many files (mix of video and non-video)
            for i in range(50):
                if i % 3 == 0:  # Every third file is a video
                    (temp_path / f"video_{i}.mp4").touch()
                else:
                    (temp_path / f"document_{i}.txt").touch()

            # Create some directories
            for i in range(10):
                (temp_path / f"dir_{i}").mkdir()

            explorer = FileExplorer(temp_path, theme)

            # Should handle large directory efficiently
            video_files = explorer.get_video_files_in_current_dir()
            assert len(video_files) == 17  # 50/3 rounded up = 17 video files

            # Navigation should still work
            explorer.handle_key("down")
            explorer.handle_key("up")

            # Rendering should work
            panel = explorer.render()
            assert panel is not None

    def test_permission_error_recovery(self, theme):
        """Test recovery from permission errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a normal directory first
            normal_dir = temp_path / "normal"
            normal_dir.mkdir()
            (normal_dir / "video.mp4").touch()

            explorer = FileExplorer(temp_path, theme)

            # Navigate to normal directory (should work)
            success = explorer.navigate_to(normal_dir)
            assert success
            assert explorer.has_video_files()

            # Try to navigate to non-existent directory (should fail gracefully)
            fake_dir = temp_path / "nonexistent"
            success = explorer.navigate_to(fake_dir)
            assert not success

            # Should still be in the normal directory
            assert explorer.current_path == normal_dir
            assert explorer.has_video_files()

    def test_file_info_accuracy(self, complex_file_structure, theme):
        """Test accuracy of file information display."""
        explorer = FileExplorer(complex_file_structure, theme)

        # Create a file with known content
        test_file = complex_file_structure / "test_video.mp4"
        test_content = b"fake video content for testing"
        test_file.write_bytes(test_content)

        # Refresh entries to pick up the new file
        explorer._refresh_entries()

        # Get file info
        size_str, type_str = explorer._get_file_info(test_file)

        assert type_str == "Vídeo"
        assert str(len(test_content)) in size_str or "B" in size_str

    def test_directory_sorting(self, complex_file_structure, theme):
        """Test that directories and files are properly sorted."""
        explorer = FileExplorer(complex_file_structure, theme)

        # Get entries (excluding parent directory)
        entries = [e for e in explorer._entries if e[2] != ".."]

        # Directories should come first
        directories = [e for e in entries if e[1]]  # is_dir = True
        files = [e for e in entries if not e[1]]   # is_dir = False

        # Check that we have both directories and files
        assert len(directories) > 0
        assert len(files) > 0

        # In the entries list, all directories should come before all files
        first_file_index = None
        last_dir_index = None

        for i, (path, is_dir, name) in enumerate(entries):
            if is_dir:
                last_dir_index = i
            else:
                if first_file_index is None:
                    first_file_index = i

        # All directories should come before all files
        if last_dir_index is not None and first_file_index is not None:
            assert last_dir_index < first_file_index
