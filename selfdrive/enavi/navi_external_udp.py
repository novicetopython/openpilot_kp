#!/usr/bin/env python3
import threading
import socket

import cereal.messaging as messaging

# KisaPilot, this is for getting navi data from external device using UDP broadcast.


def udp_broadcast_listener():
  pm = messaging.PubMaster(['liveENaviData'])

  spd_limit = 0
  safety_distance = 0
  safety_bl_distance = 0
  sign_type = ''
  road_limit_speed = 0
  road_name = ''
  current_speed = 0
  check_connection = False

  cnt1 = cnt2 = 0
  cnt_threshold = 1

  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
  sock.bind(('', 12345))
  sock.settimeout(3)

  while True:
    navi_msg = messaging.new_message('liveENaviData')
    try:
      data, addr = sock.recvfrom(1024)
      if "kisasigntype" in data.decode('utf-8'):
        cnt1 = 0
        check_connection = True
        data_str = data.decode('utf-8')
        data_dict = {}
        key_value_pairs = data_str.split('/')
        for pair in key_value_pairs:
          if pair:
            key, value = pair.split(':')
            data_dict[key] = value
        spd_limit = int(data_dict.get('kisaspdlimit'))
        safety_distance = float(data_dict.get('kisaspddist'))
        safety_bl_distance = float(data_dict.get('kisaspdbldist'))
        sign_type = str(data_dict.get('kisasigntype'))
        current_speed = int(data_dict.get('kisacurrentspd'))
      elif "Kisa_Tmap_Alive" in data.decode('utf-8'):
        cnt1 += 1
        if cnt1 > cnt_threshold:
          cnt1 = 0
          spd_limit = 0
          safety_distance = 0.0
          safety_bl_distance = 0.0
          sign_type = ''
          current_speed = 0
      if "kisaroadlimitspd" in data.decode('utf-8'):
        cnt2 = 0
        check_connection = True
        data_str = data.decode('utf-8')
        data_dict = {}
        key_value_pairs = data_str.split('/')
        for pair in key_value_pairs:
          if pair:
            key, value = pair.split(':')
            data_dict[key] = value
        road_limit_speed = int(data_dict.get('kisaroadlimitspd'))
        road_name = str(data_dict.get('kisaroadname'))
      elif "Kisa_Tmap_Alive" in data.decode('utf-8'):
        cnt2 += 1
        if cnt2 > cnt_threshold+2:
          cnt2 = 0
          road_limit_speed = 0
          road_name = ''
    except socket.timeout:
      spd_limit = 0
      safety_distance = 0.0
      safety_bl_distance = 0.0
      current_speed = 0
      sign_type = ''
      road_limit_speed = 0
      road_name = ''
      check_connection = False

    navi_msg.liveENaviData.speedLimit = int(spd_limit)
    if safety_distance != 0.0:
      navi_msg.liveENaviData.safetyDistance = float(safety_distance)
    else:
      navi_msg.liveENaviData.safetyDistance = float(safety_bl_distance)
    navi_msg.liveENaviData.safetySign = str(sign_type)
    navi_msg.liveENaviData.roadLimitSpeed = int(road_limit_speed)  
    navi_msg.liveENaviData.roadName = str(road_name)
    navi_msg.liveENaviData.connectionAlive = bool(check_connection)

    pm.send('liveENaviData', navi_msg)

  sock.close()


def main():
  udp_thread = threading.Thread(target=udp_broadcast_listener, daemon=False)
  udp_thread.start()


if __name__ == "__main__":
  main()
