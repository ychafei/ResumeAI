import pdfplumber
import re
import requests
import torch
from transformers import BertTokenizer, BertModel, pipeline
from sentence_transformers import SentenceTransformer, util

# Load the Hugging Face BERT model and tokenizer.
bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
bert_model = BertModel.from_pretrained('bert-base-uncased')

# Load a SentenceTransformer model for semantic similarity.
minilm_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
paraphrase_pipeline = pipeline("text2text-generation", model="t5-small")

def get_bert_embedding(text):
    tokens = bert_tokenizer(text, padding=True, truncation=True, max_length=512, return_tensors="pt")
    with torch.no_grad():
        output = bert_model(**tokens)
    return output.last_hidden_state.mean(dim=1)  

def bert_similarity(cv_text, jd_text):
    cv_embedding = get_bert_embedding(cv_text)
    jd_embedding = get_bert_embedding(jd_text)
    similarity = torch.nn.functional.cosine_similarity(cv_embedding, jd_embedding)
    return similarity.item() * 100 

def minilm_similarity(cv_text, jd_text):
    embeddings = minilm_model.encode([cv_text, jd_text])
    return util.pytorch_cos_sim(embeddings[0], embeddings[1]).item() * 100  # Convert to percentage

def generate_rule_based_suggestions(cv_text):
    suggestions = []
    if "Skills" not in cv_text:
        suggestions.append("Consider adding a 'Skills' section to highlight relevant abilities.")
    if re.search(r'\d{4}-\d{4}', cv_text) is None:
        suggestions.append("Add education or work experience dates for clarity.")
    if len(cv_text.split()) < 150:
        suggestions.append("Your resume seems short. Consider elaborating on your experience.")
    return suggestions

def suggest_missing_keywords(cv_text, jd_text):
    keywords = minilm_model.encode([cv_text, jd_text])
    similarity_score = util.pytorch_cos_sim(keywords[0], keywords[1]).item()
    return f"Consider adding relevant keywords for better match. Estimated similarity gain: {round(100 - similarity_score, 2)}%"

def check_grammar(text):
    url = "https://api.languagetool.org/v2/check"
    data = {"text": text, "language": "en-US"}
    response = requests.post(url, data=data)
    errors = response.json()["matches"]
    return [error["message"] for error in errors]

def check_formatting_issues(cv_text):
    issues = []
    if cv_text.count("\n") < 5:
        issues.append("Consider using more bullet points instead of long paragraphs.")
    if "@" not in cv_text:
        issues.append("Missing email address. Ensure contact details are included.")
    return issues

def analyze_resume(cv_text, jd_text):
    bert_score = bert_similarity(cv_text, jd_text)
    minilm_score = minilm_similarity(cv_text, jd_text)
    final_score = round((bert_score + minilm_score) / 2, 2)

    suggestions = []
    suggestions.extend(generate_rule_based_suggestions(cv_text))
    suggestions.append(suggest_missing_keywords(cv_text, jd_text))
    suggestions.extend(check_grammar(cv_text))
    suggestions.extend(check_formatting_issues(cv_text))

    return {
        "match_score": final_score,
        "suggestions": suggestions
    }
