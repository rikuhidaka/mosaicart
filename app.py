'''
    とりあえずこれだけで動くようにした。
    source.jpgとout.pngの表示はできるようになったが2回目以降は自動で更新してくれない
    強引だけどchromeとかでshift+F5(super reload)押せば更新される。改善する必要あり。
'''

from flask import Flask, redirect, render_template, request, session, url_for, flash, send_from_directory
from flask_dropzone import Dropzone
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class


import os
import shutil
import urllib3
import subprocess
import json
import requests
from PIL import Image
from collections import OrderedDict

app = Flask(__name__)
dropzone = Dropzone(app)

count = 0

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
app.config['UPLOADED_SOURCE_DEST'] = os.getcwd() + '/source_img'
app.config['UPLOADED_MOSAIC_DEST'] = os.getcwd() + '/mosaic_img'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB

source = UploadSet('source',IMAGES)
configure_uploads(app, source)
patch_request_class(app)  # set maximum file size, default is 16MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def resizemosaic(tl_w,tl_h,br_w,br_h):
    with open('producemosaicart.json','r') as f:
        mosaic = json.load(f,object_pairs_hook=OrderedDict)
    
    blk_size = mosaic['block_size']
    mosaic_w = mosaic['mosaic_size_w']
    tile = mosaic['images']
    images = []
    
    h1 = int(tl_h)//blk_size
    w1 = int(tl_w)//blk_size
    h2 = int(br_h)//blk_size
    w2 = int(br_w)//blk_size
    if(int(tl_h)%blk_size >= blk_size/2):
        h1+=1
    if(int(tl_w)%blk_size >= blk_size/2):
        w1+=1
    if(int(br_h)%blk_size >= blk_size/2):
        h2+=1
    if(int(br_w)%blk_size >= blk_size/2):
        w2+=1
    
    print(h2-h1)
    print(w2-w1)
    
    for j in range(h2-h1):
        for i in range(w2-w1):
            images.append(tile[w1+i+((h1+j)*mosaic_w)])
    out = OrderedDict()
    out['block_size'] = blk_size
    out['mosaic_size_h'] = h2-h1
    out['mosaic_size_w'] = w2-w1
    out['images'] = images
    
    #print(out['images'])
    fw = open('resizemosaic.json','w')
    json.dump(out,fw,indent=4)
    return tl_w+tl_h+br_w+br_h

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
def get_source():# set session for image results
    if "img_url" not in session:
        session['img_url'] = []
    # list to hold our uploaded image urls
    img_url = session['img_url']

    if request.method == 'POST':
        img_files = request.files
        for f in img_files:
            img_file = request.files.get(f)
            filename = source.save(
                img_file,
                name="source.jpg"
            )
            img_url = source.url(filename)
            # img_urls.append(source.url(filename))
        # session['img_urls'] = img_urls
        session['img_url'] = img_url
        return "uploading"
    return redirect(url_for('results'))

@app.route('/results')
def results():
    
    # redirect to home if no images to display
    """
    if "file_urls" not in session or session['file_urls'] == []:
        print('hello')
        return redirect(url_for('index'))
    """
    
    if "img_url" not in session or session['img_url'] == []:
        return redirect(url_for('index'))
    # set the file_urls and remove the session variable
    file_urls = session['file_urls']
    img_url = session['img_url']
    # img_urls = session['img_urls']
    #session.pop('file_urls', None)

    filename = img_url.split("/")[-1]
    # return render_template('index.html', file_urls=file_urls, img_urls=img_urls)
    print(img_url)
    print(filename)

    return render_template('index.html', file_urls=file_urls, source_name=filename)


@app.route('/post', methods=['POST'])
def sending_file():
    if request.method == 'POST':
        subprocess.call(['python','features.py'])
        #app.logger.info("特徴量の計算")
        #while os.path.exists("features.json") == False:
        #    print ("waiting")
        img_url = session['img_url']
        filename = img_url.split("/")[-1]
        subprocess.call(['python','Mosaicjson.py',filename])
        file_urls = session['file_urls']
        session.pop('img_url',None)
        session.pop('file_urls', None)
        return render_template('results.html')

@app.route('/mosaic',methods=['POST'])
def post():
    app.config['UPLOAD_FOLDER'] = './'
    if request.method == 'POST':
        if os.path.exists("producemosaicart.json"):
            subprocess.call(['python', 'producemosaic.py'])
        else:
            return redirect(url_for('post'))
        #return redirect(url_for('mosaic'))

        return render_template('mosaic.html')

@app.route('/re_mosaic', methods=['POST'])
def re_mosaic():
    if request.method == 'POST':
        coordinate_x1 = request.form['test1']
        coordinate_y1 = request.form['test2']
        coordinate_x2 = request.form['test3']
        coordinate_y2 = request.form['test4']
        remosaic_name = resizemosaic(coordinate_x1,coordinate_y1,coordinate_x2,coordinate_y2)
        subprocess.call(['python', 'remosaic.py', remosaic_name])
        path = 'mosaic_img/' + remosaic_name + '.png'
        return render_template('mosaic.html', remosaic_url=path)

@app.route('/backtop',methods=['POST'])
def mosaic():
    #subprocess.call(['python3','producemosaic.py'])
    #staticとsubdataの内容を削除
    target_dir = 'source_img'
    shutil.rmtree(target_dir)
    os.mkdir(target_dir)
    target_dir2 = 'mosaic_img'
    shutil.rmtree(target_dir2)
    os.mkdir(target_dir2)
    target_dir2 = 'subdata'
    shutil.rmtree(target_dir2)
    os.mkdir(target_dir2)
    #.jsonの削除
    os.remove('features.json')
    os.remove('producemosaicart.json')
    
    #resizemosaic.jsonも消したい
    #os.remove('resizemosaic.json')
    
    #最初の画面にもどる
    return redirect(url_for('index'))

@app.route('/_uploads/source/<path:filepath>')
def source_img(filepath):
    return send_from_directory(app.config['UPLOADED_SOURCE_DEST'], filepath)

@app.route('/mosaic_img/<path:filepath>')
def mosaic_img(filepath):
    return send_from_directory(app.config['UPLOADED_MOSAIC_DEST'], filepath)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)

