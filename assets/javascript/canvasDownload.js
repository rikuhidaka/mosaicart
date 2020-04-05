$(document).on("click", ".download", function () {
  let canvas = document.getElementById("mosaic");

  let link = document.createElement("a");
  link.href = canvas.toDataURL("image/png");
  link.download = "test.png";
  link.click();
});
