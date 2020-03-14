function getRGB(image_data, size) {
    let rgb = []
    let r = []
    let g = []
    let b = []

    for (let i = 0; i < size * size; i++) {
        r.push(image_data.data[i * 4]);
        g.push(image_data.data[i * 4 + 1]);
        b.push(image_data.data[i * 4 + 2]);
    }

    rgb.r = r
    rgb.b = b
    rgb.g = g
    return rgb
}

function imageAverageRGB(image_data) {
    let average_rgb
    let r = 0
    let g = 0
    let b = 0
    let size = image_data.height

    for (let i = 0; i < size; i++) {
        for (let j = 0; j < size; j++) {
            let index = (j + i * image.width) * 4;
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

function produceMosaic(tiles, tile_num, source_size, size) {
    $('.canvas').append("<canvas id='mosaic'></canvas>")
    let context = $('#mosaic').getContext('2d')
    for (let i = 0; i < source_size; i++) {
        for (let j = 0; j < source_size; j++) {
            context.drawImage(tiles[tile_num[i * source_size + j]], 0, 0, size, size, i, j, 1, 1)
        }
    }
}

$(document).on('click', '.start', function () {
    console.log('hoge')
    source = $('.source')[0].getContext('2d')
    let size = source.height
    let source_rgb = getRGB(source, size)
    let tiles_rgb = []
    let tiles = []
    let distance = []
    $('.tile').each(function (num, $tile) {
        tiles.push($tile.getContext('2d'))
        tiles_rgb.push(imageAverageRGB($tile.getContext('2d')))
    });
    tile_size = $('.tile')[0].getContext('2d').width
    for (let i = 0; i < size * size; i++) {
        let r = source_rgb.r[i]
        let g = source_rgb.b[i]
        let b = source_rgb.g[i]
        tiles_rgb.array.forEach(tile_rgb => {
            distance.push(Math.pow(r - tile_rgb.r, 2) + Math.pow(g - tile_rgb.g, 2) + Math.pow(b - tile_rgb.b, 2))
        });
        tile_num = distance.indexOf(Math.min(distance))
    }
    console.log(tiles)
    produceMosaic(tiles, tile_num, size, tile_size)
});
