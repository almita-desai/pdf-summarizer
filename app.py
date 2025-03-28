import os
from flask import Flask,request,jsonify
app=Flask(__name__)

@app.route('/uploads',methods=["POST"])
def upload_pdf():
    file=request.files.get('file')
    if not file or not file.filename.endswith('.pdf'):
        return "invalid file",400
    
    os.makedirs("uploads",exist_ok=True)
    file.save(os.path.join('uploads',file.filename))
    return "file uploaded",200


if __name__=='__main__':
    app.run(debug=True)
