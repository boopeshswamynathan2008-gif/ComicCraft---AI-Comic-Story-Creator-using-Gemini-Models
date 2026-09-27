import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image, ImageDraw

load_dotenv()


def _make_placeholder_image(
    prompt: str,
    panel_number: int,
    output_path: Path
) -> str:

    width, height = 900, 700

    image = Image.new(
        "RGB",
        (width, height),
        (20, 24, 44)
    )

    draw = ImageDraw.Draw(image)

    for y in range(0, height, 30):
        color = (
            (30 + y // 2) % 255,
            (40 + y // 3) % 255,
            (70 + y // 4) % 255
        )

        draw.rectangle(
            (0, y, width, y + 20),
            fill=color
        )

    draw.rectangle(
        (60, 60, width - 60, height - 60),
        outline=(255, 255, 255),
        width=4
    )

    draw.rounded_rectangle(
        (120, 120, width - 120, height - 120),
        radius=30,
        outline=(180, 200, 255),
        width=5
    )

    draw.text(
        (80, 90),
        f"Panel {panel_number}",
        fill=(255, 255, 255)
    )

    prompt_text = (
        prompt[:90] + "..."
        if len(prompt) > 90
        else prompt
    )

    draw.text(
        (80, 560),
        prompt_text,
        fill=(230, 240, 255)
    )

    image.save(
        output_path,
        format="PNG"
    )

    return "/" + str(output_path).replace("\\", "/")


def _generate_with_huggingface(prompt: str):

    token = os.getenv("HF_API_KEY")

    if not token:
        print("HF_API_KEY not found.")
        return None

    try:
        from huggingface_hub import InferenceClient

        client = InferenceClient(
            api_key=token,
            provider="auto"
        )

        model = os.getenv(
            "HF_IMAGE_MODEL",
            "black-forest-labs/FLUX.1-schnell"
        )

        negative_prompt = (
            "human, boy, girl, man, woman, child, person, "
            "human face, human body, speech bubble, "
            "comic text, dialogue, captions, subtitles, "
            "letters, words, numbers, watermark, logo, "
            "written language, typography, text, "
            "garbled text, distorted text"
        )

        image = client.text_to_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            model=model,
            num_inference_steps=4
        )

        return image

    except Exception as error:

        print(
            f"Hugging Face generation failed: {error}"
        )

        return None


def generate_panel_image(
    prompt: str,
    panel_number: int,
    output_dir: str = "static/panels"
) -> str:

    output_path = Path(output_dir)

    output_path.mkdir(
        parents=True,
        exist_ok=True
    )

    # Unique filename prevents browser caching old images
    image_file = (
        output_path /
        f"panel_{panel_number}_{uuid.uuid4().hex[:8]}.png"
    )

    # Strong instructions for the image model
    comic_prompt = (
        f"MAIN SUBJECT: {prompt}. "
        "The MAIN SUBJECT described above must be the central "
        "and clearly visible subject of the image. "
        "Do not replace the main subject with a human. "
        "Create ONE single comic book panel illustration. "
        "The subject must visually match the description. "
        "If the subject is an animal, show the animal clearly "
        "as the main character. "
        "Professional colorful comic artwork, "
        "cinematic composition, "
        "detailed environment, "
        "expressive character, "
        "dynamic action, "
        "high quality digital illustration. "
        "NO speech bubbles. "
        "NO dialogue. "
        "NO captions. "
        "NO written text anywhere in the image. "
        "NO letters or numbers. "
        "English-language project, but the image itself "
        "must contain absolutely no text."
    )

    print(
        f"Generating image for panel {panel_number}: "
        f"{prompt}"
    )

    image = _generate_with_huggingface(
        comic_prompt
    )

    if image is not None:

        image.save(
            image_file,
            format="PNG"
        )

        print(
            f"Hugging Face image generated: "
            f"{image_file}"
        )

        return "/" + str(image_file).replace(
            "\\",
            "/"
        )

    print(
        "Using placeholder image."
    )

    return _make_placeholder_image(
        prompt,
        panel_number,
        image_file
    )


def create_test_image() -> str:

    return generate_panel_image(
        "a majestic golden lion standing in a magical forest",
        0,
        output_dir="static/panels"
    )