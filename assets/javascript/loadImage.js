function createImageData(img) {

    var cv = document.createElement('canvas');

    cv.width = img.naturalWidth;
    cv.height = img.naturalHeight;

    var ct = cv.getContext('2d');

    ct.drawImage(img, 0, 0);

    var data = ct.getImageData(0, 0, cv.width, cv.height);

    return data;

}

$(document).on('change', '#image', function () {
    var file = this.files[0];
    if (!file.type.match(/^image\/(png|jpeg|gif)$/)) return;

    var image = createImageData(file)
    var r = []
    var g = []
    var b = []
    var size

    if (image.height < image.width) {
        size = image.height;
    } else {
        size = image.width;
    }

    for (let i = 0; i < size; i++) {
        let r_list = []
        let g_list = []
        let b_list = []
        for (let j = 0; j < size; j++) {
            let index = (j + i * image.width) * 4;
            r_list.push(image.data[index]);
            g_list.push(image.data[index + 1]);
            b_list.push(image.data[index + 2]);
        }
        r.push(r_list)
        g.push(g_list)
        b.push(b_list)
    }
});
