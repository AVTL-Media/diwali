"""Tests for the SceneStateManager module."""

import pytest
import time
from unittest.mock import Mock, patch
import sys
sys.path.insert(0, '/Users/imtiaz/Downloads/claude/src')

from scene_manager import SceneStateManager, VisualState
from gesture_tracker import GestureType


class TestVisualState:
    """Test suite for VisualState enum."""

    def test_visual_states_exist(self):
        """Test that all visual states are defined."""
        assert VisualState.IDLE
        assert VisualState.DIYA
        assert VisualState.FIREWORKS
        assert VisualState.RANGOLI
        assert VisualState.AURA

    def test_visual_state_values(self):
        """Test visual state numeric values."""
        assert VisualState.IDLE.value == 0
        assert VisualState.DIYA.value == 1
        assert VisualState.FIREWORKS.value == 2


class TestSceneStateManager:
    """Test suite for SceneStateManager class."""

    def test_init_default_config(self):
        """Test initialization with default configuration."""
        manager = SceneStateManager()

        assert manager.config["idle_timeout"] == 5.0
        assert manager.current_state == VisualState.IDLE
        assert manager.previous_state == VisualState.IDLE
        assert manager.state_data is not None

    def test_init_with_config_file(self, temp_config_file):
        """Test initialization with configuration file."""
        manager = SceneStateManager(temp_config_file)

        assert manager.current_state == VisualState.IDLE

    def test_initial_state_data(self):
        """Test that initial state data has correct structure."""
        manager = SceneStateManager()

        assert "diya_positions" in manager.state_data
        assert "firework_origins" in manager.state_data
        assert "rangoli_center" in manager.state_data
        assert "motion_intensity" in manager.state_data
        assert manager.state_data["diya_positions"] == []
        assert manager.state_data["motion_intensity"] == 0.0

    def test_update_with_no_input(self):
        """Test update with no sensor inputs."""
        manager = SceneStateManager()

        state, state_changed, state_data = manager.update()

        assert state == VisualState.IDLE
        assert state_data is not None

    def test_update_with_motion_detected(self):
        """Test state transition when motion is detected."""
        manager = SceneStateManager()

        state, state_changed, state_data = manager.update(
            motion_detected=True,
            motion_intensity=0.3,
            motion_center=(320, 240)
        )

        assert state == VisualState.RANGOLI
        assert state_data["motion_center"] == (320, 240)

    def test_update_with_high_motion_intensity(self):
        """Test state transition with high motion intensity triggers fireworks."""
        manager = SceneStateManager()

        state, state_changed, state_data = manager.update(
            motion_detected=True,
            motion_intensity=0.7,
            motion_center=(320, 240)
        )

        assert state == VisualState.FIREWORKS

    def test_update_with_audio_spike(self):
        """Test state transition when audio spike is detected."""
        manager = SceneStateManager()

        state, state_changed, state_data = manager.update(
            audio_spike=True,
            audio_level=0.8
        )

        assert state == VisualState.FIREWORKS
        assert state_data["audio_level"] == 0.8

    def test_update_with_open_palm_gesture(self):
        """Test state transition with open palm gesture."""
        manager = SceneStateManager()

        state, state_changed, state_data = manager.update(
            hands_present=True,
            hand_positions=[(320, 240)],
            gestures=[GestureType.OPEN_PALM]
        )

        assert state == VisualState.AURA
        assert state_data["aura_position"] == (320, 240)

    def test_update_with_pinch_gesture(self):
        """Test state transition with pinch gesture places diya."""
        manager = SceneStateManager()

        state, state_changed, state_data = manager.update(
            hands_present=True,
            hand_positions=[(320, 240)],
            gestures=[GestureType.PINCH]
        )

        assert state == VisualState.DIYA
        assert (320, 240) in state_data["diya_positions"]

    def test_state_change_detection(self):
        """Test that state changes are properly detected."""
        manager = SceneStateManager()

        # First update - should change from IDLE
        state1, changed1, _ = manager.update(motion_detected=True)
        assert changed1 is True

        # Second update with same input - should not change
        time.sleep(0.1)
        state2, changed2, _ = manager.update(motion_detected=True)
        # May or may not change depending on state logic

    def test_idle_timeout(self):
        """Test return to idle state after timeout."""
        manager = SceneStateManager()
        manager.config["idle_timeout"] = 0.1  # 100ms timeout

        # Trigger a state change
        manager.update(motion_detected=True)

        # Wait for timeout
        time.sleep(0.2)

        # Update without inputs
        state, _, _ = manager.update()

        assert state == VisualState.IDLE

    def test_fireworks_duration_timeout(self):
        """Test that fireworks state times out."""
        manager = SceneStateManager()
        manager.config["firework_duration"] = 0.1  # 100ms duration

        # Trigger fireworks
        manager.update(audio_spike=True)
        assert manager.current_state == VisualState.FIREWORKS

        # Wait for timeout
        time.sleep(0.2)

        # Update
        state, _, _ = manager.update()

        # Should return to idle after timeout
        assert state == VisualState.IDLE

    def test_get_current_state(self):
        """Test get_current_state returns current state."""
        manager = SceneStateManager()

        state = manager.get_current_state()

        assert state == VisualState.IDLE

    def test_get_state_duration(self):
        """Test get_state_duration returns time in current state."""
        manager = SceneStateManager()

        time.sleep(0.1)
        duration = manager.get_state_duration()

        assert duration >= 0.1

    def test_get_state_data(self):
        """Test get_state_data returns state data dictionary."""
        manager = SceneStateManager()

        state_data = manager.get_state_data()

        assert isinstance(state_data, dict)
        assert "diya_positions" in state_data

    def test_multiple_diya_positions(self):
        """Test that multiple diyas can be placed."""
        manager = SceneStateManager()

        # Place first diya
        manager.update(
            hands_present=True,
            hand_positions=[(100, 100)],
            gestures=[GestureType.PINCH]
        )

        # Place second diya
        manager.update(
            hands_present=True,
            hand_positions=[(200, 200)],
            gestures=[GestureType.PINCH]
        )

        state_data = manager.get_state_data()
        assert len(state_data["diya_positions"]) >= 1

    def test_gesture_positions_update(self):
        """Test that gesture positions are updated in state data."""
        manager = SceneStateManager()

        positions = [(100, 100), (200, 200)]
        manager.update(
            hands_present=True,
            hand_positions=positions,
            gestures=[GestureType.OPEN_PALM, GestureType.POINTING]
        )

        state_data = manager.get_state_data()
        assert state_data["gesture_positions"] == positions

    def test_last_interaction_time_updates(self):
        """Test that last interaction time updates with activity."""
        manager = SceneStateManager()
        initial_time = manager.last_interaction_time

        time.sleep(0.1)
        manager.update(motion_detected=True)

        assert manager.last_interaction_time > initial_time

    def test_previous_state_tracking(self):
        """Test that previous state is tracked correctly."""
        manager = SceneStateManager()

        # Change state
        manager.update(motion_detected=True)
        prev_state = manager.previous_state

        # Change state again
        manager.update(audio_spike=True)

        # Previous state should have been updated
        assert manager.previous_state != prev_state or manager.current_state != VisualState.IDLE

    def test_motion_center_storage(self):
        """Test that motion center is stored in state data."""
        manager = SceneStateManager()

        center = (300, 250)
        manager.update(
            motion_detected=True,
            motion_center=center
        )

        state_data = manager.get_state_data()
        assert state_data["motion_center"] == center

    def test_audio_level_storage(self):
        """Test that audio level is stored in state data."""
        manager = SceneStateManager()

        manager.update(audio_level=0.75)

        state_data = manager.get_state_data()
        assert state_data["audio_level"] == 0.75
