var firstSeatLabel = 1;

function randomIntFromInterval(min,max)
{
    return Math.floor(Math.random()*(max-min+1)+min);
}

$(document).ready(function() {
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
                $("#emotion").html(data);
            }
        });
    }
    
    window.onload = function init(){
        try{
            window.AudioContext = window.AudioContext || window.webkitAudioContext;
            navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia;
            window.URL = window.URL || window.webkitURL;
    
            audio_context = new AudioContext; 
        }catch(e){
            alert('No web audio support in this browser!');
        }
        navigator.getUserMedia({audio: true}, startUserMedia, function(e){
            __log('No live audio input: ' + e);
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
    
    function validateEmail(email) {
        var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(email);
    }

    function scrollToBottom() {
        $('#dialog').scrollTop($('#dialog')[0].scrollHeight);
    }

    function reset_dialog(){
        $("#user_input").val("");
        $.ajax({
            url: '/response?input_sentence=exit',
            type: 'GET',
            success: function(data){
                output_str = data['nl'];
                $("#dialog").empty();
                $("#dialog").append("<div class='dialog-row'><div class='bot-img'><img src='../static/img/bot.jpg'></div><div class='bot-response'>" + output_str + "</div></div>");
            }
        }); 
    }
   
    function get_response() {
        var input_str = $("#user_input").val();
        if(input_str != ""){
            $("#dialog").append("<div class='dialog-row'><div class='user-img'><img src='../static/img/user.png'></div><div class='user-response'>" + input_str + "</div></div>");
            scrollToBottom();
            $("input").prop('disabled', true);
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
                    
                    if(data['booking']){
                        output_str = output_str + "  現在幫您轉到訂票頁面，請稍候！";
                        setTimeout(function(){ 
                            $("#root").fadeOut(500, function(){
                                $("#booking-block").fadeIn(500);
                            });
                        }, 2000);
                    }
                    $("#dialog").append("<div class='dialog-row'><div class='bot-img'><img src='../static/img/bot.jpg'></div><div class='bot-response'>" + output_str + "</div></div>");
                    scrollToBottom();
                    $("input").prop('disabled', false);
                }
            });
        }
    }
    
    reset_dialog();
    
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
    
    $(document).on('click', '.dialog-selection',function(){
        var selection = $(this).html();
        $("#user_input").val(selection);
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

    $("#reset-button").click(function(){
        reset_dialog();
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
                var alert_str = "你已經訂了";
                var data = {"email": $("#email_input").val(), "movie": "神力女超人", "theater": "華納威秀", "seats": [], "time": "14:00"};
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
                alert_str = alert_str + "的票，訂票成功！\n總金額為" + recalculateTotal(sc) + "元";
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
