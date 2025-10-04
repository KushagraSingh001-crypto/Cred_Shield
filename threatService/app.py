import spacy
from collections import Counter
import re
import json
from datetime import datetime, timezone
from string import punctuation
from transformers import pipeline

# --- Configuration ---
INPUT_FILENAME = "input.txt"
OUTPUT_FILENAME = "keywords_output.json"

# --- Model Loading ---
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print(f"Spacy model not found. Please run: python -m spacy download en_core_web_sm")
    nlp = None

print("Loading toxicity detection model...")
toxicity_pipeline = pipeline("text-classification", model="unitary/toxic-bert")

print("Loading AI detection model...")
ai_detector = pipeline("text-classification", model="Hello-SimpleAI/chatgpt-detector-roberta")
# Fallback option (uncomment if needed):
# ai_detector = pipeline("text-classification", model="roberta-base-openai-detector")
print("Models loaded successfully.")


def analyze_text(paragraph: str):
    if not nlp:
        return None, None, None, None

    # --- 1. Toxicity Analysis ---
    toxicity_results = toxicity_pipeline(paragraph)[0]

    # --- 2. AI Detection ---
    ai_results = ai_detector(paragraph)[0]
    print(f"Raw AI detection result: {ai_results}")  # Log for debugging

    # Updated: Handle labels for Hello-SimpleAI/chatgpt-detector-roberta and fallback model
    if ai_results["label"] in ["ChatGPT", "LABEL_1"]:  # ChatGPT for new model, LABEL_1 for old
        is_ai_generated = True
        ai_confidence = ai_results["score"]
    elif ai_results["label"] in ["Human", "LABEL_0"]:  # Human for new model, LABEL_0 for old
        is_ai_generated = False
        ai_confidence = 1 - ai_results["score"]  # Adjust to AI probability
    else:
        print(f"Warning: Unexpected label '{ai_results['label']}' from AI detector. Treating as human-written.")
        is_ai_generated = False
        ai_confidence = 1 - ai_results["score"]  # Fallback to avoid crashes

    # --- 3. Main Sentence & Keyword Extraction ---
    doc = nlp(paragraph)
    keywords = []
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "LOC", "PRODUCT", "EVENT"]:
            keywords.append(ent.text.lower())
    for chunk in doc.noun_chunks:
        cleaned_chunk = re.sub(r'^(the|a|an)\s+', '', chunk.text.lower())
        keywords.append(cleaned_chunk)
    keyword_counts = Counter(keywords)

    word_frequencies = {}
    for word in doc:
        if word.text.lower() not in nlp.Defaults.stop_words and word.text.lower() not in punctuation:
            word_frequencies.setdefault(word.text, 0)
            word_frequencies[word.text] += 1

    max_frequency = max(word_frequencies.values()) if word_frequencies else 1
    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word] / max_frequency)

    sentence_scores = {}
    for sent in doc.sents:
        for word in sent:
            if word.text in word_frequencies.keys():
                sentence_scores.setdefault(sent, 0)
                sentence_scores[sent] += word_frequencies[word.text]

    main_sentence = max(sentence_scores, key=sentence_scores.get) if sentence_scores else None

    return main_sentence.text if main_sentence else None, keyword_counts, toxicity_results, {
        "is_ai_generated": is_ai_generated,
        "ai_confidence_score": round(ai_confidence, 4)
    }

# --- Main Execution Block ---
if __name__ == "__main__":
    try:
        with open(INPUT_FILENAME, 'r', encoding='utf-8') as f:
            paragraph_to_analyze = f.read()
        print(f"Successfully read data from '{INPUT_FILENAME}'. Analyzing...")

        main_sentence, extracted_keywords, toxicity, ai_detection = analyze_text(paragraph_to_analyze)

        if main_sentence and extracted_keywords and toxicity and ai_detection:
            keyword_list = [{"term": term, "count": count} for term, count in extracted_keywords.most_common()]

            output_data = {
                "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "is_ai_generated": ai_detection["is_ai_generated"],
                "ai_confidence_score": ai_detection["ai_confidence_score"],
                "toxicity_analysis": {
                    "label": toxicity['label'],
                    "confidence_score": round(toxicity['score'], 4)
                },
                "main_sentence": main_sentence,
                "keywords": keyword_list
            }

            with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f_out:
                json.dump(output_data, f_out, indent=4)

            print(f"✅ Success! Full analysis saved to '{OUTPUT_FILENAME}'")
        else:
            print("Could not complete the analysis.")

    except FileNotFoundError:
        print(f"❌ Error: Please create a file named '{INPUT_FILENAME}' and add your text.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")






# import spacy
# from collections import Counter
# import re
# import json
# from datetime import datetime, timezone
# from string import punctuation
# from transformers import pipeline

# # --- Configuration ---
# INPUT_FILENAME = "input.txt"
# OUTPUT_FILENAME = "keywords_output.json"

# # --- Model Loading ---
# # Load the spaCy model for keyword/sentence extraction
# try:
#     nlp = spacy.load("en_core_web_sm")
# except OSError:
#     print(f"Spacy model not found. Please run: python -m spacy download en_core_web_sm")
#     nlp = None

