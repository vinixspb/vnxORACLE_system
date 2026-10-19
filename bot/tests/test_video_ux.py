import unittest

from config_video_models import VIDEO_MODELS
from keyboards.ai_video import (
    get_post_video_generation_keyboard,
    get_video_format_keyboard,
    get_video_generation_keyboard,
    get_video_image_action_keyboard,
    get_video_menu_keyboard,
)


def callback_data(markup):
    return {
        button.callback_data
        for row in markup.inline_keyboard
        for button in row
        if button.callback_data is not None
    }


class VideoUxKeyboardTests(unittest.TestCase):
    def test_five_configured_models_are_available_in_main_video_menu(self):
        callbacks = callback_data(get_video_menu_keyboard())
        expected = {
            "video_model-seedance-2.0",
            "video_model-seedance-2.0-mini",
            "video_model-seedance-2.0-fast",
            "video_model-kling-3.0-pro",
            "video_model-veo-3.1-fast",
        }
        # Button callback ids use a prefix plus underscore, not a hyphen separator.
        expected = {value.replace("video_model-", "video_model_", 1) for value in expected}
        self.assertTrue(expected.issubset(callbacks))
        self.assertEqual(len(VIDEO_MODELS), 5)

    def test_photo_action_menu_has_random_custom_and_cancel(self):
        callbacks = callback_data(get_video_image_action_keyboard())
        self.assertTrue({
            "video_image_random",
            "video_image_custom",
            "video_image_cancel",
        }.issubset(callbacks))

    def test_format_menu_has_both_aspect_ratios_and_back(self):
        callbacks = callback_data(get_video_format_keyboard())
        self.assertTrue({
            "video_format_16_9",
            "video_format_9_16",
            "video_format_back",
        }.issubset(callbacks))

    def test_selected_model_offers_both_generation_modes(self):
        callbacks = callback_data(get_video_generation_keyboard("seedance-2.0"))
        self.assertTrue({
            "video_text_seedance-2.0",
            "video_image_seedance-2.0",
        }.issubset(callbacks))

    def test_post_generation_menu_returns_to_video_or_main_menu(self):
        callbacks = callback_data(get_post_video_generation_keyboard())
        self.assertTrue({"feature_video", "back_to_features"}.issubset(callbacks))


if __name__ == "__main__":
    unittest.main()
