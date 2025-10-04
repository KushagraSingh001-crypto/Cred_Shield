from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, GPT2LMHeadModel, GPT2Tokenizer
import numpy as np
import re
import torch
import math
import logging
from typing import List
from datetime import datetime


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


device = 0 if torch.cuda.is_available() else -1
dtype = torch.float16 if device == 0 else torch.float32

if torch.cuda.is_available():
    logger.info(f"Using GPU with {dtype} precision.")
else:
    logger.info("Using CPU. Performance will be slower.")


PRIMARY_MODEL_NAME = "openai-community/roberta-base-openai-detector"  
SECONDARY_MODEL_NAME = "distilbert-base-uncased"                     
GPT2_MODEL_NAME = "gpt2"                                             


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
        dtype=dtype,
        padding=True,
        truncation=True
    )
except Exception as e:
    logger.error(f"Failed to load primary model {PRIMARY_MODEL_NAME}: {e}")
    raise


secondary_detector = None
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
        dtype=dtype,
        padding=True,
        truncation=True
    )
except Exception as e:
    logger.warning(f"Failed to load secondary model {SECONDARY_MODEL_NAME}: {e}. Proceeding with primary only.")


try:
    perplex_tokenizer = GPT2Tokenizer.from_pretrained(GPT2_MODEL_NAME)
    perplex_model = GPT2LMHeadModel.from_pretrained(GPT2_MODEL_NAME)
    if device == 0:
        perplex_model = perplex_model.to('cuda').half()
    perplex_model.eval()
except Exception as e:
    logger.error(f"Failed to load GPT-2 model: {e}")
    raise


LABEL_MAP = {"Fake": 1, "Real": 0, "AI": 1, "Human": 0, "LABEL_1": 1, "LABEL_0": 0}


class SampleItem:
    def __init__(self, text: str, label: int):
        self.text = text
        self.label = label  # 0 = Human, 1 = AI


