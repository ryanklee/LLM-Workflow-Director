import pytest

@pytest.mark.multimodal
class TestMultimodalInput:
    @pytest.mark.fast
    def test_text_and_image_input(self):
        # TODO: Implement test for text and image input
        pass

    @pytest.mark.slow
    def test_text_and_audio_input(self):
        # TODO: Implement test for text and audio input
        pass

    @pytest.mark.fast
    def test_image_and_audio_input(self):
        # TODO: Implement test for image and audio input
        pass
