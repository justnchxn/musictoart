# app/generate.py
import base64, uuid, os, httpx
from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse
from .spotify import fetch_top
from .taste import build_taste_vector, normalize_theme, three_words
from .config import STABILITY_API_KEY, STABILITY_MODEL  # make sure these come from config

router = APIRouter()

@router.get("/api/generate")
async def generate_image(request: Request, theme: str = Query(default="oil painting")):
    try:
        if not STABILITY_API_KEY:
            return JSONResponse(
                {"error": "missing_api_key", "hint": "Set STABILITY_API_KEY in .env"},
                status_code=500,
            )

        # 1) Get user's top artists/tracks
        data = await fetch_top(request)
        if not data:
            return JSONResponse({"error": "not_authed"}, status_code=401)

        # 2) Build taste + three words
        taste = build_taste_vector(data["artists"], data["tracks"])
        theme = normalize_theme(theme)
        g, p, e = three_words(taste)

        # 3) Build the prompt (now actually defined!)
        prompt = (
            f"{g} {p} {e}, {theme}, abstract digital art, high detail, "
            f"volumetric lighting, vector shapes, generative aesthetic, 4k"
        )

        # 4) Call Stability
        url = f"https://api.stability.ai/v1/generation/{STABILITY_MODEL}/text-to-image"
        headers = {
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        payload = {
            "text_prompts": [{"text": prompt, "weight": 1}],
            "cfg_scale": 7,
            "height": 640,   
            "width": 1536,   
            "samples": 1,
            "steps": 30,
        }
 
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(url, headers=headers, json=payload)

        # Debug logging (shows in your terminal)
        print("STABILITY status:", r.status_code)
        print("STABILITY body:", r.text[:400])

        if r.status_code != 200:
            return JSONResponse(
                {"error": "generation_failed", "status": r.status_code, "details": r.text},
                status_code=500,
            )

        out = r.json()
        b64 = out["artifacts"][0]["base64"]

        # 5) Save image to /static/generated
        os.makedirs("app/static/generated", exist_ok=True)
        art_id = str(uuid.uuid4())
        img_path = f"app/static/generated/{art_id}.png"
        with open(img_path, "wb") as f:
            f.write(base64.b64decode(b64))

        return JSONResponse(
            {
                "image_url": f"/static/generated/{art_id}.png",
                "prompt": prompt,
                "theme": theme,
                "three_words": f"{g} {p} {e}",
            }
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)
