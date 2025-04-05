import os
from flask import Flask,request,jsonify
import string
import fitz
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
import nltk
import contractions
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
import spacy
from lemminflect import getInflection

nltk.download('stopwords')
nltk.download('punkt')
nlp = spacy.load("en_core_web_sm")

MAX_FILE_SIZE = 5 * 1024 * 1024 
def read_pdf(filename):
    doc=fitz.open(filename)
    text=[page.get_text() for page in doc]

    return '\n'.join(text).rstrip('\n')

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
    sentence_count=max(3,len(sentences)//3)
    parser=PlaintextParser.from_string(text,Tokenizer("english"))
    summarizer=LsaSummarizer()
    top_sentences=summarizer(parser.document,sentence_count)
    return " ".join(str(sentence) for sentence in top_sentences)

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


def apply_abstractive_summary(text):
    sentences=sent_tokenize(text)
    rewritten=[]
    for sentence in sentences:
        if detect_passive(sentence):
            active_version=rewrite_to_active(sentence)
            rewritten.append(active_version)
        else:
            rewritten.append(sentence)
    return " ".join(rewritten)

app=Flask(__name__)

@app.route('/uploads',methods=["POST"])
def upload_pdf():
    file=request.files.get('file')
    if not file or not file.filename.endswith('.pdf'):
        return "invalid file",400
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({"error": "File size exceeds 5MB limit."}), 400

    
    os.makedirs("uploads",exist_ok=True)
    filename=os.path.join('uploads',file.filename)
    file.save(filename)
    try:
        text=read_pdf(filename)
        # cleaned_text=clean_text(text)
        top_sentences=extract_top_sentences(text)
        abstractive_summary=apply_abstractive_summary(top_sentences)
        return jsonify({'text':abstractive_summary})
    except Exception as e:
        return jsonify({'error': str(e)}),500
    
    finally:
        if os.path.exists(filename):
            os.remove(filename)
if __name__=='__main__':
    app.run(debug=True)
