from flask import Flask, request, render_template, send_file, send_from_directory, jsonify
import DialogueManager
from model_acc48 import emotion_gender_recognizer_jointly_training
import pickle
import numpy as np
import subprocess
import tensorflow as tf
import base64
import smtplib, os, sys, time
import http.client, urllib.request, urllib.parse, urllib.error
import json
from random import randint
from speech_api import Speech
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

#UPLOAD_FOLDER = "./static/img/"
app = Flask(__name__)
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

g1 = tf.Graph()
with g1.as_default():
    emotion_recognizer = emotion_gender_recognizer_jointly_training.restore()

#manager = DialogueManager('dst/dst_data/dataset/table.tsv','dst/dst_data/dataset/movie_time.values')
#usergoal_file = 'dst/dst_data/data/usergoal.v2.pkl'
#template_file = 'dst/dst_data/data/template.v2.json'
print('Initialize dialogue manager')
dialogue_manager = DialogueManager.DialogueManager()
#dialogue_manager.load_policy_nn()

#dialogue_manager.load_previous_experience_pool('exp_buffer.pkl')
#dialogue_manager.load_previous_experience_pool('exp_buffer_book_directly_2.pkl')
episode_over = False
system_sf = {}
data_face = []
speech_emotion = ''
#dialog_history = ["System: Hi, 我可以幫你訂票嗎？"]

address = "icb2017ta@gmail.com"
passwd = "yunnungyunnunggogogoeatsushi"
subject = "[MovieBot] 訂票成功通知"
img_filename = './static/img/qr_code.jpg'
msBingSpeechAPIKey = "f05528cb69b2435ba22126a12ca6ca72"
voice_path = "./static/files/voice.wav"
speech_api = Speech(msBingSpeechAPIKey)

def connectSMTP():
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    if s.has_extn('STARTTLS'):
        s.starttls()
        s.ehlo()

    account = address.split('@')[0]
    s.login(account, passwd)
    print("SMTP Connected!")
    return s

def stringToBase64(s):
    return base64.b64encode(s.encode('utf-8'))

def googleTTS(s):
    subprocess.call('wget -q -U Mozilla -O static/files/voice.mp3 "http://translate.google.com/translate_tts?ie=UTF-8&total=1&idx=0&textlen=32&client=tw-ob&q=' + s + '&tl=zh-TW"', shell=True)

@app.route('/')
def api_root():
    return render_template("index.html")

