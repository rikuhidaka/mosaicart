#コマンドラインに
#
# $ export FLASK_APP=main.py
# $ flask run
#
#と入力しないと実行できないと思われ

#coding=utf-8

import os
import shutil
import json
import features
import Mosaicjson
import threading
import gscraping
import producemosaic
import numpy as np
from PIL import Image
from flask import Flask,request,url_for,send_from_directory,Response,jsonify

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif','json'])

app = Flask(__name__)
progress = 0.00
list = {}
key = 0

@app.errorhandler(404)
def error(e):
    return "{}, {}".format(e.message, e.description)

#cookie処理(未確定)
@app.route('/')
def index():
    user = request.cookie.get('user')
    list[key] = "user"
    os.mkdir("./"+user)
    key += 1

#source.pngを受け取る
@app.route('/source/',methods=['POST'])
def source():
    app.config['UPLOAD_FOLDER'] = './'
    if request.method == 'POST':
        img_file = request.files['file']
        filename = "source.png"
        img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return 0
    else:
        return flask.redirect('/404')

#features.jsonを受け取る
@app.route('/post/',methods=['POST'])
def post():
    app.config['UPLOAD_FOLDER'] = './'
    if request.method == 'POST':
        json_data = request.get_json()
        filename = "features.json"
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename),'w') as f:
            json.dump(json_data,f,indent=4)
        return Response(status=200, mimetype='application/json')
    else:
        return flask.redirect('/404')

#gscraping.pyを実行
@app.route('/scrape/',methods=['POST'])
def scrape():
    if request.method == 'POST':
        keyword = request.args.get("keyword",type=string)
        gscraping.main(keyword)
        return Response(status=200, mimetype='application/json')

#out.pngを返す
@app.route('/out/',methods=['GET'])
def out():
    if request.method == 'GET':
        img = open('out.png','rb')
        image = img.read()
        return Response(response=image, content_type='image/png')
    else:
        return flask.redirect('/404')

@app.route('/feature/')
def feature():
    feature_div = request.args.get("feature_div",type=int)
    features.main(feature_div)
    return 200
    
#Mosaicjson.pyを実行
@app.route('/mosaic/')
def mosaic():
    json_data = request.get_json()
    feature_div = json_data["feature_div"]
    blk_size = json_data["blk_size"]

    th = threading.Thread(target=Mosaicjson.main,args=[feature_div,blk_size])
    th.daemon = True
    th.start()

    return 200

#進捗を渡す
@app.route('/progress/',methods=['GET'])
def progess():
    return jsonify({"progress":Mosaicjson.hoge})

#producemosaicart.jsonを返す
@app.route('/get/',methods=['GET'])
def download():
    if request.method == 'GET':
        with open('producemosaicart.json','r') as f:
            json_data = json.load(f)
        return jsonify(json_data)
    else:
        return Response(status=201, mimetype='application/json')

#dataディレクトリ内のファイルを全消去
@app.route('/reset/')
def reset():
    shutil.rmtree("./data")
    os.mkdir("./data")
    return Response(status=200, mimetype='application/json')

if __name__ == "__main__":
    app.run(debug=True)
