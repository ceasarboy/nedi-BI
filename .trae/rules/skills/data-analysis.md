# PB-BI 数据分析模块指南

## 一、功能模块概览

| 功能 | API端点 | 说明 |
|------|---------|------|
| 多表聚合 | `/api/analysis/aggregate` | UNION、JOIN等操作 |
| 字段筛选 | `/api/analysis/transform` | 选择特定字段 |
| 数据统计 | `/api/analysis/statistical` | 计数、求和、平均等 |
| 统计描述 | `/api/analysis/statistical` | 均值、标准差、偏度等 |
| 分布拟合 | `/api/analysis/distribution` | 正态、指数、伽马等分布 |
| 回归分析 | `/api/analysis/regression` | 线性、岭、Lasso回归 |
| 相关分析 | `/api/analysis/correlation` | 皮尔逊相关系数 |
| 蒙特卡洛 | `/api/analysis/montecarlo` | 随机模拟分析 |

---

## 二、多表聚合

### 1. 支持的聚合类型
| 类型 | 说明 | SQL等价 |
|------|------|---------|
| UNION ALL | 合并所有数据 | `SELECT * FROM t1 UNION ALL SELECT * FROM t2` |
| UNION | 合并并去重 | `SELECT * FROM t1 UNION SELECT * FROM t2` |
| JOIN | 内连接 | `SELECT * FROM t1 JOIN t2 ON t1.key = t2.key` |
| LEFT JOIN | 左连接 | `SELECT * FROM t1 LEFT JOIN t2 ON t1.key = t2.key` |
| RIGHT JOIN | 右连接 | `SELECT * FROM t1 RIGHT JOIN t2 ON t1.key = t2.key` |
| FULL JOIN | 全连接 | `SELECT * FROM t1 FULL JOIN t2 ON t1.key = t2.key` |

### 2. pandas实现
```python
def aggregate_snapshots(snapshots: list, agg_type: str):
    dfs = [pd.DataFrame(s['rows']) for s in snapshots]
    
    if agg_type == 'union_all':
        result = pd.concat(dfs, ignore_index=True)
    elif agg_type == 'union':
        result = pd.concat(dfs, ignore_index=True).drop_duplicates()
    elif agg_type == 'join':
        result = dfs[0]
        for df in dfs[1:]:
            common_cols = list(set(result.columns) & set(df.columns))
            result = pd.merge(result, df, on=common_cols, how='inner')
    # ... 其他类型
    
    return result.to_dict('records')
```

---

## 三、统计分析

### 1. 统计描述
```python
def statistical_analysis(data: pd.DataFrame, column: str):
    series = pd.to_numeric(data[column], errors='coerce').dropna()
    
    return {
        'count': len(series),
        'mean': float(series.mean()),
        'std': float(series.std()),
        'min': float(series.min()),
        '25%': float(series.quantile(0.25)),
        '50%': float(series.median()),
        '75%': float(series.quantile(0.75)),
        'max': float(series.max()),
        'skewness': float(series.skew()),
        'kurtosis': float(series.kurtosis()),
        'confidence_interval_95': [
            float(series.mean() - 1.96 * series.std() / len(series)**0.5),
            float(series.mean() + 1.96 * series.std() / len(series)**0.5)
        ]
    }
```

### 2. 正态性检验
```python
from scipy import stats

def normality_test(data: pd.Series):
    # Shapiro-Wilk检验
    shapiro_stat, shapiro_p = stats.shapiro(data)
    # Kolmogorov-Smirnov检验
    ks_stat, ks_p = stats.kstest(data, 'norm', args=(data.mean(), data.std()))
    # Jarque-Bera检验
    jb_stat, jb_p = stats.jarque_bera(data)
    
    return {
        'shapiro': {'statistic': shapiro_stat, 'p_value': shapiro_p},
        'ks': {'statistic': ks_stat, 'p_value': ks_p},
        'jarque_bera': {'statistic': jb_stat, 'p_value': jb_p}
    }
```

---

## 四、分布拟合

### 1. 支持的分布类型
| 分布 | 参数 | 适用场景 |
|------|------|----------|
| 正态分布 | μ, σ | 自然现象、测量误差 |
| 指数分布 | λ | 等待时间、寿命 |
| 伽马分布 | k, θ | 降雨量、服务时间 |
| 对数正态分布 | μ, σ | 收入分布、股票价格 |
| 泊松分布 | λ | 计数数据、到达事件 |

### 2. 拟合与评估
```python
from scipy import stats

def fit_distribution(data: pd.Series, dist_type: str):
    if dist_type == 'norm':
        params = stats.norm.fit(data)
        dist = stats.norm(*params)
    elif dist_type == 'expon':
        params = stats.expon.fit(data)
        dist = stats.expon(*params)
    # ... 其他分布
    
    # KS检验评估拟合优度
    ks_stat, ks_p = stats.kstest(data, dist.cdf)
    
    return {
        'distribution': dist_type,
        'parameters': params,
        'ks_statistic': ks_stat,
        'ks_p_value': ks_p,
        'is_good_fit': ks_p > 0.05
    }
```

---

## 五、回归分析

### 1. 支持的回归类型
| 类型 | 说明 | 适用场景 |
|------|------|----------|
| 线性回归 | y = ax + b | 线性关系 |
| 岭回归 | L2正则化 | 多重共线性 |
| Lasso回归 | L1正则化 | 特征选择 |
| 多项式回归 | y = a₀ + a₁x + a₂x² + ... | 非线性关系 |

