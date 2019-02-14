# coding: UTF-8
# 注意: mosaic.pyを実行する前にtable.pyを実行してね 
# いつ実行すべきかの詳細はtable.pyのコメントに書いた

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

# dataディレクトリ内の素材画像(pngファイル)をすべて読み込んでリストで返す
# 素材画像は自動的に切り抜かれる．tlxが切り抜く正方形の左上のx座標,tlyがy座標，szが正方形の一辺の長さ
# 切り抜く正方形が画像からはみ出している場合ちゃんと動かないので注意 (多分エラーになる)
# 素材画像の一辺の長さはsizeに調整される
def load_data(size=64):
    tlx = 0
    tly = 0
    sz = 300

    img_paths = list( Path('data/').glob('**/*.jpeg') )
    img_paths = [str(path) for path in img_paths]

    img_list = [ load_img(img) for img in img_paths ]
    img_list = [ img[tly:tly+sz, tlx:tlx+sz, :] for img in img_list ]

    img_list = [ np.asarray(Image.fromarray(img).resize((size, size))) for img in img_list ]

    return (img_paths, img_list)

# 分割数
feature_div = 1

# 画像の特徴量を計算
def feature(img):
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

if __name__ == '__main__':
    # 近似対象画像をどれくらいの細かさでモザイク化するか
    # blk_size×blk_sizeの正方形を最小単位としてモザイク化する
    # 1のとき1×1の正方形が最小単位となるので最も細かいが，処理に時間がかかるし生成される画像が大きくなる
    blk_size = 3

    # 事前に計算した素材画像の特徴量を読み込む
    with open('features.json', 'r') as f:
        tiles_features = json.load(f, object_pairs_hook=OrderedDict)

    # 近似対象画像を読み込む
    img = load_img('source.jpg')

    # 素材画像を読み込む
    _, data_list = load_data()

    # 近似対象画像のサイズ(画素)
    h = img.shape[0] # 縦
    w = img.shape[1] # 横

    # モザイク化された近似対象画像のタイルの数
    n = h//blk_size # 縦
    m = w//blk_size # 横

    tile_blksz = tiles_features['block_size']
    tiles_features = tiles_features['features'].values()

    out = np.zeros((tile_blksz*n, tile_blksz*m, 3), dtype=np.uint8)
    for i in tqdm.trange(n):
        for j in range(m):
            tly = blk_size*i
            tlx = blk_size*j
            bry = blk_size*(i+1)
            brx = blk_size*(j+1)

            block = img[tly:bry, tlx:brx, :]
            nearest = np.argmin([distance_feature(feature(block), x) for x in tiles_features])

            out_tly = tile_blksz*i
            out_tlx = tile_blksz*j
            out_bry = tile_blksz*(i+1)
            out_brx = tile_blksz*(j+1)
            out[out_tly:out_bry, out_tlx:out_brx, :] = data_list[nearest]

    Image.fromarray(out).save('out.png')