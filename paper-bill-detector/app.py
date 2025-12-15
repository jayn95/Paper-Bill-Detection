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

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/jpg"
}

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
async def detect_bill(file: UploadFile = File(...), coins: str = Form(None)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid file type. Only PNG and JPG images are allowed."}
        )

    image_bytes = await file.read()

    if len(image_bytes) > MAX_FILE_SIZE:
        return JSONResponse(
            status_code=400,
            content={"error": "File too large. Maximum size is 5MB."}
        )

    try:
        image = Image.open(io.BytesIO(image_bytes))
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "Uploaded file is not a valid image."}
        )

    image = minimal_preprocess(image)

    detected_classes = bill_detector.detect(image)

    if not detected_classes:
        return {
            "total_amount": 0,
            "bills_detected": {},
            "coin_change": {},
            "message": "No paper bills detected"
        }

    bills_detected = aggregate_bills(detected_classes)
    total_amount = compute_total_amount(bills_detected)

    if coins:
        try:
            coins_list = [int(c.strip()) for c in coins.split(',') if c.strip().isdigit()]
        except ValueError:
            coins_list = None
    else:
        coins_list = None

    coin_change = compute_change(total_amount, coins=coins_list)

    return {
        "total_amount": total_amount,
        "bills_detected": bills_detected,
        "coin_change": coin_change
    }

@app.get("/about", response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})
