from flask import Flask, request, render_template, send_file, send_from_directory, jsonify
import DialogueManager
#from model_acc48 import emotion_gender_recognizer_jointly_training
import pickle
import numpy as np
import subprocess
import tensorflow as tf

import smtplib, os, sys, time
from random import randint
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

app = Flask(__name__)

#g1 = tf.Graph()
#with g1.as_default():
#    emotion_recognizer = emotion_gender_recognizer_jointly_training.restore()

#template_file = 'dst/dst_data/data/template.v2.json'
#print('Initialize user simulator')
dialogue_manager = DialogueManager.DialogueManager()
print('Initialize dialogue manager...')

episode_over = False
system_sf = {}

address = "icb2017ta@gmail.com"
passwd = "yunnungyunnunggogogoeatsushi"
subject = "[MovieBot] 訂票成功通知"
img_filename = './static/img/qr_code.jpg'

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

@app.route('/')
def api_root():
    return render_template("index.html")

@app.route('/response')
def api_response():

    input_sentence = request.args['input_sentence']
    print(input_sentence)

    global episode_over
    global system_sf
    #global dialog_history

    if input_sentence.rstrip() == 'exit':        
        print('A new episode begin, reset')
        dialogue_manager.reset()
        return jsonify(booking=False, nl="您好您好, 請問我可以幫你訂票嗎？")
    elif input_sentence.strip() == 'reset':
        dialogue_manager.reset()
        return jsonify(booking=False, nl="系統已經被重置, 請問我可以幫你訂票嗎？")
      

    system_rf, nn_nlg = dialogue_manager.update(input_sentence)
    if system_rf['act_type'] == 'booking':
      return jsonify(booking = True, nl = nn_nlg)
    #system_sf, nn_nlg, avg_bleu, max_bleu = dialogue_manager.next()
    #print(nn_nlg)
    #print(system_sf)

    return jsonify(booking = False, nl = nn_nlg)

    '''
    Check whether valid ticket exists.
    '''
    '''
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
            #dialog_history.append("System: 抱歉，沒有符合條件的選項")
            return jsonify(booking=False, nl="抱歉，沒有符合條件的選項")
    
    if system_sf['action_type'] == 'booking':
        episode_over = True
        #dialog_history.append("System: " + nn_nlg)
        return jsonify(booking=True, nl=nn_nlg, system_sf=system_sf)
    else:
        #dialog_history.append("System: " + nn_nlg)
        return jsonify(booking=False, nl=nn_nlg)
    '''
@app.route('/mail', methods=['POST'])
def api_mail():
    data = request.get_json(force=True)
    print(data["email"])
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
        #rc = subprocess.call("bash script/extract_feat.sh -i ./static/files/sound.wav -o ./static/files -f 30", shell=True)
        #p = emotion_gender_recognizer_jointly_training.classify_emotion(emotion_recognizer, "./static/files/sound.audio.npy")
        p = [0.1,0.1,0.1,0.1,0.5]
        return emotion_list[np.argmax(p)] 
    else:
        return "Getting record failed..."

if __name__ == '__main__':
    context = ('static/resources/udara.com.crt', 'static/resources/udara.com.key')
    app.run(port = 8000, host='0.0.0.0', ssl_context = context)
