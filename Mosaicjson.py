#coding=utf-8

from PIL import Image
import numpy as np
import json
from collections import OrderedDict
from pathlib import Path
import tqdm


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

def main(feature_div,blk_size,distance_pix,hoge,keyword):
    # 近似対象画像をどれくらいの細かさでモザイク化するか
    # blk_size×blk_sizeの正方形を最小単位としてモザイク化する
    # 1のとき1×1の正方形が最小単位となるので最も細かいが，処理に時間がかかるし生成される画像が大きくなる
    # 事前に計算した素材画像の特徴量を読み込む

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

    out = OrderedDict()
    out['block_size'] = tile_blksz
    out['mosaic_size_h'] = n
    out['mosaic_size_w'] = m
    abatement = [[] for i in range(distance_pix+1)] 
    dele = []
    sa = []
    nouse = []
    nears = []
    huga = {}
    tile_num = list(range(len(tiles_features)))
    count = 0
    hoge=0
    c = 0
    
    #for i in range(m*2-1):
    for i in tqdm.trange(m*2-1):
        #print('-------------------------------------------------------    '+str(i))
        j = i
        k = 0
        count = count%(distance_pix)
        #print(count)
        
        while True:
            while j>m-1:
                j-=1
                k+=1
                if(k==n):
                    break
            if(k==n):
                break
            c = c%distance_pix
            
            tly = blk_size*k
            tlx = blk_size*j
            bry = blk_size*(k+1)
            brx = blk_size*(j+1)
            block = img[tly:bry, tlx:brx, :]
            
            #一番平均が近い画像番号探す
            for x in range(distance_pix):
                dele = dele + abatement[x]
            dele = dele + nouse
            dele.sort()
            tiles = list(set(tile_num) - set(dele) )
            number = np.argmin([distance_feature(feature(block,feature_div), tiles_features[tiles[y]]) for y in range(len(tiles))])
            nearest = tiles[number]
            hoge+=1
            huga[k*m + j] = nearest 
            #次のループで使ってはいけない画像番号の行列
            abatement[distance_pix].append(nearest)
            a = nearest
            if(k == 0):
                nouse = [a]
            else:
                nouse = [a,b]
            b = a
            c+=1
            dele = []
            tiles = []
                          
            j-=1
            k+=1
            if j < 0:
                dele = []
                abatement[count] = []
                abatement[count] = abatement[distance_pix]
                nears = nears + abatement[distance_pix]
                abatement[distance_pix] = []
                count+=1
                break
    
    nears = sorted(huga.items())
    out['images'] = [nears[i][1] for i in range(len(nears))]
    print(nears)
    print(out['images'])
    fw = open('producemosaicart.json','w')
    json.dump(out,fw,indent=4)

if __name__ == '__main__':
    main(1,30,3,0,"")
