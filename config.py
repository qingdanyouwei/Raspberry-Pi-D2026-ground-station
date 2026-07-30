"""
D题陆空协同 - 场地配置
原点=右下角, X轴向左(0~400cm), Y轴向上(0~500cm)
跑道: 两边直线+两端半圆(半径75cm)
"""
import math

FIELD_X = 400
FIELD_Y = 500

MAP_LEFT = 30
MAP_TOP = 20
MAP_W = 540
MAP_H = 432

def field_to_screen(x_cm, y_cm):
    sx = MAP_LEFT + MAP_W - int(x_cm * MAP_W / FIELD_X)
    sy = MAP_TOP + MAP_H - int(y_cm * MAP_H / FIELD_Y)
    return sx, sy

# 关键点 (X=距右边, Y=距下边)
H_X, H_Y = 300, 100
A_X, A_Y = 250, 200
B_X, B_Y = 250, 350
C_X, C_Y = 100, 350
D_X, D_Y = 100, 200

# 半圆圆心和半径
R = 75
TOP_CX, TOP_CY = 175, 350    # B-C弧圆心
BOT_CX, BOT_CY = 175, 200    # D-A弧圆心

def arc_points(cx, cy, r, start_deg, end_deg, n=12):
    """生成圆弧上的n个点"""
    pts = []
    for i in range(n + 1):
        rad = math.radians(start_deg + (end_deg - start_deg) * i / n)
        x = cx + r * math.cos(rad)
        y = cy + r * math.sin(rad)
        pts.append((x, y))
    return pts

def get_track_points():
    """A→B直线 → B→C上弧 → C→D直线 → D→A下弧 → A"""
    track = []
    # A→B直线
    track.append((A_X, A_Y))
    # B→C半圆 (0°→180°, 向上画弧)
    track.extend(arc_points(TOP_CX, TOP_CY, R, 0, 180))
    track.append((C_X, C_Y))
    # D→A半圆 (180°→360°, 向下画弧)
    track.extend(arc_points(BOT_CX, BOT_CY, R, 180, 360))
    track.append((A_X, A_Y))
    # 转屏幕坐标
    return [field_to_screen(x, y) for x, y in track]
