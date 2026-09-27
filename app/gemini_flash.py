import json
import os
from typing import Any, Dict, List

try:
    from google import genai
except Exception:
    genai = None


def _has_gemini_key() -> bool:
    return bool(os.getenv("GEMINI_API_KEY")) and genai is not None


def _fallback_outline(
    prompt: str,
    character: str,
    setting: str,
    tone: str,
    style: str
) -> List[Dict[str, Any]]:

    prompt = prompt.strip() or "A brave explorer discovers a hidden magical world."
    character = character.strip() or "Alex"
    setting = setting.strip() or "Enchanted forest"
    tone = tone.strip() or "Dramatic"
    style = style.strip() or "Anime"

    titles = [
        "The Beginning",
        "A Strange Discovery",
        "The Hidden Secret",
        "The Challenge",
        "A New Beginning"
    ]

    scenes = [
        f"{character} begins the adventure in the {setting}.",
        f"{character} discovers something mysterious inside the {setting}.",
        f"{character} follows the mystery deeper into the {setting}.",
        f"{character} faces a dangerous challenge.",
        f"{character} overcomes the challenge and discovers a new path."
    ]

    panels = []

    for index, (title, scene) in enumerate(
        zip(titles, scenes),
        start=1
    ):

        image_prompt = (
            f"MAIN CHARACTER: {character}. "
            f"SCENE: {scene}. "
            f"SETTING: {setting}. "
            f"ART STYLE: {style}. "
            f"TONE: {tone}. "
            "The main character must remain visually consistent. "
            "If the main character is an animal, it must remain "
            "an animal and must never become a human. "
            "Professional comic illustration, cinematic composition, "
            "detailed environment, expressive character, "
            "dynamic lighting, high quality. "
            "No text, no letters, no numbers, no speech bubbles."
        )

        panels.append({
            "panel": index,
            "title": title,
            "scene": scene,
            "image_prompt": image_prompt
        })

    return panels


def _parse_json_response(raw_text: str) -> List[Dict[str, Any]]:

    cleaned = raw_text.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")

        if "json" in cleaned.lower():
            cleaned = cleaned.split("json", 1)[1].strip()

    start = cleaned.find("[")
    end = cleaned.rfind("]")

    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start:end + 1]

    payload = json.loads(cleaned)

    if isinstance(payload, dict):
        payload = payload.get(
            "panels",
            payload.get("story", [])
        )

    if not isinstance(payload, list):
        raise ValueError(
            "Gemini response was not a list."
        )

    return payload


def build_outline(
    prompt: str,
    character: str,
    setting: str,
    tone: str,
    style: str
) -> List[Dict[str, Any]]:

    if not _has_gemini_key():
        return _fallback_outline(
            prompt,
            character,
            setting,
            tone,
            style
        )

    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY")
    )

    instruction = """
You are the STORY PLANNER for an AI comic generator.

Create exactly 5 comic panels.

IMPORTANT CHARACTER RULE:

The user-provided character is the MAIN CHARACTER.

You MUST preserve the character exactly.

If the character is an animal such as:
lion, tiger, elephant, dog, cat, fox, wolf, bird, etc.,
the character MUST remain that animal in every panel.

NEVER replace an animal with:
- a boy
- a girl
- a man
- a woman
- a human
- a humanoid

Do not invent a different main character.

The same main character must appear consistently across all
five panels.

IMAGE PROMPT RULES:

Each image_prompt will be sent directly to an image generation model.

Therefore every image_prompt must clearly contain:

1. The exact main character.
2. The character's important visual features.
3. The action happening in that panel.
4. The environment.
5. The requested art style.
6. The requested tone.
7. Camera/composition information.

Every image_prompt MUST explicitly state:

"The main character is [CHARACTER]."

If the character is an animal, explicitly describe it as an animal.

For example:

"The main character is a majestic golden lion.
It is a real lion, not a human and not a humanoid."

IMAGE CONTENT RULES:

Do NOT request:
- speech bubbles
- dialogue inside the image
- captions
- subtitles
- written words
- letters
- numbers
- logos
- watermarks
- signs containing text

The image generator must create ONLY the visual artwork.

Dialogue and narration will be displayed separately by the web application.

OUTPUT RULE:

Return ONLY valid JSON.

Return exactly 5 objects.

Each object must contain:

panel
title
scene
image_prompt
"""

    story = f"""
USER STORY PROMPT:
{prompt}

MAIN CHARACTER:
{character}

SETTING:
{setting}

TONE:
{tone}

ART STYLE:
{style}
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=f"{instruction}\n\n{story}",
        )

        text = getattr(
            response,
            "text",
            None
        ) or str(response)

        panels = _parse_json_response(text)

        normalized = []

        for idx, panel in enumerate(
            panels[:5],
            start=1
        ):

            normalized.append({
                "panel": int(
                    panel.get("panel", idx)
                ),

                "title": str(
                    panel.get(
                        "title",
                        f"Panel {idx}"
                    )
                ),

                "scene": str(
                    panel.get(
                        "scene",
                        ""
                    )
                ),

                "image_prompt": str(
                    panel.get(
                        "image_prompt",
                        ""
                    )
                )
            })

        if len(normalized) == 5:
            return normalized

    except Exception as error:

        print(
            f"Gemini Flash error: {error}"
        )

    return _fallback_outline(
        prompt,
        character,
        setting,
        tone,
        style
    )