SAMPLE_STORE: List[SampleItem] = [
    SampleItem(
        text=("Coronavirus disease 2019, COVID-19, is a contagious disease caused by the coronavirus SARS-CoV-2. "
              "In January 2020, the disease spread worldwide, resulting in the COVID-19 pandemic. The symptoms of "
              "COVID-19 can vary but often include fever, fatigue, cough, breathing difficulties, loss of smell, and "
              "loss of taste. Symptoms may begin one to fourteen days after exposure to the virus. At least a third of "
              "people who are infected do not develop noticeable symptoms. Of those who develop symptoms noticeable "
              "enough to be classified as patients, most, about eighty-one percent, develop mild to moderate symptoms, "
              "up to mild pneumonia, while fourteen percent develop severe symptoms such as dyspnea, hypoxia, or more "
              "than fifty percent lung involvement on imaging, and five percent develop critical symptoms including "
              "respiratory failure, shock, or multiorgan dysfunction. Older people have a higher risk of developing "
              "severe symptoms. Some complications result in death. Some people continue to experience a range of "
              "effects, called long COVID, for months or years after infection, and damage to organs has been observed. "
              "Multi-year studies on the long-term effects are ongoing. COVID-19 transmission occurs when infectious "
              "particles are breathed in or come into contact with the eyes, nose, or mouth. The risk is highest when "
              "people are in close proximity, but small airborne particles containing the virus can remain suspended "
              "in the air and travel over longer distances, particularly indoors. Transmission can also occur when "
              "people touch their eyes, nose, or mouth after touching surfaces or objects contaminated by the virus. "
              "People remain contagious for up to twenty days and can spread the virus even if they do not develop "
              "symptoms. Testing methods for COVID-19 to detect the virus's nucleic acid include real-time reverse "
              "transcription polymerase chain reaction, RT-PCR, transcription-mediated amplification, and reverse "
              "transcription loop-mediated isothermal amplification, RT-LAMP, from a nasopharyngeal swab."),
        label=0
    ),
    SampleItem(
        text=("I love you. I love you with everything I got. I think I always will. I've been in love a lot but this "
              "love I have with you is so deep. It’s different and new and I think that you are so so special. I love "
              "you so much. I love that we’re friends. I love that we’re lovers. I love how you know me. How your face "
              "gets when you feel things. I love when you crinkle up your nose. I love when you hug me. I love how you "
              "love me. I love that you don’t judge me and I know you love me. I know you do. You show me everyday and "
              "I know that we’ll be together forever. Soulmates forever. I love sleeping next to you. I love you body. "
              "Every part. Even your feet. I love your smile. I love your laugh. You make me so happy and I love that. "
              "I’m so so comfortable with you. I love you. I will protect you. I will ride for you. I’d die for you. "
              "My love for you is as deep as the sea. Thank you for being my man and soon my husband. No matter what "
              "I will support you and whatever changes you wanna make I’ll make them with you. You’re the best. Thank you."),
        label=0
    ),
    SampleItem(
        text=("I love you more than words could ever capture. Every moment with you feels like a world of its own, "
              "where time slows down and nothing else matters. I love how your presence makes even the quietest spaces "
              "feel alive, how your laughter echoes in my mind long after it's gone, and how your smile has the power "
              "to change the darkest days into something bright. I love your curiosity, your kindness, your stubborn "
              "streak, and the way you care without expecting anything in return. I love the way you notice the "
              "smallest details about me, how you remember things I’ve forgotten, and how you make me feel seen and "
              "understood. I love the comfort of your arms, the warmth of your voice, and the safety I feel just being "
              "near you. I love the dreams we share, the plans we make, and even the disagreements that teach us "
              "patience and understanding. I love knowing that we’re building something that’s ours alone, something "
              "deep and lasting, something that will continue to grow as we grow. I love you with every piece of my "
              "being, every thought, every heartbeat, every breath, and I can’t imagine life without you by my side."),
        label=1
    ),
    SampleItem(
        text=("The rapid evolution of urban mobility is reshaping the way people move within cities, driven by the "
              "convergence of technology, sustainability, and population growth. Electric vehicles, ranging from cars "
              "to scooters, are increasingly replacing fossil-fueled transportation, reducing emissions while "
              "integrating seamlessly with renewable energy infrastructure. Autonomous systems further enhance "
              "efficiency by optimizing traffic flow, lowering accident rates, and offering new options for those "
              "unable to drive. At the same time, shared mobility platforms, including ride-hailing and micro-mobility "
              "services, decrease reliance on private car ownership and generate actionable data that informs urban "
              "planning decisions. Multimodal networks that allow commuters to combine walking, cycling, public "
              "transit, and on-demand transport are becoming standard in forward-thinking cities, improving "
              "convenience and reducing congestion. Collectively, these innovations illustrate a trend toward smarter, "
              "cleaner, and more adaptable urban environments, where technological solutions align with social and "
              "environmental priorities, ultimately fostering sustainable growth and higher quality of life for city "
              "dwellers."),
        label=1
    ),
    SampleItem(
        text=("Others in line were BMW X1, Audi Q3, Mercedes C Class and Lexus Es300h However, this beauty made it "
              "out. I almost finalised the X1 but later realised I was only paying for the logo. I then went for a test "
              "drive of the new Camry and good lord, I was in awe. The driving experience, the backseat comfort, the "
              "suspension, the mileage… this car is brilliant. It is a status symbol, it is hybrid, you get good value "
              "for money, good mileage, looks better than most cars, has good road presence, is rare to spot. I live "
              "in Pune and don’t see many Camry’s around, BMW, Merc etc. are a dime a dozen"),
        label=0
    ),
    SampleItem(
        text=("In the remote valleys of Lumeria, scholars discovered a previously unknown species of luminescent fungi that only blooms during"    "lunar eclipses. These fungi, tentatively named Noctiluma mystica, emit a soft blue glow that researchers believe may be a form of communication" "between individual colonies. Early chemical analysis suggests the presence of unique alkaloids capable of enhancing short-term memory in small" "mammals, though human trials have not been conducted. Local folklore claims that consuming the spores during a lunar eclipse allows one to" "experience vivid dreams that predict future events, a story passed down for generations among the valley’s inhabitants. Scientists are currently" "attempting to cultivate Noctiluma mystica in laboratory conditions, facing challenges due to its strict dependency on lunar light cycles and" "highly specific soil composition. If these challenges are overcome, the fungi could open new avenues in both pharmacology and cognitive research," "potentially revolutionizing how humans understand neural processing and dream phenomena."),
        label=1
    )
]


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


