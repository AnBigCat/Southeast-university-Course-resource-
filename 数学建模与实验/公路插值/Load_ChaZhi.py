import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
from scipy import integrate

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class RoadModeling:
    def __init__(self, X, Y):
        """初始化道路建模类"""
        self.raw_X = np.array(X)
        self.raw_Y = np.array(Y)
        self.validate_data()
        self.process_data()

    def validate_data(self):
        """数据验证"""
        assert len(self.raw_X) == len(self.raw_Y), "X和Y数据长度不一致"
        if len(self.raw_X) < 4:
            raise ValueError("至少需要4个测量点进行样条插值")

    def process_data(self):
        """数据预处理"""
        # 直接使用原始数据，不移除重复点
        self.X = self.raw_X
        self.Y = self.raw_Y

        # 计算累积弦长参数
        dx = np.diff(self.X)
        dy = np.diff(self.Y)
        self.distances = np.sqrt(dx ** 2 + dy ** 2)
        self.t = np.concatenate(([0], np.cumsum(self.distances)))

    def build_splines(self):
        """构建三次样条模型"""
        self.cs_X = CubicSpline(self.t, self.X, bc_type='natural')
        self.cs_Y = CubicSpline(self.t, self.Y, bc_type='natural')

    def calculate_length(self):
        """计算公路长度"""

        def integrand(t):
            dx = self.cs_X(t, 1)  # X 关于 t 的一阶导数
            dy = self.cs_Y(t, 1)  # Y 关于 t 的一阶导数
            return np.sqrt(dx ** 2 + dy ** 2)

        total_length_segments = 0
        segment_lengths = []

        for i in range(len(self.t) - 1):
            length_segment, _ = integrate.quad(integrand, self.t[i], self.t[i+1])
            total_length_segments += length_segment
            segment_lengths.append(length_segment)

        print(f"总长度 (分段累加): {total_length_segments:.1f} 米")
        print(f"各段长度: {segment_lengths}")

        self.total_length, self.error = integrate.quad(
            integrand, self.t[0], self.t[-1], limit=1000
        )

    def calculate_curvature(self, t):
        """计算曲率"""
        dx = self.cs_X(t, 1)
        ddx = self.cs_X(t, 2)
        dy = self.cs_Y(t, 1)
        ddy = self.cs_Y(t, 2)

        numerator = np.abs(dx * ddy - dy * ddx)
        denominator = (dx ** 2 + dy ** 2) ** 1.5
        return np.divide(numerator, denominator,
                         out=np.zeros_like(numerator),
                         where=denominator != 0)

    def visualize(self):
        """可视化结果"""
        # 生成插值点
        t_interp = np.linspace(self.t.min(), self.t.max(), 1000)
        X_interp = self.cs_X(t_interp)
        Y_interp = self.cs_Y(t_interp)

        # 创建画布
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # 路径图
        ax1.plot(X_interp, Y_interp, 'r-', lw=1.5, label='插值路径')
        ax1.plot(self.X, self.Y, 'ko', ms=6, mfc='yellow', label='原始测点')
        ax1.quiver(self.X[:-1], self.Y[:-1],
                   np.diff(self.X), np.diff(self.Y),
                   angles='xy', scale_units='xy', scale=1,
                   color='blue', width=0.003, label='路段方向')

        ax1.set_xlabel('X坐标（米）')
        ax1.set_ylabel('Y坐标（米）')
        ax1.set_title(f'公路路径重建（总长度：{self.total_length:.1f}米）')
        ax1.axis('equal')
        ax1.grid(True, ls='--', alpha=0.5)
        ax1.legend()

        # 曲率图
        curvature = self.calculate_curvature(t_interp)
        ax2.plot(t_interp, curvature, 'b-', lw=1.2)
        ax2.set_xlabel('累积弦长参数 t（米）')
        ax2.set_ylabel('曲率 (1/米)')
        ax2.set_title('路径曲率分布')
        ax2.grid(True, ls='--', alpha=0.5)

        plt.tight_layout()

    def validate_model(self):
        """模型验证"""
        # 终点闭合误差
        end_X = self.cs_X(self.t[-1])
        end_Y = self.cs_Y(self.t[-1])
        closure_error = np.sqrt((end_X - self.X[-1]) ** 2 +
                                (end_Y - self.Y[-1]) ** 2)

        # 打印验证结果
        print("=" * 40)
        print(f"{'模型验证结果':^40}")
        print("=" * 40)
        print(f"原始测点数: {len(self.X)}个")
        print(f"有效测点数: {len(self.X)}个")
        print(f"参数t范围: [{self.t[0]:.1f}, {self.t[-1]:.1f}]米")
        print(f"公路总长度: {self.total_length:.1f} ± {self.error:.1f}米")
        print(f"相对误差: {self.error / self.total_length * 100:.2f}%")
        print(f"终点闭合误差: {closure_error:.3e}米")
        print("=" * 40)


# 原始数据
X = [0, 30, 50, 70, 80, 90, 120, 148, 170, 180, 202, 212, 230, 248, 268, 271,
     280, 290, 300, 312, 320, 340, 360, 372, 382, 390, 416, 430, 478, 440,
     420, 380, 360, 340, 320, 314, 280, 240, 200]

Y = [80, 64, 47, 42, 48, 66, 80, 120, 121, 138, 160, 182, 200, 208, 212, 210,
     200, 196, 188, 186, 200, 184, 188, 200, 202, 240, 246, 280, 296, 308,
     334, 328, 334, 346, 356, 360, 392, 390, 400]

# 执行建模流程
try:
    model = RoadModeling(X, Y)
    model.build_splines()
    model.calculate_length()
    model.visualize()
    model.validate_model()
    plt.show()

except Exception as e:
    print(f"建模过程中发生错误: {str(e)}")



