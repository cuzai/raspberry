# -*- coding: utf-8 -*-
from flask import Flask, request, make_response, jsonify
import os
import threading
import time

app = Flask(__name__)
cur_temp = 26
fan = 1
airOffIn = 0
delay = ''

def get_temp(temp, fan):
    os.system('sudo python /home/pi/Desktop/iot/irrp.py -p -g14 -f/home/pi/Desktop/iot/codes {}-{}'.format(temp, fan))

def results():
    # build a request object
    req = request.get_json(force=True)
    # fetch action from json
    gotJson = req.get('queryResult').get('parameters')

    if gotJson.get('timer') == None:
        return setTemp(gotJson)
    else:
        delay = gotJson.get('timer').encode('utf-8')

        return startTimer(delay)


def setTemp(gotJson):
    global cur_temp
    global fan
    global airOffIn
    if gotJson.get('onOff') != '' and gotJson.get('onOff') != None:
        if gotJson.get('onOff') == 'on':
            cur_temp = 26
            fan = 1
            response = "네, 에어컨을 기본 설정인 {}도, 바람 세기 {}로 켭니다옹".format(cur_temp, fan)
        else:
            cur_temp = 'off'
            airOffIn = 0
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
    global airOffIn
    global t_stop
    global t
    availLi = ['3초', '1분', '30분', '1시간 30분','2시간','2시간 30분','3시간','3시간 30분','4시간','4시간 30분','5시간']
    if delay not in availLi :
        return "예약 가능한 시간이 아닙니다."
    else :
        if delay == '3초':
            airOffIn = 3
        elif delay == '1분':
            airOffIn = 1 * 60
        elif delay == '30분':
            airOffIn = 30 * 60
        elif delay == '1시간 30분':
            airOffIn = (1 * 60 * 60) + (30 * 60)
        elif delay == '2시간':
            airOffIn = (2 * 60 * 60)
        elif delay == '2시간 30분':
            airOffIn = (2 * 60 * 60) + (30 * 60)
        elif delay == '3시간':
            airOffIn = (3 * 60 * 60)
        elif delay == '3시간 30분':
            airOffIn = (3 * 60 * 60) + (30 * 60)
        elif delay == '4시간':
            airOffIn = (4 * 60 * 60)
        elif delay == '4시간 30분':
            airOffIn = (4 * 60 * 60) + (30 * 60)
        elif delay == '5시간':
            airOffIn = (5 * 60 * 60)
        t_stop.set()
        t = threading.Thread(target=myTimer, args=(1, t_stop))
        t.start()
        return "{}뒤에 에어컨을 끕니다.".format(delay)

def myTimer(arg1, stop_event):
    print('in Thread')
    global airOffIn
    print(airOffIn)
    global delay
    for i in range(airOffIn):
        while not stop_event.is_set() :
            print('{} : {}'.format(delay, airOffIn))
            airOffIn = airOffIn - 1
            stop_event.wait(timeout=1)
            if airOffIn == 0 :
                get_temp('off', 1)
                print('air should be off')

@app.route('/air', methods=['POST'])
def air():
    response = results()
    return make_response(jsonify({'fulfillmentText': response}))

t_stop = threading.Event()
t = threading.Thread(target=myTimer, args=(1, t_stop))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5093)

