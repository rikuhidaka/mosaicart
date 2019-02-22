from flask import Flask, redirect, render_template, request, session, url_for, flash
from flask_dropzone import Dropzone
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class

import os
import urllib3
import subprocess
import json
import requests
from PIL import Image

app = Flask(__name__)
dropzone = Dropzone(app)

URL = "http://127.0.0.1:5000/upload/" 
UPLOAD_FOLDER = './source'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['JPG', 'jpg', 'jpeg'])

app.config['SECRET_KEY'] = 'supersecretkeygoeshere'

# Dropzone settings
app.config['DROPZONE_UPLOAD_MULTIPLE'] = True
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image/*'
app.config['DROPZONE_REDIRECT_VIEW'] = 'results'

# Uploads settings
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + '/uploads'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    
    # set session for image results
    if "file_urls" not in session:
        session['file_urls'] = []
    # list to hold our uploaded image urls
    file_urls = session['file_urls']

    # handle image upload from Dropszone
    if request.method == 'POST':
        file_obj = request.files
        for f in file_obj:
            file = request.files.get(f)
            # save the file with to our photos folder
            filename = photos.save(
                file,
                name=file.filename    
            )
            # append image urls
            file_urls.append(photos.url(filename))
            
        session['file_urls'] = file_urls
        return "uploading..."
    # return dropzone template on GET request    
    return render_template('index.html')

@app.route('/source',methods=['POST'])
def get_source():
    if request.method == 'POST':
        img_files = request.files
        for f in img_files:
            img_file = request.files.get(f)
            if img_file and allowed_file(img_file.filename):
                img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'source.jpg'))    
                return redirect(url_for('results'))
                #return render_template('source.html', img_url='./source' + img_file.filename)
            else:
                flash('対応していません')
                return redirect(url_for('results'))
    else:
        return redirect(url_for('results'))


@app.route('/results')
def results():
    
    # redirect to home if no images to display
    if "file_urls" not in session or session['file_urls'] == []:
        return redirect(url_for('index'))
        
    # set the file_urls and remove the session variable
    file_urls = session['file_urls']
    #session.pop('file_urls', None)
    
    return render_template('index.html', file_urls=file_urls)

@app.route('/post', methods=['POST'])
def sending_file():
    if request.method == 'POST':
        subprocess.call(['python3','feat.py'])
        app.logger.info("特徴量の計算")
        url = "http://127.0.0.1:5000/post/" 
        url2 = "http://127.0.0.1:5000/source/"
        headers = {"Content-Type" : "application/json"}
        with open("features.json", 'r') as f:
            json_data = json.load(f)
        # httpリクエストを準備してPOST
        #source_img = Image.open("source/source.jpg")
        #res = requests.post(url, files=source_img)
        file = {'source.jpg': open('source/source.jpg', 'rb')}
        r = requests.post(url, headers=headers,json=json_data)
        res = requests.post(url2, files=file)
        file_urls = session['file_urls']
        session.pop('file_urls', None)
        return render_template('results.html')

@app.route('/mosaic',methods=['POST'])
def post():
    app.config['UPLOAD_FOLDER'] = './'
    if request.method == 'POST':
        url3 = "http://127.0.0.1:5000/get/"
        headers = {"Content-Type" : "application/json"}
        #out.jsonの受け取り
        r_get = requests.get(url3, headers=headers)
        with open("out.json",'w') as f:
            json.dump(r_get.json(),f,indent=4)
        return redirect(url_for('mosaic'))

@app.route('/art')
def mosaic():
    subprocess.call(['python3','producemosaicart.py'])
    app.logger.info("モザイクアート作成中")
    img = Image.open('out.jpg')
    return render_template('mosaic.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8888)


