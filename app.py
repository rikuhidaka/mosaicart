'''
    とりあえずこれだけで動くようにした。
    source.jpgとout.pngの表示はできるようになったが2回目以降は自動で更新してくれない
    強引だけどchromeとかでshift+F5(super reload)押せば更新される。改善する必要あり。
'''

from flask import Flask, redirect, render_template, request, session, url_for, flash
from flask_dropzone import Dropzone
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class

import os
import shutil
import urllib3
import subprocess
import json
import requests
from PIL import Image

app = Flask(__name__)
dropzone = Dropzone(app)

URL = "http://127.0.0.1:5000/upload/" 
UPLOAD_FOLDER = './static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['JPG', 'jpg', 'jpeg'])

app.config['SECRET_KEY'] = 'supersecretkeygoeshere'

# Dropzone settings
app.config['DROPZONE_UPLOAD_MULTIPLE'] = True
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image/*'
app.config['DROPZONE_REDIRECT_VIEW'] = 'results'

# Uploads settings
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + '/subdata'

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
            print (file_urls)
            
        session['file_urls'] = file_urls
        return "uploading..."
    # return dropzone template on GET request    
    return render_template('index.html')

@app.route('/source',methods=['POST'])
def get_source():
    app.config['UPLOAD_FOLDER'] = './static'
    if request.method == 'POST':
        img_files = request.files
        for f in img_files:
            img_file = request.files.get(f)
            if img_file and allowed_file(img_file.filename):
                img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'source.jpg'))
                #return render_template('index.html')
                #return redirect(url_for('index'))    
                return redirect(url_for('results'))
                #return render_template('index.html', img_url=os.listdir(UPLOAD_FOLDER)[::-1])
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
        subprocess.call(['python3','features.py'])
        #app.logger.info("特徴量の計算")
        while os.path.exists("features.json") == False:
            print ("waiting")
        subprocess.call(['python3','Mosaicjson.py'])
        file_urls = session['file_urls']
        session.pop('file_urls', None)
        return render_template('results.html')

@app.route('/mosaic',methods=['POST'])
def post():
    app.config['UPLOAD_FOLDER'] = './'
    if request.method == 'POST':
        if os.path.exists("producemosaicart.json"):
            subprocess.call(['python3', 'producemosaic.py'])
        else:
            return redirect(url_for('post'))
        #return redirect(url_for('mosaic'))
        return render_template('mosaic.html')

@app.route('/backtop',methods=['POST'])
def mosaic():
    #subprocess.call(['python3','producemosaic.py'])
    #staticとsubdataの内容を削除
    target_dir = 'static'
    shutil.rmtree(target_dir)
    os.mkdir(target_dir)
    target_dir2 = 'subdata'
    shutil.rmtree(target_dir2)
    os.mkdir(target_dir2)
    #.jsonの削除
    os.remove('features.json')
    os.remove('producemosaicart.json')
    #最初の画面にもどる
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8888)


