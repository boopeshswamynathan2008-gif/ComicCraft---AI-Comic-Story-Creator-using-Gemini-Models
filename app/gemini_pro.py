import json
import os
from typing import Any, Dict, List

try:
    from google import genai
except Exception:
    genai = None


def _fallback_enrichment(
    panels: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    enriched = []

    for panel in panels:

        title = str(
            panel.get(
                "title",
                f"Panel {panel.get('panel', 1)}"
            )
        )

        narration = (
            f"The adventure continues as "
            f"{title.lower()} unfolds."
        )

        dialogue = (
            "Main Character: "
            "We must keep going!"
        )

        enriched.append({
            **panel,
            "narration": narration,
            "dialogue": dialogue,
            "character_interaction": (
                "The main character reacts "
                "to the situation with determination."
            )
        })

    return enriched


def enrich_panels(
    panels: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    if not panels:
        return []

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key or genai is None:
        return _fallback_enrichment(
            panels
        )

    client = genai.Client(
        api_key=api_key
    )

    payload = json.dumps(
        panels,
        ensure_ascii=False
    )

    prompt = """
You are the SENIOR COMIC SCRIPT WRITER
for an AI comic generation system.

You are given a 5-panel comic outline.

Your job is to enrich every panel with:

- scene
- image_prompt
- narration
- dialogue
- character_interaction

IMPORTANT:

The original main character MUST NOT change.

The main character from the original outline
must remain the same in every panel.

If the main character is an animal,
KEEP IT AS THE SAME ANIMAL.

For example:

If the character is "Lion":

CORRECT:
"The main character is a majestic golden lion."

WRONG:
"A young boy walks through the forest."

WRONG:
"A warrior explores the forest."

WRONG:
"A humanoid lion walks through the forest."

The character must remain exactly what the user requested.

--------------------------------------------------

IMAGE PROMPT REQUIREMENTS

The image_prompt will be sent directly to an
AI image generation model.

Write a highly descriptive visual prompt.

Every image_prompt must contain:

MAIN CHARACTER:
Clearly identify the exact main character.

CHARACTER APPEARANCE:
Describe physical appearance and important visual features.

ACTION:
Describe exactly what the character is doing.

ENVIRONMENT:
Describe the location and surroundings.

COMPOSITION:
Describe camera angle, framing and visual composition.

LIGHTING:
Describe appropriate lighting.

STYLE:
Use the requested art style.

TONE:
Match the requested emotional tone.

--------------------------------------------------

VERY IMPORTANT:

The image must contain NO TEXT.

Do not include:

- speech bubbles
- dialogue bubbles
- captions
- subtitles
- written words
- letters
- numbers
- logos
- watermarks
- signs with writing
- UI elements
- typography

Dialogue and narration are handled separately by
the application.

Therefore image_prompt must describe ONLY visual content.

--------------------------------------------------

CONSISTENCY:

All five images should look like they belong
to the same comic.

Keep the following consistent:

- main character
- character appearance
- art style
- visual identity
- setting
- color mood

The character should not randomly change between panels.

--------------------------------------------------

OUTPUT:

Return ONLY valid JSON.

Return exactly the same number of panels as the input.

Each object MUST contain:

panel
title
scene
image_prompt
narration
dialogue
character_interaction
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=(
                f"{prompt}\n\n"
                f"ORIGINAL 5-PANEL OUTLINE:\n"
                f"{payload}"
            ),
        )

        text = getattr(
            response,
            "text",
            None
        ) or str(response)

        cleaned = text.strip()

        if cleaned.startswith("```"):

            cleaned = cleaned.strip("`")

            if "json" in cleaned.lower():

                cleaned = cleaned.split(
                    "json",
                    1
                )[1].strip()

        start = cleaned.find("[")
        end = cleaned.rfind("]")

        if start != -1 and end != -1:

            cleaned = cleaned[
                start:end + 1
            ]

        generated = json.loads(
            cleaned
        )

        if (
            isinstance(generated, list)
            and len(generated) == len(panels)
        ):

            normalized = []

            for idx, item in enumerate(
                generated,
                start=1
            ):

                normalized.append({

                    "panel": int(
                        item.get(
                            "panel",
                            idx
                        )
                    ),

                    "title": str(
                        item.get(
                            "title",
                            f"Panel {idx}"
                        )
                    ),

                    "scene": str(
                        item.get(
                            "scene",
                            ""
                        )
                    ),

                    "image_prompt": str(
                        item.get(
                            "image_prompt",
                            ""
                        )
                    ),

                    "narration": str(
                        item.get(
                            "narration",
                            "The story continues."
                        )
                    ),

                    "dialogue": str(
                        item.get(
                            "dialogue",
                            ""
                        )
                    ),

                    "character_interaction": str(
                        item.get(
                            "character_interaction",
                            ""
                        )
                    )
                })

            return normalized

    except Exception as error:

        print(
            f"Gemini Flash error: {error}"
        )

    return _fallback_enrichment(
        panels
    )