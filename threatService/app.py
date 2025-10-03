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
# Load the spaCy model for keyword/sentence extraction
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print(f"Spacy model not found. Please run: python -m spacy download en_core_web_sm")
    nlp = None

# Load the pre-trained model for toxicity detection
# This will download the model the first time you run it
print("Loading toxicity detection model...")
toxicity_pipeline = pipeline("text-classification", model="unitary/toxic-bert")
print("Models loaded successfully.")


def analyze_text(paragraph: str):
    """
    Analyzes a paragraph for its main sentence, keywords, and toxicity.
    """
    if not nlp:
        return None, None, None

    # --- 1. Toxicity Analysis (NEW) ---
    toxicity_results = toxicity_pipeline(paragraph)[0] # Get the top result
    
    # --- 2. Main Sentence & Keyword Extraction ---
    doc = nlp(paragraph)
    
    # Keyword Extraction
    keywords = []
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "LOC", "PRODUCT", "EVENT"]:
            keywords.append(ent.text.lower())
    for chunk in doc.noun_chunks:
        cleaned_chunk = re.sub(r'^(the|a|an)\s+', '', chunk.text.lower())
        keywords.append(cleaned_chunk)
    keyword_counts = Counter(keywords)

    # Main Sentence Extraction
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

    return main_sentence.text if main_sentence else None, keyword_counts, toxicity_results

# --- Main Execution Block ---
if __name__ == "__main__":
    try:
        with open(INPUT_FILENAME, 'r', encoding='utf-8') as f:
            paragraph_to_analyze = f.read()
        print(f"Successfully read data from '{INPUT_FILENAME}'. Analyzing...")

        main_sentence, extracted_keywords, toxicity = analyze_text(paragraph_to_analyze)

        if main_sentence and extracted_keywords and toxicity:
            # Build the structured JSON output
            keyword_list = [{"term": term, "count": count} for term, count in extracted_keywords.most_common()]
            
            output_data = {
                "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "toxicity_analysis": {
                    "label": toxicity['label'],
                    "confidence_score": round(toxicity['score'], 4)
                },
                "main_sentence": main_sentence,
                "keywords": keyword_list
            }

            # Save the dictionary as a formatted JSON file
            with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f_out:
                json.dump(output_data, f_out, indent=4)
            
            print(f"✅ Success! Full analysis saved to '{OUTPUT_FILENAME}'")
        else:
             print("Could not complete the analysis.")

    except FileNotFoundError:
        print(f"❌ Error: Please create a file named '{INPUT_FILENAME}' and add your text.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")