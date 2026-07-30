"""
D题陆空协同 - 场地配置
原点=右下角, X轴向左(0~400cm), Y轴向上(0~500cm)
"""
FIELD_X = 400  # X轴(短边, 距右边)
FIELD_Y = 500  # Y轴(长边, 距下边)

MAP_LEFT = 30
MAP_TOP = 20
MAP_W = 540
MAP_H = 432

def field_to_screen(x_cm, y_cm):
    """x:距右边(cm) y:距下边(cm) → 屏幕像素"""
    sx = MAP_LEFT + MAP_W - int(x_cm * MAP_W / FIELD_X)
    sy = MAP_TOP + MAP_H - int(y_cm * MAP_H / FIELD_Y)
    return sx, sy

# 关键点 (X=距右边, Y=距下边)
H_X, H_Y = 300, 100   # 无人机起降点
A_X, A_Y = 350, 200   # 小车出发点
B_X, B_Y = 250, 350   # B点
C_X, C_Y = 100, 350   # C点
D_X, D_Y = 100, 200   # D点

# 循线轨迹 A→B→C→D→A
TRACK = [
    (A_X, A_Y), (B_X, B_Y), (C_X, C_Y), (D_X, D_Y), (A_X, A_Y),
]
