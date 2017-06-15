var firstSeatLabel = 1;
var booking_info;
var booking_dialog;
user_img_path = "../static/img/user.png";

function randomIntFromInterval(min,max)
{
    return Math.floor(Math.random()*(max-min+1)+min);
}

$(document).ready(function() {
    
    //initialize user media
    function init(){
        try{
            window.AudioContext = window.AudioContext || window.webkitAudioContext;
            navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia;
            window.URL = window.URL || window.webkitURL;
    
            audio_context = new AudioContext; 
        }catch(e){
            alert('No web audio support in this browser!');
        }
        navigator.getUserMedia({audio: true}, startUserMedia, function(e){
            __log('No live audio input: ' + e);
        });
    }

    init();
   
    //user camera capture
    var audio_player = document.getElementById('audio-element'); 
    var player = document.getElementById('player'); 
    var snapshotCanvas = document.getElementById('snapshot');
    var captureButton = document.getElementById('capture-btn');   
    var videoTracks;

    var handleSuccess = function(stream) {
        // Attach the video stream to the video element and autoplay.
        player.srcObject = stream;
        videoTracks = stream.getVideoTracks();
    };

    captureButton.addEventListener('click', function() {
        var context = snapshot.getContext('2d');
        // Draw the video frame to the canvas.
        context.drawImage(player, 0, 0, snapshotCanvas.width, snapshotCanvas.height);
        $("#capture-btns").css("display", "none");
        $("#confirm-btns").css("display", "table");
        $("#player").css("display", "none");
        $("#snapshot").css("display", "table");
    });

    $("#no-capture-btn").click(function(){
        $("#capture-block").fadeOut(1000);
        videoTracks.forEach(function(track){track.stop()});
        audio_player.play();
    });

    $("#upload-btn").click(function(){
        var dataURL = snapshotCanvas.toDataURL();
        //console.log(dataURL);
        $.ajax({
            type: "POST",
            url: "/capture",
            data: JSON.stringify({imgBase64: dataURL}),
            success: function(res){
                console.log(res);
                var rand_int = randomIntFromInterval(1,999999);
                user_img_path = "../static/img/user_upload.png?" + rand_int.toString(); 
                $("#capture-block").fadeOut(1000);
                audio_player.play();
            }
        });
        videoTracks.forEach(function(track){track.stop()});
    });

    $("#redo-btn").click(function(){
        $("#capture-btns").css("display", "table");
        $("#confirm-btns").css("display", "none");
        $("#player").css("display", "table");
        $("#snapshot").css("display", "none");
    });

    navigator.getUserMedia(
            {video: true},
            function(stream){
                handleSuccess(stream);
            },
            function(err){
                $("#capture-block").css("display","none");
                console.log(err.name);
                audio_player.play();
            }
    );

    //user audio recognition
    var audio_context;
    var recorder;
        
    function __log(e, data){
        console.log(e + " " + (data || ''));
    }

    function startUserMedia(stream){
        var input = audio_context.createMediaStreamSource(stream);
        __log('Media stream created.');
        recorder = new Recorder(input);
        __log('Recorder initialised.');
    }

    function passFile(blob){
        var formData = new FormData();
        formData.append('command', 'record');
        formData.append('source', blob);
        $.ajax({
            url: "/record",
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function(data){
                console.log("getting emotion response success!"); 
                //$("#emotion").html(data);
            }
        });
    }

    if(!('webkitSpeechRecognition' in window)){
        alert("您的瀏覽器不支援語音辨識，如果需要使用語音辨識，請用Chrome瀏覽器！");
    }
    else{
        var recognition = new webkitSpeechRecognition();
        var recognizing = false;
        
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = "cmn-Hant-TW";

        recognition.onstart = function(){
            console.log("開始辨識...");
        }

        recognition.onend = function(){
            console.log("停止辨識!");
            recognizing = false;
            $("#user_input").val(final_transcript);
            $("#mic-btn").attr("src", "../static/img/mic.png");
            recorder && recorder.stop();
            __log("Stopped recording.");
            recorder && recorder.exportWAV(function(blob){
                passFile(blob);
            });
            recorder.clear();
        }

        recognition.onresult = function(event){
            var interim_transcript = '';
            for(var i = event.resultIndex; i < event.results.length; ++i){
                if(event.results[i].isFinal){
                    final_transcript += event.results[i][0].transcript;
                    console.log(final_transcript);
                }
                else{
                    interim_transcript += event.results[i][0].transcript;
                    console.log(interim_transcript);
                }
            }
            //final_transcript = event.results[event.results.length - 1][0].transcript;
            $("#user_input").val(final_transcript);
            $("#user_input").val(interim_transcript);
        }
        
        $("#mic-btn").click(function(){
            if(recognizing){
                recognition.stop();
                /*$("#mic-btn").attr("src", "../static/img/mic.png");
                recorder && recorder.stop();
                __log("Stopped recording.");
                recorder && recorder.exportWAV(function(blob){
                    passFile(blob);
                });
                recorder.clear();*/
            }
            else{
                final_transcript = "";
                recognition.start();
                recognizing = true;
                $("#user_input").val("");
                $("#mic-btn").attr("src", "../static/img/mic_on.png");
                recorder && recorder.record();
                __log('Recording...');
            }
        });
    }
   
    //check email address format
    function validateEmail(email) {
        var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(email);
    }

    //dialog box auto scroll to bottom
    function scrollToBottom() {
        $('#dialog').scrollTop($('#dialog')[0].scrollHeight);
    }

    //reset dialog
    function reset_dialog(play_or_not=false){
        $("#user_input").val("");
        $("#user_input").prop('disabled', false);
        $.ajax({
            url: '/response?input_sentence=exit',
            type: 'GET',
            success: function(data){
                output_str = data['nl'];
                $("#dialog").empty();
                $("#dialog").append("<div class='dialog-row'><div class='bot-img'><img src='../static/img/bot.jpg'></div><div class='bot-response'>" + output_str + "</div></div>");
                var rand_int = randomIntFromInterval(1,999999);
                $("#audio-element").attr("src", "../static/files/voice.wav?" + rand_int.toString());
                if(play_or_not){
                    audio_player.play(); 
                }
            }
        }); 
    }
  
    //get chatbot response 
    function get_response() {
        var input_str = $("#user_input").val();
        if(input_str != ""){
            $("#dialog").append("<div class='dialog-row'><div class='user-img'><img src=" + user_img_path + "></div><div class='user-response'>" + input_str + "</div></div>");
            scrollToBottom();
            $("#user_input").prop('disabled', true);
            $("#user_input").val("");
            $.ajax({
                url: '/response?input_sentence=' + input_str,
                type: 'GET',
                success: function(data){
                    //console.log(data);
                    
                    //var output_str = "";
                    //for(var i in data['dialog']){
                    //    output_str = output_str + data['dialog'][i] + '\n';
                    //}
                    output_str = data['nl'];
                    //console.log(data['sf']); 
                    if(data['booking']){
                        /*output_str = output_str + "  現在幫您轉到訂票頁面，請稍候！";
                        setTimeout(function(){ 
                            $("#root").fadeOut(500, function(){
                                $("#booking-block").fadeIn(500);
                            });
                        }, 2000);*/
                        //console.log("booking");
                        $("#user_input").prop('disabled', true);
                        booking_info = data["sf"]["slot_value"][0];
                        booking_dialog = $("<div>" + output_str + "</div>").dialog({
                            buttons: {
                                "是": function(){
                                    $("#dialog").append("<div class='dialog-row'><div class='bot-img'><img src='../static/img/bot.jpg'></div><div class='bot-response'>現在幫您轉到訂票頁面，請稍候！</div></div>");
                                    scrollToBottom();
                                    $("#audio-element").attr("src", "../static/files/booking.mp3");
                                    audio_player.play();
                                    $(this).dialog('close');
                                    $("#movie-info-name").html("電影名稱: " + booking_info["movie_name"]);
                                    $("#movie-info-theater").html("放映影院: " + booking_info["theater_name"]);
                                    $("#movie-info-time").html("放映時間: " + booking_info["showing_time"]);
                                    setTimeout(function(){ 
                                        $("#root").fadeOut(500, function(){
                                            $("#booking-block").fadeIn(500);
                                        });
                                    }, 3000);
                                },
                                "否": function(){
                                    $(this).dialog('close');
                                    reset_dialog(true);
                                }
                            },
                            closeOnEscape: false,
                            open: function(event, ui) {
                                $(".ui-dialog-titlebar-close", ui.dialog | ui).hide();
                            }
                        });
                    }
                    else{
                        $("#user_input").prop('disabled', false);
                    }
                    $("#dialog").append("<div class='dialog-row'><div class='bot-img'><img src='../static/img/bot.jpg'></div><div class='bot-response'>" + output_str + "</div></div>");
                    scrollToBottom();
                    var rand_int = randomIntFromInterval(1,999999);
                    $("#audio-element").attr("src", "../static/files/voice.wav?" + rand_int.toString());
                    audio_player.play();
                }
            });
        }
    }
    
    reset_dialog();
   
    //seat selection implement 
    var $cart = $('#selected-seats'),
        $counter = $('#counter'),
        $total = $('#total'),
        sc = $('#seat-map').seatCharts({
        map: [
            'fff__ffffffffff__fff',
            'fff__ffffffffff__fff',
            'fff__ffffffffff__fff',
            'fff__ffffffffff__fff',
            'fff__ffffffffff__fff',
            'fff__ffffffffff__fff',
            'fff__ffffffffff__fff',
            'fff__ffffffffff__fff',
            'fff__ffffffffff__fff',
            'fff__ffffffffff__fff',
            'fff__ffffffffff__fff',
            'fff__ffffffffff__fff'
        ],
        seats: {
            f: {
                price   : 320,
                classes : 'first-class', //your custom CSS class
                category: 'First Class'
            }
            /*e: {
                price   : 40,
                classes : 'economy-class', //your custom CSS class
                category: 'Economy Class'
            }*/					
        
        },
        naming : {
            top : false,
            getLabel : function (character, row, column) {
                return firstSeatLabel++;
            },
        },
        legend : {
            node : $('#legend'),
            items : [
                [ 'f', 'available',   'Seat Available' ],
                //[ 'e', 'available',   'Economy Class'],
                [ 'f', 'unavailable', 'Already Booked']
            ]					
        },
        click: function () {
            if (this.status() == 'available') {
                //let's create a new <li> which we'll add to the cart items
                $('<li>Seat # '+this.settings.label+': <b>$'+this.data().price+'</b> <a href="#" class="cancel-cart-item">[cancel]</a></li>')
                    .attr('id', 'cart-item-'+this.settings.id)
                    .data('seatId', this.settings.id)
                    .appendTo($cart);
                
                /*
                 * Lets update the counter and total
                 *
                 * .find function will not find the current seat, because it will change its stauts only after return
                 * 'selected'. This is why we have to add 1 to the length and the current seat price to the total.
                 */
                $counter.text(sc.find('selected').length+1);
                $total.text(recalculateTotal(sc)+this.data().price);
                
                return 'selected';
            } else if (this.status() == 'selected') {
                //update the counter
                $counter.text(sc.find('selected').length-1);
                //and total
                $total.text(recalculateTotal(sc)-this.data().price);
            
                //remove the item from our cart
                $('#cart-item-'+this.settings.id).remove();
            
                //seat has been vacated
                return 'available';
            } else if (this.status() == 'unavailable') {
                //seat has been already booked
                return 'unavailable';
            } else {
                return this.style();
            }
        }
    });

    //this will handle "[cancel]" link clicks
    $('#selected-seats').on('click', '.cancel-cart-item', function () {
        //let's just trigger Click event on the appropriate seat, so we don't have to repeat the logic here
        sc.get($(this).parents('li:first').data('seatId')).click();
    });
    
    var booked_list = [];
    var booked_num = randomIntFromInterval(10,50);

    for(var i = 0; i < booked_num; i++){
        var s = randomIntFromInterval(1,12).toString() + "_" + randomIntFromInterval(1,20);
        booked_list.push(s);
    } 
    //console.log(booked_list);
    
    //let's pretend some seats have already been booked
    sc.get(booked_list).status('unavailable');
    
    //dialog selection event
    $(document).on('click', '.dialog-selection',function(){
        var selection = $(this).html();
        $("#user_input").val(selection);
        get_response();
    });

    //button click events
    $("#reset-button").click(function(){
        if(booking_dialog)
            booking_dialog.dialog('close');
        reset_dialog(true); 
    });

    $("#next-button").click(function(){
        get_response(); 
    });

    $("#user_input").keypress(function(e){
        code = (e.keyCode ? e.keyCode : e.which);
        if (code == 13){
            get_response();
        }
    });
    
    $('.checkout-button').click(function(){
        if(validateEmail($("#email_input").val())){
            if(sc.find('selected').length != 0){
                var alert_str = "你已經訂了" + booking_info["theater_name"] + "於" + booking_info["showing_time"] + "放映的" + booking_info["movie_name"] + "的票\n座位為";
                console.log(booking_info);
                var data = {"email": $("#email_input").val(), "movie": booking_info["movie_name"], "theater": booking_info["theater_name"], "seats": [], "time": booking_info["showing_time"]};
                sc.find('selected').each(function(){
                    var tokens = this.settings.id.split("_");
                    tokens[1] = parseInt(tokens[1]);
                    if(tokens[1] >= 6){
                        tokens[1] = tokens[1] - 2;
                    }
                    else if(tokens[1] >= 18){
                        tokens[1] = tokens[1] - 4;
                    }
                    var seat_str = "第" + tokens[0] + "排" + tokens[1].toString() + "號"
                    data["seats"].push(seat_str);
                    alert_str = alert_str + seat_str + "、";
                });

                $.ajax({
                    url: '/mail',
                    type: "POST", 
                    data: JSON.stringify(data),
                    contentType: "application/json",
                    complete: function(){
                        alert(alert_str);
                        location.reload();
                    }
                });

                alert_str = alert_str.slice(0, -1);
                alert_str = alert_str + "，訂票成功！\n總金額為" + recalculateTotal(sc) + "元";
            }
            else{
                alert("尚未選取座位！");
            }
        }
        else{
                alert("請輸入正確的email address！");
        }
    });

});

function recalculateTotal(sc) {
    var total = 0;

    //basically find every selected seat and sum its price
    sc.find('selected').each(function () {
        total += this.data().price;
    });
    
    return total;
}
