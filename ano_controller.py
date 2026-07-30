"""
ANO飞控通讯模块 - D题陆空协同
解析0xF2帧(34字节): 无人机UWB+小车UWB+高度+状态
"""
import struct
import threading
import time
import serial

FRAME_HEAD = 0xAA
ANO_PORT = "/dev/ttyACM0"
ANO_BAUD = 500000

MISSION_NAMES = {
    0: "空闲", 1: "起飞", 2: "巡航", 3: "悬停",
    4: "返航", 5: "降落", 6: "完成",
    7: "悬停3秒", 8: "伴飞", 9: "投掷逼近", 10: "投掷",
}

def calc_checksum(frame):
    s = a = 0
    for b in frame:
        s = (s + b) & 0xFF
        a = (a + s) & 0xFF
    return s, a


class AnoController:
    def __init__(self):
        self.ser = None
        self.ok = False
        self.running = False
        self.rx_buf = bytearray()
        self.lock = threading.Lock()
        self.data = {"drone_x": 0, "drone_y": 0, "drone_h": 0,
                     "laser_h": 0, "car_x": 0, "car_y": 0,
                     "mode": 0, "state": 0, "car_online": 0,
                     "flying": 0, "running": 0, "section": 0}
        self.callback = None

    def open(self):
        try:
            self.ser = serial.Serial(ANO_PORT, ANO_BAUD, timeout=0.05)
            self.ok = True
            self.running = True
            t = threading.Thread(target=self._rx_loop, daemon=True)
            t.start()
            print(f"[ANO飞控] 已连接 {ANO_PORT}")
            return True
        except Exception as e:
            print(f"[ANO飞控] 未连接: {e}")
            return False

    def close(self):
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()

    def set_callback(self, cb):
        self.callback = cb

    def _rx_loop(self):
        while self.running:
            try:
                d = self.ser.read(512)
                if d:
                    self._parse(d)
            except:
                time.sleep(0.01)

    def _parse(self, data):
        self.rx_buf.extend(data)
        while True:
            while self.rx_buf and self.rx_buf[0] != FRAME_HEAD:
                self.rx_buf.pop(0)
            if len(self.rx_buf) < 4:
                return
            dlen = self.rx_buf[3]
            if dlen > 128:
                self.rx_buf.pop(0)
                continue
            flen = 4 + dlen + 2
            if len(self.rx_buf) < flen:
                return
            frame = bytes(self.rx_buf[:flen])
            del self.rx_buf[:flen]
            s, a = calc_checksum(frame[:-2])
            if s != frame[-2] or a != frame[-1]:
                continue
            msg_id = frame[2]
            payload = frame[4:4+dlen]
            if msg_id == 0xA0 and len(payload) >= 2:
                t = payload[1:].decode("ascii", "ignore").strip("\x00\r\n ")
                if t:
                    print(f"[ANO飞控] <- {t}")
            elif msg_id == 0xF2 and dlen >= 30:
                self._update_f2(payload)

    def _update_f2(self, p):
        if p[0] != 2:
            return
        ver, mode, state, flags = struct.unpack_from("<4B", p, 0)
        drone_x = struct.unpack_from("<i", p, 4)[0]
        drone_y = struct.unpack_from("<i", p, 8)[0]
        fusion_h = struct.unpack_from("<i", p, 12)[0]
        laser_h = struct.unpack_from("<i", p, 16)[0]
        car_x = struct.unpack_from("<i", p, 20)[0]
        car_y = struct.unpack_from("<i", p, 24)[0]
        section = p[28]
        running = (flags >> 0) & 1
        car_on = (flags >> 2) & 1
        flying = (flags >> 3) & 1
        with self.lock:
            self.data = {
                "drone_x": drone_x, "drone_y": drone_y,
                "drone_h": fusion_h, "laser_h": laser_h,
                "car_x": car_x, "car_y": car_y,
                "mode": mode, "state": state,
                "car_online": car_on, "flying": flying,
                "running": running, "section": section,
                "state_name": MISSION_NAMES.get(state, str(state)),
            }
        if self.callback:
            self.callback(dict(self.data))
