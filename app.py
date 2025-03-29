import os
from flask import Flask,request,jsonify
import string
import fitz
from nltk.corpus import stopwords
import nltk
import contractions
nltk.download('stopwords')


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

def clean_text(text):
    text=expand_contractions(text)
    text=text.lower()
    text=text.translate(str.maketrans('','',string.punctuation))
    text=' '.join(text.split())
    text=text.strip()
    text=remove_stopwords(text)
    return text


app=Flask(__name__)

@app.route('/uploads',methods=["POST"])
def upload_pdf():
    file=request.files.get('file')
    if not file or not file.filename.endswith('.pdf'):
        return "invalid file",400
    
    os.makedirs("uploads",exist_ok=True)
    filename=os.path.join('uploads',file.filename)
    file.save(filename)
    try:
        text=read_pdf(filename)
        cleaned_text=clean_text(text)
        return jsonify({'text':cleaned_text})
    except Exception as e:
        return jsonify({'error': str(e)}),500
    
    finally:
        if os.path.exists(filename):
            os.remove(filename)
if __name__=='__main__':
    app.run(debug=True)
