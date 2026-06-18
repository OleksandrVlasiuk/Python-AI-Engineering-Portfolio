# ==============================================================================
# PHASE 1: SYSTEM SETUP & ONNX INFERENCE ENGINE INITIALIZATION
# Here we configure the environment, setup GPU acceleration (cuDNN) if available,
# and initialize the ONNX Runtime session with graph optimizations.
# ==============================================================================

import os
import sys

# .\venv\Scripts\activate
# uvicorn main:app --host 127.0.0.1 --port 8000

# --- WINDOWS CUDNN AUTOCONNECT HOOK ---
if sys.platform == "win32":
    cudnn_bin_path = os.path.join(sys.prefix, "Lib", "site-packages", "nvidia", "cudnn", "bin")
    if os.path.exists(cudnn_bin_path):
        os.add_dll_directory(cudnn_bin_path)
        print(f"🚀 cuDNN libraries successfully loaded from: {cudnn_bin_path}")

# --- Core Dependencies Import ---
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import onnxruntime as ort
import numpy as np
from PIL import Image
import io
import time

app = FastAPI(title="Flower Classifier API")

MODEL_PATH = "efficientnetb0_clean.onnx"
CLASS_NAMES = ['daisy', 'dandelion', 'roses', 'sunflowers', 'tulips']

# Global variables for ONNX session and model layer tracking
session = None
input_name = None
output_name = None

# --- MODEL INITIALIZATION & GRAPH OPTIMIZATION ---
sess_options = ort.SessionOptions()
sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

# Determine available execution providers (Prioritizing GPU/CUDA)
available_providers = ort.get_available_providers()
if 'CUDAExecutionProvider' in available_providers:
    providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
else:
    providers = ['CPUExecutionProvider']

try:
    session = ort.InferenceSession(MODEL_PATH, sess_options=sess_options, providers=providers)
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    print(f"✅ Model successfully loaded! Active Execution Provider: {session.get_providers()[0]}")
except Exception as e:
    print(f"❌ Critical model loading error: {e}")


# ==============================================================================
# PHASE 2: DATA VALIDATION SCHEMAS & PREPROCESSING PIPELINE
# Defining Pydantic models for structured API responses and creating a helper
# function to process incoming image bytes into valid ONNX input tensors.
# ==============================================================================

# --- PYDANTIC SCHEMAS FOR DATA VALIDATION ---
class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    active_provider: str


class PredictionResponse(BaseModel):
    class_name: str
    confidence: float
    latency_ms: float


# --- IMAGE PREPROCESSING PIPELINE ---
def preprocess_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img = img.resize((224, 224))
    img_array = np.expand_dims(np.array(img).astype(np.float32), axis=0)
    return img_array


# ==============================================================================
# PHASE 3: REST-API ENDPOINTS
# Implementing the GET endpoint for system health checks and the POST endpoint
# to handle asynchronous image classification requests.
# ==============================================================================

# --- REST-API ENDPOINTS ---

@app.get("/health", response_model=HealthResponse)
def health_check():
    is_loaded = session is not None
    provider = session.get_providers()[0] if is_loaded else "None"
    return {
        "status": "ok",
        "model_loaded": is_loaded,
        "active_provider": provider
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    if session is None:
        raise HTTPException(status_code=500, detail="Inference model is not loaded on the server.")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="The uploaded file must be an image.")

    try:
        image_bytes = await file.read()
        input_data = preprocess_image(image_bytes)

        # Track inference latency
        start_time = time.time()
        predictions = session.run([output_name], {input_name: input_data})[0]
        latency_ms = (time.time() - start_time) * 1000

        predicted_index = np.argmax(predictions[0])

        return PredictionResponse(
            class_name=CLASS_NAMES[predicted_index],
            confidence=float(predictions[0][predicted_index]),
            latency_ms=round(latency_ms, 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Request processing error: {str(e)}")