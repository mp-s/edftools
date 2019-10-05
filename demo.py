# -*- coding: utf-8 -*-
import os
import bvm_decompiler
from flask import Flask, request, url_for, send_from_directory
from werkzeug import secure_filename

ALLOWED_EXTENSIONS = set(['bvm', 'BVM'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

html = '''
    <!DOCTYPE html>
    <title>Upload File</title>
    <h4>bvm上传</h4>
    <form method=post enctype=multipart/form-data>
         <input type=file name=file>
         <input type=submit value=上传>
    </form>
    <br/>
    '''

import uuid
def random_filename(filename):
    ext = '.bvm'
    new_filename = uuid.uuid4().hex + ext
    return new_filename

def allowed_file(filename: str):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/asm', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = random_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_url = url_for('uploaded_file', filename=filename)
            s_bvm = bvm_decompiler.bvm_data(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            list_bvm = s_bvm.asm_decompiler()
            str_ = '<br>'.join(list_bvm)
            return html + str_
    return html

@app.route('/fullstr', methods=['GET', 'POST'])
def upload_file_v2():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = random_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_url = url_for('uploaded_file', filename=filename)
            s_bvm = bvm_decompiler.bvm_data(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            list_str = s_bvm.get_all_str()
            str_ = '<br>'.join(list_str)
            return html + str_
    return html

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=28000,
        debug=False
    )