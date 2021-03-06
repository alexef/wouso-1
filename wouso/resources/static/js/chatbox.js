$(document).ready(function() {

    /* hide button */
    $("#ShoutboxHideButton").click(function() {
        $("#Shoutbox").hide("slide", {direction: "right"});
        $("#ShoutboxShowButton").delay("350").show("slide", {direction:"right"});
    });

    /* show button */
    $("#ShoutboxShowButton").click(function() {
        $("#ShoutboxShowButton").hide();
        $("#Shoutbox").show("slide", {direction: "right"});
    });

    /* csrf crap */
    $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    function getCookie(name) {
                        var cookieValue = null;
                        if (document.cookie && document.cookie != '') {
                            var cookies = document.cookie.split(';');
                            for (var i = 0; i < cookies.length; i++) {
                                var cookie = jQuery.trim(cookies[i]);
                                // Does this cookie string begin with the name we want?
                                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                    break;
                                }
                            }
                        }
                        return cookieValue;
                    }
                    if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                    // Only send the token to relative URLs i.e. locally.
                    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                    }
                }
            });

    function AutoScroll() {
        $('#ShoutboxTextArea').scrollTop($('#ShoutboxTextArea')[0].scrollHeight);
    }

    function SendPing() {
        var mdata = {'opcode': 'keepAlive'};
        var args = {type:'POST', url:'m/', data:mdata, complete:ReceiveMessage};
        $.ajax(args);
    }

    $(document).everyTime(1000, SendPing);
    $(document).everyTime(500, AutoScroll);


    function AddToHist(input) {
        /* adds input to history array */
        hist[i] = input;
        i = (i + 1) % 10;
        j = (i + 9) % 10;
        nr_max_steps = hist.length;
        k = 0;
        was_writing = 0;
    }

    var SendMessage = function() {
        var input = $('#ShoutboxTextBox').val();

        if (input) {
            AddToHist(input);
            var msgdata = {'opcode':'message', 'msg':input, 'room':''};
            var args = {type:"POST", url:"m/", data:msgdata, complete:ReceiveMessage};
            $.ajax(args);
            $('#ShoutboxTextBox').val("");
        }
        return false;
    };

    var ReceiveMessage = function(res, status) {
        if (status == "success") {
            var obj = jQuery.parseJSON(res.responseText);

            if (!obj) {
                return false;
            }

            $('#ShoutboxUserName').val(obj.user);

            var i;

            for (i = 0; i < obj.count; ++i) {
                $('#ShoutboxTextArea').append(obj.msgs[i].user + " : " + obj.msgs[i].text + "<br />" )
            }

        }
        else if (res.status == 400) {
            $('#ShoutboxTextArea').append('<p id="warn_spam"> Stop spamming! </p>');
        }
        AutoScroll();

    };

    /* clear on refresh */
    $('#ShoutboxTextArea').val("");
    $('#ShoutboxTextBox').val('');

    /* create an emtpy array sized for 10 elements */
    var hist = [];
    var i = hist.length % 10; // iter pentru inserare
    var j = (i + 9) % 10; // iter pentru de unde incepe cautarea
    var k = 0; // iter pentru pasi de history
    var nr_max_steps; // limita pt k
    var change_dir; // anti inertie la schimbare de directie
    var was_writing;

    $('#ShoutboxSendButton').click(SendMessage);

    function HistUp() {
        if (was_writing) {
            /* bagat in hist */
            var input = $('#ShoutboxTextBox').val();
            if (input) {
                hist[i] = input;
                i = (i + 1) % 10;
                j = (i + 8) % 10;
                nr_max_steps = hist.length;
                k++;
                was_writing = 0;
            }
        }

        if (k < nr_max_steps) {
            $('#ShoutboxTextBox').val(hist[j]);
            j = (j + 9) % 10;
            k++;
            change_dir = 1;
        }
    }

    function HistDown() {
        if (k == 0 && !was_writing) {
            $('#ShoutboxTextBox').val("");
        }

        else if (change_dir) {
            change_dir = 0;
            //j = (j + 1) % 10;
            /*k--;*/
        }

        if (k) {
            j = (j + 1) % 10;
            $('#ShoutboxTextBox').val(hist[j]);
            k--;
        }
    }

    $("#ShoutboxTextBox").keyup(function(event) {
        if (event.keyCode == 13) {
            /* enter */
            $("#ShoutboxSendButton").click();
        }

        else if (event.keyCode == 38) {
            /* up_arrow */
            HistUp();
        }

        else if (event.keyCode == 40) {
            /* down_arrow */
            HistDown();
        }
        else {
            /* other key */
            was_writing = 1;
        }

    });

});
