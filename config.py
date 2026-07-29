"""
D题陆空协同 - 场地配置
场地: X轴(短边)400cm × Y轴(长边)500cm
"""
FIELD_W = 500
FIELD_H = 400

# 地图在屏幕上的位置和缩放
MAP_LEFT = 30
MAP_TOP = 20
MAP_W = 540   # 500cm * 1.08
MAP_H = 432   # 400cm * 1.08

def field_to_screen(x_cm, y_cm):
    """场地坐标→屏幕像素"""
    sx = MAP_LEFT + int(y_cm * MAP_W / FIELD_W)
    sy = MAP_TOP + int((FIELD_H - x_cm) * MAP_H / FIELD_H)
    return sx, sy

# 关键点坐标
H_X, H_Y = 100, 100
A_X, A_Y = 200, 150
B_X, B_Y = 350, 150
D_X, D_Y = 200, 300
