from flask import Flask, render_template, flash, session, redirect, url_for, send_from_directory
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
import os

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024
app.config['UPLOAD_PATH'] = os.path.join(app.root_path, 'uploads')
app.config['SECRET_KEY'] = 'awdejvaneio'

import uuid
def random_filename(filename):
    ext = 'bvm'
    new_filename = uuid.uuid4().hex + ext
    return new_filename

class UploadForm(FlaskForm):
    bvm_file = FileField('Upload BVM', validators=[
        FileRequired(), FileAllowed(['bvm'])
    ])
    submit = SubmitField()

@app.route('/uploaded-bvm')
def show_bvm_decompile():
    return render_template('uploaded.html')

@app.route('/uploads/<path:filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = UploadForm()
    if form.validate_on_submit():
        f = form.bvm_file.data
        filename = random_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        flash('Upload success.')
        session['filenames'] = [filename]
        return redirect(url_for('show_bvm_decompile'))
    return render_template('index.html', form=form)