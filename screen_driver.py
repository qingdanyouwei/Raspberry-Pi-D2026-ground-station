"""
串口屏驱动 - D题陆空协同
背景图(exp0) + 无人机图标(drone) + 小车图标(car) + 右侧状态文字
"""
import serial
import time
from config import *

SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200
ENCODING = "GB2312"
END = b'\xff\xff\xff'

C_WHITE = 65535
C_BLACK = 0

class ScreenDriver:
    def __init__(self):
        self.ser = None
        self.ok = False
        self.encoding = ENCODING

    def open(self):
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
            self.ok = True
            print("[串口屏] 已连接")
            return True
        except:
            print("[串口屏] 未连接")
            return False

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()

    def cmd(self, s: str):
        if self.ok:
            self.ser.write(s.encode(self.encoding))
            self.ser.write(END)
            time.sleep(0.003)

    def init_display(self):
        """初始化：刷新背景图，配置图标"""
        self.cmd("ref exp0")
        self.cmd("vis drone,0")
        self.cmd("vis car,0")

    def update_positions(self, drone_xy, car_xy, status_text):
        """移动无人机和图标"""
        # 无人机
        if drone_xy:
            sx, sy = field_to_screen(drone_xy[0], drone_xy[1])
            self.cmd(f"vis drone,1")
            self.cmd(f"drone.x={sx-10}")
            self.cmd(f"drone.y={sy-10}")
        # 小车
        if car_xy:
            sx, sy = field_to_screen(car_xy[0], car_xy[1])
            self.cmd(f"vis car,1")
            self.cmd(f"car.x={sx-10}")
            self.cmd(f"car.y={sy-10}")
        # 状态文字
        self.cmd(f'xstr 585,20,200,440,1,{C_WHITE},0,"{status_text}"')
