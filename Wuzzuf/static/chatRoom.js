$(document).ready(function () {
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('response', function (msg) {
        $('#chat_area').append(" bot" + ": " + msg.data + "\n");
    });


    $("#message").keypress(function (event) {
        if (event.which == 13) {
            var msg = $('#message').val();
            socket.emit('question', {data: msg});
            $('#message').val("");
            $('#chat_area').append(" me: " + msg + "\n");
        }
    });


});