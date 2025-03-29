import os
from flask import Flask,request,jsonify
import fitz

def read_pdf(filename):
    doc=fitz.open(filename)
    text=[page.get_text() for page in doc]

    return '\n'.join(text).rstrip('\n')

app=Flask(__name__)

@app.route('/uploads',methods=["POST"])
def upload_pdf():
    file=request.files.get('file')
    if not file or not file.filename.endswith('.pdf'):
        return "invalid file",400
    
    os.makedirs("uploads",exist_ok=True)
    filename=os.path.join('uploads',file.filename)
    file.save(filename)
    text=read_pdf(filename)
    return jsonify({'text':text})

if __name__=='__main__':
    app.run(debug=True)


#make commit first-Add Pdf text extraction functionality