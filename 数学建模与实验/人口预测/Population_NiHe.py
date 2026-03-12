import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 原始数据（单位：万人）
years = np.arange(2013, 2023)
population = np.array([136726, 137646, 138326, 139232, 140011,
                       140541, 141008, 141212, 141260, 141175])

# 划分训练集和测试集
train_year = years[:8]  # 2013-2020
train_pop = population[:8]
test_year = years[8:]  # 2021-2022
test_pop = population[8:]

# 时间变量处理（以2013年为基准年）
t_train = train_year - 2013
t_test = test_year - 2013
t_full = years - 2013


# ================== Malthus模型 ==================
def malthus_model(t, r, P0):
    return P0 * np.exp(r * t)


# 参数拟合
p0_malthus = [0.01, train_pop[0]]  # 初始猜测值
params_malthus, _ = curve_fit(malthus_model, t_train, train_pop, p0=p0_malthus)
r_fit, P0_fit = params_malthus

# 预测
malthus_pred = malthus_model(t_full, r_fit, P0_fit)


# ================== Logistic模型 ==================
def logistic_model(t, r, K, P0):
    return K / (1 + (K / P0 - 1) * np.exp(-r * t))


# 参数拟合
p0_logistic = [0.01, 150000, train_pop[0]]  # 初始猜测值
params_logistic, _ = curve_fit(logistic_model, t_train, train_pop,
                               p0=p0_logistic, maxfev=1000)
r_log, K_log, P0_log = params_logistic

# 预测
logistic_pred = logistic_model(t_full, r_log, K_log, P0_log)

# ================== SVR模型 ==================
# 特征工程：增加更多的特征
X_train = np.column_stack((t_train, t_train**2, t_train**3))  # 添加二次项和三次项特征
y_train = train_pop

# 标准化特征
scaler_X = StandardScaler()
scaler_y = StandardScaler()

X_train_scaled = scaler_X.fit_transform(X_train)
y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()

# 创建SVR模型并进行网格搜索调优
param_grid = {
    'C': [10, 100, 1000],
    'gamma': [0.01, 0.1, 1],
    'epsilon': [0.01, 0.1, 1]
}

svr_model = SVR(kernel='rbf')
grid_search = GridSearchCV(svr_model, param_grid, cv=3, scoring='neg_mean_squared_error')
grid_search.fit(X_train_scaled, y_train_scaled)

best_svr_model = grid_search.best_estimator_

# 预测
X_full = np.column_stack((t_full, t_full**2, t_full**3))
X_full_scaled = scaler_X.transform(X_full)
svr_pred_scaled = best_svr_model.predict(X_full_scaled)
svr_pred = scaler_y.inverse_transform(svr_pred_scaled.reshape(-1, 1)).flatten()


# ================== 结果分析 ==================
# 计算误差
def calculate_error(true, pred):
    return mean_absolute_percentage_error(true, pred) * 100


# 计算每个年份的误差
error_malthus_2021 = calculate_error(test_pop[:1], malthus_pred[8:9])
error_malthus_2022 = calculate_error(test_pop[1:], malthus_pred[9:10])

error_logistic_2021 = calculate_error(test_pop[:1], logistic_pred[8:9])
error_logistic_2022 = calculate_error(test_pop[1:], logistic_pred[9:10])

error_svr_2021 = calculate_error(test_pop[:1], svr_pred[8:9])
error_svr_2022 = calculate_error(test_pop[1:], svr_pred[9:10])

# 结果表格
results = pd.DataFrame({
    "模型": ["Malthus", "Logistic", "SVR"],
    "2021误差(%)": [error_malthus_2021, error_logistic_2021, error_svr_2021],
    "2022误差(%)": [error_malthus_2022, error_logistic_2022, error_svr_2022]
})

# ================== 可视化 ==================
plt.figure(figsize=(10, 6))
plt.plot(years, population, 'ko-', label='实际人口')
plt.plot(years, malthus_pred, 'r--', label='Malthus预测')
plt.plot(years, logistic_pred, 'g-.', label='Logistic预测')
plt.plot(years, svr_pred, 'c-', label='SVR预测')

plt.fill_between(test_year, test_pop*0.95, test_pop*1.05, color='gray', alpha=0.2, label='测试区间')
plt.xlabel('年份')
plt.ylabel('人口（万人）')
plt.title('人口预测模型对比')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()

# 显示结果
print("模型预测误差对比：")
print(results)
plt.savefig('population_prediction.pdf')  # 保存图表以便在LaTeX文档中引用
plt.show()



