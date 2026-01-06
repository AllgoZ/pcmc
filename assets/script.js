// script.js


function changeContent(contentId) {
    // Hide all content areas
    var allContents = document.querySelectorAll('.right-content');
    allContents.forEach(function (content) {
        content.style.display = 'none';
    });

    // Show the selected content
    var selectedContent = document.getElementById(contentId);
    if (selectedContent) {
        selectedContent.style.display = 'block';
    }
}

function openVideoModal(videoUrl, title) {
$('#videoModalLabel').text(title);
$('#videoFrame').attr('src', videoUrl); 
$('#videoModal').modal('show');
}

function stopVideo() {
// Reset the src attribute to stop the video
$('#videoFrame').attr('src', '');
}

$(document).ready(function () {
$('.menu-item').on('click', function () {
    $('.menu-item').css('background', '');
    $(this).css('background', '#FCBF49');
});
});
