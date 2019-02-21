#coding=utf-8

import json
from collections import OrderedDict
from PIL import Image
from pathlib import Path
import numpy as np
import tqdm
import os
#import glob

def load_img(path):
    img = Image.open(path)
    img.convert('HSV')
    return np.asarray(img)[:, :, :3]

def load_data(size=50):
    tlx = 0
    tly = 0
    sz = 500
        
    for i in Path('subdata').glob('**/*.png'):
        print(type(i))
        rgb_im = Image.open(str(i)).convert('RGB')
        root,_ = os.path.splitext(str(i))
        name = root + '.jpg'
        rgb_im.save(name)
        os.remove(str(i))
    
    img_paths = list( Path('subdata/').glob('**/*.jpg') )
    img_paths = [str(path) for path in img_paths]

    img_list = [ load_img(img) for img in img_paths ]
    img_list = [ img[tly:tly+sz, tlx:tlx+sz, :] for img in img_list ]

    img_list = [ np.asarray(Image.fromarray(img).resize((size, size))) for img in img_list ]

    return (img_paths, img_list)

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

def main(feature_div):
    img_paths, img_list = load_data() # 素材画像の読み込み
    #print(img_list)
    assert(len(set((img.shape for img in img_list))) == 1) # 素材画像がすべて同じ大きさかチェック
    assert(img_list[0].shape[0] == img_list[0].shape[1]) # 素材画像が正方形かチェック
    block_size = img_list[0].shape[0] # 素材画像の一辺の長さをblock_sizeとする

    # 全画像の特徴量を計算
    features = [feature(img,feature_div).tolist() for img in img_list]

    # jsonに書き込む
    with open('features.json', 'w') as f:
        json.dump( OrderedDict([
            ('block_size', block_size),
            ('features', OrderedDict(zip(img_paths, features)))
        ]), f, indent=4 )

if __name__ == '__main__':
    main(2)
