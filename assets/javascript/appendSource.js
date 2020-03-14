function viewSource(sourceFile) {
    let file = sourceFile.files[0]
    // 画像ファイル以外の場合は処理を終了する
    if (!file.type.match(/^image\/(png|jpeg|gif)$/)) return;

    $('.hiddenCanvas').empty()
    $('.hiddenCanvas').append("<canvas id='source'></canvas>\r\n");

    loadFile(file).then(function (source) {
        //canvas設定
        let context = document.getElementById('source').getContext('2d')

        loadImage(source).then(function (source) {
            context.drawImage(source, 0, 0, source.width, source.height)
        }).catch(function (e) {
            console.log(e, "Failed to load image")
        })
    }).catch(function (e) {
        console.log(e, "Failed to load file");
    })
}

function loadFile(file) {
    return new Promise((resolve, reject) => {
        const fileReader = new FileReader();
        fileReader.onload = (event) => resolve(event.target.result);
        fileReader.onerror = (e) => reject(e);
        fileReader.readAsDataURL(file);
    });
}

$(document).on('change', '.sourceImage', function () {
    viewSource(this);
});

