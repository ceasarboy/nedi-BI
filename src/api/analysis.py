from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import chisquare
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score, mean_squared_error
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import jarque_bera

from src.core.database import get_db
from src.models.config import DataSnapshot

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

def generate_chart_data(series, fit_params_dict):
    """生成分布拟合图表数据"""
    chart_data = {}
    
    # 1. 生成直方图数据
    hist, bin_edges = np.histogram(series, bins='auto', density=False)
    chart_data["histogram"] = {
        "bin_edges": bin_edges.tolist(),
        "counts": hist.tolist()
    }
    
    # 2. 生成拟合曲线数据 - 与直方图在同一个区间
    chart_data["fitted_curves"] = []
    
    x_min = bin_edges[0]
    x_max = bin_edges[-1]
    x = np.linspace(x_min, x_max, 200)
    
    # 计算直方图的尺度
    hist_sum = np.sum(hist)
    bin_widths = np.diff(bin_edges)
    hist_scale = hist_sum * bin_widths[0] if len(bin_widths) > 0 else 1
    
    for dist_name, info in fit_params_dict.items():
        try:
            params = info["params"]
            name = info["name"]
            
            if dist_name == "norm":
                pdf = stats.norm.pdf(x, *params)
            elif dist_name == "expon":
                pdf = stats.expon.pdf(x, *params)
            elif dist_name == "gamma":
                pdf = stats.gamma.pdf(x, *params)
            elif dist_name == "lognorm":
                pdf = stats.lognorm.pdf(x, *params)
            elif dist_name == "poisson":
                # 泊松分布是离散的，需要特殊处理
                continue
            else:
                continue
            
            # 将密度转换为与直方图匹配的尺度
            scaled_pdf = pdf * hist_scale
            
            chart_data["fitted_curves"].append({
                "distribution": name,
                "x": x.tolist(),
                "y": scaled_pdf.tolist()
            })
        except Exception:
            continue
    
    return chart_data

class AggregateRequest(BaseModel):
    snapshot_ids: List[int]
    aggregate_type: str
    join_fields: Optional[dict] = None

class TransformRequest(BaseModel):
    snapshot_id: int
    transform_rules: dict

class CustomCalcRequest(BaseModel):
    snapshot_id: int
    code: str

class StatisticalRequest(BaseModel):
    snapshot_id: int
    field: str

class DistributionRequest(BaseModel):
    snapshot_id: int
    field: str
    distributions: List[str] = ["norm", "expon", "gamma", "lognorm"]
    remove_empty: bool = True

class RegressionRequest(BaseModel):
    snapshot_id: int
    dependent_var: str
    independent_vars: List[str]
    regression_type: str = "linear"  # linear, ridge, lasso, polynomial
    polynomial_degree: int = 2

class CorrelationRequest(BaseModel):
    snapshot_id: int
    fields: List[str]

class MonteCarloVariable(BaseModel):
    name: str
    distribution: str  # norm, uniform, expon, gamma
    params: List[float]

class MonteCarloRequest(BaseModel):
    snapshot_id: int
    variables: List[MonteCarloVariable]
    formula: str
    simulation_count: int = 10000

class CorrelationFieldRequest(BaseModel):
    snapshot_id: int
    field_name: str

class MultiCorrelationRequest(BaseModel):
    fields: List[CorrelationFieldRequest]
    correlation_method: str = "pearson"  # pearson, spearman, kendall
    correlation_threshold: float = 0.7

class CorrelationExploreRequest(BaseModel):
    fields: List[CorrelationFieldRequest]
    correlation_method: str = "pearson"  # pearson, spearman, kendall
    correlation_threshold: float = 0.8

class MonteCarloPiRequest(BaseModel):
    simulation_count: int = 10000

class MonteCarloIntegralRequest(BaseModel):
    x_min: float = 0.0
    x_max: float = 1.0
    function: str = "x**2"
    simulation_count: int = 10000

class MonteCarloQueueRequest(BaseModel):
    num_people: int = 20
    arrival_min: float = 0.0
    arrival_max: float = 10.0
    service_min: float = 1.0
    service_max: float = 3.0
    simulation_count: int = 1000

