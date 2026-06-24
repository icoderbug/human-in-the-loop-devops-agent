import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = (
    os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
)


def _build_model():

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "Missing Gemini API key. Add GEMINI_API_KEY to your .env file."
        )

    genai.configure(
        api_key=GEMINI_API_KEY
    )

    return genai.GenerativeModel(
        model_name="gemini-2.5-flash"
    )


try:
    model = _build_model()
    MODEL_INIT_ERROR = None
except Exception as exc:
    model = None
    MODEL_INIT_ERROR = str(exc)


def require_model():

    if model is None:
        raise RuntimeError(MODEL_INIT_ERROR)

    return model

print("GEMINI_API_KEY =", GEMINI_API_KEY)

if MODEL_INIT_ERROR:
    print("MODEL ERROR =", MODEL_INIT_ERROR)
else:
    print("MODEL LOADED SUCCESSFULLY")
