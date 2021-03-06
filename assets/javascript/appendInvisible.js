function appendInvisible(inputElement) {
    // ファイルリストを取得
    let fileList = inputElement.files;

    // ファイルの数を取得
    let fileCount = fileList.length;

    //canvas初期化
    $('.hiddenCanvas').empty();


    // 選択されたファイルの数だけ処理する
    for (let i = 0; i < fileCount; i++) {

        // ファイルを取得
        let file = fileList[i];

        // 画像ファイル以外の場合は処理を終了する
        if (!file.type.match(/^image\/(png|jpeg|gif)$/)) return;

        // <canvas>タグの追加
        $(".hiddenCanvas").append("<canvas></canvas>\r\n");

        // 読み込み完了時の処理を追加
        loadFile(file).then(function (response) {
            //canvas設定
            let canvas = $(".hiddenCanvas").children()[i];

            let ctx = canvas.getContext('2d');

            loadImage(response).then(function (response) {
                canvas.width = response.naturalWidth;
                canvas.height = response.naturalHeight;
                ctx.clearRect(0, 0, response.naturalWidth, response.naturalHeight);
                ctx.drawImage(response, 0, 0, response.naturalWidth, response.naturalHeight);
            }).catch(function (e) {
                console.log(e, "Failed to load image")
            })
        }).catch(function (e) {
            console.log(e, "Failed to load file");
        })
    }
}

function loadFile(file) {
    return new Promise((resolve, reject) => {
        const fileReader = new FileReader();
        fileReader.onload = (event) => resolve(event.target.result);
        fileReader.onerror = (e) => reject(e);
        fileReader.readAsDataURL(file);
    });
}

function loadImage(src) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = (e) => reject(e);
        img.src = src;
    });
}

$(document).on('change', '.toCanvas', function () {
    appendInvisible(this);
    $(".materialInput").css("display","inline")
});

