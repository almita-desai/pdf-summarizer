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

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')

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

app=Flask(__name__)

@app.route('/uploads',methods=["POST"])
def upload_pdf():
    file=request.files.get('file')
    if not file or not file.filename.endswith('.pdf'):
        return "invalid file",400
    file.seek(0, os.SEEK_END)  # Move cursor to end of file
    file_size = file.tell()
    file.seek(0)  # Reset cursor
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({"error": "File size exceeds 5MB limit."}), 400

    
    os.makedirs("uploads",exist_ok=True)
    filename=os.path.join('uploads',file.filename)
    file.save(filename)
    try:
        text=read_pdf(filename)
        # cleaned_text=clean_text(text)
        top_sentences=extract_top_sentences(text)
        return jsonify({'text':top_sentences})
    except Exception as e:
        return jsonify({'error': str(e)}),500
    
    finally:
        if os.path.exists(filename):
            os.remove(filename)
if __name__=='__main__':
    app.run(debug=True)
