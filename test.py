# -*- coding: utf-8 -*-
from flask import Flask, request, make_response, jsonify
import os
import threading
import time

app = Flask(__name__)
cur_temp = 26
fan = 1
timer = 0
isTimerOn = False

def get_temp(temp, fan):
    os.system('sudo python /home/pi/Desktop/iot/irrp.py -p -g14 -f/home/pi/Desktop/iot/codes {}-{}'.format(temp, fan))

def timerDetector():
    global timer
    while True:
        if timer == -1:
            get_temp('off', 1)
            print('air should be off')
            timer = 0

detectThread = threading.Thread(target=timerDetector)
detectThread.start()

def results():
    # build a request object
    req = request.get_json(force=True)
    # fetch action from json
    gotJson = req.get('queryResult').get('parameters')

    if gotJson.get('timer') == None:
        return setTemp(gotJson)
    else:
        delay = gotJson.get('timer')
        return startTimer(delay)


def setTemp(gotJson):
    global cur_temp
    global fan
    global timer
    global isTimerOn
    if gotJson.get('onOff') != '' and gotJson.get('onOff') != None:
        if gotJson.get('onOff') == 'on':
            cur_temp = 26
            fan = 1
            response = "네, 에어컨을 기본 설정인 {}도, 바람 세기 {}로 켭니다옹".format(cur_temp, fan)
        else:
            cur_temp = 'off'
            isTimerOn = False
            response = "에어컨을 끕니다옹"
    elif gotJson.get('curTemp') != '' and gotJson.get('curTemp') != None:
        if cur_temp == 'off':
            response = "현재 에어컨이 꺼져 있습니다."
        else:
            response = "현재 에어컨은 {}도, 바렘 세기 {}로 세팅되어 있습니다옹".format(cur_temp, fan)
        return response
    else:
        if gotJson.get('myTemp') != "" and gotJson.get('myTemp') != None:
            got_cur_temp = gotJson.get('myTemp')
            cur_temp = int(got_cur_temp)
        if gotJson.get('fan') != "" and gotJson.get('fan') != None:
            got_fan = gotJson.get('fan')
            fan = int(got_fan)

        response = "네 에어컨을 {}도, 바람 세기 {}로 설정했다옹".format(cur_temp, fan)
        get_temp(cur_temp, fan)
        return response

    # interact with air
    try:
        get_temp(cur_temp, fan)
    except Exception:
        pass

    return response

def startTimer(delay):
    global  isTimerOn
    isTimerOn = False
    isTimerOn = True
    t = threading.Thread(target=myTimer, args=(delay,))
    t.start()
    availLi = ['3초', '1분', '30분', '1시간 30분','2시간','2시간 30분','3시간','3시간 30분','4시간','4시간 30분','5시간']
    if delay.encode('utf-8') not in availLi :
        return "예약 가능한 시간이 아닙니다."
    else :
        return "{}뒤에 에어컨을 끕니다.".format(delay.encode('utf-8'))


def myTimer(delay):
    global timer
    global isTimerOn
    delay = delay.encode('utf-8')
    if delay == '3초':
        timer = 3
    elif delay == '1분':
        timer = 1 * 60
    elif delay == '30분' :
        timer = 30 * 60
    elif delay == '1시간 30분':
        timer = (1 * 60 * 60) + (30 * 60)
    elif delay == '2시간':
        timer = (2 * 60 * 60)
    elif delay == '2시간 30분':
        timer = (2 * 60 * 60) + (30 * 60)
    elif delay == '3시간':
        timer = (3 * 60 * 60)
    elif delay == '3시간 30분':
        timer = (3 * 60 * 60) + (30 * 60)
    elif delay == '4시간':
        timer = (4 * 60 * 60)
    elif delay == '4시간 30분':
        timer = (4 * 60 * 60) + (30 * 60)
    elif delay == '5시간':
        timer = (5 * 60 * 60)

    for i in range(timer):
        if isTimerOn == True:
            print(delay, timer)
            timer = timer - 1
            time.sleep(1)
    timer = -1
    isTimerOn = False

@app.route('/air', methods=['POST'])
def air():
    response = results()
    return make_response(jsonify({'fulfillmentText': response}))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5093)