@router.post("/aggregate")
async def aggregate_data(request: AggregateRequest, db: Session = Depends(get_db)):
    try:
        snapshots = db.query(DataSnapshot).filter(
            DataSnapshot.id.in_(request.snapshot_ids)
        ).all()
        
        if len(snapshots) < 2:
            raise HTTPException(status_code=400, detail="至少需要选择2个数据快照")
        
        dfs = []
        all_fields = []
        
        for snapshot in snapshots:
            try:
                data = json.loads(snapshot.data)
                fields = json.loads(snapshot.fields)
                
                df = pd.DataFrame(data)
                dfs.append(df)
                
                for field in fields:
                    if not any(f["field_id"] == field["field_id"] for f in all_fields):
                        all_fields.append(field)
            except json.JSONDecodeError:
                continue
        
        aggregate_type = request.aggregate_type
        result_df = None
        
        if aggregate_type in ["union_all", "union"]:
            result_df = pd.concat(dfs, ignore_index=True)
            if aggregate_type == "union":
                result_df = result_df.drop_duplicates()
        elif aggregate_type == "join":
            if len(dfs) >= 2:
                result_df = dfs[0]
                for i in range(1, len(dfs)):
                    common_cols = list(set(result_df.columns) & set(dfs[i].columns))
                    if common_cols:
                        result_df = pd.merge(result_df, dfs[i], on=common_cols, how="inner")
                    else:
                        raise HTTPException(status_code=400, detail=f"快照 {snapshots[i].name} 没有共同的列用于 JOIN")
        elif aggregate_type == "left_join":
            if len(dfs) >= 2:
                result_df = dfs[0]
                for i in range(1, len(dfs)):
                    common_cols = list(set(result_df.columns) & set(dfs[i].columns))
                    if common_cols:
                        result_df = pd.merge(result_df, dfs[i], on=common_cols, how="left")
                    else:
                        raise HTTPException(status_code=400, detail=f"快照 {snapshots[i].name} 没有共同的列用于 LEFT JOIN")
        elif aggregate_type == "right_join":
            if len(dfs) >= 2:
                result_df = dfs[0]
                for i in range(1, len(dfs)):
                    common_cols = list(set(result_df.columns) & set(dfs[i].columns))
                    if common_cols:
                        result_df = pd.merge(result_df, dfs[i], on=common_cols, how="right")
                    else:
                        raise HTTPException(status_code=400, detail=f"快照 {snapshots[i].name} 没有共同的列用于 RIGHT JOIN")
        elif aggregate_type == "full_join":
            if len(dfs) >= 2:
                result_df = dfs[0]
                for i in range(1, len(dfs)):
                    common_cols = list(set(result_df.columns) & set(dfs[i].columns))
                    if common_cols:
                        result_df = pd.merge(result_df, dfs[i], on=common_cols, how="outer")
                    else:
                        result_df = pd.merge(result_df, dfs[i], left_index=True, right_index=True, how="outer")
        
        if result_df is None:
            raise HTTPException(status_code=400, detail="不支持的聚合类型")
        
        def clean_nan(obj):
            if isinstance(obj, float) and pd.isna(obj):
                return None
            elif isinstance(obj, dict):
                return {k: clean_nan(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_nan(item) for item in obj]
            return obj
        
        result_rows = result_df.to_dict('records')
        result_rows = [clean_nan(row) for row in result_rows]
        
        result_fields = []
        for col in result_df.columns:
            field_info = next((f for f in all_fields if f["field_id"] == str(col)), None)
            result_fields.append({
                "field_id": str(col),
                "field_name": str(col),
                "data_type": field_info["data_type"] if field_info else "string",
                "is_enabled": "true"
            })
        
        result = {
            "success": True,
            "message": f"聚合成功，使用方式: {aggregate_type}",
            "aggregate_type": aggregate_type,
            "snapshots_used": [
                {"id": s.id, "name": s.name} for s in snapshots
            ],
            "fields": result_fields,
            "rows": result_rows
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"聚合失败: {str(e)}")

@router.post("/transform")
async def transform_data(request: TransformRequest, db: Session = Depends(get_db)):
    try:
        snapshot = db.query(DataSnapshot).filter(
            DataSnapshot.id == request.snapshot_id
        ).first()
        
        if not snapshot:
            raise HTTPException(status_code=404, detail="快照不存在")
        
        return {
            "success": True,
            "message": "数据转换功能开发中",
            "snapshot_id": request.snapshot_id,
            "transform_rules": request.transform_rules
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")

@router.post("/custom")
async def custom_calculation(request: CustomCalcRequest, db: Session = Depends(get_db)):
    try:
        snapshot = db.query(DataSnapshot).filter(
            DataSnapshot.id == request.snapshot_id
        ).first()
        
        if not snapshot:
            raise HTTPException(status_code=404, detail="快照不存在")
        
        return {
            "success": True,
            "message": "自定义计算功能开发中",
            "snapshot_id": request.snapshot_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算失败: {str(e)}")

@router.post("/statistical")
async def statistical_analysis(request: StatisticalRequest, db: Session = Depends(get_db)):
    """统计描述分析"""
    try:
        snapshot = db.query(DataSnapshot).filter(
            DataSnapshot.id == request.snapshot_id
        ).first()
        
        if not snapshot:
            raise HTTPException(status_code=404, detail="快照不存在")
        
        data = json.loads(snapshot.data)
        df = pd.DataFrame(data)
        
        if request.field not in df.columns:
            raise HTTPException(status_code=400, detail=f"字段 '{request.field}' 不存在")
        
        # 转换为数值类型
        series = pd.to_numeric(df[request.field], errors='coerce').dropna()
        
        if len(series) == 0:
            raise HTTPException(status_code=400, detail="没有有效的数值数据")
        
        # 确保 series 是 numpy 数组，并过滤掉 NaN 和 Inf
        series = np.array(series)
        series = series[np.isfinite(series)]
        
        if len(series) < 3:
            raise HTTPException(status_code=400, detail="有效数值数据不足（至少需要3个）")
        
        # 基础统计量
        n = len(series)
        mean = float(series.mean())
        median = float(series.median())
        std = float(series.std())
        var = float(series.var())
        min_val = float(series.min())
        max_val = float(series.max())
        range_val = max_val - min_val
        
        # 分位数
        q1 = float(series.quantile(0.25))
        q3 = float(series.quantile(0.75))
        iqr = q3 - q1
        
        # 偏度和峰度
        skewness = float(series.skew())
        kurtosis = float(series.kurtosis())
        
        # 变异系数
        cv = std / mean if mean != 0 else None
        
        # 置信区间 (95%)
        confidence_level = 0.95
        alpha = 1 - confidence_level
        se = std / np.sqrt(n)
        t_value = stats.t.ppf(1 - alpha/2, n-1)
        ci_lower = mean - t_value * se
        ci_upper = mean + t_value * se
        
        # 正态性检验
        try:
            if n <= 5000:
                shapiro_result = stats.shapiro(series)
                shapiro_stat, shapiro_p = float(shapiro_result.statistic), float(shapiro_result.pvalue)
            else:
                shapiro_stat, shapiro_p = None, None
        except Exception:
            shapiro_stat, shapiro_p = None, None
        
        try:
            ks_result = stats.kstest(series, 'norm', args=(mean, std))
            ks_stat, ks_p = float(ks_result.statistic), float(ks_result.pvalue)
        except Exception:
            ks_stat, ks_p = None, None
        
        try:
            jb_result = jarque_bera(series)
            jarque_stat = float(jb_result.statistic)
            jarque_p = float(jb_result.pvalue)
        except Exception:
            jarque_stat, jarque_p = None, None
        
        result = {
            "success": True,
            "field": request.field,
            "sample_size": n,
            "basic_stats": {
                "mean": round(mean, 4),
                "median": round(median, 4),
                "std": round(std, 4),
                "variance": round(var, 4),
                "min": round(min_val, 4),
                "max": round(max_val, 4),
                "range": round(range_val, 4)
            },
            "quantiles": {
                "q1": round(q1, 4),
                "q3": round(q3, 4),
                "iqr": round(iqr, 4)
            },
            "shape_stats": {
                "skewness": round(skewness, 4),
                "kurtosis": round(kurtosis, 4),
                "cv": round(cv, 4) if cv else None
            },
            "confidence_interval": {
                "level": confidence_level,
                "lower": round(ci_lower, 4),
                "upper": round(ci_upper, 4)
            },
            "normality_tests": {
                "shapiro_wilk": {
                    "statistic": round(float(shapiro_stat), 4) if shapiro_stat is not None else None,
                    "p_value": round(float(shapiro_p), 4) if shapiro_p is not None else None,
                    "is_normal": bool(shapiro_p > 0.05) if shapiro_p is not None else None
                },
                "kolmogorov_smirnov": {
                    "statistic": round(float(ks_stat), 4) if ks_stat is not None else None,
                    "p_value": round(float(ks_p), 4) if ks_p is not None else None,
                    "is_normal": bool(ks_p > 0.05) if ks_p is not None else None
                },
                "jarque_bera": {
                    "statistic": round(float(jarque_stat), 4) if jarque_stat is not None else None,
                    "p_value": round(float(jarque_p), 4) if jarque_p is not None else None,
                    "is_normal": bool(jarque_p > 0.05) if jarque_p is not None else None
                }
            }
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"统计分析失败: {str(e)}")

@router.post("/distribution")
async def distribution_fit(request: DistributionRequest, db: Session = Depends(get_db)):
    """分布拟合分析"""
    try:
        snapshot = db.query(DataSnapshot).filter(
            DataSnapshot.id == request.snapshot_id
        ).first()
        
        if not snapshot:
            raise HTTPException(status_code=404, detail="快照不存在")
        
        data = json.loads(snapshot.data)
        df = pd.DataFrame(data)
        
        if request.field not in df.columns:
            raise HTTPException(status_code=400, detail=f"字段 '{request.field}' 不存在")
        
        series = pd.to_numeric(df[request.field], errors='coerce')
        
        if request.remove_empty:
            series = series.dropna()
        
        if len(series) == 0:
            raise HTTPException(status_code=400, detail="没有有效的数值数据")
        
        # 确保 series 是 numpy 数组，并过滤掉 NaN 和 Inf
        series = np.array(series)
        series = series[np.isfinite(series)]
        
        if len(series) < 3:
            raise HTTPException(status_code=400, detail="有效数值数据不足（至少需要3个）")
        
        print(f"分布拟合分析 - 字段: {request.field}, 样本数: {len(series)}, 分布类型: {request.distributions}")
        
        # 分布拟合结果
        fit_results = []
        fit_params_dict = {}
        
        for dist_name in request.distributions:
            try:
                if dist_name == "norm":
                    # 正态分布
                    params = stats.norm.fit(series)
                    ks_result = stats.kstest(series, 'norm', args=params)
                    ks_stat, ks_p = float(ks_result.statistic), float(ks_result.pvalue)
                    
                    fit_result = {
                        "distribution": "正态分布 (Normal)",
                        "parameters": {
                            "mean": round(float(params[0]), 4),
                            "std": round(float(params[1]), 4)
                        },
                        "ks_test": {
                            "statistic": round(ks_stat, 4),
                            "p_value": round(ks_p, 4),
                            "fit_good": bool(ks_p > 0.05)
                        }
                    }
                    fit_results.append(fit_result)
                    fit_params_dict["norm"] = {"params": params, "name": "正态分布 (Normal)"}
                    
                elif dist_name == "expon":
                    # 指数分布
                    params = stats.expon.fit(series)
                    ks_result = stats.kstest(series, 'expon', args=params)
                    ks_stat, ks_p = float(ks_result.statistic), float(ks_result.pvalue)
                    
                    fit_result = {
                        "distribution": "指数分布 (Exponential)",
                        "parameters": {
                            "loc": round(float(params[0]), 4),
                            "scale": round(float(params[1]), 4)
                        },
                        "ks_test": {
                            "statistic": round(ks_stat, 4),
                            "p_value": round(ks_p, 4),
                            "fit_good": bool(ks_p > 0.05)
                        }
                    }
                    fit_results.append(fit_result)
                    fit_params_dict["expon"] = {"params": params, "name": "指数分布 (Exponential)"}
                    
                elif dist_name == "gamma":
                    # 伽马分布
                    params = stats.gamma.fit(series)
                    ks_result = stats.kstest(series, 'gamma', args=params)
                    ks_stat, ks_p = float(ks_result.statistic), float(ks_result.pvalue)
                    
                    fit_result = {
                        "distribution": "伽马分布 (Gamma)",
                        "parameters": {
                            "shape": round(float(params[0]), 4),
                            "loc": round(float(params[1]), 4),
                            "scale": round(float(params[2]), 4)
                        },
                        "ks_test": {
                            "statistic": round(ks_stat, 4),
                            "p_value": round(ks_p, 4),
                            "fit_good": bool(ks_p > 0.05)
                        }
                    }
                    fit_results.append(fit_result)
                    fit_params_dict["gamma"] = {"params": params, "name": "伽马分布 (Gamma)"}
                    
                elif dist_name == "lognorm":
                    # 对数正态分布
                    params = stats.lognorm.fit(series)
                    ks_result = stats.kstest(series, 'lognorm', args=params)
                    ks_stat, ks_p = float(ks_result.statistic), float(ks_result.pvalue)
                    
                    fit_result = {
                        "distribution": "对数正态分布 (Log-Normal)",
                        "parameters": {
                            "shape": round(float(params[0]), 4),
                            "loc": round(float(params[1]), 4),
                            "scale": round(float(params[2]), 4)
                        },
                        "ks_test": {
                            "statistic": round(ks_stat, 4),
                            "p_value": round(ks_p, 4),
                            "fit_good": bool(ks_p > 0.05)
                        }
                    }
                    fit_results.append(fit_result)
                    fit_params_dict["lognorm"] = {"params": params, "name": "对数正态分布 (Log-Normal)"}
                    
                elif dist_name == "poisson":
                    # 泊松分布 - 只适用于整数数据
                    try:
                        # 检查数据是否为整数
                        int_check = np.all(series == series.astype(int))
                        if not int_check:
                            fit_results.append({
                                "distribution": "泊松分布 (Poisson)",
                                "error": "泊松分布只适用于整数数据"
                            })
                        else:
                            mu = float(series.mean())
                            # 对于泊松分布，使用卡方检验更合适
                            observed = series.value_counts().sort_index()
                            expected = stats.poisson.pmf(observed.index, mu) * len(series)
                            chi2_result = chisquare(observed, expected)
                            chi2_stat, chi2_p = float(chi2_result.statistic), float(chi2_result.pvalue)
                            
                            fit_result = {
                                "distribution": "泊松分布 (Poisson)",
                                "parameters": {
                                    "mu": round(mu, 4)
                                },
                                "ks_test": {
                                    "statistic": round(chi2_stat, 4),
                                    "p_value": round(chi2_p, 4),
                                    "fit_good": bool(chi2_p > 0.05)
                                }
                            }
                            fit_results.append(fit_result)
                            fit_params_dict["poisson"] = {"params": (mu,), "name": "泊松分布 (Poisson)"}
                    except Exception as e:
                        fit_results.append({
                            "distribution": "泊松分布 (Poisson)",
                            "error": str(e)
                        })
                    
            except Exception as e:
                fit_results.append({
                    "distribution": dist_name,
                    "error": str(e)
                })
        
        # 按拟合优度排序
        fit_results = sorted(
            [r for r in fit_results if "ks_test" in r],
            key=lambda x: x["ks_test"]["p_value"],
            reverse=True
        )
        
        # 生成图表数据
        chart_data = generate_chart_data(series, fit_params_dict)
        
        result = {
            "success": True,
            "field": request.field,
            "sample_size": len(series),
            "best_fit": fit_results[0] if fit_results else None,
            "all_fits": fit_results,
            "chart_data": chart_data
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分布拟合分析失败: {str(e)}")

@router.post("/regression")
async def regression_analysis(request: RegressionRequest, db: Session = Depends(get_db)):
    """回归分析"""
    try:
        snapshot = db.query(DataSnapshot).filter(
            DataSnapshot.id == request.snapshot_id
        ).first()
        
        if not snapshot:
            raise HTTPException(status_code=404, detail="快照不存在")
        
        data = json.loads(snapshot.data)
        df = pd.DataFrame(data)
        
        # 检查字段是否存在
        if request.dependent_var not in df.columns:
            raise HTTPException(status_code=400, detail=f"因变量 '{request.dependent_var}' 不存在")
        
        for var in request.independent_vars:
            if var not in df.columns:
                raise HTTPException(status_code=400, detail=f"自变量 '{var}' 不存在")
        
        # 准备数据
        y = pd.to_numeric(df[request.dependent_var], errors='coerce')
        X = df[request.independent_vars].apply(pd.to_numeric, errors='coerce')
        
        # 删除缺失值
        valid_idx = y.notna() & X.notna().all(axis=1)
        y = y[valid_idx]
        X = X[valid_idx]
        
        if len(y) < 10:
            raise HTTPException(status_code=400, detail="有效样本数量太少（至少需要10个）")
        
        n = len(y)
        p = len(request.independent_vars)
        
        # 根据回归类型选择模型
        if request.regression_type == "linear":
            model = LinearRegression()
            model.fit(X, y)
            y_pred = model.predict(X)
            
            # 使用statsmodels获取详细统计信息
            X_with_const = sm.add_constant(X)
            sm_model = sm.OLS(y, X_with_const).fit()
            
            # 提取结果
            coefficients = {}
            for i, var in enumerate(request.independent_vars):
                coefficients[var] = {
                    "coefficient": round(sm_model.params[var], 4),
                    "std_error": round(sm_model.bse[var], 4),
                    "t_value": round(sm_model.tvalues[var], 4),
                    "p_value": round(sm_model.pvalues[var], 4),
                    "significant": bool(sm_model.pvalues[var] < 0.05)
                }
            
            # 生成拟合公式
            intercept = round(sm_model.params['const'], 4)
            formula_parts = [f"{request.dependent_var} = {intercept:.4f}"]
            for var in request.independent_vars:
                coef = round(sm_model.params[var], 4)
                if coef >= 0:
                    formula_parts.append(f"+ {coef:.4f} * {var}")
                else:
                    formula_parts.append(f"- {abs(coef):.4f} * {var}")
            formula = " ".join(formula_parts)
            
            # 生成图表数据
            chart_data = {
                "actual": list(zip(X.iloc[:, 0].tolist(), y.tolist())),
                "predicted": list(zip(X.iloc[:, 0].tolist(), y_pred.tolist()))
            }
            
            # 模型评估指标
            r2 = r2_score(y, y_pred)
            adj_r2 = 1 - (1 - r2) * (n - 1) / (n - p - 1)
            mse = mean_squared_error(y, y_pred)
            
            result = {
                "success": True,
                "regression_type": "线性回归 (Linear Regression)",
                "dependent_var": request.dependent_var,
                "independent_vars": request.independent_vars,
                "sample_size": n,
                "formula": formula,
                "coefficients": coefficients,
                "intercept": intercept,
                "chart_data": chart_data,
                "model_stats": {
                    "r_squared": round(r2, 4),
                    "adjusted_r_squared": round(adj_r2, 4),
                    "mse": round(mse, 4),
                    "f_statistic": round(sm_model.fvalue, 4),
                    "f_pvalue": round(sm_model.f_pvalue, 4),
                    "aic": round(sm_model.aic, 4),
                    "bic": round(sm_model.bic, 4)
                },
                "residual_stats": {
                    "durbin_watson": round(sm.stats.stattools.durbin_watson(sm_model.resid), 4),
                    "jarque_bera": round(jarque_bera(sm_model.resid)[0], 4),
                    "jarque_bera_pvalue": round(jarque_bera(sm_model.resid)[1], 4)
                }
            }
            
        elif request.regression_type == "ridge":
            model = Ridge(alpha=1.0)
            model.fit(X, y)
            y_pred = model.predict(X)
            r2 = r2_score(y, y_pred)
            mse = mean_squared_error(y, y_pred)
            
            # 生成拟合公式
            intercept = round(model.intercept_, 4)
            formula_parts = [f"{request.dependent_var} = {intercept:.4f}"]
            for var, coef in zip(request.independent_vars, model.coef_):
                coef_rounded = round(coef, 4)
                if coef_rounded >= 0:
                    formula_parts.append(f"+ {coef_rounded:.4f} * {var}")
                else:
                    formula_parts.append(f"- {abs(coef_rounded):.4f} * {var}")
            formula = " ".join(formula_parts)
            
            # 生成图表数据
            chart_data = {
                "actual": list(zip(X.iloc[:, 0].tolist(), y.tolist())),
                "predicted": list(zip(X.iloc[:, 0].tolist(), y_pred.tolist()))
            }
            
            result = {
                "success": True,
                "regression_type": "岭回归 (Ridge Regression)",
                "dependent_var": request.dependent_var,
                "independent_vars": request.independent_vars,
                "sample_size": n,
                "formula": formula,
                "coefficients": {
                    var: round(coef, 4) 
                    for var, coef in zip(request.independent_vars, model.coef_)
                },
                "intercept": intercept,
                "chart_data": chart_data,
                "model_stats": {
                    "r_squared": round(r2, 4),
                    "mse": round(mse, 4),
                    "alpha": 1.0
                }
            }
            
        elif request.regression_type == "lasso":
            model = Lasso(alpha=0.1)
            model.fit(X, y)
            y_pred = model.predict(X)
            r2 = r2_score(y, y_pred)
            mse = mean_squared_error(y, y_pred)
            
            # 生成拟合公式
            intercept = round(model.intercept_, 4)
            formula_parts = [f"{request.dependent_var} = {intercept:.4f}"]
            for var, coef in zip(request.independent_vars, model.coef_):
                coef_rounded = round(coef, 4)
                if coef_rounded >= 0:
                    formula_parts.append(f"+ {coef_rounded:.4f} * {var}")
                else:
                    formula_parts.append(f"- {abs(coef_rounded):.4f} * {var}")
            formula = " ".join(formula_parts)
            
            # 生成图表数据
            chart_data = {
                "actual": list(zip(X.iloc[:, 0].tolist(), y.tolist())),
                "predicted": list(zip(X.iloc[:, 0].tolist(), y_pred.tolist()))
            }
            
            result = {
                "success": True,
                "regression_type": "Lasso回归 (Lasso Regression)",
                "dependent_var": request.dependent_var,
                "independent_vars": request.independent_vars,
                "sample_size": n,
                "formula": formula,
                "coefficients": {
                    var: round(coef, 4) 
                    for var, coef in zip(request.independent_vars, model.coef_)
                },
                "intercept": intercept,
                "chart_data": chart_data,
                "model_stats": {
                    "r_squared": round(r2, 4),
                    "mse": round(mse, 4),
                    "alpha": 0.1
                }
            }
            
        elif request.regression_type == "polynomial":
            poly_features = PolynomialFeatures(degree=request.polynomial_degree)
            X_poly = poly_features.fit_transform(X)
            
            model = LinearRegression()
            model.fit(X_poly, y)
            y_pred = model.predict(X_poly)
            r2 = r2_score(y, y_pred)
            mse = mean_squared_error(y, y_pred)
            
            # 生成拟合公式
            intercept = round(model.intercept_, 4)
            formula_parts = [f"{request.dependent_var} = {intercept:.4f}"]
            feature_names = poly_features.get_feature_names_out(request.independent_vars)
            for i in range(1, len(feature_names)):
                coef = round(model.coef_[i], 4)
                if coef >= 0:
                    formula_parts.append(f"+ {coef:.4f} * {feature_names[i]}")
                else:
                    formula_parts.append(f"- {abs(coef):.4f} * {feature_names[i]}")
            formula = " ".join(formula_parts)
            
            # 生成图表数据
            chart_data = {
                "actual": list(zip(X.iloc[:, 0].tolist(), y.tolist())),
                "predicted": list(zip(X.iloc[:, 0].tolist(), y_pred.tolist()))
            }
            
            result = {
                "success": True,
                "regression_type": f"多项式回归 (Polynomial Regression, degree={request.polynomial_degree})",
                "dependent_var": request.dependent_var,
                "independent_vars": request.independent_vars,
                "sample_size": n,
                "formula": formula,
                "polynomial_degree": request.polynomial_degree,
                "intercept": intercept,
                "chart_data": chart_data,
                "model_stats": {
                    "r_squared": round(r2, 4),
                    "mse": round(mse, 4)
                }
            }
        else:
            raise HTTPException(status_code=400, detail=f"不支持的回归类型: {request.regression_type}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"回归分析失败: {str(e)}")

@router.post("/correlation")
async def correlation_analysis(request: CorrelationRequest, db: Session = Depends(get_db)):
    """相关分析"""
    try:
        snapshot = db.query(DataSnapshot).filter(
            DataSnapshot.id == request.snapshot_id
        ).first()
        
        if not snapshot:
            raise HTTPException(status_code=404, detail="快照不存在")
        
        data = json.loads(snapshot.data)
        df = pd.DataFrame(data)
        
        # 检查字段是否存在
        for field in request.fields:
            if field not in df.columns:
                raise HTTPException(status_code=400, detail=f"字段 '{field}' 不存在")
        
        # 转换为数值类型
        numeric_df = df[request.fields].apply(pd.to_numeric, errors='coerce')
        
        # 删除全部为空的行
        numeric_df = numeric_df.dropna(how='all')
        
        if len(numeric_df) < 3:
            raise HTTPException(status_code=400, detail="有效数值数据不足（至少需要3个）")
        
        # 计算相关系数矩阵
        corr_matrix = numeric_df.corr(method='pearson')
        
        # 准备结果
        fields = request.fields
        corr_matrix_list = corr_matrix.values.tolist()
        
        # 准备图表数据
        chart_data = {
            "x": fields,
            "y": fields,
            "values": corr_matrix_list
        }
        
        result = {
            "success": True,
            "fields": fields,
            "correlation_matrix": corr_matrix_list,
            "chart_data": chart_data
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"相关分析失败: {str(e)}")

@router.post("/montecarlo")
async def monte_carlo_analysis(request: MonteCarloRequest, db: Session = Depends(get_db)):
    """蒙特卡洛分析"""
    try:
        simulation_count = request.simulation_count
        
        if simulation_count < 100:
            raise HTTPException(status_code=400, detail="模拟次数至少需要100次")
        
        if simulation_count > 100000:
            raise HTTPException(status_code=400, detail="模拟次数不能超过100000次")
        
        # 生成随机数据
        simulation_results = []
        variable_data = {}
        
        for var in request.variables:
            if var.distribution == "norm":
                # 正态分布：params = [mean, std]
                samples = stats.norm.rvs(*var.params, size=simulation_count)
            elif var.distribution == "uniform":
                # 均匀分布：params = [min, max]
                samples = stats.uniform.rvs(loc=var.params[0], scale=var.params[1]-var.params[0], size=simulation_count)
            elif var.distribution == "expon":
                # 指数分布：params = [scale]
                samples = stats.expon.rvs(scale=var.params[0], size=simulation_count)
            elif var.distribution == "gamma":
                # 伽马分布：params = [shape, loc, scale]
                samples = stats.gamma.rvs(*var.params, size=simulation_count)
            else:
                raise HTTPException(status_code=400, detail=f"不支持的分布类型: {var.distribution}")
            
            variable_data[var.name] = samples
        
        # 执行公式计算
        try:
            # 安全地执行公式
            local_vars = variable_data.copy()
            results = []
            
            for i in range(simulation_count):
                eval_vars = {k: v[i] for k, v in variable_data.items()}
                try:
                    result = eval(request.formula, {"__builtins__": {}}, eval_vars)
                    results.append(float(result))
                except:
                    results.append(np.nan)
            
            results = np.array(results)
            valid_results = results[np.isfinite(results)]
            
            if len(valid_results) == 0:
                raise HTTPException(status_code=400, detail="没有有效的模拟结果，请检查公式")
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"公式计算失败: {str(e)}")
        
        # 计算统计量
        mean = float(valid_results.mean())
        std = float(valid_results.std())
        median = float(np.median(valid_results))
        min_val = float(valid_results.min())
        max_val = float(valid_results.max())
        p5 = float(np.percentile(valid_results, 5))
        p95 = float(np.percentile(valid_results, 95))
        
        # 置信区间
        ci_95_lower = float(np.percentile(valid_results, 2.5))
        ci_95_upper = float(np.percentile(valid_results, 97.5))
        ci_99_lower = float(np.percentile(valid_results, 0.5))
        ci_99_upper = float(np.percentile(valid_results, 99.5))
        
        # 生成直方图数据
        hist, bin_edges = np.histogram(valid_results, bins='auto')
        
        # 敏感性分析（简化版本）
        sensitivity = []
        for var in request.variables:
            # 计算该变量与结果的相关系数
            var_samples = variable_data[var.name][np.isfinite(results)]
            if len(var_samples) > 0 and len(valid_results) > 0:
                corr = np.corrcoef(var_samples, valid_results)[0, 1]
                sensitivity.append({
                    "variable": var.name,
                    "impact": abs(float(corr)) if not np.isnan(corr) else 0
                })
        
        # 按影响排序
        sensitivity = sorted(sensitivity, key=lambda x: x["impact"], reverse=True)
        
        result = {
            "success": True,
            "simulation_count": len(valid_results),
            "result_stats": {
                "mean": round(mean, 4),
                "std": round(std, 4),
                "median": round(median, 4),
                "min": round(min_val, 4),
                "max": round(max_val, 4),
                "p5": round(p5, 4),
                "p95": round(p95, 4)
            },
            "confidence_intervals": {
                "95%": [round(ci_95_lower, 4), round(ci_95_upper, 4)],
                "99%": [round(ci_99_lower, 4), round(ci_99_upper, 4)]
            },
            "chart_data": {
                "histogram": {
                    "bin_edges": bin_edges.tolist(),
                    "counts": hist.tolist()
                }
            },
            "sensitivity_analysis": sensitivity
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"蒙特卡洛分析失败: {str(e)}")

@router.post("/multi-correlation")
async def multi_correlation_analysis(request: MultiCorrelationRequest, db: Session = Depends(get_db)):
    """多数据流字段相关分析"""
    try:
        if len(request.fields) < 2:
            raise HTTPException(status_code=400, detail="至少需要选择2个字段")
        
        if request.correlation_method not in ["pearson", "spearman", "kendall"]:
            raise HTTPException(status_code=400, detail="不支持的相关系数类型，仅支持 pearson, spearman, kendall")
        
        # 收集所有字段数据
        all_data = {}
        field_info = []
        
        for field_req in request.fields:
            # 获取快照
            snapshot = db.query(DataSnapshot).filter(
                DataSnapshot.id == field_req.snapshot_id
            ).first()
            
            if not snapshot:
                raise HTTPException(status_code=404, detail=f"快照 {field_req.snapshot_id} 不存在")
            
            # 读取数据
            data = json.loads(snapshot.data)
            df = pd.DataFrame(data)
            
            if field_req.field_name not in df.columns:
                raise HTTPException(status_code=400, detail=f"字段 '{field_req.field_name}' 在快照 {snapshot.name} 中不存在")
            
            # 转换为数值类型
            series = pd.to_numeric(df[field_req.field_name], errors='coerce')
            
            # 生成唯一字段名（避免重名）
            unique_field_name = f"{snapshot.name}-{field_req.field_name}"
            all_data[unique_field_name] = series
            
            field_info.append({
                "snapshot_id": field_req.snapshot_id,
                "snapshot_name": snapshot.name,
                "field_name": field_req.field_name,
                "unique_name": unique_field_name
            })
        
        # 合并所有数据到一个DataFrame
        combined_df = pd.DataFrame(all_data)
        
        # 删除全部为空的行
        combined_df = combined_df.dropna(how='all')
        
        if len(combined_df) < 3:
            raise HTTPException(status_code=400, detail="有效数据不足（至少需要3个有效样本）")
        
        # 计算相关系数矩阵
        corr_matrix = combined_df.corr(method=request.correlation_method)
        
        # 准备字段列表
        fields_list = [f["unique_name"] for f in field_info]
        
        # 识别高相关对（|r| > threshold）
        high_correlations = []
        n = len(fields_list)
        threshold = request.correlation_threshold
        for i in range(n):
            for j in range(i + 1, n):
                corr = float(corr_matrix.iloc[i, j])
                if abs(corr) > threshold:
                    if corr > 0:
                        corr_type = "强正相关"
                    else:
                        corr_type = "强负相关"
                    
                    high_correlations.append({
                        "field1": fields_list[i],
                        "field2": fields_list[j],
                        "correlation": round(corr, 4),
                        "type": corr_type
                    })
        
        # 准备图表数据
        chart_data = {
            "x": fields_list,
            "y": fields_list,
            "values": corr_matrix.values.tolist()
        }
        
        result = {
            "success": True,
            "fields": field_info,
            "correlation_method": request.correlation_method,
            "correlation_threshold": threshold,
            "correlation_matrix": corr_matrix.values.tolist(),
            "high_correlations": high_correlations,
            "chart_data": chart_data
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"多数据流相关分析失败: {str(e)}")


@router.post("/correlation-explore")
async def correlation_explore(request: CorrelationExploreRequest, db: Session = Depends(get_db)):
    """相关性探索：两两字段组合分析，提取高相关对"""
    try:
        if len(request.fields) < 2:
            raise HTTPException(status_code=400, detail="至少需要选择2个字段")
        
        if request.correlation_method not in ["pearson", "spearman", "kendall"]:
            raise HTTPException(status_code=400, detail="不支持的相关系数类型，仅支持 pearson, spearman, kendall")
        
        # 收集所有字段数据
        all_data = {}
        field_info = []
        
        for field_req in request.fields:
            # 获取快照
            snapshot = db.query(DataSnapshot).filter(
                DataSnapshot.id == field_req.snapshot_id
            ).first()
            
            if not snapshot:
                raise HTTPException(status_code=404, detail=f"快照 {field_req.snapshot_id} 不存在")
            
            # 读取数据
            data = json.loads(snapshot.data)
            df = pd.DataFrame(data)
            
            if field_req.field_name not in df.columns:
                raise HTTPException(status_code=400, detail=f"字段 '{field_req.field_name}' 在快照 {snapshot.name} 中不存在")
            
            # 转换为数值类型
            series = pd.to_numeric(df[field_req.field_name], errors='coerce')
            
            # 生成唯一字段名（避免重名）
            unique_field_name = f"{snapshot.name}-{field_req.field_name}"
            all_data[unique_field_name] = series
            
            field_info.append({
                "snapshot_id": field_req.snapshot_id,
                "snapshot_name": snapshot.name,
                "field_name": field_req.field_name,
                "unique_name": unique_field_name
            })
        
        # 合并所有数据到一个DataFrame
        combined_df = pd.DataFrame(all_data)
        
        # 删除全部为空的行
        combined_df = combined_df.dropna(how='all')
        
        if len(combined_df) < 3:
            raise HTTPException(status_code=400, detail="有效数据不足（至少需要3个有效样本）")
        
        # 计算相关系数矩阵
        corr_matrix = combined_df.corr(method=request.correlation_method)
        
        # 准备字段列表
        fields_list = [f["unique_name"] for f in field_info]
        
        # 遍历所有两两组合，计算相关系数
        high_correlation_pairs = []
        n = len(fields_list)
        threshold = request.correlation_threshold
        total_pairs = n * (n - 1) // 2
        
        for i in range(n):
            for j in range(i + 1, n):
                corr = float(corr_matrix.iloc[i, j])
                if abs(corr) > threshold:
                    if corr > 0:
                        corr_type = "强正相关"
                    else:
                        corr_type = "强负相关"
                    
                    high_correlation_pairs.append({
                        "field1": field_info[i],
                        "field2": field_info[j],
                        "correlation": round(corr, 4),
                        "type": corr_type
                    })
        
        # 按相关系数绝对值从高到低排序
        high_correlation_pairs.sort(
            key=lambda x: abs(x["correlation"]),
            reverse=True
        )
        
        result = {
            "success": True,
            "fields": field_info,
            "correlation_method": request.correlation_method,
            "correlation_threshold": threshold,
            "high_correlation_pairs": high_correlation_pairs,
            "total_pairs": total_pairs,
            "high_correlation_count": len(high_correlation_pairs)
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"相关性探索失败: {str(e)}")


@router.post("/montecarlo/pi")
async def monte_carlo_pi(request: MonteCarloPiRequest):
    """蒙特卡洛方法计算圆周率 π"""
    try:
        n = request.simulation_count
        
        if n < 100:
            raise HTTPException(status_code=400, detail="模拟次数至少需要100次")
        
        if n > 1000000:
            raise HTTPException(status_code=400, detail="模拟次数不能超过1000000次")
        
        # 生成随机点
        x = np.random.uniform(-1, 1, n)
        y = np.random.uniform(-1, 1, n)
        
        # 计算距离
        distance = np.sqrt(x ** 2 + y ** 2)
        
        # 统计圆内点
        inside = distance < 1
        inside_count = int(np.sum(inside))
        outside_count = n - inside_count
        
        # 估计π值
        pi_estimate = (inside_count / n) * 4
        error = abs(pi_estimate - np.pi)
        
        # 准备图表数据（采样1000个点用于可视化）
        sample_size = min(1000, n)
        indices = np.random.choice(n, sample_size, replace=False)
        x_sample = x[indices]
        y_sample = y[indices]
        inside_sample = inside[indices]
        
        points_inside = []
        points_outside = []
        for i in range(sample_size):
            if inside_sample[i]:
                points_inside.append([float(x_sample[i]), float(y_sample[i])])
            else:
                points_outside.append([float(x_sample[i]), float(y_sample[i])])
        
        result = {
            "success": True,
            "simulation_count": n,
            "pi_estimate": round(pi_estimate, 6),
            "error": round(error, 6),
            "inside_count": inside_count,
            "outside_count": outside_count,
            "chart_data": {
                "points_inside": points_inside,
                "points_outside": points_outside,
                "circle_center": [0, 0],
                "circle_radius": 1
            }
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算圆周率失败: {str(e)}")


@router.post("/montecarlo/integral")
async def monte_carlo_integral(request: MonteCarloIntegralRequest):
    """蒙特卡洛方法计算定积分"""
    try:
        x_min = request.x_min
        x_max = request.x_max
        function_str = request.function
        n = request.simulation_count
        
        if n < 100:
            raise HTTPException(status_code=400, detail="模拟次数至少需要100次")
        
        if n > 1000000:
            raise HTTPException(status_code=400, detail="模拟次数不能超过1000000次")
        
        if x_max <= x_min:
            raise HTTPException(status_code=400, detail="x_max必须大于x_min")
        
        # 定义函数
        def f(x_val):
            try:
                return eval(function_str, {"__builtins__": {}}, {"x": x_val, "np": np})
            except:
                raise HTTPException(status_code=400, detail=f"函数表达式无效: {function_str}")
        
        # 计算函数在区间内的值，确定y的范围
        x_test = np.linspace(x_min, x_max, 1000)
        y_test = np.array([f(x) for x in x_test])
        y_min = float(np.min(y_test))
        y_max = float(np.max(y_test))
        
        # 确保y_min <= 0
        y_min = min(y_min, 0)
        y_max = max(y_max, 1)
        
        # 生成随机点
        x = np.random.uniform(x_min, x_max, n)
        y = np.random.uniform(y_min, y_max, n)
        
        # 计算函数值
        f_x = np.array([f(x_val) for x_val in x])
        
        # 统计曲线下的点（考虑正负）
        below = np.logical_and(y >= 0, y <= f_x)
        above = np.logical_and(y < 0, y >= f_x)
        valid = np.logical_or(below, above)
        
        below_count = int(np.sum(below))
        above_count = int(np.sum(above))
        valid_count = below_count + above_count
        invalid_count = n - valid_count
        
        # 估计积分值
        area = (x_max - x_min) * (y_max - y_min)
        integral_estimate = (below_count - above_count) / n * area
        
        # 计算真实值（使用数值积分）
        from scipy.integrate import quad
        try:
            real_integral, _ = quad(f, x_min, x_max)
            error = abs(integral_estimate - real_integral)
        except:
            real_integral = None
            error = None
        
        # 准备图表数据（采样1000个点用于可视化）
        sample_size = min(1000, n)
        indices = np.random.choice(n, sample_size, replace=False)
        x_sample = x[indices]
        y_sample = y[indices]
        valid_sample = valid[indices]
        
        points_below = []
        points_above = []
        for i in range(sample_size):
            if valid_sample[i]:
                if y_sample[i] >= 0:
                    points_below.append([float(x_sample[i]), float(y_sample[i])])
                else:
                    points_above.append([float(x_sample[i]), float(y_sample[i])])
        
        # 函数曲线
        function_curve = []
        x_curve = np.linspace(x_min, x_max, 200)
        for x_val in x_curve:
            function_curve.append([float(x_val), float(f(x_val))])
        
        result = {
            "success": True,
            "simulation_count": n,
            "integral_estimate": round(integral_estimate, 6),
            "real_integral": round(real_integral, 6) if real_integral is not None else None,
            "error": round(error, 6) if error is not None else None,
            "below_count": below_count,
            "above_count": above_count,
            "chart_data": {
                "points_below": points_below,
                "points_above": points_above,
                "function_curve": function_curve,
                "x_min": x_min,
                "x_max": x_max,
                "y_min": y_min,
                "y_max": y_max
            }
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算定积分失败: {str(e)}")


@router.post("/montecarlo/queue")
async def monte_carlo_queue(request: MonteCarloQueueRequest):
    """蒙特卡洛方法模拟排队问题"""
    try:
        num_people = request.num_people
        arrival_min = request.arrival_min
        arrival_max = request.arrival_max
        service_min = request.service_min
        service_max = request.service_max
        simulation_count = request.simulation_count
        
        if num_people < 1:
            raise HTTPException(status_code=400, detail="人数至少需要1人")
        
        if num_people > 100:
            raise HTTPException(status_code=400, detail="人数不能超过100人")
        
        if simulation_count < 10:
            raise HTTPException(status_code=400, detail="模拟次数至少需要10次")
        
        if simulation_count > 10000:
            raise HTTPException(status_code=400, detail="模拟次数不能超过10000次")
        
        if arrival_max <= arrival_min:
            raise HTTPException(status_code=400, detail="arrival_max必须大于arrival_min")
        
        if service_max <= service_min:
            raise HTTPException(status_code=400, detail="service_max必须大于service_min")
        
        # 多次模拟
        all_waiting_times = []
        all_service_times = []
        all_empty_times = []
        
        for _ in range(simulation_count):
            # 生成到达时间
            arrival_times = np.random.uniform(arrival_min, arrival_max, num_people)
            arrival_times.sort()
            
            # 生成服务时间
            service_times = np.random.uniform(service_min, service_max, num_people)
            
            # 模拟排队过程
            start_time = [0.0] * num_people
            finish_time = [0.0] * num_people
            waiting_time = [0.0] * num_people
            empty_time = [0.0] * num_people
            
            current_time = 0.0
            
            for i in range(num_people):
                if arrival_times[i] > current_time:
                    empty_time[i] = arrival_times[i] - current_time
                    current_time = arrival_times[i]
                
                start_time[i] = current_time
                waiting_time[i] = start_time[i] - arrival_times[i]
                finish_time[i] = start_time[i] + service_times[i]
                current_time = finish_time[i]
            
            # 收集统计数据
            all_waiting_times.extend(waiting_time)
            all_service_times.extend(service_times)
            all_empty_times.extend(empty_time)
        
        # 计算统计量
        waiting_times = np.array(all_waiting_times)
        service_times = np.array(all_service_times)
        empty_times = np.array(all_empty_times)
        
        waiting_stats = {
            "mean": round(float(np.mean(waiting_times)), 4),
            "std": round(float(np.std(waiting_times)), 4),
            "median": round(float(np.median(waiting_times)), 4),
            "min": round(float(np.min(waiting_times)), 4),
            "max": round(float(np.max(waiting_times)), 4)
        }
        
        service_stats = {
            "mean": round(float(np.mean(service_times)), 4),
            "std": round(float(np.std(service_times)), 4)
        }
        
        empty_stats = {
            "mean": round(float(np.mean(empty_times)), 4),
            "std": round(float(np.std(empty_times)), 4)
        }
        
        # 生成直方图数据
        hist, bin_edges = np.histogram(waiting_times, bins='auto')
        
        result = {
            "success": True,
            "simulation_count": simulation_count,
            "waiting_time": waiting_stats,
            "service_time": service_stats,
            "empty_time": empty_stats,
            "chart_data": {
                "waiting_time_histogram": {
                    "bin_edges": bin_edges.tolist(),
                    "counts": hist.tolist()
                }
            }
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模拟排队问题失败: {str(e)}")
