from app.gemini_flash import build_outline
from app.layout_builder import build_panel_layout


def test_build_outline_returns_five_panels():
    result = build_outline("A brave fox exploring a magical forest", "Alex", "Forest", "Dramatic", "Anime")
    assert isinstance(result, list)
    assert len(result) == 5
    for panel in result:
        assert "title" in panel
        assert "scene" in panel
        assert "image_prompt" in panel


def test_build_panel_layout_contains_required_fields():
    panels = [
        {
            "panel": 1,
            "title": "Into the Forest",
            "scene": "Alex enters the forest.",
            "image_prompt": "fox in bright forest",
            "narration": "A hush settles over the forest.",
            "dialogue": "Alex: I can feel something magical here.",
        }
    ]
    layout = build_panel_layout(panels)
    assert len(layout) == 1
    assert layout[0]["panel"] == 1
    assert layout[0]["text"]
    assert layout[0]["image"].endswith(".png")
