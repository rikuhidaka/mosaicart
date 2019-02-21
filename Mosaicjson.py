#coding=utf-8

from PIL import Image
import numpy as np
import json
from collections import OrderedDict
from pathlib import Path


# pathで指定された画像ファイルを読み込んで三次元配列(numpyのndarray)で返す
def load_img(path):
    img = Image.open(path)
    img.convert('HSV')
    return np.asarray(img)[:, :, :3]

# 画像の特徴量を計算
def feature(img,feature_div):
    chunk_sz = img.shape[0]/feature_div
    n_chunk_pixels = chunk_sz*chunk_sz

    f = np.zeros((feature_div, feature_div, img.shape[2]))
    for i in range(feature_div):
        for j in range(feature_div):
            tly = int(chunk_sz*i)
            tlx = int(chunk_sz*j)
            bry = int(chunk_sz*(i+1))
            brx = int(chunk_sz*(j+1))
            f[i,j] = np.sum(img[tly:bry, tlx:brx, :], axis=(0,1))

    return f / n_chunk_pixels

# 2つの特徴量の差(距離，どのくらい違うか)を計算
def distance_feature(x, y):
    return np.sum(np.linalg.norm(x - y, axis=2))

hoge = 0.00

def main(feature_div,blk_size):
    # 近似対象画像をどれくらいの細かさでモザイク化するか
    # blk_size×blk_sizeの正方形を最小単位としてモザイク化する
    # 1のとき1×1の正方形が最小単位となるので最も細かいが，処理に時間がかかるし生成される画像が大きくなる
    # 事前に計算した素材画像の特徴量を読み込む
    global hoge

    with open('features.json', 'r') as f:
        tiles_features = json.load(f, object_pairs_hook=OrderedDict)

    # 近似対象画像を読み込む
    img = load_img('source.jpg')

    # 近似対象画像のサイズ(画素)
    h = img.shape[0] # 縦
    w = img.shape[1] # 横

    # モザイク化された近似対象画像のタイルの数
    n = h//blk_size # 縦
    m = w//blk_size # 横

    tile_blksz = tiles_features['block_size']
    tiles_data = tiles_features['data']
    tiles_features = tiles_data[1][:len(tiles_data[1])][1]
    print(tiles_features)
    tiles_name = tiles_data[0][:len(tiles_data[0])][1]

    out = OrderedDict()
    out['block_size'] = tile_blksz
    out['mosaic_size_h'] = n
    out['mosaic_size_w'] = m
    
    
    for i in range(n):
        hoge = round(float(i)/float(n)-float(1),2)
        for j in range(m):
            tly = blk_size*i
            tlx = blk_size*j
            bry = blk_size*(i+1)
            brx = blk_size*(j+1)

            block = img[tly:bry, tlx:brx, :]
            nearest = np.argmin([distance_feature(feature(block,feature_div), x) for x in tiles_features])
            
            out[str((i*m) + j)] = str(nearest)
            
    fw = open('producemosaicart.json','w')
    json.dump(out,fw,indent=4)

if __name__ == '__main__':
    main(1,10)
