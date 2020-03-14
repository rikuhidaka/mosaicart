function createImageData(img) {
    let ct = $('#canvas').getContext('2d');
    ct.drawImage(img, 0, 0);
    let data = ct.getImageData(0, 0, cv.width, cv.height);

    return data;
}

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

$(document).on('change', '#image', function () {
    let file = this.files[0];
    if (!file.type.match(/^image\/(png|jpeg|gif)$/)) return;

    let size = image_data.height
    let image_data = createImageData(file)
    let RGB = getRGB(image_data, size)
    let distance = []
    for (let i = 0; i < size * size; i++) {
        let r = RGB.r[i]
        let g = RGB.b[i]
        let b = RGB.g[i]
        let tile_rgb = imageAverageRGB()
        distance.push(Math.pow(r - tile_rgb.r, 2) + Math.pow(g - tile_rgb.g, 2) + Math.pow(b - tile_rgb.b, 2))
    }
    tile_num = distance.indexOf(Math.min(distance))
});
