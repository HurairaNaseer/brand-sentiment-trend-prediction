
"""
main.py — FastAPI Backend
Run: uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

import pickle
import numpy as np
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional, List
from enum import Enum

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator, model_validator
import uvicorn

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1 — SENTIMENT ENGINE
#  (Yahi word lists train.py mein bhi hain — dono match karne chahiye)
# ══════════════════════════════════════════════════════════════════════════════
POSITIVE_WORDS = [
    "acha", "best", "zabardast", "wah", "lajawab", "perfect",
    "love", "amazing", "gorgeous", "beautiful", "nice",
    "compliment", "khubsoorat", "pasand", "dil jeet", "superb",
    "excellent", "recommend", "quality", "satisfied", "happy",
    "stunning", "good", "worth", "awesome", "fantastic", "delightful",
]
NEGATIVE_WORDS = [
    "bekar", "kharab", "bura", "disappointed", "worst",
    "late", "delay", "return", "waste", "overpriced",
    "poor", "bad", "fake", "cheating", "wrong", "inaccurate",
    "refund", "complaint", "pathetic", "horrible", "never buy",
    "crash", "expensive", "lousy", "disgusting", "ghatiya", "bekaar",
    "kisi kaam ka nain hai", "fuzool",
]

# Voting thresholds — train.py ke output se match karte hain
LIKES_MEDIAN  = 92.0
SHARES_MEDIAN = 327.0


def analyze_sentiment(text: str):
    """Returns (score, {positive:[...], negative:[...]})"""
    t = str(text).lower()
    pos = [w for w in POSITIVE_WORDS if w in t]
    neg = [w for w in NEGATIVE_WORDS if w in t]
    return len(pos) - len(neg), {"positive": pos, "negative": neg}


def score_to_label(score: int) -> str:
    return "Positive" if score > 0 else ("Negative" if score < 0 else "Neutral")


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 2 — MODEL LOADER
# ══════════════════════════════════════════════════════════════════════════════
MODEL = BRAND_ENCODER = PLATFORM_ENCODER = None


def _load_pkl(path: str):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    with open(p, "rb") as f:
        return pickle.load(f)


def load_all_models():
    global MODEL, BRAND_ENCODER, PLATFORM_ENCODER
    MODEL         = _load_pkl("model.pkl")
    BRAND_ENCODER = _load_pkl("le_brand.pkl")
    try:
        PLATFORM_ENCODER = _load_pkl("le_platform.pkl")
    except FileNotFoundError:
        PLATFORM_ENCODER = None
        print("⚠️  le_platform.pkl nahi mila — platform default 0 hoga.")
    print(f"✅ Model loaded | Brands: {list(BRAND_ENCODER.classes_)}")


def known_brands()    -> list: return list(BRAND_ENCODER.classes_)
def known_platforms() -> list: return list(PLATFORM_ENCODER.classes_) if PLATFORM_ENCODER else []


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 3 — PYDANTIC SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════
class TrendLabel(str, Enum):
    UP   = "UP"
    DOWN = "DOWN"


class PredictionRequest(BaseModel):
    brand_name:      str            = Field(..., min_length=1, max_length=100, example="Khaadi")
    platform:        str            = Field("Instagram", max_length=50,        example="Instagram")
    likes:           float          = Field(..., ge=0,                         example=2500)
    shares:          float          = Field(..., ge=0,                         example=500)
    comment_review:  Optional[str]  = Field(None, max_length=2000,
                          example="Amazing quality, love this brand!")
    sentiment_score: Optional[int]  = Field(None, ge=-10, le=10,
                          description="Manual override. Agar diya nahi toh comment se auto-compute hoga.")

    @field_validator("brand_name", "platform", mode="before")
    @classmethod
    def strip_str(cls, v: str) -> str:
        return v.strip()

    @model_validator(mode="after")
    def needs_source(self) -> "PredictionRequest":
        if self.sentiment_score is None and not self.comment_review:
            raise ValueError("'comment_review' ya 'sentiment_score' dono mein se ek zaroori hai.")
        return self


class BatchPredictionRequest(BaseModel):
    predictions: List[PredictionRequest] = Field(..., min_length=1, max_length=50)


class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000,
                      example="Zabardast quality! Best brand ever!")


class PredictionResponse(BaseModel):
    brand_name:      str
    platform:        str
    likes:           float
    shares:          float
    sentiment_score: int
    sentiment_label: str          # "Positive" / "Negative" / "Neutral"
    vote_likes:      int          # 1 = likes zyada, 0 = kam
    vote_shares:     int          # 1 = shares zyada, 0 = kam
    vote_sentiment:  int          # 1 = positive, 0 = negative/neutral
    total_votes:     int          # 0-3
    trend:           TrendLabel
    confidence:      float
    message:         str
    recommendation:  str


class BatchPredictionResponse(BaseModel):
    total:   int
    results: List[PredictionResponse]


class SentimentResponse(BaseModel):
    text:            str
    sentiment_score: int
    label:           str
    detected_words:  dict


class BrandInfoResponse(BaseModel):
    known_brands:    List[str]
    known_platforms: List[str]
    total_brands:    int
    total_platforms: int


class HealthResponse(BaseModel):
    status:         str
    model_loaded:   bool
    encoder_loaded: bool
    known_brands:   int
    api_version:    str


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 4 — PREDICTION LOGIC
# ══════════════════════════════════════════════════════════════════════════════
def _encode_brand(name: str) -> int:
    try:
        return int(BRAND_ENCODER.transform([name])[0])
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error":        "Unknown brand",
                "brand":        name,
                "known_brands": known_brands(),
                "hint":         "GET /api/v1/brands se sahi brands dekhein.",
            },
        )


def _encode_platform(name: str) -> int:
    if PLATFORM_ENCODER is None:
        return 0
    try:
        return int(PLATFORM_ENCODER.transform([name])[0])
    except ValueError:
        return 0


def _recommendation(pred: int, sentiment: int, v_likes: int,
                    v_shares: int, total_votes: int) -> str:
    if pred == 1:
        reasons = []
        if v_likes  == 1: reasons.append("high likes engagement")
        if v_shares == 1: reasons.append("high share rate")
        if sentiment > 0: reasons.append("positive customer sentiment")
        r = ", ".join(reasons) if reasons else "good overall engagement"
        return f"✅ Brand TRENDING UP — {r}. Capitalize on momentum: run targeted ads, engage with positive commenters, boost top posts."
    else:
        reasons = []
        if v_likes  == 0: reasons.append("low likes engagement")
        if v_shares == 0: reasons.append("low share rate")
        if sentiment < 0: reasons.append("negative customer sentiment")
        elif sentiment == 0: reasons.append("neutral sentiment")
        r = ", ".join(reasons) if reasons else "low overall engagement"
        return f"⚠️ Brand TRENDING DOWN — {r}. Respond to complaints, run re-engagement campaign, improve product/service quality."


def run_prediction(req: PredictionRequest) -> PredictionResponse:
    # ── Sentiment ──────────────────────────────────────────────
    if req.sentiment_score is not None:
        sentiment = req.sentiment_score
        detected  = {"positive": [], "negative": []}
    else:
        sentiment, detected = analyze_sentiment(req.comment_review or "")

    # ── Voting (2/3 majority = UP) ─────────────────────────────
    v_sentiment = 1 if sentiment > 0 else 0
    v_likes     = 1 if req.likes  > LIKES_MEDIAN  else 0
    v_shares    = 1 if req.shares > SHARES_MEDIAN else 0
    total_votes = v_sentiment + v_likes + v_shares

    # ── ML prediction ──────────────────────────────────────────
    features = np.array([[
        _encode_brand(req.brand_name),
        _encode_platform(req.platform),
        req.likes,
        req.shares,
        sentiment,
    ]])
    pred       = int(MODEL.predict(features)[0])
    proba      = MODEL.predict_proba(features)[0]
    confidence = round(float(proba[pred]) * 100, 2)
    trend      = TrendLabel.UP if pred == 1 else TrendLabel.DOWN

    return PredictionResponse(
        brand_name      = req.brand_name,
        platform        = req.platform,
        likes           = req.likes,
        shares          = req.shares,
        sentiment_score = sentiment,
        sentiment_label = score_to_label(sentiment),
        vote_likes      = v_likes,
        vote_shares     = v_shares,
        vote_sentiment  = v_sentiment,
        total_votes     = total_votes,
        trend           = trend,
        confidence      = confidence,
        message         = (
            f"Brand '{req.brand_name}' is TRENDING {trend.value} "
            f"with {confidence}% confidence. "
            f"Votes: Sentiment={v_sentiment} | Likes={v_likes} | Shares={v_shares} "
            f"→ Total {total_votes}/3"
        ),
        recommendation  = _recommendation(pred, sentiment, v_likes, v_shares, total_votes),
    )


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 5 — FASTAPI APP
# ══════════════════════════════════════════════════════════════════════════════
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 ML models load ho rahe hain...")
    load_all_models()
    yield
    print("🛑 Shutting down.")


app = FastAPI(
    title       = "Brand Monitoring & Sentiment Analysis API",
    description = (
        "AI-powered social media brand monitoring — Random Forest + 2/3 Voting System.\n\n"
        "**Voting Rules:**\n"
        "- Vote 1: Sentiment positive? (comment > 0)\n"
        "- Vote 2: Likes > median (92)?\n"
        "- Vote 3: Shares > median (327)?\n"
        "- 2 ya 3 votes = **UP** ✅ | 0 ya 1 vote = **DOWN** ❌"
    ),
    version  = "2.0.0",
    lifespan = lifespan,
    docs_url = "/docs",
    redoc_url= "/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"],
    allow_headers=["*"], allow_credentials=True,
)


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Brand Monitoring API 🎯", "docs": "/docs", "version": "2.0.0"}


@app.get("/api/v1/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    ok = MODEL is not None and BRAND_ENCODER is not None
    return HealthResponse(
        status         = "healthy" if ok else "degraded",
        model_loaded   = MODEL is not None,
        encoder_loaded = BRAND_ENCODER is not None,
        known_brands   = len(known_brands()) if BRAND_ENCODER else 0,
        api_version    = "2.0.0",
    )


@app.get("/api/v1/brands", response_model=BrandInfoResponse, tags=["Analytics"])
async def list_brands():
    return BrandInfoResponse(
        known_brands    = known_brands(),
        known_platforms = known_platforms(),
        total_brands    = len(known_brands()),
        total_platforms = len(known_platforms()),
    )


@app.post("/api/v1/sentiment", response_model=SentimentResponse, tags=["Analytics"])
async def sentiment_endpoint(req: SentimentRequest):
    score, detected = analyze_sentiment(req.text)
    return SentimentResponse(
        text            = req.text,
        sentiment_score = score,
        label           = score_to_label(score),
        detected_words  = detected,
    )


@app.post("/api/v1/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict_single(req: PredictionRequest):
    return run_prediction(req)


@app.post("/api/v1/predict/batch", response_model=BatchPredictionResponse, tags=["Prediction"])
async def predict_batch(req: BatchPredictionRequest):
    results = [run_prediction(r) for r in req.predictions]
    return BatchPredictionResponse(total=len(results), results=results)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)