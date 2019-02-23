#coding=utf-8

#コマンドラインに
#
# $ export FLASK_APP=main.py
# $ flask run
#
#と入力しないと実行できないと思われ

import os
import shutil
import json
from collections import OrderedDict
import threading
import binascii
import datetime

import features
import Mosaicjson
import gscraping
import producemosaic

import numpy as np
from PIL import Image
from flask import Flask,request,url_for,send_from_directory,Response,make_response,jsonify

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif','json'])

app = Flask("main")
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.config['JSON_SORT_KEYS'] = False

progress = {}
IDlist = []

@app.errorhandler(404)
def error(error):
    return jsonify({"error":"logic error occured"}),error.code

@app.route('/cookie/')
def set_cookie():
    response = make_response("sessionID has been set!")

    sessionID = binascii.hexlify(os.urandom(8))
    lifespan = 60 * 60 * 24
    expires = int(datetime.now().timestamp()) + lifespan

    IDlist.append(sessionID)

    response.set_cookie(key='ID', value=sessionID ,max_age=lifespan, expires=expires)
    
    return response

def cookie_check():
    if request.cookie.get('ID') in IDlist:
        return request.cookie.get('ID')
    else:
        abort(404)

@app.route('/mkdir/')
def make_directory():
    ID = request.cookie.get('ID')
    os.mkdir("./"+ID)

#source.pngを受け取る
@app.route('/source/',methods=['GET','POST'])
def source():
    directory = cookie_check()
    app.config['UPLOAD_FOLDER'] = './' + directory + '/'
    img_file = request.files['source']
    print(img_file.name)
    if 'source' not in request.files:
        return make_response(jsonify({'result':'field name needs to be "source"'}))
    if img_file.mimetype == "image/png":
        filename = "source.png"
    elif img_file.mimetype == "image/jpeg":
        filename = "source.jpg"
    else:
        return make_response(jsonify({'result':"mimetype not acceptable"}))

    img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return make_response(jsonify({'result':"ok"}))

#features.jsonを受け取る
@app.route('/post/',methods=['GET','POST'])
def json_post():
    directory = cookie_check()
    app.config['UPLOAD_FOLDER'] = './' + directory + '/'
    img_file = request.files['source']
    json_data = request.get_json(force=True)
    filename = "features.json"
    with open(os.path.join(app.config['UPLOAD_FOLDER'], filename),'w') as f:
        json.dump(json_data,f,indent=4)
    return make_response(jsonify({"result":"succeeded"}))

#producemosaicart.jsonを返す
@app.route('/get/',methods=['GET'])
def json_get():
    if request.method == 'GET':
        #directory = cookie_check()
        app.config['UPLOAD_FOLDER'] = './'# + directory + '/'
        filename = "producemosaicart.json"
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename),'r') as f:
            json_data = json.load(f)
        return jsonify(json_data)
    else:
        return jsonify({"result":"Don't POST"})

#gscraping.pyを実行
@app.route('/scrape/',methods=['GET','POST'])
def scrape():
    json_data = request.get_json(force=True)
    keyword = json_data["keyword"]
    gscraping.main(keyword)
    return make_response(jsonify({"result":"succeeded"}))

#features.pyを実行
@app.route('/features/')
def features():
    json_data = request.get_json(force=True)
    feature_div = json_data["feature_div"]
    features.main(feature_div)
    return make_response(jsonify({"result":"succeeded"}))
 
#out.pngを返す
@app.route('/out/',methods=['GET'])
def out():
    if request.method == 'GET':
        directory = cookie_check()
        app.config['UPLOAD_FOLDER'] = './' + directory + '/'
        filename = "out.png"
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename),'r') as f:
            image = f.read()
        return Response(response=image, content_type='image/png')
    else:
        abort(404)

#Mosaicjson.pyを実行
@app.route('/mosaic/',methods=['GET','POST'])
def mosaic():
    json_data = request.get_json(force=True)
    feature_div = json_data["feature_div"]
    blk_size = json_data["blk_size"]

    th = threading.Thread(target=Mosaicjson.main,args=[feature_div,blk_size,directory,request.cookie.get('ID'),progress])
    th.daemon = True
    th.start()

    return make_response(jsonify({"result":"succeeded"}))

#進捗を渡す
@app.route('/progress/',methods=['GET'])
def progess():
    return make_response(jsonify({"progress":progress[request.cookie.get('ID')]}))

#作業ディレクトリを消去
@app.route('/delete/')
def reset():
    directory = cookie_check()
    app.config['UPLOAD_FOLDER'] = './' + directory + '/'
    shutil.rmtree(os.path.join(app.config['UPLOAD_FOLDER']))
    return make_response(jsonify({"result":"deleted"}))

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=80,threaded=True)