# # Load the pre-trained model for toxicity detection
# # This will download the model the first time you run it
# print("Loading toxicity detection model...")
# toxicity_pipeline = pipeline("text-classification", model="unitary/toxic-bert")
# print("Models loaded successfully.")


# def analyze_text(paragraph: str):
#     """
#     Analyzes a paragraph for its main sentence, keywords, and toxicity.
#     """
#     if not nlp:
#         return None, None, None

#     # --- 1. Toxicity Analysis (NEW) ---
#     toxicity_results = toxicity_pipeline(paragraph)[0] # Get the top result

#     # --- 2. Main Sentence & Keyword Extraction ---
#     doc = nlp(paragraph)

#     # Keyword Extraction
#     keywords = []
#     for ent in doc.ents:
#         if ent.label_ in ["PERSON", "ORG", "GPE", "LOC", "PRODUCT", "EVENT"]:
#             keywords.append(ent.text.lower())
#     for chunk in doc.noun_chunks:
#         cleaned_chunk = re.sub(r'^(the|a|an)\s+', '', chunk.text.lower())
#         keywords.append(cleaned_chunk)
#     keyword_counts = Counter(keywords)

#     # Main Sentence Extraction
#     word_frequencies = {}
#     for word in doc:
#         if word.text.lower() not in nlp.Defaults.stop_words and word.text.lower() not in punctuation:
#             word_frequencies.setdefault(word.text, 0)
#             word_frequencies[word.text] += 1

#     max_frequency = max(word_frequencies.values()) if word_frequencies else 1
#     for word in word_frequencies.keys():
#         word_frequencies[word] = (word_frequencies[word] / max_frequency)

#     sentence_scores = {}
#     for sent in doc.sents:
#         for word in sent:
#             if word.text in word_frequencies.keys():
#                 sentence_scores.setdefault(sent, 0)
#                 sentence_scores[sent] += word_frequencies[word.text]

#     main_sentence = max(sentence_scores, key=sentence_scores.get) if sentence_scores else None

#     return main_sentence.text if main_sentence else None, keyword_counts, toxicity_results

# # --- Main Execution Block ---
# if __name__ == "__main__":
#     try:
#         with open(INPUT_FILENAME, 'r', encoding='utf-8') as f:
#             paragraph_to_analyze = f.read()
#         print(f"Successfully read data from '{INPUT_FILENAME}'. Analyzing...")

#         main_sentence, extracted_keywords, toxicity = analyze_text(paragraph_to_analyze)

#         if main_sentence and extracted_keywords and toxicity:
#             # Build the structured JSON output
#             keyword_list = [{"term": term, "count": count} for term, count in extracted_keywords.most_common()]

#             output_data = {
#                 "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
#                 "toxicity_analysis": {
#                     "label": toxicity['label'],
#                     "confidence_score": round(toxicity['score'], 4)
#                 },
#                 "main_sentence": main_sentence,
#                 "keywords": keyword_list
#             }

#             # Save the dictionary as a formatted JSON file
#             with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f_out:
#                 json.dump(output_data, f_out, indent=4)

#             print(f"✅ Success! Full analysis saved to '{OUTPUT_FILENAME}'")
#         else:
#              print("Could not complete the analysis.")

#     except FileNotFoundError:
#         print(f"❌ Error: Please create a file named '{INPUT_FILENAME}' and add your text.")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")





# import spacy
# from collections import Counter
# import re
# import json
# from datetime import datetime, timezone
# from string import punctuation
# from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
# import torch
# import math

# # --- Configuration ---
# INPUT_FILENAME = "input.txt"
# OUTPUT_FILENAME = "keywords_output.json"

# # --- Model Loading ---
# try:
#     nlp = spacy.load("en_core_web_sm")
# except OSError:
#     print(f"Spacy model not found. Please run: python -m spacy download en_core_web_sm")
#     nlp = None

# print("Loading sentiment/toxicity detection model...")
# sentiment_pipeline = pipeline("text-classification", model="nlptown/bert-base-multilingual-uncased-sentiment")

# print("Loading AI-generated text detection model...")
# ai_detector_pipeline = pipeline("text-classification", model="openai-community/roberta-large-openai-detector")

# print("Loading perplexity model...")
# perplexity_model = AutoModelForCausalLM.from_pretrained("distilgpt2")
# perplexity_tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
# print("Models loaded successfully.")

# def calculate_perplexity(paragraph: str) -> float:
#     """
#     Calculates perplexity using distilgpt2. Lower perplexity suggests AI-generated text.
#     """
#     encodings = perplexity_tokenizer(paragraph, return_tensors="pt", truncation=True, max_length=512)
#     input_ids = encodings["input_ids"]
#     with torch.no_grad():
#         outputs = perplexity_model(input_ids, labels=input_ids)
#         loss = outputs.loss
#         perplexity = math.exp(loss.item())
#     print(f"DEBUG: Perplexity calculated: {perplexity:.2f}")
#     return perplexity

