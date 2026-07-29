"""
串口屏驱动 - D题陆空协同
显示场地+轨迹+无人机/小车实时位置+状态文字
"""
import serial
import time

SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200
ENCODING = "GB2312"
END = b'\xff\xff\xff'

C_WHITE = 65535
C_RED   = 63488
C_GREEN = 2016
C_YELLOW = 65504
C_BLUE  = 31
C_GRAY  = 33840
C_BLACK = 0

class ScreenDriver:
    def __init__(self):
        self.ser = None
        self.ok = False
        self.encoding = ENCODING
        self._drone_pos = None
        self._car_pos = None

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

    def draw_field(self, track_points):
        """画场地+轨迹，一次性"""
        from config import FIELD_W, FIELD_H, OFFSET_X, OFFSET_Y, SCALE, H_X, H_Y, A_X, A_Y
        self.cmd(f"fill 0,0,800,480,{C_BLACK}")
        # 场地边框
        x1, y1 = OFFSET_X, OFFSET_Y
        w, h = int(FIELD_W*SCALE), int(FIELD_H*SCALE)
        self.cmd(f"draw {x1},{y1},{w},{h},{C_WHITE}")
        # 循线轨迹
        for i in range(len(track_points)-1):
            sx1, sy1 = track_points[i]
            sx2, sy2 = track_points[i+1]
            self.cmd(f"line {sx1},{sy1},{sx2},{sy2},{C_WHITE}")
        # H点标记 (无人机)
        h_sx, h_sy = self._field_to_screen(H_X, H_Y)
        self.cmd(f"cirs {h_sx},{h_sy},8,{C_RED}")
        # A点标记 (小车出发点)
        a_sx, a_sy = self._field_to_screen(A_X, A_Y)
        self.cmd(f"cirs {a_sx},{a_sy},8,{C_GREEN}")

    def _field_to_screen(self, x_cm, y_cm):
        from config import SCALE, OFFSET_X, OFFSET_Y, FIELD_H
        sx = OFFSET_X + int(y_cm * SCALE)
        sy = OFFSET_Y + int((FIELD_H - x_cm) * SCALE)
        return sx, sy

    def update_positions(self, drone_xy, car_xy, status_text):
        """更新无人机和小车位置"""
        # 清除旧位置(用黑色覆盖)
        if self._drone_pos:
            self.cmd(f"cirs {self._drone_pos[0]},{self._drone_pos[1]},8,{C_BLACK}")
        if self._car_pos:
            self.cmd(f"cirs {self._car_pos[0]},{self._car_pos[1]},8,{C_BLACK}")
        # 画新位置
        if drone_xy:
            sx, sy = self._field_to_screen(drone_xy[0], drone_xy[1])
            self.cmd(f"cirs {sx},{sy},8,{C_RED}")
            self._drone_pos = (sx, sy)
        if car_xy:
            sx, sy = self._field_to_screen(car_xy[0], car_xy[1])
            self.cmd(f"cirs {sx},{sy},8,{C_GREEN}")
            self._car_pos = (sx, sy)
        # 状态文字
        self.cmd(f'xstr 580,40,200,400,1,{C_WHITE},0,"{status_text}"')

    def show_status_text(self, text):
        """右侧显示状态文字"""
        self.cmd(f'xstr 580,40,200,400,1,{C_WHITE},0,"{text}"')
