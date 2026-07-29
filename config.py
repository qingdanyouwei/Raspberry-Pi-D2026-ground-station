"""
D题陆空协同 - 场地配置
场地: 400cm(X) × 500cm(Y)
H点: 左下角无人机起降点
A点: 小车出发点
"""
FIELD_W = 500  # Y方向, 屏幕X轴 (长边)
FIELD_H = 400  # X方向, 屏幕Y轴 (短边)

SCALE = 1.0     # 1像素/cm
OFFSET_X = 50   # 屏幕左边距
OFFSET_Y = 40   # 屏幕上边距

# H点: 左下角起降点
H_X = 50
H_Y = 50

# A点: 小车出发点
A_X = 50
A_Y = 100

# 场地坐标→屏幕像素
def field_to_screen(x_cm, y_cm):
    """x_cm: X方向(短边400cm), y_cm: Y方向(长边500cm)"""
    sx = OFFSET_X + int(y_cm * SCALE)
    sy = OFFSET_Y + int((FIELD_H - x_cm) * SCALE)
    return sx, sy

# 循线轨迹坐标 (顺时针闭合)
TRACK = [
    (80, 50), (350, 50), (350, 100), (420, 100),
    (420, 350), (120, 350), (120, 200), (50, 200),
    (50, 150), (80, 150),
]

def get_track_points():
    """返回循线轨迹的屏幕坐标列表"""
    points = []
    for x, y in TRACK:
        sx, sy = field_to_screen(x, y)
        points.append((sx, sy))
    return points