@app.route('/response')
def api_response():

    input_sentence = request.args['input_sentence']
    print(input_sentence)

    if input_sentence.rstrip() == 'exit':
        print('A new episode begin, reset')
        dialogue_manager.reset()
        # greeting based on face recognition
        greeting_sentence = "您好您好，請問我可以幫你訂票嗎？"
        if data_face:
            if data_face[0]['faceAttributes']['gender'] == 'female':
                if data_face[0]['faceAttributes']['age'] < 20:
                    greeting_sentence = "妹妹~我是不是在哪裡看過妳, 請問我可以幫妳訂票嗎？"
                elif data_face[0]['faceAttributes']['age'] > 30:
                    greeting_sentence = "姊姊~我是不是在哪裡看過妳, 請問我可以幫妳訂票嗎？"
                else:
                    greeting_sentence = "美女~我是不是在哪裡看過妳, 請問我可以幫妳訂票嗎？"
            if data_face[0]['faceAttributes']['gender'] == 'male':
                if data_face[0]['faceAttributes']['age'] < 20:
                    greeting_sentence = "弟弟~我是不是在哪裡看過你, 請問我可以幫你訂票嗎？"
                elif data_face[0]['faceAttributes']['age'] > 30:
                    greeting_sentence = "歐巴~我是不是在哪裡看過你, 請問我可以幫你訂票嗎？"
                else:
                    greeting_sentence = "帥哥~我是不是在哪裡看過你, 請問我可以幫你訂票嗎？"
        binary = speech_api.text_to_speech(greeting_sentence.encode("utf-8").decode("latin-1"), female=False)
        with open(voice_path, "wb") as f:
            f.write(binary)
        return jsonify(booking=False, nl=greeting_sentence)
    elif input_sentence.strip() == 'reset':
        dialogue_manager.reset()
        binary = speech_api.text_to_speech("系統已經被重置, 請問我可以幫你訂票嗎？".encode("utf-8").decode("latin-1"), female=False)
        with open(voice_path, "wb") as f:
            f.write(binary)
        return jsonify(booking=False, nl="系統已經被重置, 請問我可以幫你訂票嗎？")


    system_rf, nn_nlg = dialogue_manager.update(input_sentence)
    # response based on speech emotion
    global speech_emotion
    print(speech_emotion)
    if speech_emotion == 'angry':
        nn_nlg = "好啦, 不要森七七了~{}".format(nn_nlg)
    elif speech_emotion == 'happy':
        nn_nlg = "你是不是覺得這個機器人很強, {}".format(nn_nlg)
    elif speech_emotion == 'fear':
        nn_nlg = "別怕, 我也是第一次...幫人訂票, {}".format(nn_nlg)
    elif speech_emotion == 'sad':
        nn_nlg = "不哭不哭, 眼淚是珍珠~{}".format(nn_nlg)
    speech_emotion = 'neutral'
    print(nn_nlg)

    if "我和我的冠軍女友" in input_sentence:
        nn_nlg = "醒醒吧！你沒有女友，" + nn_nlg

    binary = speech_api.text_to_speech(nn_nlg.split("<br>")[0].encode("utf-8").decode("latin-1"), female=False)
    with open(voice_path, "wb") as f:
        f.write(binary)
    if system_rf['act_type'] == 'confirm':
      return jsonify(booking = True, nl = nn_nlg, sf=system_rf)

    return jsonify(booking = False, nl = nn_nlg, sf=system_rf)

    """
    dialogue_manager.convert_user_nl_to_next_dst_state(input_sentence, episode_over)
    dialogue_manager.copy_next_state_to_cuttent_exp()
    system_sf, nn_nlg, avg_bleu, max_bleu = dialogue_manager.next()
    print(nn_nlg)
    print(system_sf)

    if system_sf['action_type'] != 'booking' and len(system_sf['request_slots']) == 0:
        responseFound = False
        for slot in system_sf['inform_slots']:
            if len(system_sf['inform_slots'][slot]) != 0:
                responseFound = True
        if not responseFound:
            print('系統：抱歉，沒有符合條件的選項')
            episode_over = True
            #dialog_history.append("System: 抱歉，沒有符合條件的選項")
            googleTTS("抱歉，沒有符合條件的選項")
            return jsonify(booking=False, nl="抱歉，沒有符合條件的選項")
    """

    '''
    Check whether valid ticket exists.
    '''
    """
    if system_sf['action_type'] == 'booking' and len(system_sf['inform_slots']) == 0:
        filled_slots_count = 0
        if len(dialogue_manager.state['obtain_slots']['movie_name']) > 0:
            filled_slots_count += 1
        if len(dialogue_manager.state['obtain_slots']['movie_time']) > 0:
            filled_slots_count += 1
        if len(dialogue_manager.state['obtain_slots']['theater']) > 0:
            filled_slots_count += 1
        if len(dialogue_manager.state['obtain_slots']['location']) > 0:
            filled_slots_count += 1
        if filled_slots_count == 4:
            print('系統：抱歉，沒有符合條件的票')
            episode_over = True
            googleTTS("抱歉，沒有符合條件的選項")
            #dialog_history.append("System: 抱歉，沒有符合條件的選項")
            return jsonify(booking=False, nl="抱歉，沒有符合條件的選項")

    googleTTS(nn_nlg)

    if system_sf['action_type'] == 'booking':
        episode_over = True
        #dialog_history.append("System: " + nn_nlg)
        return jsonify(booking=True, nl=nn_nlg, system_sf=system_sf)
    else:
        #dialog_history.append("System: " + nn_nlg)
        return jsonify(booking=False, nl=nn_nlg)
    """
