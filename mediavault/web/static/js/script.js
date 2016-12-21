var vid, playbtn, seekslider;
function intializePlayer() {
    vid = document.getElementById("media-player");
    console.log(vid);
    vid.onseeking = function () {
        console.log('Seeking');
        video.currentTime = video.seekslider.value*100/vid.duration;
    }
}
window.onload = intializePlayer;
