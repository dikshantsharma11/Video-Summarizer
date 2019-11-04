from flask import Flask, request, redirect, url_for, render_template, flash, send_file
import os
from werkzeug.utils import secure_filename
from models import basic

UPLOAD_FOLDER = 'static/video/input/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50*1024*1024  # upload limit 50MB
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            basic.main(os.path.join(
                app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('processed', filename=filename))
    return render_template('index.html')


@app.route('/out/<filename>')
def processed(filename):
    x = basic.graph("static/video/output/output.mp4",
     os.path.join(app.config['UPLOAD_FOLDER'], filename), basic.fps)
    return render_template('video-out.html', filename=filename,x=x)


@app.route('/download')
def download():
    return send_file('static/video/output/output.mp4', as_attachment=True, attachment_filename='processed-video.mp4', cache_timeout=0)



if __name__ == '__main__':
    app.run(debug=True)