@app.route('/mail', methods=['POST'])
def api_mail():
    data = request.get_json(force=True)
    print(data)
    server = connectSMTP()
    sender = address
    seat_str = ""

    for t in data["seats"]:
        seat_str = seat_str + t + '\t'

    html = '<!DOCTYPE html><html><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /></head><body>親愛的使用者您好!<br>非常感謝您使用我們的系統<br>您的訂票資訊如下：<br>電影名稱：' + data["movie"] + '<br>電影院：' + data["theater"] + '<br>時間：' + data["time"] + '<br>座位：' + seat_str + '<br>進場時出示附檔的QR code即可入場<br>MovieBot期待您下次的使用！<br><br>科技始終來自人性 只有MovieBot 沒有距離</body></html>'

    recipient = data["email"]
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = subject
    msgRoot['From'] = sender
    msgRoot['To'] = recipient
    #msg['Bcc'] = sender

    msg = MIMEMultipart('alternative')
    msgRoot.attach(msg)
    mailText = MIMEText(html, 'html')
    msg.attach(mailText)

    img_data = open(img_filename, 'rb')
    image = MIMEImage(img_data.read(), name=os.path.basename(img_filename))
    img_data.close()
    image.add_header('Content-ID', '<image1>')
    msgRoot.attach(image)

    try:
        server.sendmail(sender, recipient, msgRoot.as_string())
    except Exception as e:
        print(type(e).__name__)

    server.quit()

    return "mail sended!"

@app.route('/record', methods=['POST'])
def api_record():
    if request.form['command'] == 'record':
        print("get record...")
        f = open('static/files/sound.wav', 'wb')
        f.write(request.files['source'].stream.read())
        f.close()
        emotion_list = ['happy', 'angry', 'sad', 'fear', 'neutral']
        rc = subprocess.call("bash script/extract_feat.sh -i ./static/files/sound.wav -o ./static/files -f 30", shell=True)
        p = emotion_gender_recognizer_jointly_training.classify_emotion(emotion_recognizer, "./static/files/sound.audio.npy")
        print("="*15 + "Emotion recognizer" + "="*15)
        print(emotion_list)
        print(p)
        print(emotion_list[np.argmax(p)])
        global speech_emotion
        speech_emotion = emotion_list[np.argmax(p)]
        return emotion_list[np.argmax(p)]
    else:
        return "Getting record failed..."

@app.route('/capture', methods=['POST'])
def api_capture():
    data = request.get_json(force=True)
    global data_face
    #base64_str = data["imgBase64"]
    if data:
        base64_str = data["imgBase64"].replace('data:image/png;base64,','')
        f = open("static/img/user_upload.png", "wb")
        f.write(base64.decodestring(base64_str.encode()))
        print("get capture data")

        headers = {
            'Content-Type': 'application/octet-stream',
            'Ocp-Apim-Subscription-Key': '54b997bce88d4a4f8583d30702a3e00b',
        }

        params = urllib.parse.urlencode({
            'returnFaceId': 'true',
            'returnFaceLandmarks': 'false',
            'returnFaceAttributes': 'age,gender,emotion'
        })

        try:
            conn = http.client.HTTPSConnection('southeastasia.api.cognitive.microsoft.com')
            conn.request("POST", "/face/v1.0/detect?%s" % params, base64.decodestring(base64_str.encode()), headers)
            response = conn.getresponse()
            data_face = json.loads(response.read().decode('utf-8'))
            conn.close()
        except Exception as e:
            print(e)
    else:
        data_face = []
    #print(base64_str)
    print(data_face)
    return "upload capture image success!"

if __name__ == '__main__':
    context = ('static/resources/udara.com.crt', 'static/resources/udara.com.key')
    app.run(port = 8000, host='0.0.0.0', ssl_context = context)
