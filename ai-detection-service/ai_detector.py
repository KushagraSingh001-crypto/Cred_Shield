from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, GPT2LMHeadModel, GPT2Tokenizer #IMPORTS TO HANDLE PRE_MODEL
import numpy as np
import re
import torch
import math
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


device = 0 if torch.cuda.is_available() else -1
if torch.cuda.is_available():
    logger.info("Using GPU: YASH BHAI KA GPU") #YASH TERMINAL PE YE SHOW HONA CHAYIE WHILE STARTING
else:
    logger.info("Using CPU") #YE SHOW NHI HONA CHAYIE


PRIMARY_MODEL_NAME = "openai-community/roberta-base-openai-detector" #CORE IDEA ROBERTA
try:
    primary_tokenizer = AutoTokenizer.from_pretrained(PRIMARY_MODEL_NAME)
    primary_model = AutoModelForSequenceClassification.from_pretrained(PRIMARY_MODEL_NAME)
    if device == 0:
        primary_model = primary_model.to('cuda').half()
    primary_detector = pipeline(
        "text-classification",
        model=primary_model,
        tokenizer=primary_tokenizer,
        device=device,
        dtype=torch.float16 if device == 0 else torch.float32
    )
except Exception as e:
    logger.error(f"Failed to load primary model {PRIMARY_MODEL_NAME}: {e}")  #AGAR BOLO TO EXCEPTION MAIN CUSTOMIZE KRDU
    raise


SECONDARY_MODEL_NAME = "desklib/ai-text-detector-v1.01"   #ANOTHER MODEL
try:
    secondary_tokenizer = AutoTokenizer.from_pretrained(SECONDARY_MODEL_NAME)
    secondary_model = AutoModelForSequenceClassification.from_pretrained(SECONDARY_MODEL_NAME)
    if device == 0:
        secondary_model = secondary_model.to('cuda').half()
    secondary_detector = pipeline(
        "text-classification",
        model=secondary_model,
        tokenizer=secondary_tokenizer,
        device=device,
        dtype=torch.float16 if device == 0 else torch.float32
    )
except Exception as e:
    logger.error(f"Failed to load secondary model {SECONDARY_MODEL_NAME}: {e}")
    raise

# GPT-2 for perplexity
try:
    perplex_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    perplex_model = GPT2LMHeadModel.from_pretrained("gpt2")
    if device == 0:
        perplex_model = perplex_model.to('cuda').half()
except Exception as e:
    logger.error(f"Failed to load GPT-2 model: {e}")
    raise

# Label mapping (covers both models)
LABEL_MAP = {"Fake": 1, "Real": 0, "AI": 1, "Human": 0, "LABEL_1": 1, "LABEL_0": 0}

# Chunk text for memory efficiency
def chunk_text_by_words(text, words_per_chunk=300, overlap=60):
    words = text.split()
    n = len(words)
    if n <= words_per_chunk:
        return [text]
    chunks = []
    start = 0
    while start < n:
        end = min(start + words_per_chunk, n)
        chunks.append(" ".join(words[start:end]))
        if end == n:
            break
        start = end - overlap
    return chunks

# Compute perplexity
def compute_perplexity(text: str) -> float:
    try:
        inputs = perplex_tokenizer(text, return_tensors="pt", truncation=True, max_length=1024).to('cuda' if device == 0 else 'cpu')
        with torch.no_grad():
            loss = perplex_model(**inputs, labels=inputs["input_ids"]).loss
        return float(math.exp(loss))
    except Exception as e:
        logger.warning(f"Perplexity calculation failed: {e}. Returning default value.")
        return 100.0  # Default for robustness


def compute_burstiness(text: str) -> float:
    sentences = re.split(r'[.!?]+', text)
    lengths = [len(s.split()) for s in sentences if s.strip()]
    return float(np.std(lengths) / (np.mean(lengths) + 1e-6)) if lengths else 0.0


def compute_ai_score(text: str, words_per_chunk=300) -> dict:
    text = text.strip()
    if not text:
        return {"ai_prob": 0.0, "uncertainty": 0.0, "chunks": 0}
    
    chunks = chunk_text_by_words(text, words_per_chunk=words_per_chunk)
    primary_probs = []
    secondary_probs = []
    
    for ch in chunks:
        try:
            out = primary_detector(ch, truncation=True, max_length=512)
            top = out[0] if isinstance(out, list) else out
            label = str(top.get("label", ""))
            score = float(top.get("score", 0.5))
            mapped = LABEL_MAP.get(label, 1 if "ai" in label.lower() else 0)
            ai_p = score if mapped == 1 else 1.0 - score
            primary_probs.append(ai_p)
        except Exception as e:
            logger.warning(f"Primary detector failed on chunk: {e}. Skipping chunk.")
            primary_probs.append(0.5)  
        

        try:
            sec_out = secondary_detector(ch, truncation=True, max_length=512)
            sec_top = sec_out[0] if isinstance(sec_out, list) else sec_out
            sec_label = str(sec_top.get("label", ""))
            sec_score = float(sec_top.get("score", 0.5))
            sec_mapped = LABEL_MAP.get(sec_label, 1 if "ai" in sec_label.lower() else 0)
            sec_ai_p = sec_score if sec_mapped == 1 else 1.0 - sec_score
            secondary_probs.append(sec_ai_p)
        except Exception as e:
            logger.warning(f"Secondary detector failed on chunk: {e}. Skipping chunk.")
            secondary_probs.append(0.5)  
    

    avg_probs = [(p + s) / 2 for p, s in zip(primary_probs, secondary_probs)]
    weights = np.linspace(1.0, 0.7, len(avg_probs))
    ai_prob = float(np.average(avg_probs, weights=weights)) if avg_probs else 0.5
    

    try:
        perplex = compute_perplexity(text)
        burst = compute_burstiness(text)
        adjustment = (perplex / 100.0) * 0.2 + burst * 0.1
        ai_prob = max(0.0, min(1.0, ai_prob - adjustment))
    except Exception as e:
        logger.warning(f"Feature adjustment failed: {e}. Using raw ai_prob.")
    
    def entropy(p_list):
        p_list = np.clip(p_list, 1e-6, 1 - 1e-6)
        ent = - (p_list * np.log2(p_list) + (1 - p_list) * np.log2(1 - p_list))
        return float(np.mean(ent))
    
    unc = entropy(np.array(avg_probs)) if avg_probs else 0.0
    return {"ai_prob": ai_prob, "uncertainty": unc, "chunks": len(avg_probs)}

# FastAPI setup
app = FastAPI()

class AssessRequest(BaseModel):
    text: str

#THRESHOLD CHANGE KARKE TRY KARO AGR NHI ACCURATE HAI
THRESHOLD_A = 0.80
THRESHOLD_B = 0.40
UNCERTAINTY_THRESHOLD = 0.7

# API endpoint
@app.post("/infer/assess")
async def assess(request: AssessRequest):
    text = (request.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    ai_res = compute_ai_score(text)
    ai_prob = ai_res["ai_prob"]
    uncertainty = ai_res["uncertainty"]
    
    if ai_prob >= THRESHOLD_A and uncertainty < UNCERTAINTY_THRESHOLD:
        advisory = "AI"
    elif ai_prob <= THRESHOLD_B and uncertainty < UNCERTAINTY_THRESHOLD:
        advisory = "Human"
    else:
        advisory = "Uncertain"
    
    response = {
        "advisory": advisory
    }
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
