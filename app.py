import os
import uuid
import json 
from flask import Flask,request,jsonify
import fitz
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
import nltk
import contractions
import spacy
from lemminflect import getInflection
from werkzeug.utils import secure_filename
from flask import render_template
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from nltk.tokenize import sent_tokenize

nltk.data.path.append("./nltk_data")
try:
    nlp = spacy.load("en_core_web_sm")
except:
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


MAX_FILE_SIZE =  1 * 1024 * 1024 
def read_pdf(filename):
    doc=fitz.open(filename)
    text=[page.get_text() for page in doc]

    return '\n'.join(text).rstrip('\n')

def load_simplification_rules(path='simplification_rules.json'):
    with open(path, 'r') as file:
        return json.load(file)
simplification_rules = load_simplification_rules()

def expand_contractions(text):
    return contractions.fix(text)

def remove_stopwords(text):
    stop_words=set(stopwords.words('english'))
    text=text.split()
    text=[word for word in text if word not in stop_words]
    return ' '.join(text)

# def clean_text(text):
#     text=expand_contractions(text)
#     text=text.lower()
#     text=text.translate(str.maketrans('','',string.punctuation))
#     text=' '.join(text.split())
#     text=text.strip()
#     text=remove_stopwords(text)
#     return text

def extract_top_sentences(text):
    sentences = sent_tokenize(text)
    if len(sentences) < 3:
        return text

    sentence_count = max(3, len(sentences) // 3)

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(sentences)

    sim_matrix = cosine_similarity(tfidf_matrix)

    nx_graph = nx.from_numpy_array(sim_matrix)
    scores = nx.pagerank(nx_graph)

    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    top_sentences = [s for _, s in ranked_sentences[:sentence_count]]

    if sentences[0] not in top_sentences:
        top_sentences.append(sentences[0])
    if sentences[-1] not in top_sentences:
        top_sentences.append(sentences[-1])

    sorted_summary = sorted(top_sentences, key=lambda s: sentences.index(s))

    return " ".join(sorted_summary)


def detect_passive(text):
    doc=nlp(text)
    for token in doc:
        if token.dep_=="auxpass":
            return True
    return False

def rewrite_to_active(sentence):
    doc=nlp(sentence)
    subject=None
    verb=None
    agent=None
    aux=None
    for token in doc:
        if token.dep_=='nsubjpass':
            subject=token
        elif token.dep_=='auxpass':
            aux=token
        elif token.dep_=='ROOT':
            verb=token
        elif token.dep_=='agent':
            for child in token.children:
                if child.dep_=='pobj':
                    agent=child
    if subject and verb and agent:
        try:
            active_verb=getInflection(verb.lemma_,tag='VBD')[0]
        except:
            active_verb=verb.text
        return f"{agent.text.capitalize()} {active_verb} {subject.text}."
    return sentence

def simplify_sentence(sentence):
    for long,short in simplification_rules.items():
        sentence=sentence.replace(long,short)
    return sentence 

def apply_abstractive_summary(text):
    sentences=sent_tokenize(text)
    rewritten=[]
    for sentence in sentences:
        if detect_passive(sentence):
            sentence=rewrite_to_active(sentence)
        simplified_sentence=simplify_sentence(sentence)
        rewritten.append(simplified_sentence)
    return " ".join(rewritten)

app=Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/uploads',methods=["POST"])
def upload_pdf():
    file=request.files.get('file')
    if not file or not file.filename.endswith('.pdf'):
        return jsonify({"error": "Invalid file format. Please upload a PDF file."}), 400
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({"error": "File size exceeds limit."}), 400

    
    os.makedirs("uploads",exist_ok=True)
    filename=secure_filename(file.filename)
    unique_filename = f"{os.path.splitext(filename)[0]}_{uuid.uuid4().hex}.pdf"
    file_path = os.path.join('uploads', unique_filename)


    try:
        file.save(file_path)    
        text=read_pdf(file_path)
        # cleaned_text=clean_text(text)
        top_sentences=extract_top_sentences(text)
        abstractive_summary=apply_abstractive_summary(top_sentences)
        return jsonify({'text':abstractive_summary})
    except (ValueError, FileNotFoundError, RuntimeError) as e:
        return jsonify({
            "error": f"An error occurred while processing the file: {str(e)}"
        }), 500
    finally:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass


     
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)