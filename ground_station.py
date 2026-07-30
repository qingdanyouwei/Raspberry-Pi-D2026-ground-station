#!/usr/bin/env python3
"""
D题陆空协同 - 地面站主程序
0xF2帧接收: 无人机/小车UWB坐标+高度+状态
"""
import threading, time
import rospy
from screen_driver import ScreenDriver
from ano_controller import AnoController

class GroundStation:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

        rospy.init_node('ground_station', anonymous=True)
        self.screen = ScreenDriver()
        self.screen.open()
        self.screen.init_display()

        self.ano = AnoController()
        self.ano.open()
        self.ano.set_callback(self._on_data)

        self._running = True
        t = threading.Thread(target=self._draw_loop, daemon=True)
        t.start()
        rospy.loginfo("[地面站] 初始化完成")

    def _on_data(self, d):
        with self.lock:
            self.data = d

    def _draw_loop(self):
        while self._running:
            try:
                with self.lock:
                    d = dict(self.data)
                drone_xy = (d.get("drone_x", 0), d.get("drone_y", 0))
                car_xy = (d.get("car_x", 0), d.get("car_y", 0))
                lines = [
                    f"状态:{d.get('state_name','-')}",
                    f"模式:{d.get('mode','-')}",
                    f"运行:{d.get('running','-')}",
                    f"飞行:{d.get('flying','-')}",
                    f"小车在线:{d.get('car_online','-')}",
                    f"路段:{d.get('section','-')}",
                    f"",
                    f"无人机",
                    f"X:{drone_xy[0]}cm",
                    f"Y:{drone_xy[1]}cm",
                    f"融合H:{d.get('drone_h','-')}cm",
                    f"激光H:{d.get('laser_h','-')}cm",
                    f"",
                    f"小车",
                    f"X:{car_xy[0]}cm",
                    f"Y:{car_xy[1]}cm",
                ]
                text = "\\r".join(lines)
                self.screen.update_positions(drone_xy, car_xy, text)
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
