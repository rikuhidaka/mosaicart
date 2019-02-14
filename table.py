# coding: UTF-8
# 素材となる画像(dataディレクトリ内の画像)の特徴量を計算してjsonに保存するスクリプト
# mosaic.pyで生成する前に事前に実行する必要がある
# 既にtable.pyを実行済みで, dataディレクトリ内を弄っていなければ実行する必要なし
# 素材画像を変更, 追加, 削除したときに実行する必要がある

from mosaic import feature, load_data

import json
from collections import OrderedDict

if __name__ == '__main__':
    img_paths, img_list = load_data() # 素材画像の読み込み
    assert(len(set((img.shape for img in img_list))) == 1) # 素材画像がすべて同じ大きさかチェック
    assert(img_list[0].shape[0] == img_list[0].shape[1]) # 素材画像が正方形かチェック
    block_size = img_list[0].shape[0] # 素材画像の一辺の長さをblock_sizeとする

    # 全画像の特徴量を計算
    features = [feature(img).tolist() for img in img_list]

    # jsonに書き込む
    with open('features.json', 'w') as f:
        json.dump( OrderedDict([
            ('block_size', block_size),
            ('features', OrderedDict(zip(img_paths, features)))
        ]), f, indent=4 )
