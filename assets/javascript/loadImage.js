function getRGB(image_data, size) {
    let rgb = []
    let r = []
    let g = []
    let b = []

    for (let i = 0; i < size; i++) {
        r.push(image_data.data[i * 4]);
        g.push(image_data.data[i * 4 + 1]);
        b.push(image_data.data[i * 4 + 2]);
    }

    rgb.r = r
    rgb.b = b
    rgb.g = g
    return rgb
}

function tileAverageRGB(image_data, size) {
    let average_rgb = {}
    let r = 0
    let g = 0
    let b = 0

    for (let i = 0; i < size; i++) {
        for (let j = 0; j < size; j++) {
            let index = (j + i * size) * 4;
            r += image_data[index]
            g += image_data[index + 1]
            b += image_data[index + 2]
        }
    }
    average_rgb.r = r / (size * size)
    average_rgb.g = g / (size * size)
    average_rgb.b = b / (size * size)

    return average_rgb
}

function produceMosaicArt(tiles, tile_num, source_height, source_width, size) {
    $('#canvas').append("<canvas id='mosaic'></canvas>")
    $('#mosaic').attr({
        width: size * source_width / 10,
        height: size * source_height / 10
    })
    let context = document.getElementById('mosaic').getContext('2d')
    for (let i = 0; i < source_height; i++) {
        for (let j = 0; j < source_width; j++) {
            context.drawImage(tiles[tile_num[i * source_width + j]], 0, 0, size, size, j * size / 10, i * size / 10, size / 10, size / 10)
        }
    }
}

$(document).on('click', '.start', function () {
    let source = document.getElementById('source')
    let context = source.getContext('2d')
    let width = source.width
    let height = source.height
    let source_rgb = getRGB(context.getImageData(0, 0, width, height), width * height)
    let tiles_rgb = []
    let tiles = []
    let tile_num = []
    let tiles_list = document.getElementsByClassName('tile')
    tile_size = tiles_list[0].width
    for (let i = 0; i < tiles_list.length; i++) {
        let tile = tiles_list[i]
        tiles.push(tile)
        tiles_rgb.push(tileAverageRGB(tile.getContext('2d').getImageData(0, 0, tile_size, tile_size).data, tile_size))
    }

    for (let i = 0; i < height * width; i++) {
        let distance = []
        let r = source_rgb.r[i]
        let g = source_rgb.b[i]
        let b = source_rgb.g[i]
        for (let j = 0; j < tiles_rgb.length; j++) {
            distance.push(Math.pow(r - tiles_rgb[j].r, 2) + Math.pow(g - tiles_rgb[j].g, 2) + Math.pow(b - tiles_rgb[j].b, 2))
        }
        tile_num.push(distance.indexOf(Math.min(...distance)))
    }
    produceMosaicArt(tiles, tile_num, height, width, tile_size)
    $(".download").css("display", "inline")
});