# def detect_ai_generated(paragraph: str) -> tuple[bool, float]:
#     """
#     Detects if text is AI-generated using perplexity as the primary criterion.
#     Returns a tuple of (is_ai_generated: bool, confidence_score: float).
#     Flags as AI-generated if perplexity < 50, else human-written.
#     """
#     if not nlp:
#         return False, 0.0

#     # Model-based detection (for confidence score only)
#     result = ai_detector_pipeline(paragraph, truncation=True, max_length=512)[0]
#     confidence_score = result["score"]
#     print(f"DEBUG: AI Detector - Label: {result['label']}, Confidence: {confidence_score:.4f}")

#     # Perplexity-based detection (sole criterion)
#     perplexity = calculate_perplexity(paragraph)
#     is_ai_generated = perplexity < 50
#     print(f"DEBUG: is_ai_generated: {is_ai_generated}, Perplexity: {perplexity:.2f}")

#     return is_ai_generated, confidence_score

# def analyze_text(paragraph: str):
#     """
#     Analyzes a paragraph for its main sentence, keywords, sentiment/toxicity, and AI-generated status.
#     """
#     if not nlp:
#         return None, None, None, None, None

#     # --- 1. AI-Generated Text Detection ---
#     is_ai_generated, ai_confidence = detect_ai_generated(paragraph)

#     # --- 2. Sentiment/Toxicity Analysis ---
#     sentiment_results = sentiment_pipeline(paragraph, truncation=True, max_length=512)[0]
#     # Map sentiment to toxicity (1-2 stars: toxic, 3-5 stars: non-toxic)
#     sentiment_score = int(sentiment_results["label"].split()[0])
#     toxicity_label = "toxic" if sentiment_score <= 2 else "non-toxic"
#     toxicity_confidence = sentiment_results["score"]
#     print(f"DEBUG: Sentiment - Label: {sentiment_results['label']}, Confidence: {toxicity_confidence:.4f}, Toxicity: {toxicity_label}")

#     # --- 3. Main Sentence & Keyword Extraction ---
#     doc = nlp(paragraph)

#     # Keyword Extraction
#     keywords = []
#     for ent in doc.ents:
#         if ent.label_ in ["PERSON", "ORG", "GPE", "LOC", "PRODUCT", "EVENT"]:
#             keywords.append(ent.text.lower())
#     for chunk in doc.noun_chunks:
#         cleaned_chunk = re.sub(r'^(the|a|an)\s+', '', chunk.text.lower())
#         keywords.append(cleaned_chunk)
#     keyword_counts = Counter(keywords)

#     # Main Sentence Extraction
#     word_frequencies = {}
#     for word in doc:
#         if word.text.lower() not in nlp.Defaults.stop_words and word.text.lower() not in punctuation:
#             word_frequencies.setdefault(word.text, 0)
#             word_frequencies[word.text] += 1

#     max_frequency = max(word_frequencies.values()) if word_frequencies else 1
#     for word in word_frequencies.keys():
#         word_frequencies[word] = (word_frequencies[word] / max_frequency)

#     sentence_scores = {}
#     for sent in doc.sents:
#         for word in sent:
#             if word.text in word_frequencies.keys():
#                 sentence_scores.setdefault(sent, 0)
#                 sentence_scores[sent] += word_frequencies[word.text]

#     main_sentence = max(sentence_scores, key=sentence_scores.get) if sentence_scores else None

#     return main_sentence.text if main_sentence else None, keyword_counts, {
#         "label": toxicity_label,
#         "confidence_score": toxicity_confidence
#     }, is_ai_generated, ai_confidence

# # --- Main Execution Block ---
# if __name__ == "__main__":
#     try:
#         with open(INPUT_FILENAME, 'r', encoding='utf-8') as f:
#             paragraph_to_analyze = f.read()
#         print(f"Successfully read data from '{INPUT_FILENAME}'. Analyzing...")

#         main_sentence, extracted_keywords, toxicity, is_ai_generated, ai_confidence = analyze_text(paragraph_to_analyze)

#         if main_sentence and extracted_keywords:
#             # Build the structured JSON output
#             keyword_list = [{"term": term, "count": count} for term, count in extracted_keywords.most_common()]

#             output_data = {
#                 "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
#                 "is_ai_generated": is_ai_generated,
#                 "ai_confidence_score": round(ai_confidence, 4),
#                 "toxicity_analysis": {
#                     "label": toxicity["label"],
#                     "confidence_score": round(toxicity["confidence_score"], 4)
#                 },
#                 "main_sentence": main_sentence,
#                 "keywords": keyword_list
#             }

#             # Save the dictionary as a formatted JSON file
#             with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f_out:
#                 json.dump(output_data, f_out, indent=4)

#             print(f"✅ Success! Full analysis saved to '{OUTPUT_FILENAME}'")
#         else:
#             print("Could not complete the analysis.")

#     except FileNotFoundError:
#         print(f"❌ Error: Please create a file named '{INPUT_FILENAME}' and add your text.")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
