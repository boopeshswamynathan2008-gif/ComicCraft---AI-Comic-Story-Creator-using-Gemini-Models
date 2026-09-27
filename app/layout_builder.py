from typing import Any, Dict, List


def build_panel_layout(panels: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    layout = []
    for index, panel in enumerate(panels, start=1):
        panel_number = int(panel.get("panel", index))
        title = str(panel.get("title") or f"Panel {panel_number}")
        narration = str(panel.get("narration") or panel.get("scene") or "")
        dialogue = str(panel.get("dialogue") or "")
        image_path = panel.get("image_path") or f"/static/panels/panel_{panel_number}.png"

        layout.append({
            "panel": panel_number,
            "title": title,
            "image": image_path,
            "narration": narration,
            "dialogue": dialogue,
            "text": f"Narration: {narration}\nDialogue: {dialogue}".strip(),
        })
    return layout
