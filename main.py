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
import features
import Mosaicjson
import threading
import gscraping
import producemosaic
import numpy as np
from PIL import Image
from flask import Flask,request,url_for,send_from_directory,Response,make_response,jsonify

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif','json'])

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

progress = {}
list = {}
key = 0

#明日実装予定
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
        img_file = request.files['image']
        if 'image' not in request.files:
            return make_response(jsonify({'result':'field name needs to be "image"'}))
        if img_file.mimetype == "image/png":
            filename = "source.png"
        elif img_file.mimetype == "image/jpeg":
            filename = "source.jpg"
        else:
            return make_response(jsonify({'result':"mimetype not acceptable"}))

        img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        return make_response(jsonify({'result':"ok"}))
    else:
        return flask.redirect('/404')

#features.jsonを受け取る
@app.route('/post/',methods=['POST'])
def post():
    app.config['UPLOAD_FOLDER'] = './'
    if request.method == 'POST':
        json_data = request.get_json(force=True)
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
    progess[request.cookie.get('user')] = Mosaicjson.hoge
    return jsonify({"progress":progress[request.cookie.get('user')]})

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
    app.run(debug=True,host="0.0.0.0",port=80,threaded=True)