### 2. 实现示例
```python
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score, mean_squared_error

def regression_analysis(X, y, reg_type: str, degree: int = 2):
    if reg_type == 'linear':
        model = LinearRegression()
    elif reg_type == 'ridge':
        model = Ridge(alpha=1.0)
    elif reg_type == 'lasso':
        model = Lasso(alpha=1.0)
    elif reg_type == 'polynomial':
        poly = PolynomialFeatures(degree=degree)
        X = poly.fit_transform(X)
        model = LinearRegression()
    
    model.fit(X, y)
    y_pred = model.predict(X)
    
    return {
        'coefficients': model.coef_.tolist(),
        'intercept': float(model.intercept_),
        'r2': float(r2_score(y, y_pred)),
        'mse': float(mean_squared_error(y, y_pred)),
        'formula': generate_formula(model, reg_type)
    }
```

---

## 六、相关性分析

### 1. 相关系数类型
| 类型 | 适用场景 | 取值范围 |
|------|----------|----------|
| 皮尔逊 | 线性关系 | [-1, 1] |
| 斯皮尔曼 | 单调关系 | [-1, 1] |
| 肯德尔 | 秩相关 | [-1, 1] |

### 2. 多数据流字段分析
```python
def multi_correlation_analysis(snapshots: list, fields: list, method: str = 'pearson'):
    # 合并所有字段数据
    data_dict = {}
    for snapshot in snapshots:
        df = pd.DataFrame(snapshot['rows'])
        for field in fields:
            if field in df.columns:
                key = f"{snapshot['name']}-{field}"
                data_dict[key] = pd.to_numeric(df[field], errors='coerce')
    
    # 创建合并DataFrame
    combined = pd.DataFrame(data_dict)
    
    # 计算相关系数矩阵
    corr_matrix = combined.corr(method=method)
    
    # 识别高相关对
    high_corr_pairs = []
    for i, col1 in enumerate(corr_matrix.columns):
        for col2 in corr_matrix.columns[i+1:]:
            r = corr_matrix.loc[col1, col2]
            if abs(r) >= 0.7:
                high_corr_pairs.append({
                    'field1': col1,
                    'field2': col2,
                    'correlation': float(r)
                })
    
    return {
        'correlation_matrix': corr_matrix.to_dict(),
        'high_correlation_pairs': sorted(high_corr_pairs, key=lambda x: abs(x['correlation']), reverse=True)
    }
```

---

## 七、蒙特卡洛分析

### 1. 经典案例

#### 计算圆周率π
```python
def monte_carlo_pi(n_points: int = 10000):
    # 在单位正方形内随机投点
    x = np.random.uniform(-1, 1, n_points)
    y = np.random.uniform(-1, 1, n_points)
    
    # 计算落在单位圆内的点数
    inside = (x**2 + y**2) <= 1
    pi_estimate = 4 * np.sum(inside) / n_points
    
    return {
        'pi_estimate': pi_estimate,
        'error': abs(pi_estimate - np.pi),
        'points_inside': np.sum(inside),
        'total_points': n_points
    }
```

#### 定积分计算
```python
def monte_carlo_integral(func: str, a: float, b: float, n_points: int = 10000):
    # 在[a,b]区间内随机采样
    x = np.random.uniform(a, b, n_points)
    
    # 安全执行函数
    y = eval(func, {"__builtins__": {}}, {"x": x, "np": np})
    
    # 估计积分值
    integral = (b - a) * np.mean(y)
    
    return {
        'integral_estimate': float(integral),
        'function': func,
        'interval': [a, b]
    }
```

#### 排队问题模拟
```python
def monte_carlo_queue(arrival_rate: float, service_rate: float, n_customers: int = 1000):
    # 生成到达时间间隔和服务时间
    arrival_times = np.random.exponential(1/arrival_rate, n_customers)
    service_times = np.random.exponential(1/service_rate, n_customers)
    
    # 模拟排队过程
    wait_times = []
    current_time = 0
    service_end_time = 0
    
    for i in range(n_customers):
        arrival_time = current_time + arrival_times[i]
        start_service = max(arrival_time, service_end_time)
        wait_time = start_service - arrival_time
        wait_times.append(wait_time)
        service_end_time = start_service + service_times[i]
        current_time = arrival_time
    
    return {
        'avg_wait_time': float(np.mean(wait_times)),
        'max_wait_time': float(np.max(wait_times)),
        'utilization': float(np.sum(service_times) / service_end_time)
    }
```

---

## 八、NaN值处理

### 重要：JSON序列化问题
```python
def clean_nan(obj):
    """递归清理NaN值，转换为None"""
    if isinstance(obj, float) and pd.isna(obj):
        return None
    elif isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan(item) for item in obj]
    return obj
```

---

## 九、相关文件

| 文件 | 说明 |
|------|------|
| `src/api/analysis.py` | 分析API路由 |
| `frontend/src/pages/AnalysisPage.jsx` | 数据分析页面 |
| `frontend/src/pages/CorrelationPage.jsx` | 相关性分析页面 |
| `frontend/src/pages/MonteCarloPage.jsx` | 蒙特卡洛分析页面 |
| `frontend/src/components/AdvancedStats.jsx` | 高级统计组件 |

---

## 十、经验教训

1. **NaN值处理**：pandas数据分析经常产生NaN值，JSON序列化前必须清理
2. **数值类型转换**：使用`pd.to_numeric(..., errors='coerce')`安全转换
3. **公式安全执行**：使用eval时限制`__builtins__`防止安全风险
4. **大数据量优化**：限制前端显示行数，提供分页或导出功能
5. **统计结果格式化**：使用`.4f`格式化确保小数位数一致
