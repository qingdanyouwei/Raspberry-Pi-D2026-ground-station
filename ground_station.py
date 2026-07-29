#!/usr/bin/env python3
"""
D题陆空协同 - 地面站主程序
实时显示无人机+小车位置、状态信息
"""
import json, threading, time
import rospy
from std_msgs.msg import String
from config import *
from screen_driver import ScreenDriver
from ano_controller import AnoController

class GroundStation:
    def __init__(self):
        self.drone_xy = None
        self.car_xy = None
        self.drone_h = 0
        self.status = "等待飞控连接..."

        rospy.init_node('ground_station', anonymous=True)
        self.screen = ScreenDriver()
        self.screen.open()

        self.ano = AnoController()
        self.ano.open()
        self.ano.set_position_callback(self._on_position)

        self._running = True
        t = threading.Thread(target=self._read_serial, daemon=True)
        t.start()
        self._draw_thread = threading.Thread(target=self._draw_loop, daemon=True)
        self._draw_thread.start()
        rospy.loginfo("[地面站] 初始化完成")

    def _on_position(self, dx, dy, dh, cx, cy):
        self.drone_xy = (dx, dy)
        self.drone_h = dh
        self.car_xy = (cx, cy)

    def _draw_loop(self):
        track = get_track_points()
        self.screen.draw_field(track)
        time.sleep(1)
        while self._running:
            try:
                status_lines = [
                    f"无人机X:{self.drone_xy[0] if self.drone_xy else '-'}cm",
                    f"无人机Y:{self.drone_xy[1] if self.drone_xy else '-'}cm",
                    f"高度:{self.drone_h}cm",
                    f"小车X:{self.car_xy[0] if self.car_xy else '-'}cm",
                    f"小车Y:{self.car_xy[1] if self.car_xy else '-'}cm",
                    f"",
                    f"{self.status}",
                ]
                status_text = "\\r".join(status_lines)
                self.screen.update_positions(
                    self.drone_xy, self.car_xy, status_text
                )
            except:
                pass
            time.sleep(0.5)

    def _read_serial(self):
        while self._running:
            if not self.screen.ok:
                time.sleep(0.1)
                continue
            try:
                if self.screen.ser.in_waiting:
                    raw = self.screen.ser.read(self.screen.ser.in_waiting)
                    text = raw.decode(self.screen.encoding, errors='ignore')
                    if 'START' in text:
                        self.status = "任务启动"
                    elif 'DROP' in text:
                        self.status = "抛投中..."
                    elif 'LAND' in text:
                        self.status = "降落中..."
            except:
                time.sleep(0.1)

    def run(self):
        rospy.spin()

    def shutdown(self):
        self._running = False
        self.screen.close()
        self.ano.close()

if __name__ == '__main__':
    gs = GroundStation()
    gs.run()
