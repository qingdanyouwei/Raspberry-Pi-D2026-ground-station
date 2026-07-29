"""
ANO飞控通讯模块 - D题陆空协同
接收无人机UWB(0xF9)和小车UWB(0xF8)
"""
import struct
import threading
import time
import serial
from config import *

FRAME_HEAD = 0xAA
ANO_PORT = "/dev/ttyACM0"
ANO_BAUD = 500000


def calc_checksum(frame_without_checksum: bytes):
    sumcheck = addcheck = 0
    for b in frame_without_checksum:
        sumcheck = (sumcheck + b) & 0xFF
        addcheck = (addcheck + sumcheck) & 0xFF
    return sumcheck, addcheck


class AnoController:
    def __init__(self):
        self.ser = None
        self.ok = False
        self.running = False
        self.rx_buf = bytearray()
        self.data_lock = threading.Lock()
        self.drone_pos = None  # (x_cm, y_cm, alt_cm)
        self.car_pos = None    # (x_cm, y_cm)
        self.fc_log = []
        self.position_callback = None

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

    def set_position_callback(self, cb):
        """回调: cb(drone_x, drone_y, drone_h, car_x, car_y)"""
        self.position_callback = cb

    def _rx_loop(self):
        while self.running:
            try:
                data = self.ser.read(512)
                if data:
                    self._parse_rx(data)
            except:
                time.sleep(0.01)

    def _parse_rx(self, data):
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
                text = payload[1:].decode("ascii", errors="ignore").strip("\x00\r\n ")
                if text:
                    self.fc_log.append(text)
                    print(f"[ANO飞控] <- {text}")
            elif msg_id == 0xF9 and len(payload) >= 27:
                self._update_drone(payload)
            elif msg_id == 0xF8 and len(payload) >= 8:
                cx, cy = struct.unpack_from("<ii", payload, 0)
                cx, cy = -cx, -cy  # 临时：坐标可能需要取反
                with self.data_lock:
                    self.car_pos = (cx, cy)
                self._notify()

    def _update_drone(self, payload):
        plen = len(payload)
        if plen >= 40 and payload[0] == 5:
            (ver, found, online, ex, ey, off, cid, cnt, evt,
             h, x, y, *_) = struct.unpack_from("<3B2hH2BI3i6BIBH", payload, 0)
        elif plen >= 27:
            (ver, found, online, ex, ey, off, cid, cnt, evt,
             h, x, y) = struct.unpack_from("<3B2hH2BI3i", payload, 0)
        else:
            return
        with self.data_lock:
            self.drone_pos = (x, y, h)
        self._notify()

    def _notify(self):
        if self.position_callback:
            with self.data_lock:
                d = self.drone_pos
                c = self.car_pos
            dx, dy, dh = d if d else (0, 0, 0)
            cx, cy = c if c else (0, 0)
            self.position_callback(dx, dy, dh, cx, cy)
