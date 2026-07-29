#!/usr/bin/env python3
"""
D题陆空协同 - 地面站主程序
"""
import threading, time
import rospy
from config import *
from screen_driver import ScreenDriver
from ano_controller import AnoController

class GroundStation:
    def __init__(self):
        self.drone_xy = None
        self.car_xy = None
        self.drone_h = 0
        self.status = "等待飞控..."

        rospy.init_node('ground_station', anonymous=True)
        self.screen = ScreenDriver()
        self.screen.open()
        self.screen.init_display()

        self.ano = AnoController()
        self.ano.open()
        self.ano.set_position_callback(self._on_position)

        self._running = True
        t = threading.Thread(target=self._draw_loop, daemon=True)
        t.start()
        rospy.loginfo("[地面站] 初始化完成")

    def _on_position(self, dx, dy, dh, cx, cy):
        self.drone_xy = (dx, dy)
        self.drone_h = dh
        self.car_xy = (cx, cy)

    def _draw_loop(self):
        while self._running:
            try:
                lines = [
                    f"无人机",
                    f"X:{self.drone_xy[0] if self.drone_xy else '-'}cm",
                    f"Y:{self.drone_xy[1] if self.drone_xy else '-'}cm",
                    f"H:{self.drone_h}cm",
                    f"",
                    f"小车",
                    f"X:{self.car_xy[0] if self.car_xy else '-'}cm",
                    f"Y:{self.car_xy[1] if self.car_xy else '-'}cm",
                    f"",
                    f"{self.status}",
                ]
                text = "\\r".join(lines)
                self.screen.update_positions(self.drone_xy, self.car_xy, text)
            except:
                pass
            time.sleep(0.3)

    def run(self):
        rospy.spin()

    def shutdown(self):
        self._running = False
        self.screen.close()
        self.ano.close()

if __name__ == '__main__':
    gs = GroundStation()
    gs.run()
