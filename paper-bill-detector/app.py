from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image
import io

from utils.detect import BillDetector
from utils.change import aggregate_bills, compute_total_amount, compute_change

# =========================
# App Initialization
# =========================
app = FastAPI(title="Paper Bill Detector API")

# CORS (safe default for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Static & Templates
# =========================
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# =========================
# Load YOLOv8 Model (once)
# =========================
MODEL_PATH = "model/best.pt"
bill_detector = BillDetector(MODEL_PATH)

# =========================
# Routes
# =========================
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/detect")
async def detect_bill(file: UploadFile = File(...), coins: str = Form(None)):
    # Validate file type
    if not file.content_type.startswith("image/"):
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid file type. Please upload an image."}
        )

    # Read image
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Run detection
    detected_classes = bill_detector.detect(image)

    if not detected_classes:
        return {
            "total_amount": 0,
            "bills_detected": {},
            "coin_change": {},
            "message": "No paper bills detected"
        }

    # Aggregate & compute
    bills_detected = aggregate_bills(detected_classes)
    total_amount = compute_total_amount(bills_detected)

    # Parse user-provided coins (comma-separated string) or default
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