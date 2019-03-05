import json
from collections import OrderedDict

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
    if(tl_h%blk_size >= blk_size/2):
        h1+=1
    if(tl_w%blk_size >= blk_size/2):
        w1+=1
    if(br_h%blk_size >= blk_size/2):
        h2+=1
    if(br_w%blk_size >= blk_size/2):
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