def compute_perplexity(text: str) -> float:
    try:
        inputs = perplex_tokenizer(text, return_tensors="pt", truncation=True, max_length=1024).to('cuda' if device == 0 else 'cpu')
        with torch.no_grad():
            loss = perplex_model(**inputs, labels=inputs["input_ids"]).loss
        return float(math.exp(loss))
    except Exception as e:
        logger.warning(f"Perplexity calculation failed: {e}. Returning default value.")
        return 100.0

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
            if secondary_detector:
                sec_out = secondary_detector(ch, truncation=True, max_length=512)
                sec_top = sec_out[0] if isinstance(sec_out, list) else sec_out
                sec_label = str(sec_top.get("label", ""))
                sec_score = float(sec_top.get("score", 0.5))
                sec_mapped = LABEL_MAP.get(sec_label, 1 if "ai" in sec_label.lower() else 0)
                sec_ai_p = sec_score if sec_mapped == 1 else 1.0 - score
                secondary_probs.append(sec_ai_p)
            else:
                secondary_probs.append(0.5)
        except Exception as e:
            logger.warning(f"Secondary detector failed on chunk: {e}. Skipping chunk.")
            secondary_probs.append(0.5)
    
    # Give more weight to primary model (0.8) vs. secondary (0.2) due to fine-tuning
    avg_probs = [0.8 * p + 0.2 * s for p, s in zip(primary_probs, secondary_probs)]
    weights = np.linspace(1.0, 0.7, len(avg_probs))
    ai_prob = float(np.average(avg_probs, weights=weights)) if avg_probs else 0.5
    
    try:
        perplex = compute_perplexity(text)
        burst = compute_burstiness(text)
        # Adjust: lower perplexity (AI) increases prob, higher burst (human) decreases prob
        adjustment = (perplex / 100.0) * 0.3 - burst * 0.4  # Tweaked weights based on samples
        ai_prob = max(0.0, min(1.0, ai_prob + adjustment if perplex < 50 else ai_prob - adjustment))
    except Exception as e:
        logger.warning(f"Feature adjustment failed: {e}. Using raw ai_prob.")
    
    def entropy(p_list):
        p_list = np.clip(p_list, 1e-6, 1 - 1e-6)
        ent = - (p_list * np.log2(p_list) + (1 - p_list) * np.log2(1 - p_list))
        return float(np.mean(ent))
    
    unc = entropy(np.array(avg_probs)) if avg_probs else 0.0
    return {"ai_prob": ai_prob, "uncertainty": unc, "chunks": len(avg_probs)}


app = FastAPI()
OUTPUT_FILE = "detected_ai_texts.txt"

class AssessRequest(BaseModel):
    text: str = Field(..., description="Input text to classify", example="Sample text")


THRESHOLD_BASE = 0.6  # base threshold
UNCERTAINTY_LIMIT = 0.25  # above this, we increase threshold

@app.post("/infer/assess")
async def assess(request: AssessRequest):
    text = (request.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    ai_res = compute_ai_score(text)
    ai_prob = ai_res["ai_prob"]
    uncertainty = ai_res["uncertainty"]

    # Dynamic threshold calibration
    threshold = THRESHOLD_BASE
    if uncertainty > UNCERTAINTY_LIMIT:
        threshold += 0.1  # be stricter when uncertain

    if ai_prob >= threshold:
        # AI detected
        response = {
            "advisory": "AI",
            "original_text": text,
        }
        # Append full AI text to file
        try:
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n--- Detected AI Text ---\n")
                f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"AI Probability: {ai_prob:.4f}\n")
                f.write(text + "\n")
                f.write("-" * 40 + "\n")
        except Exception as fe:
            logger.error(f"Failed to append AI text: {fe}")
    else:
        # Human detected
        response = {
            "advisory": "Human",
        }    
    logger.info(f"AI Probability: {ai_prob:.4f}, Uncertainty: {uncertainty:.4f}, Text: {text[:50]}...")
    return response
