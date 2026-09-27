from __future__ import annotations

from typing import Any, Dict, List

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.exporters import export_comic_pdf
from app.gemini_flash import build_outline
from app.gemini_pro import enrich_panels
from app.image_generator import create_test_image, generate_panel_image
from app.layout_builder import build_panel_layout

app = FastAPI(title="ComicCraft")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})


@app.post("/generate")
async def generate_comic(
    request: Request,
    prompt: str = Form(...),
    character: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    style: str = Form(...),
):
    panels = build_outline(prompt, character, setting, tone, style)
    rich_panels = enrich_panels(panels)
    generated_layout = []

    for panel in rich_panels:
        image_path = generate_panel_image(panel.get("image_prompt", prompt), int(panel.get("panel", 1)))
        panel["image_path"] = image_path
        generated_layout.append(panel)

    comic_layout = build_panel_layout(generated_layout)
    return templates.TemplateResponse(request, "comic_preview.html", {
        "request": request,
        "panels": comic_layout,
        "story_title": f"{character} in {setting}",
    })


@app.get("/generate-comic/json")
async def generate_comic_json():
    sample = build_outline("A brave fox exploring a magical forest", "Alex", "Forest", "Dramatic", "Anime")
    return {"panels": enrich_panels(sample)}


@app.get("/test-image")
async def test_image():
    return {"image": create_test_image()}


@app.get("/export-success")
async def export_success(request: Request):
    return templates.TemplateResponse(request, "export_success.html", {"request": request})


@app.post("/export-pdf")
async def export_pdf(request: Request):
    form = await request.form()
    panels = []
    for key in sorted(form.keys()):
        if key.startswith("panel_"):
            panels.append({
                "title": form.get(key),
                "narration": form.get(f"{key}_narration"),
                "dialogue": form.get(f"{key}_dialogue"),
                "image": form.get(f"{key}_image"),
            })

    if not panels:
        return RedirectResponse(url="/", status_code=303)

    pdf_path = export_comic_pdf(panels)
    return RedirectResponse(url=f"/export-success?pdf={pdf_path}", status_code=303)
