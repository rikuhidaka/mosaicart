# coding: UTF-8
import json
import os
import sys
import tqdm
import numpy as np
from PIL import Image
from collections import OrderedDict
from pathlib import Path

def cut_img(img):
    #画像をトリミングする
    w,h = img.size
    if(w>=h):
        img = img.crop((0,0,h,h))
    else:
        img = img.crop((0,0,w,w))   
    return img

#5～23は処理が重複するので省略する
def load_img(path):
    img = Image.open(path)
    img.convert('HSV')
    return np.asarray(img)[:, :, :3]

def load_data(size=50):
        
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
    img_list = [ np.asarray(Image.fromarray(img).resize((size, size))) for img in img_list ]

    return (img_paths, img_list)

def main(filename):
    with open('resizemosaic.json','r') as f:
        mosaic = json.load(f,object_pairs_hook=OrderedDict)
        
    _, data_list = load_data()
    size = mosaic['block_size']
    h = mosaic['mosaic_size_h']
    w = mosaic['mosaic_size_w']
    images = mosaic['images']
    
    out = np.zeros((size*h, size*w, 3), dtype=np.uint8)
    for i in tqdm.trange(h):
        for j in range(w):

            out_tly = size*i
            out_tlx = size*j
            out_bry = size*(i+1)
            out_brx = size*(j+1)
            out[out_tly:out_bry, out_tlx:out_brx, :] = data_list[images[(i*w)+j]] 
        
    Image.fromarray(out).save('mosaic_img/'+filename+'.png')

if __name__ == '__main__':
    args = sys.argv
    main(args[1])