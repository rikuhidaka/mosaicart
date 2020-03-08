function OnFileSelect(inputElement) {
    // ファイルリストを取得
    var fileList = inputElement.files;

    // ファイルの数を取得
    var fileCount = fileList.length;

    var loadCompleteCount = 0;
    var imageList = "";

    // 選択されたファイルの数だけ処理する
    for (var i = 0; i < fileCount; i++) {

        // FileReaderを生成
        var fileReader = new FileReader();

        // ファイルを取得
        var file = fileList[i];

        // 読み込み完了時の処理を追加
        fileReader.onload = function () {

            // <li>,<img>タグの生成
            imageList += "<li><img src=\"" + this.result + "\" /></li>\r\n";

            // 選択されたファイルすべの処理が完了したら、<ul>タグに流し込む
            if (++loadCompleteCount == fileCount) {

                // <ul>タグに<li>,<img>を流し込む
                document.getElementById("ID001").innerHTML = imageList;
            }
        };

        // ファイルの読み込み(Data URI Schemeの取得)
        fileReader.readAsDataURL(file);
    }
}

$(document).on('change', '.image', function () {
    OnFileSelect(this);
});

$(document).ready(function () {
    $('.dropify').dropify({
        messages: {
            'default': '元となる画像をここにドラッグ＆ドロップするか、ここをクリックして選択してください',
            'replace': 'ドラッグ&ドロップ or 選択して別の画像に置換できます',
            'remove': '削除',
            'error': 'エラーが発生しました'
        }
    });
});