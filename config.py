"""
D题陆空协同 - 场地配置
场地: X轴(短边)400cm × Y轴(长边)500cm
原点: 左下角
"""
FIELD_W = 500  # Y方向(长边)
FIELD_H = 400  # X方向(短边)

SCALE = 1.0
OFFSET_X = 50
OFFSET_Y = 40

H_X, H_Y = 100, 100       # 无人机起降点 (距左下角各100cm)
A_X, A_Y = 200, 150        # 小车出发点 (X距下边200, Y距左边150)
B_X, B_Y = 350, 150        # B点 (X距下边350, Y距左边150)
C_X, C_Y = 350, 300        # C点 (推断右上角)
D_X, D_Y = 200, 300        # D点 (X距下边200, Y距左边300)

# 循线轨迹 A→B→C→D→A (顺时针)
TRACK = [
    (A_X, A_Y), (B_X, B_Y), (C_X, C_Y), (D_X, D_Y), (A_X, A_Y),
]

def field_to_screen(x_cm, y_cm):
    """x:X方向(短边), y:Y方向(长边) → 屏幕像素"""
    sx = OFFSET_X + int(y_cm * SCALE)
    sy = OFFSET_Y + int((FIELD_H - x_cm) * SCALE)
    return sx, sy

def get_track_points():
    return [field_to_screen(x, y) for x, y in TRACK]
