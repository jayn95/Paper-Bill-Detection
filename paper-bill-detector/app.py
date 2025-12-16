from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image, ImageOps
import io

from utils.detect import BillDetector
from utils.change import aggregate_bills, compute_total_amount, compute_change

app = FastAPI(title="Paper Bill Detector API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

MODEL_PATH = "model/best.pt"
bill_detector = BillDetector(MODEL_PATH)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# ✅ STRICT backend formats
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}
ALLOWED_PIL_FORMATS = {"JPEG", "PNG"}


def minimal_preprocess(image: Image.Image) -> Image.Image:
    try:
        image = ImageOps.exif_transpose(image)
    except Exception:
        pass
    return image.convert("RGB")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/detect")
async def detect_bill(
    file: UploadFile = File(...),
    coins: str = Form(None)
):

    # ❌ MIME check (browser lies sometimes, but still UX)
    if file.content_type not in ALLOWED_MIME_TYPES:
        return JSONResponse(
            status_code=400,
            content={"error": "Unsupported file type. Only JPG and PNG are allowed."}
        )

    image_bytes = await file.read()

    if not image_bytes:
        return JSONResponse(
            status_code=400,
            content={"error": "Empty file uploaded."}
        )

    if len(image_bytes) > MAX_FILE_SIZE:
        return JSONResponse(
            status_code=400,
            content={"error": "File too large. Max 5MB."}
        )

    # ✅ Real image validation
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "File is not a valid image."}
        )

    # 🔁 PIL requires reopen
    image = Image.open(io.BytesIO(image_bytes))

    # ❌ HARD BLOCK WEBP / HEIC / AVIF / TIFF
    if image.format not in ALLOWED_PIL_FORMATS:
        return JSONResponse(
            status_code=400,
            content={"error": f"Unsupported image format ({image.format}). Only JPG and PNG allowed."}
        )

    # ❌ DoS protection
    if image.width * image.height > 20_000_000:
        return JSONResponse(
            status_code=400,
            content={"error": "Image resolution too large."}
        )

    image = minimal_preprocess(image)

    detected_classes = bill_detector.detect(image)

    if not detected_classes:
        return {
            "total_amount": 0,
            "bills_detected": {},
            "coin_change": {},
            "message": "No paper bills detected."
        }

    bills_detected = aggregate_bills(detected_classes)
    total_amount = compute_total_amount(bills_detected)

    # Coins parsing
    coins_list = None
    if coins:
        coins_list = [int(c) for c in coins.split(",") if c.isdigit()]

    coin_change = compute_change(total_amount, coins=coins_list)

    return {
        "total_amount": total_amount,
        "bills_detected": bills_detected,
        "coin_change": coin_change
    }


@app.get("/about", response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})
