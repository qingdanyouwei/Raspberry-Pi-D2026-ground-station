"""
串口屏驱动 - D题陆空协同
显示场地+轨迹+标记点+无人机/小车实时位置
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
        """一次性绘制场地背景（边框+轨迹+标记）"""
        import config as cfg
        self.cmd(f"fill 0,0,800,480,{C_BLACK}")
        # 场地边框
        x1, y1 = cfg.OFFSET_X, cfg.OFFSET_Y
        w, h = int(cfg.FIELD_W * cfg.SCALE), int(cfg.FIELD_H * cfg.SCALE)
        self.cmd(f"draw {x1},{y1},{w},{h},{C_WHITE}")
        # 循线轨迹
        for i in range(len(track_points) - 1):
            sx1, sy1 = track_points[i]
            sx2, sy2 = track_points[i + 1]
            self.cmd(f"line {sx1},{sy1},{sx2},{sy2},{C_WHITE}")
        # 标记点: H(红) A(绿) B C D(黄)
        for name, x, y, color in [
            ("H", cfg.H_X, cfg.H_Y, C_RED),
            ("A", cfg.A_X, cfg.A_Y, C_GREEN),
            ("B", cfg.B_X, cfg.B_Y, C_YELLOW),
            ("C", cfg.C_X, cfg.C_Y, C_YELLOW),
            ("D", cfg.D_X, cfg.D_Y, C_YELLOW),
        ]:
            sx, sy = self._field_to_screen(x, y)
            self.cmd(f"cirs {sx},{sy},6,{color}")
            self.cmd(f'xstr {sx-8},{sy-16},{20},{14},1,{C_WHITE},2,"{name}"')

    def _field_to_screen(self, x_cm, y_cm):
        import config as cfg
        sx = cfg.OFFSET_X + int(y_cm * cfg.SCALE)
        sy = cfg.OFFSET_Y + int((cfg.FIELD_H - x_cm) * cfg.SCALE)
        return sx, sy

    def update_positions(self, drone_xy, car_xy, status_text):
        """刷新无人机(红)和小车(绿)位置"""
        import config as cfg
        # 用fill覆盖旧的场地区域再重画(简单粗暴)
        x1 = cfg.OFFSET_X
        y1 = cfg.OFFSET_Y
        w = int(cfg.FIELD_W * cfg.SCALE)
        h = int(cfg.FIELD_H * cfg.SCALE)
        self.cmd(f"fill {x1},{y1},{w},{h},{C_BLACK}")
        # 重画边框
        self.cmd(f"draw {x1},{y1},{w},{h},{C_WHITE}")
        # 重画轨迹
        import config
        track = config.get_track_points()
        for i in range(len(track) - 1):
            self.cmd(f"line {track[i][0]},{track[i][1]},{track[i+1][0]},{track[i+1][1]},{C_WHITE}")
        # 重画标记点
        for name, x, y, color in [
            ("H", cfg.H_X, cfg.H_Y, C_RED),
            ("A", cfg.A_X, cfg.A_Y, C_GREEN),
        ]:
            sx, sy = self._field_to_screen(x, y)
            self.cmd(f"cirs {sx},{sy},6,{color}")
        # 小车绿点
        if car_xy:
            sx, sy = self._field_to_screen(car_xy[0], car_xy[1])
            self.cmd(f"cirs {sx},{sy},7,{C_GREEN}")
            self.cmd(f'xstr {sx-10},{sy+10},{20},{14},1,{C_GREEN},2,"车"')
        # 无人机红点
        if drone_xy:
            sx, sy = self._field_to_screen(drone_xy[0], drone_xy[1])
            self.cmd(f"cirs {sx},{sy},7,{C_RED}")
            self.cmd(f'xstr {sx-10},{sy-20},{20},{14},1,{C_RED},2,"机"')
        # 右侧状态
        self.cmd(f'fill 570,40,220,440,{C_BLACK}')
        self.cmd(f'xstr 580,40,200,400,1,{C_WHITE},0,"{status_text}"')
