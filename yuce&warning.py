import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import os
import re
import calendar
import math
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.ticker import MaxNLocator

warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="销售预测与库存管理综合分析平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        color: #1f3867;
        text-align: center;
        margin-bottom: 1rem;
    }
    .card-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #444444;
    }
    .card-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1f3867;
    }
    .metric-card {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
        margin-bottom: 1rem;
    }
    .card-text {
        font-size: 0.9rem;
        color: #6c757d;
    }
    .alert-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .alert-success {
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 0.5rem solid #4CAF50;
    }
    .alert-warning {
        background-color: rgba(255, 152, 0, 0.1);
        border-left: 0.5rem solid #FF9800;
    }
    .alert-danger {
        background-color: rgba(244, 67, 54, 0.1);
        border-left: 0.5rem solid #F44336;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f3867;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .chart-explanation {
        background-color: rgba(76, 175, 80, 0.1);
        padding: 0.9rem;
        border-radius: 0.5rem;
        margin: 0.8rem 0;
        border-left: 0.5rem solid #4CAF50;
    }
    .low-accuracy {
        border: 2px solid #F44336;
        box-shadow: 0 0 8px #F44336;
    }
    .logo-container {
        position: absolute;
        top: 0.5rem;
        right: 1rem;
        z-index: 1000;
    }
    .logo-img {
        height: 40px;
    }
    .pagination-btn {
        background-color: #1f3867;
        color: white;
        border: none;
        padding: 5px 10px;
        border-radius: 3px;
        margin: 5px;
        cursor: pointer;
    }
    .pagination-btn:hover {
        background-color: #2c4f8f;
    }
    .pagination-info {
        display: inline-block;
        padding: 5px;
        margin: 5px;
    }
    .hover-info {
        background-color: rgba(0,0,0,0.7);
        color: white;
        padding: 8px;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    .slider-container {
        padding: 10px 0;
    }
    .highlight-product {
        font-weight: bold;
        background-color: #ffeb3b;
        padding: 2px 5px;
        border-radius: 3px;
    }
    .recommendation-tag {
        display: inline-block;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-left: 5px;
    }
    .recommendation-increase {
        background-color: #4CAF50;
        color: white;
    }
    .recommendation-maintain {
        background-color: #FFC107;
        color: black;
    }
    .recommendation-decrease {
        background-color: #F44336;
        color: white;
    }
    /* 新增的风险管理相关样式 */
    .risk-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1f3867;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .risk-card {
        background-color: white;
        border-radius: 0.5rem;
        padding: 0.8rem;
        box-shadow: 0 0.1rem 1rem 0 rgba(58, 59, 69, 0.15);
        margin-bottom: 0.8rem;
    }
    .risk-extreme-high {
        border-left: 0.5rem solid #8B0000;
    }
    .risk-high {
        border-left: 0.5rem solid #FF5252;
    }
    .risk-medium {
        border-left: 0.5rem solid #FFC107;
    }
    .risk-low {
        border-left: 0.5rem solid #4CAF50;
    }
    .risk-extreme-low {
        border-left: 0.5rem solid #2196F3;
    }
    .responsibility-detail {
        font-size: 0.85rem;
        color: #555;
        margin-top: 0.3rem;
    }
    .clearance-warning {
        color: #F44336;
        font-weight: bold;
    }
    .clearance-ok {
        color: #4CAF50;
    }
    .batch-age-high {
        color: #F44336;
        font-weight: bold;
    }
    .batch-age-medium {
        color: #FF9800;
    }
    .batch-age-low {
        color: #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# 登录界面
if not st.session_state.authenticated:
    st.markdown(
        '<div style="font-size: 1.5rem; color: #1f3867; text-align: center; margin-bottom: 1rem;">销售预测与库存管理综合分析平台 | 登录</div>',
        unsafe_allow_html=True)

    # 创建居中的登录框
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);">
            <h2 style="text-align: center; color: #1f3867; margin-bottom: 20px;">请输入密码</h2>
        </div>
        """, unsafe_allow_html=True)

        # 密码输入框
        password = st.text_input("密码", type="password", key="password_input")

        # 登录按钮
        login_button = st.button("登录")

        # 验证密码
        if login_button:
            if password == 'SAL':  # 简易密码，实际应用中应更安全
                st.session_state['authenticated'] = True
                st.success("登录成功！")
                try:
                    st.rerun()  # 使用新版本方法
                except AttributeError:
                    try:
                        st.experimental_rerun()  # 尝试使用旧版本方法
                    except:
                        st.error("请刷新页面以查看更改")
            else:
                st.error("密码错误，请重试！")

    # 如果未认证，不显示后续内容
    st.stop()


# 添加Logo到右上角
def add_logo():
    st.markdown(
        """
        <div class="logo-container">
            <img src="https://www.example.com/logo.png" class="logo-img">
        </div>
        """,
        unsafe_allow_html=True
    )


# 格式化数值的函数
def format_number(value):
    """格式化数量显示为逗号分隔的完整数字"""
    return f"{int(value):,} 箱"


# 添加图表解释
def add_chart_explanation(explanation_text):
    """添加图表解释"""
    st.markdown(f'<div class="chart-explanation">{explanation_text}</div>', unsafe_allow_html=True)


# 修改后的产品名称简化函数
def simplify_product_name(code, full_name):
    """将产品完整名称简化为更简短的格式"""
    # 检查输入有效性
    if not full_name or not isinstance(full_name, str):
        return full_name

    # 如果符合"口力X-中国"格式，则简化
    if "口力" in full_name and "-中国" in full_name:
        # 去除"口力"前缀和"-中国"后缀
        return full_name.replace("口力", "").replace("-中国", "").strip()

    # 否则返回原始名称
    return full_name


def safe_mean(series, default=0):
    """安全地计算Series的均值，处理空值和异常"""
    if series is None or len(series) == 0 or (hasattr(series, 'empty') and series.empty) or (
            hasattr(series, 'isna') and series.isna().all()):
        return default

    try:
        # 尝试使用pandas内置mean方法
        if hasattr(series, 'mean'):
            return series.mean()

        # 如果不是pandas Series，尝试使用numpy
        import numpy as np
        return np.nanmean(series)
    except (OverflowError, ValueError, TypeError, ZeroDivisionError):
        # 处理任何计算错误
        return default


def calculate_unified_accuracy(actual, forecast):
    """统一计算准确率的函数，适用于全国和区域"""
    if actual == 0 and forecast == 0:
        return 1.0  # 如果实际和预测都为0，准确率为100%

    if actual == 0:
        return 0.0  # 如果实际为0但预测不为0，准确率为0%

    # 计算差异率
    diff_rate = (actual - forecast) / actual

    # 计算准确率 (基础公式: 1 - |差异率|)
    return max(0, 1 - abs(diff_rate))


# 优化备货建议生成函数
def generate_recommendation(growth_rate):
    """优化的备货建议生成函数"""
    # 基于增长率生成建议
    if growth_rate > 15:
        return {
            "建议": "增加备货",
            "调整比例": round(growth_rate),
            "颜色": "#4CAF50",
            "样式类": "recommendation-increase",
            "图标": "↑"
        }
    elif growth_rate > 0:
        return {
            "建议": "小幅增加",
            "调整比例": round(growth_rate / 2),
            "颜色": "#8BC34A",
            "样式类": "recommendation-increase",
            "图标": "↗"
        }
    elif growth_rate > -10:
        return {
            "建议": "维持现状",
            "调整比例": 0,
            "颜色": "#FFC107",
            "样式类": "recommendation-maintain",
            "图标": "→"
        }
    else:
        adjust = abs(round(growth_rate / 2))
        return {
            "建议": "减少备货",
            "调整比例": adjust,
            "颜色": "#F44336",
            "样式类": "recommendation-decrease",
            "图标": "↓"
        }


# 生成动态标题
def generate_dynamic_title(base_title, include_filters=False):
    """生成简洁的动态标题，避免冗余信息"""
    return base_title  # 简化标题，移除冗余信息


# 从附件二整合的批次库存风险评估函数
def calculate_risk_percentage(days_to_clear, batch_age, target_days):
    """
    优化的风险计算方法，合理地考虑库龄与清库天数
    """
    # 核心规则1: 库龄已经超过目标天数，风险直接为100%
    if batch_age >= target_days:
        return 100.0

    # 核心规则2: 无法清库情况
    if days_to_clear == float('inf'):
        return 100.0

    # 核心规则3: 清库天数超过目标的3倍，风险为100%
    if days_to_clear >= 3 * target_days:
        return 100.0

    # 计算基于清库天数的风险（使用sigmoid函数提供更好的区分度）
    clearance_ratio = days_to_clear / target_days
    clearance_risk = 100 / (1 + math.exp(-4 * (clearance_ratio - 1)))

    # 计算基于库龄的风险（线性比例）
    age_risk = 100 * batch_age / target_days

    # 组合风险 - 加权平均，更强调高风险因素
    combined_risk = 0.8 * max(clearance_risk, age_risk) + 0.2 * min(clearance_risk, age_risk)

    # 阈值规则1: 清库天数超过目标，风险至少为80%
    if days_to_clear > target_days:
        combined_risk = max(combined_risk, 80)

    # 阈值规则2: 清库天数超过目标的2倍，风险至少为90%
    if days_to_clear >= 2 * target_days:
        combined_risk = max(combined_risk, 90)

    # 阈值规则3: 库龄超过目标的75%，风险至少为75%
    if batch_age >= 0.75 * target_days:
        combined_risk = max(combined_risk, 75)

    return min(100, round(combined_risk, 1))


# 从附件二整合的责任分析函数
# 从附件二整合的责任分析函数
def analyze_responsibility_collaborative(shipping_data, forecast_data, sales_person_region_mapping, product_code,
                                         batch_date, batch_qty=0):
    """
    简化版的责任归属分析函数，重点分析预测与实际销售差异
    """
    today = datetime.now().date()
    batch_date = batch_date.date() if isinstance(batch_date, datetime) else batch_date

    # 默认责任信息
    default_person = "系统管理员"
    default_region = "未知区域"

    # 收集相关数据
    # 预测窗口：批次生产前90天到批次生产后30天
    forecast_start_date = batch_date - timedelta(days=90)
    forecast_end_date = batch_date + timedelta(days=30)

    product_forecasts = forecast_data[
        (forecast_data['产品代码'] == product_code) &
        (forecast_data['所属年月'].dt.date >= forecast_start_date) &
        (forecast_data['所属年月'].dt.date <= forecast_end_date)
        ]

    # 销售窗口：批次生产日期到今天
    sales_start_date = batch_date
    sales_end_date = min(today, batch_date + timedelta(days=90))

    product_sales = shipping_data[
        (shipping_data['产品代码'] == product_code) &
        (shipping_data['订单日期'].dt.date >= sales_start_date) &
        (shipping_data['订单日期'].dt.date <= sales_end_date)
        ]

    # 初始化评分系统
    person_scores = {}
    person_allocations = {}

    # 分析预测与销售差异
    if not product_forecasts.empty:
        # 按销售人员分组的预测量
        person_forecast_totals = product_forecasts.groupby('销售员')['预计销售量'].sum()

        # 按销售人员分组的实际销量
        person_sales = {}
        for person in person_forecast_totals.index:
            # 修改这里 - 使用求和项:数量（箱）而不是数量
            person_actual_sales = product_sales[product_sales['申请人'] == person][
                '求和项:数量（箱）'].sum() if not product_sales.empty else 0
            person_sales[person] = person_actual_sales

            # 计算未兑现预测量
            forecast_qty = person_forecast_totals[person]
            unfulfilled = max(0, forecast_qty - person_actual_sales)

            # 只有有预测的人才计入责任分数
            if forecast_qty > 0:
                # 预测占比
                forecast_proportion = forecast_qty / person_forecast_totals.sum()
                # 履行率
                fulfillment_rate = person_actual_sales / forecast_qty if forecast_qty > 0 else 1.0

                # 预测销售差异得分 (60%)
                diff_score = 0.6 * (1 - fulfillment_rate) * (0.5 + 0.5 * forecast_proportion)
                person_scores[person] = person_scores.get(person, 0) + diff_score

        # 计算库存责任分配
        # 1. 计算总未兑现预测量
        total_unfulfilled = 0
        person_unfulfilled = {}

        for person, forecast_qty in person_forecast_totals.items():
            actual_sales = person_sales.get(person, 0)
            unfulfilled = max(0, forecast_qty - actual_sales)
            if unfulfilled > 0:
                person_unfulfilled[person] = unfulfilled
                total_unfulfilled += unfulfilled

        # 2. 按未兑现预测量比例分配库存责任
        if total_unfulfilled > 0:
            for person, unfulfilled in person_unfulfilled.items():
                allocation = int(batch_qty * (unfulfilled / total_unfulfilled))
                person_allocations[person] = allocation

        # 确保所有库存都被分配
        allocated_total = sum(person_allocations.values())
        if allocated_total < batch_qty and person_allocations:
            # 将剩余库存分配给未兑现预测量最高的人
            top_person = max(person_unfulfilled.items(), key=lambda x: x[1])[0]
            person_allocations[top_person] = person_allocations.get(top_person, 0) + (batch_qty - allocated_total)

    # 如果没有找到责任人，使用默认值
    if not person_allocations:
        person_allocations[default_person] = batch_qty

    # 确定主要责任人 - 应承担库存最多的人
    if person_allocations:
        responsible_person = max(person_allocations.items(), key=lambda x: x[1])[0]

        # 获取对应区域
        if responsible_person in sales_person_region_mapping:
            responsible_region = sales_person_region_mapping[responsible_person]
        else:
            responsible_region = default_region
    else:
        responsible_person = default_person
        responsible_region = default_region

    # 构建责任分析摘要
    responsibility_summary = []

    # 主要责任人信息
    main_person_forecast = person_forecast_totals.get(responsible_person, 0) if not product_forecasts.empty else 0
    main_person_sales = person_sales.get(responsible_person, 0) if responsible_person in person_sales else 0
    main_person_allocation = person_allocations.get(responsible_person, 0)

    # 履行率计算
    fulfillment_rate = (main_person_sales / main_person_forecast * 100) if main_person_forecast > 0 else 100

    # 主责任人摘要
    responsibility_summary.append(
        f"{responsible_person}主要责任(预测{main_person_forecast:.0f}件但仅销售{main_person_sales:.0f}件(履行率{fulfillment_rate:.0f}%)、未兑现预测{max(0, main_person_forecast - main_person_sales):.0f}件，承担{main_person_allocation}件)")

    # 共同责任人摘要
    secondary_persons = [(p, a) for p, a in person_allocations.items() if p != responsible_person]
    if secondary_persons:
        # 按分配库存量降序排序
        secondary_persons.sort(key=lambda x: x[1], reverse=True)
        secondary_summary = []

        for person, allocation in secondary_persons:
            forecast = person_forecast_totals.get(person, 0)
            sales = person_sales.get(person, 0)
            unfulfilled = max(0, forecast - sales)
            secondary_summary.append(f"{person}(未兑现预测{unfulfilled:.0f}件，承担{allocation}件)")

        if secondary_summary:
            responsibility_summary.append("共同责任：" + "，".join(secondary_summary))

    # 合并摘要
    full_summary = "，".join(responsibility_summary)

    return responsible_region, responsible_person, full_summary


# 批次库存风险评估
# 批次库存风险评估
# 批次库存风险评估
def assess_batch_risk(batch_data, shipping_data, forecast_data, sales_person_region_mapping):
    """
    对批次库存进行风险评估
    """
    # 风险阈值参数
    high_stock_days = 90  # 库存超过90天视为高风险
    medium_stock_days = 60  # 库存超过60天视为中风险
    low_stock_days = 30  # 库存超过30天视为低风险

    # 清库天数阈值
    high_clearance_days = 90  # 预计清库天数超过90天视为高风险
    medium_clearance_days = 60  # 预计清库天数超过60天视为中风险
    low_clearance_days = 30  # 预计清库天数超过30天视为低风险

    # 最小日均销量阈值，防止清库天数计算为无穷大
    min_daily_sales = 0.5  # 每天至少0.5件的销售量

    # 季节性指数下限
    min_seasonal_index = 0.3  # 季节性指数最低为0.3

    today = datetime.now().date()
    risk_assessment = []

    # 计算每个产品的销售指标
    product_sales_metrics = {}

    for product_code in batch_data['产品代码'].unique():
        # 获取该产品的销售记录
        product_sales = shipping_data[shipping_data['产品代码'] == product_code]

        if len(product_sales) == 0:
            # 无销售记录
            product_sales_metrics[product_code] = {
                'daily_avg_sales': 0,
                'sales_std': 0,
                'coefficient_of_variation': float('inf'),
                'total_sales': 0
            }
        else:
            try:
                # 计算总销量
                total_sales = product_sales['求和项:数量（箱）'].sum()

                # 计算日均销量 - 添加错误处理
                try:
                    min_date = product_sales['订单日期'].min()
                    if pd.isna(min_date):
                        days_range = 1  # 如果没有有效日期，默认为1天
                    else:
                        days_range = (today - min_date.dt.date).days + 1
                        if days_range <= 0:  # 防止除以零或负数
                            days_range = 1
                except (AttributeError, TypeError) as e:
                    # 如果日期处理出错，设置默认值
                    days_range = 1

                daily_avg_sales = total_sales / days_range

                # 计算销量标准差 - 添加错误处理
                try:
                    daily_sales = product_sales.groupby(product_sales['订单日期'].dt.date)['求和项:数量（箱）'].sum()
                    sales_std = daily_sales.std() if len(daily_sales) > 1 else 0
                except (AttributeError, TypeError):
                    sales_std = 0

                # 计算变异系数（波动系数）
                coefficient_of_variation = sales_std / daily_avg_sales if daily_avg_sales > 0 else float('inf')

                product_sales_metrics[product_code] = {
                    'daily_avg_sales': daily_avg_sales,
                    'sales_std': sales_std,
                    'coefficient_of_variation': coefficient_of_variation,
                    'total_sales': total_sales
                }
            except Exception as e:
                # 如果处理过程中出现任何错误，使用默认值
                print(f"处理产品 {product_code} 销售指标时出错: {str(e)}")
                product_sales_metrics[product_code] = {
                    'daily_avg_sales': 0,
                    'sales_std': 0,
                    'coefficient_of_variation': float('inf'),
                    'total_sales': 0
                }

    # 计算每个产品的季节性指数
    seasonal_indices = {}
    for product_code in batch_data['产品代码'].unique():
        product_sales = shipping_data[shipping_data['产品代码'] == product_code]
        seasonal_index = 1.0  # 默认值

        if len(product_sales) > 0:
            try:
                # 按月分组销量
                product_sales['月份'] = product_sales['订单日期'].dt.month
                monthly_sales = product_sales.groupby('月份')['求和项:数量（箱）'].sum()

                if len(monthly_sales) > 1:
                    # 计算平均月销量
                    avg_monthly_sales = monthly_sales.mean()

                    # 当前月份的季节性指数
                    current_month = today.month
                    if current_month in monthly_sales.index:
                        seasonal_index = monthly_sales[current_month] / avg_monthly_sales
            except Exception as e:
                # 如果处理过程中出现任何错误，使用默认值
                print(f"计算产品 {product_code} 季节性指数时出错: {str(e)}")
                seasonal_index = 1.0

        # 应用季节性指数下限
        seasonal_index = max(seasonal_index, min_seasonal_index)
        seasonal_indices[product_code] = seasonal_index

    # 评估每个批次的风险
    for _, batch in batch_data.iterrows():
        try:
            product_code = batch['产品代码']
            batch_date = batch['生产日期']
            batch_qty = batch['数量']

            # 计算库龄（从生产日期到今天的天数）
            try:
                if isinstance(batch_date, datetime):
                    batch_age = (today - batch_date.date()).days
                else:
                    # 尝试转换为datetime
                    batch_date = pd.to_datetime(batch_date)
                    batch_age = (today - batch_date.date()).days
            except (AttributeError, TypeError, ValueError):
                # 如果日期处理失败，设置默认库龄
                batch_age = 30  # 默认30天
                print(f"计算批次库龄时出错，产品: {product_code}, 批次日期: {batch_date}")

            # 获取销售指标
            sales_metrics = product_sales_metrics.get(product_code, {
                'daily_avg_sales': 0,
                'sales_std': 0,
                'coefficient_of_variation': float('inf'),
                'total_sales': 0
            })

            # 获取季节性指数
            seasonal_index = seasonal_indices.get(product_code, 1.0)

            # 计算预计清库天数
            daily_avg_sales = sales_metrics['daily_avg_sales']

            # 考虑季节性调整，并应用最小销量阈值
            daily_avg_sales_adjusted = max(daily_avg_sales * seasonal_index, min_daily_sales)

            # 计算清库天数
            if daily_avg_sales_adjusted > 0:
                days_to_clear = batch_qty / daily_avg_sales_adjusted
            else:
                days_to_clear = float('inf')

            # 计算积压风险百分比
            one_month_risk = calculate_risk_percentage(days_to_clear, batch_age, low_stock_days)
            two_month_risk = calculate_risk_percentage(days_to_clear, batch_age, medium_stock_days)
            three_month_risk = calculate_risk_percentage(days_to_clear, batch_age, high_stock_days)

            # 确定积压原因
            stocking_reasons = []
            if batch_age > 60:
                stocking_reasons.append("库龄过长")
            if sales_metrics['coefficient_of_variation'] > 1.0:
                stocking_reasons.append("销量波动大")
            if seasonal_index < 0.8:
                stocking_reasons.append("季节性影响")
            if not stocking_reasons:
                stocking_reasons.append("正常库存")

            # 改进风险等级评估 - 使用综合评分方法
            risk_score = 0

            # 库龄因素 (0-40分)
            if batch_age > 90:
                risk_score += 40
            elif batch_age > 60:
                risk_score += 30
            elif batch_age > 30:
                risk_score += 20
            else:
                risk_score += 10

            # 清库天数因素 (0-40分)
            if days_to_clear == float('inf'):
                risk_score += 40
            elif days_to_clear > 180:  # 半年以上
                risk_score += 35
            elif days_to_clear > 90:
                risk_score += 30
            elif days_to_clear > 60:
                risk_score += 20
            elif days_to_clear > 30:
                risk_score += 10

            # 销量波动系数 (0-10分)
            if sales_metrics['coefficient_of_variation'] > 2.0:
                risk_score += 10
            elif sales_metrics['coefficient_of_variation'] > 1.0:
                risk_score += 5

            # 根据总分确定风险等级
            if risk_score >= 80:
                risk_level = "极高风险"
            elif risk_score >= 60:
                risk_level = "高风险"
            elif risk_score >= 40:
                risk_level = "中风险"
            elif risk_score >= 20:
                risk_level = "低风险"
            else:
                risk_level = "极低风险"

            # 生成建议措施
            if risk_level == "极高风险":
                recommendation = "紧急清理：考虑折价促销"
            elif risk_level == "高风险":
                recommendation = "优先处理：降价促销或转仓调配"
            elif risk_level == "中风险":
                recommendation = "密切监控：调整采购计划"
            elif risk_level == "低风险":
                recommendation = "常规管理：定期审查库存周转"
            else:
                recommendation = "维持现状：正常库存水平"

            # 责任分析
            try:
                responsible_region, responsible_person, responsibility_summary = analyze_responsibility_collaborative(
                    shipping_data, forecast_data, sales_person_region_mapping, product_code, batch_date, batch_qty
                )
            except Exception as e:
                print(f"进行责任分析时出错: {str(e)}")
                responsible_region = "未知区域"
                responsible_person = "系统管理员"
                responsibility_summary = "责任分析过程中出错"

            # 尝试获取批次日期的日期表示
            try:
                batch_date_display = batch_date.date() if isinstance(batch_date, datetime) else batch_date
            except AttributeError:
                batch_date_display = "未知日期"

            # 构建风险评估结果
            risk_assessment.append({
                '物料': product_code,
                '描述': batch['描述'],
                '批次日期': batch_date_display,
                '批次库存': batch_qty,
                '库龄': batch_age,
                '日均出货': round(daily_avg_sales, 2),
                '出货波动系数': round(sales_metrics['coefficient_of_variation'], 2),
                '预计清库天数': days_to_clear,
                '一个月积压风险': f"{round(one_month_risk, 1)}%",
                '两个月积压风险': f"{round(two_month_risk, 1)}%",
                '三个月积压风险': f"{round(three_month_risk, 1)}%",
                '积压原因': '，'.join(stocking_reasons),
                '季节性指数': round(seasonal_index, 2),
                '责任区域': responsible_region,
                '责任人': responsible_person,
                '责任分析摘要': responsibility_summary,
                '风险程度': risk_level,
                '风险得分': risk_score,
                '建议措施': recommendation
            })
        except Exception as e:
            print(f"处理批次时出错: {str(e)}")
            # 跳过有问题的批次，继续处理下一个

    # 转换为DataFrame并按风险程度和库龄排序
    risk_df = pd.DataFrame(risk_assessment)

    if not risk_df.empty:
        risk_order = {
            "极高风险": 0,
            "高风险": 1,
            "中风险": 2,
            "低风险": 3,
            "极低风险": 4
        }
        risk_df['风险排序'] = risk_df['风险程度'].map(risk_order)
        risk_df = risk_df.sort_values(by=['风险排序', '库龄'], ascending=[True, False])
        risk_df = risk_df.drop(columns=['风险排序'])

    return risk_df


# 创建销售人员与区域映射
# 创建销售人员与区域映射
def create_person_region_mapping(shipping_data, forecast_data):
    """
    创建销售人员与区域的对应关系
    """
    sales_person_region_mapping = {}

    # 从出货数据中提取映射关系
    person_region_data = shipping_data[['申请人', '所属区域']].drop_duplicates()

    # 统计每个销售人员最常出现的区域
    person_region_counts = shipping_data.groupby(['申请人', '所属区域']).size().unstack(fill_value=0)

    # 对于每个销售人员，找出他们最常用的区域
    for person in shipping_data['申请人'].unique():
        if person == "系统管理员":
            sales_person_region_mapping[person] = ""
        elif person in person_region_counts.index:
            # 找出该人员最常见的区域
            most_common_region = person_region_counts.loc[person].idxmax()
            sales_person_region_mapping[person] = most_common_region
        else:
            # 如果没有记录，使用"未知区域"
            sales_person_region_mapping[person] = "未知区域"

    # 对预测数据中的销售员也添加区域映射
    for person in forecast_data['销售员'].unique():
        if person == "系统管理员":
            continue

        if person not in sales_person_region_mapping:
            # 在预测数据中查找该销售员的区域
            person_regions = forecast_data[forecast_data['销售员'] == person]['所属大区'].unique()
            if len(person_regions) > 0:
                sales_person_region_mapping[person] = person_regions[0]
            else:
                sales_person_region_mapping[person] = "未知区域"

    # 确保系统管理员的区域为空字符串
    sales_person_region_mapping["系统管理员"] = ""

    return sales_person_region_mapping


# 显示风险分布饼图
def display_risk_distribution_chart(risk_assessment):
    """
    显示批次风险分布饼图
    """
    if risk_assessment.empty:
        st.warning("未发现批次数据，无法显示风险分布")
        return

    risk_counts = risk_assessment['风险程度'].value_counts()

    # 准备饼图数据
    labels = risk_counts.index
    values = risk_counts.values

    # 设置颜色
    colors = {
        '极高风险': '#8B0000',
        '高风险': '#FF0000',
        '中风险': '#FFA500',
        '低风险': '#4CAF50',
        '极低风险': '#2196F3'
    }

    color_values = [colors.get(label, '#CCCCCC') for label in labels]

    # 创建饼图
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=color_values),
        textinfo='label+percent',
        hoverinfo='label+value+percent',
        textfont=dict(size=14),
        hole=0.3
    )])

    fig.update_layout(
        title='批次风险分布',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )

    # 添加注解：总批次数
    total_batches = sum(values)
    fig.add_annotation(
        x=0.5, y=0.5,
        text=f"总批次数<br>{total_batches}",
        showarrow=False,
        font=dict(size=16)
    )

    st.plotly_chart(fig, use_container_width=True)

    # 添加解释
    high_risk = risk_counts.get('极高风险', 0) + risk_counts.get('高风险', 0)
    high_risk_pct = (high_risk / total_batches * 100) if total_batches > 0 else 0

    explanation = f"""
    <b>图表解读：</b> 此图展示了库存批次按风险等级的分布情况。
    当前有 <b>{high_risk}个</b> 批次处于高风险或极高风险状态，占比 <b>{high_risk_pct:.1f}%</b>。
    这些批次需要优先处理，以减少库存积压和资金占用。
    """
    add_chart_explanation(explanation)


# 显示高风险批次库龄分布
def display_high_risk_age_chart(risk_assessment):
    """
    显示高风险批次的库龄分布
    """
    # 筛选高风险和极高风险批次
    high_risk_batches = risk_assessment[risk_assessment['风险程度'].isin(['极高风险', '高风险'])]

    if high_risk_batches.empty:
        st.warning("未发现高风险批次，无法显示库龄分布")
        return

    # 排序并选择前10个高库龄批次
    high_risk_batches = high_risk_batches.sort_values('库龄', ascending=False).head(10)

    # 创建批次标签
    batch_labels = [f"{code} ({date})" for code, date in
                    zip(high_risk_batches['物料'], high_risk_batches['批次日期'].astype(str))]

    # 设置颜色
    bar_colors = ['#8B0000' if x == '极高风险' else '#FF5252' for x in high_risk_batches['风险程度']]

    # 创建水平条形图
    fig = go.Figure()

    # 添加库龄条形图
    fig.add_trace(go.Bar(
        y=batch_labels,
        x=high_risk_batches['库龄'],
        orientation='h',
        marker_color=bar_colors,
        name='库龄（天）',
        text=high_risk_batches['库龄'],
        textposition='outside'
    ))

    # 添加参考线
    fig.add_shape(
        type="line",
        x0=90, x1=90,
        y0=-0.5, y1=len(batch_labels) - 0.5,
        line=dict(color="red", width=2, dash="dash"),
        name="高风险阈值(90天)"
    )

    fig.add_shape(
        type="line",
        x0=60, x1=60,
        y0=-0.5, y1=len(batch_labels) - 0.5,
        line=dict(color="orange", width=2, dash="dash"),
        name="中风险阈值(60天)"
    )

    fig.add_shape(
        type="line",
        x0=30, x1=30,
        y0=-0.5, y1=len(batch_labels) - 0.5,
        line=dict(color="green", width=2, dash="dash"),
        name="低风险阈值(30天)"
    )

    # 更新布局
    fig.update_layout(
        title='高风险批次库龄分布',
        xaxis_title='库龄（天）',
        yaxis_title='批次',
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    # 添加悬停信息
    hover_texts = []
    for _, batch in high_risk_batches.iterrows():
        hover_text = f"物料: {batch['物料']}<br>" + \
                     f"描述: {batch['描述']}<br>" + \
                     f"批次日期: {batch['批次日期']}<br>" + \
                     f"批次库存: {batch['批次库存']}件<br>" + \
                     f"库龄: {batch['库龄']}天<br>" + \
                     f"风险等级: {batch['风险程度']}"
        hover_texts.append(hover_text)

    fig.update_traces(
        hovertemplate='%{text}<extra></extra>',
        text=hover_texts
    )

    st.plotly_chart(fig, use_container_width=True)

    # 添加解释
    avg_age = high_risk_batches['库龄'].mean()
    max_age = high_risk_batches['库龄'].max()

    explanation = f"""
    <b>图表解读：</b> 此图展示了高风险批次的库龄分布。
    平均库龄为 <b>{avg_age:.1f}天</b>，最大库龄为 <b>{max_age}天</b>。
    虚线表示风险阈值：红线(90天)、橙线(60天)、绿线(30天)。
    长期呆滞批次占用仓储空间并增加资金成本，建议优先处理库龄超过90天的批次。
    """
    add_chart_explanation(explanation)


# 显示清库预测图
def display_clearance_forecast_chart(risk_assessment):
    """
    显示批次清库预测时间图表
    """
    if risk_assessment.empty:
        st.warning("未发现批次数据，无法显示清库预测")
        return

    # 筛选高风险批次
    high_risk_batches = risk_assessment[risk_assessment['风险程度'].isin(['极高风险', '高风险'])]

    if high_risk_batches.empty:
        st.warning("未发现高风险批次，无法显示清库预测")
        return

    # 处理无穷大的清库天数
    high_risk_batches = high_risk_batches.copy()
    high_risk_batches['清库天数值'] = high_risk_batches['预计清库天数'].apply(
        lambda x: 365 if x == float('inf') else float(x)
    )

    # 选择前8个清库天数最长的批次
    sorted_batches = high_risk_batches.sort_values('清库天数值', ascending=False).head(8)

    # 准备批次标签
    batch_labels = [f"{code}" for code in sorted_batches['物料']]

    # 创建图表
    fig = go.Figure()

    # 添加清库天数条形图
    fig.add_trace(go.Bar(
        y=batch_labels,
        x=sorted_batches['清库天数值'],
        orientation='h',
        marker_color='#FF5252',
        name='预计清库天数',
        text=[f"{x:.0f}天" if x < 365 else "∞" for x in sorted_batches['清库天数值']],
        textposition='outside'
    ))

    # 添加库龄条形图，使用错开的位置
    fig.add_trace(go.Bar(
        y=[f"{label}" for label in batch_labels],
        x=sorted_batches['库龄'],
        orientation='h',
        marker_color='#4682B4',
        name='当前库龄',
        text=[f"{x}天" for x in sorted_batches['库龄']],
        textposition='outside',
        offsetgroup=1
    ))

    # 添加风险阈值参考线
    fig.add_shape(
        type="line",
        x0=90, x1=90,
        y0=-0.5, y1=len(batch_labels) - 0.5,
        line=dict(color="red", width=2, dash="dash"),
        name="高风险阈值(90天)"
    )

    # 更新布局
    fig.update_layout(
        title='高风险批次清库预测',
        barmode='group',
        xaxis_title='天数',
        yaxis_title='批次',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )

    # 添加悬停信息
    hover_texts_clearance = []
    hover_texts_age = []

    for _, batch in sorted_batches.iterrows():
        clearance_text = f"物料: {batch['物料']}<br>" + \
                         f"描述: {batch['描述']}<br>" + \
                         f"预计清库天数: {batch['清库天数值']:.0f}天<br>" + \
                         f"日均出货: {batch['日均出货']}件<br>" + \
                         f"批次库存: {batch['批次库存']}件<br>" + \
                         f"责任人: {batch['责任人']}"

        age_text = f"物料: {batch['物料']}<br>" + \
                   f"描述: {batch['描述']}<br>" + \
                   f"当前库龄: {batch['库龄']}天<br>" + \
                   f"批次日期: {batch['批次日期']}<br>" + \
                   f"批次库存: {batch['批次库存']}件"

        hover_texts_clearance.append(clearance_text)
        hover_texts_age.append(age_text)

    fig.update_traces(
        hovertemplate='%{text}<extra></extra>',
        text=hover_texts_clearance,
        selector=dict(name='预计清库天数')
    )

    fig.update_traces(
        hovertemplate='%{text}<extra></extra>',
        text=hover_texts_age,
        selector=dict(name='当前库龄')
    )

    st.plotly_chart(fig, use_container_width=True)

    # 添加解释
    avg_clearance = sorted_batches['清库天数值'].mean()
    infinite_count = sum(high_risk_batches['预计清库天数'] == float('inf'))
    total_count = len(high_risk_batches)

    explanation = f"""
    <b>图表解读：</b> 此图对比展示了高风险批次的预计清库天数(红色)和当前库龄(蓝色)。
    平均清库时间为 <b>{avg_clearance:.1f}天</b>，远超90天风险阈值(红色虚线)。
    总共有 <b>{infinite_count}个</b> 批次因无销量导致清库天数为无穷大，占高风险批次总数的 <b>{infinite_count / total_count * 100:.1f}%</b>。
    这些批次需要特别干预措施，建议考虑促销、转仓或特价处理。
    """
    add_chart_explanation(explanation)


# 显示责任分析图
def display_responsibility_analysis(risk_assessment):
    """
    显示责任人和区域的批次数量分析
    """
    if risk_assessment.empty:
        st.warning("未发现批次数据，无法显示责任分析")
        return

    # 责任人分析
    person_counts = risk_assessment.groupby(['责任人', '风险程度']).size().unstack(fill_value=0)

    # 只分析有批次数据的责任人，按批次总数排序
    person_counts['总数'] = person_counts.sum(axis=1)
    person_counts = person_counts.sort_values('总数', ascending=False).head(10)

    # 创建堆叠条形图
    fig = go.Figure()

    # 按风险等级添加条形
    risk_levels = ['极高风险', '高风险', '中风险', '低风险', '极低风险']
    colors = ['#8B0000', '#FF5252', '#FFA500', '#4CAF50', '#2196F3']

    for risk, color in zip(risk_levels, colors):
        if risk in person_counts.columns:
            fig.add_trace(go.Bar(
                y=person_counts.index,
                x=person_counts[risk],
                name=risk,
                orientation='h',
                marker_color=color
            ))

    # 更新布局
    fig.update_layout(
        title='责任人批次分布',
        barmode='stack',
        xaxis_title='批次数量',
        yaxis_title='责任人',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

    # 添加解释
    top_person = person_counts.index[0]
    top_person_high_risk = person_counts.loc[top_person].get('极高风险', 0) + person_counts.loc[top_person].get(
        '高风险', 0)

    explanation = f"""
    <b>图表解读：</b> 此图展示了负责批次最多的10个责任人及其批次风险分布。
    <b>{top_person}</b> 负责的批次数量最多，其中高风险和极高风险批次有 <b>{top_person_high_risk}个</b>。
    建议重点关注负责高风险批次较多的责任人，协助其制定库存处理计划。
    """
    add_chart_explanation(explanation)

    # 区域分析
    region_counts = risk_assessment[risk_assessment['责任区域'] != ''].groupby(['责任区域', '风险程度']).size().unstack(
        fill_value=0)

    if not region_counts.empty:
        # 只分析有批次数据的区域，按批次总数排序
        region_counts['总数'] = region_counts.sum(axis=1)
        region_counts = region_counts.sort_values('总数', ascending=False)

        # 创建饼图
        region_total = region_counts['总数']

        fig = go.Figure(data=[go.Pie(
            labels=region_total.index,
            values=region_total.values,
            textinfo='label+percent',
            hole=0.3
        )])

        fig.update_layout(
            title='各区域批次分布',
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

        # 添加解释
        top_region = region_total.index[0]
        top_region_pct = region_total.iloc[0] / region_total.sum() * 100

        explanation = f"""
        <b>图表解读：</b> 此图展示了各区域负责的批次分布情况。
        <b>{top_region}区</b> 负责的批次最多，占比 <b>{top_region_pct:.1f}%</b>。
        """
        add_chart_explanation(explanation)


# 风险详情列表组件
def display_risk_detail_list(risk_assessment, filter_option=None):
    """
    显示风险详情列表，支持筛选
    """
    if risk_assessment.empty:
        st.warning("未发现批次数据")
        return

    # 应用筛选
    filtered_data = risk_assessment
    if filter_option and filter_option != "全部":
        filtered_data = risk_assessment[risk_assessment['风险程度'] == filter_option]

    if filtered_data.empty:
        st.warning(f"没有符合条件的{filter_option}批次")
        return

    # 为每个批次创建详情卡片
    for _, batch in filtered_data.head(10).iterrows():
        risk_level = batch['风险程度']
        risk_class = ""

        # 根据风险等级设置卡片样式
        if risk_level == "极高风险":
            risk_class = "risk-extreme-high"
        elif risk_level == "高风险":
            risk_class = "risk-high"
        elif risk_level == "中风险":
            risk_class = "risk-medium"
        elif risk_level == "低风险":
            risk_class = "risk-low"
        else:
            risk_class = "risk-extreme-low"

        # 清库天数样式
        clearance_days = batch['预计清库天数']
        clearance_class = ""
        clearance_display = ""

        if clearance_days == float('inf'):
            clearance_display = "∞ (无法预计)"
            clearance_class = "clearance-warning"
        else:
            clearance_display = f"{clearance_days:.1f}天"
            if clearance_days > 90:
                clearance_class = "clearance-warning"
            else:
                clearance_class = "clearance-ok"

        # 库龄样式
        batch_age = batch['库龄']
        age_class = ""

        if batch_age > 90:
            age_class = "batch-age-high"
        elif batch_age > 60:
            age_class = "batch-age-medium"
        else:
            age_class = "batch-age-low"

        # 创建卡片
        st.markdown(f"""
        <div class="risk-card {risk_class}">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <h3 style="margin: 0;">{batch['物料']} - {batch['描述']}</h3>
                    <p style="margin: 0.2rem 0;">批次日期: {batch['批次日期']} | 批次库存: {batch['批次库存']}件</p>
                </div>
                <div style="text-align: right;">
                    <span style="font-weight: bold; color: {colors_for_risk(risk_level)};">{risk_level}</span>
                    <p style="margin: 0;">风险得分: {batch['风险得分']}</p>
                </div>
            </div>

            <div style="display: flex; margin-top: 0.5rem;">
                <div style="flex: 1;">
                    <p style="margin: 0.2rem 0;">库龄: <span class="{age_class}">{batch_age}天</span></p>
                    <p style="margin: 0.2rem 0;">预计清库: <span class="{clearance_class}">{clearance_display}</span></p>
                    <p style="margin: 0.2rem 0;">日均出货: {batch['日均出货']}件 | 出货波动系数: {batch['出货波动系数']}</p>
                </div>
                <div style="flex: 1;">
                    <p style="margin: 0.2rem 0;">责任区域: {batch['责任区域']}</p>
                    <p style="margin: 0.2rem 0;">责任人: {batch['责任人']}</p>
                    <p style="margin: 0.2rem 0;">建议措施: {batch['建议措施']}</p>
                </div>
            </div>

            <div class="responsibility-detail">
                <p>责任分析: {batch['责任分析摘要']}</p>
                <p>积压原因: {batch['积压原因']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 显示更多按钮（如果批次数超过10个）
    if len(filtered_data) > 10:
        st.markdown(f"<p style='text-align:center;'>显示前10个批次，共{len(filtered_data)}个批次符合条件</p>",
                    unsafe_allow_html=True)

        if st.button(f"查看全部{len(filtered_data)}个批次", key=f"show_all_{filter_option}"):
            # 显示完整表格
            st.dataframe(filtered_data[['物料', '描述', '批次日期', '批次库存', '库龄',
                                        '预计清库天数', '责任人', '风险程度', '建议措施']])


# 辅助函数：为风险等级提供对应颜色
def colors_for_risk(risk_level):
    """
    根据风险等级返回对应的颜色
    """
    colors = {
        "极高风险": "#8B0000",
        "高风险": "#FF0000",
        "中风险": "#FFA500",
        "低风险": "#4CAF50",
        "极低风险": "#2196F3"
    }
    return colors.get(risk_level, "#777777")


# 数据加载函数增强
@st.cache_data
def load_product_info(file_path=None):
    """加载产品信息数据"""
    try:
        # 默认路径或示例数据
        if file_path is None or not os.path.exists(file_path):
            # 创建示例数据
            return create_sample_product_info()

        # 加载数据
        df = pd.read_excel(file_path)

        # 确保列名格式一致
        required_columns = ['产品代码', '产品名称']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.error(f"产品信息文件缺少必要的列: {', '.join(missing_columns)}。使用示例数据进行演示。")
            return create_sample_product_info()

        # 确保数据类型正确
        df['产品代码'] = df['产品代码'].astype(str)
        df['产品名称'] = df['产品名称'].astype(str)

        # 添加简化产品名称列
        df['简化产品名称'] = df.apply(lambda row: simplify_product_name(row['产品代码'], row['产品名称']), axis=1)

        return df

    except Exception as e:
        st.error(f"加载产品信息数据时出错: {str(e)}。使用示例数据进行演示。")
        return create_sample_product_info()


def create_sample_product_info():
    """创建示例产品信息数据"""
    # 产品代码列表
    product_codes = [
        'F0104L', 'F01E4P', 'F01E6C', 'F3406B', 'F3409N', 'F3411A',
        'F01E4B', 'F0183F', 'F0110C', 'F0104J', 'F0104M', 'F0104P',
        'F0110A', 'F0110B', 'F0115C', 'F0101P'
    ]

    # 产品名称列表
    product_names = [
        '口力比萨68克袋装-中国', '口力汉堡大袋120g-中国', '口力汉堡中袋108g-中国',
        '口力海洋动物100g-中国', '口力幻彩蜥蜴105g-中国', '口力午餐袋77g-中国',
        '口力汉堡137g-中国', '口力热狗120g-中国', '口力奶酪90g-中国',
        '口力比萨小包60g-中国', '口力比萨中包80g-中国', '口力比萨大包100g-中国',
        '口力薯条65g-中国', '口力鸡块75g-中国', '口力汉堡圈85g-中国',
        '口力德果汉堡108g-中国'
    ]

    # 产品规格
    product_specs = [
        '68g*24', '120g*24', '108g*24', '100g*24', '105g*24', '77g*24',
        '137g*24', '120g*24', '90g*24', '60g*24', '80g*24', '100g*24',
        '65g*24', '75g*24', '85g*24', '108g*24'
    ]

    # 创建DataFrame
    data = {'产品代码': product_codes,
            '产品名称': product_names,
            '产品规格': product_specs}

    df = pd.DataFrame(data)

    # 添加简化产品名称列
    df['简化产品名称'] = df.apply(lambda row: simplify_product_name(row['产品代码'], row['产品名称']), axis=1)

    return df


# 产品代码映射函数 - 优化使用简化名称
def format_product_code(code, product_info_df, include_name=True):
    """将产品代码格式化为只显示简化名称，不显示代码"""
    if product_info_df is None or code not in product_info_df['产品代码'].values:
        return code

    if include_name:
        # 仅使用简化名称，不包含代码
        filtered_df = product_info_df[product_info_df['产品代码'] == code]
        if not filtered_df.empty and '简化产品名称' in filtered_df.columns:
            simplified_name = filtered_df['简化产品名称'].iloc[0]
            if not pd.isna(simplified_name) and simplified_name:
                # 移除代码部分，只保留简化产品名称部分
                return simplified_name.replace(code, "").strip()

        # 回退到只显示产品名称，不显示代码
        product_name = filtered_df['产品名称'].iloc[0]
        return product_name
    else:
        return code


@st.cache_data
def load_batch_inventory(file_path=None):
    """加载批次库存数据"""
    try:
        # 默认路径或示例数据
        if file_path is None or not os.path.exists(file_path):
            # 创建示例数据
            return create_sample_batch_inventory()

        # 加载数据
        inventory_raw = pd.read_excel(file_path, header=0)

        # 处理第一层数据（产品信息）
        product_rows = inventory_raw[inventory_raw.iloc[:, 0].notna()]
        inventory_data = product_rows.iloc[:, :7].copy()
        inventory_data.columns = ['产品代码', '描述', '现有库存', '已分配量',
                                  '现有库存可订量', '待入库量', '本月剩余可订量']

        # 处理第二层数据（批次信息）
        batch_with_product = []

        product_code = None
        product_description = None

        for i, row in inventory_raw.iterrows():
            if pd.notna(row.iloc[0]):
                # 这是产品行
                product_code = row.iloc[0]
                product_description = row.iloc[1]  # 获取产品描述
            elif pd.notna(row.iloc[7]):
                # 这是批次行
                batch_row = row.iloc[7:].copy()
                batch_row_with_product = pd.Series([product_code, product_description] + batch_row.tolist())
                batch_with_product.append(batch_row_with_product)

        batch_data = pd.DataFrame(batch_with_product)
        batch_data.columns = ['产品代码', '描述', '库位', '生产日期', '生产批号', '数量']

        # 转换日期列
        batch_data['生产日期'] = pd.to_datetime(batch_data['生产日期'])

        return batch_data

    except Exception as e:
        st.error(f"加载批次库存数据时出错: {str(e)}。使用示例数据进行演示。")
        return create_sample_batch_inventory()


def create_sample_batch_inventory():
    """创建示例批次库存数据"""
    # 产品代码列表
    product_codes = [
        'F0104L', 'F01E4P', 'F01E6C', 'F3406B', 'F3409N', 'F3411A',
        'F01E4B', 'F0183F', 'F0110C', 'F0104J', 'F0104M', 'F0104P',
        'F0110A', 'F0110B', 'F0115C', 'F0101P'
    ]

    # 产品描述列表
    product_descriptions = [
        '口力比萨68克袋装-中国', '口力汉堡大袋120g-中国', '口力汉堡中袋108g-中国',
        '口力海洋动物100g-中国', '口力幻彩蜥蜴105g-中国', '口力午餐袋77g-中国',
        '口力汉堡137g-中国', '口力热狗120g-中国', '口力奶酪90g-中国',
        '口力比萨小包60g-中国', '口力比萨中包80g-中国', '口力比萨大包100g-中国',
        '口力薯条65g-中国', '口力鸡块75g-中国', '口力汉堡圈85g-中国',
        '口力德果汉堡108g-中国'
    ]

    # 批次数量范围
    batch_qty_range = (50, 1000)

    # 生成随机批次数据
    today = datetime.now()
    batch_data = []

    for i in range(30):  # 生成30个批次
        product_idx = np.random.randint(0, len(product_codes))
        product_code = product_codes[product_idx]
        product_description = product_descriptions[product_idx]

        # 随机生成批次日期 (15-200天前)
        days_ago = np.random.randint(15, 200)
        batch_date = today - timedelta(days=days_ago)

        # 随机生成批次号
        batch_number = f"LOT{np.random.randint(10000, 99999)}"

        # 随机生成库位
        warehouse = f"WH{np.random.randint(1, 10)}"

        # 随机生成数量
        quantity = np.random.randint(batch_qty_range[0], batch_qty_range[1])

        batch_data.append({
            '产品代码': product_code,
            '描述': product_description,
            '库位': warehouse,
            '生产日期': batch_date,
            '生产批号': batch_number,
            '数量': quantity
        })

    return pd.DataFrame(batch_data)


@st.cache_data
def load_actual_data(file_path=None):
    """加载实际销售数据"""
    try:
        # 默认路径或示例数据
        if file_path is None or not os.path.exists(file_path):
            # 创建示例数据
            return load_sample_actual_data()

        # 加载数据
        df = pd.read_excel(file_path)

        # 确保列名格式一致
        required_columns = ['订单日期', '所属区域', '申请人', '产品代码', '求和项:数量（箱）']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.error(f"实际销售数据文件缺少必要的列: {', '.join(missing_columns)}。使用示例数据进行演示。")
            return load_sample_actual_data()

        # 确保数据类型正确
        df['订单日期'] = pd.to_datetime(df['订单日期'])
        df['所属区域'] = df['所属区域'].astype(str)
        df['申请人'] = df['申请人'].astype(str)
        df['产品代码'] = df['产品代码'].astype(str)
        df['求和项:数量（箱）'] = pd.to_numeric(df['求和项:数量（箱）'], errors='coerce')

        # 创建年月字段，用于与预测数据对齐
        df['所属年月'] = df['订单日期'].dt.strftime('%Y-%m')

        return df

    except Exception as e:
        st.error(f"加载实际销售数据时出错: {str(e)}。使用示例数据进行演示。")
        return load_sample_actual_data()


@st.cache_data
def load_forecast_data(file_path=None):
    """加载预测数据"""
    try:
        # 默认路径或示例数据
        if file_path is None or not os.path.exists(file_path):
            # 创建示例数据
            return load_sample_forecast_data()

        # 加载数据
        df = pd.read_excel(file_path)

        # 确保列名格式一致
        required_columns = ['所属大区', '销售员', '所属年月', '产品代码', '预计销售量']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.error(f"预测数据文件缺少必要的列: {', '.join(missing_columns)}。使用示例数据进行演示。")
            return load_sample_forecast_data()

        # 确保数据类型正确
        df['所属大区'] = df['所属大区'].astype(str)
        df['销售员'] = df['销售员'].astype(str)
        df['所属年月'] = pd.to_datetime(df['所属年月']).dt.strftime('%Y-%m')
        df['产品代码'] = df['产品代码'].astype(str)
        df['预计销售量'] = pd.to_numeric(df['预计销售量'], errors='coerce')

        # 为了保持一致，将'所属大区'列重命名为'所属区域'
        df = df.rename(columns={'所属大区': '所属区域'})

        return df

    except Exception as e:
        st.error(f"加载预测数据时出错: {str(e)}。使用示例数据进行演示。")
        return load_sample_forecast_data()


# 示例数据创建函数
def load_sample_actual_data():
    """创建示例实际销售数据"""
    # 产品代码列表
    product_codes = [
        'F0104L', 'F01E4P', 'F01E6C', 'F3406B', 'F3409N', 'F3411A',
        'F01E4B', 'F0183F', 'F0110C', 'F0104J', 'F0104M', 'F0104P',
        'F0110A', 'F0110B', 'F0115C', 'F0101P'
    ]

    # 区域列表
    regions = ['北', '南', '东', '西']

    # 申请人列表
    applicants = ['孙杨', '李根', '张伟', '王芳', '刘涛', '陈明']

    # 生成日期范围
    start_date = datetime(2023, 9, 1)
    end_date = datetime(2025, 2, 24)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')

    # 创建数据
    data = []
    for date in date_range:
        # 为每天生成随机数量的记录
        num_records = np.random.randint(3, 10)

        for _ in range(num_records):
            region = np.random.choice(regions)
            applicant = np.random.choice(applicants)
            product_code = np.random.choice(product_codes)
            quantity = np.random.randint(5, 300)

            data.append({
                '订单日期': date,
                '所属区域': region,
                '申请人': applicant,
                '产品代码': product_code,
                '求和项:数量（箱）': quantity
            })

    # 创建DataFrame
    df = pd.DataFrame(data)

    # 添加年月字段
    df['所属年月'] = df['订单日期'].dt.strftime('%Y-%m')

    return df


def load_sample_forecast_data():
    """创建示例预测数据"""
    # 产品代码列表
    product_codes = [
        'F0104L', 'F01E4P', 'F01E6C', 'F3406B', 'F3409N', 'F3411A',
        'F01E4B', 'F0183F', 'F0110C', 'F0104J', 'F0104M', 'F0104P',
        'F0110A', 'F0110B', 'F0115C', 'F0101P'
    ]

    # 区域列表
    regions = ['北', '南', '东', '西']

    # 销售员列表
    sales_people = ['李根', '张伟', '王芳', '刘涛', '陈明', '孙杨']

    # 生成月份范围
    start_date = datetime(2023, 9, 1)
    end_date = datetime(2025, 2, 1)
    month_range = pd.date_range(start=start_date, end=end_date, freq='MS')

    # 创建数据
    data = []
    for month in month_range:
        month_str = month.strftime('%Y-%m')

        for region in regions:
            for sales_person in sales_people:
                for product_code in product_codes:
                    # 使用正态分布生成预测值，使其变化更自然
                    forecast = max(0, np.random.normal(150, 50))

                    # 有些产品可能没有预测
                    if np.random.random() > 0.1:  # 90%的概率有预测
                        data.append({
                            '所属大区': region,
                            '销售员': sales_person,
                            '所属年月': month_str,
                            '产品代码': product_code,
                            '预计销售量': round(forecast)
                        })

    # 创建DataFrame
    df = pd.DataFrame(data)
    return df


@st.cache_data
def load_price_data(file_path=None):
    """加载产品单价数据"""
    # 指定的产品单价信息
    default_prices = {
        'F01E4B': 137.04,
        'F3411A': 137.04,
        'F0104L': 126.72,
        'F3406B': 129.36,
        'F01C5D': 153.6,
        'F01L3A': 182.4,
        'F01L6A': 307.2,
        'F01A3C': 175.5,
        'F01H2B': 307.2,
        'F01L4A': 182.4,
        'F0104J': 216.96,
        'F0101P': 119.76,
        'F01E4P': 144.0,
        'F01E6C': 129.6,
        'F3409N': 126.0,
        'F0183F': 144.0,
        'F0110C': 108.0,
        'F0104M': 96.0,
        'F0104P': 120.0,
        'F0110A': 78.0,
        'F0110B': 90.0,
        'F0115C': 102.0
    }

    try:
        if file_path and os.path.exists(file_path):
            price_df = pd.read_excel(file_path)
            price_data = {}

            for _, row in price_df.iterrows():
                price_data[row['产品代码']] = row['单价']

            # 合并自定义价格和默认价格
            all_prices = {**default_prices, **price_data}
            return all_prices
        else:
            return default_prices

    except Exception as e:
        st.warning(f"单价数据加载失败: {str(e)}，使用默认单价")
        return default_prices


def get_common_months(actual_df, forecast_df):
    """获取两个数据集共有的月份"""
    actual_months = set(actual_df['所属年月'].unique())
    forecast_months = set(forecast_df['所属年月'].unique())
    common_months = sorted(list(actual_months.intersection(forecast_months)))
    return common_months


# 获取最近3个月的函数
def get_last_three_months():
    today = datetime.now()
    current_month = today.replace(day=1)

    last_month = current_month - timedelta(days=1)
    last_month = last_month.replace(day=1)

    two_months_ago = last_month - timedelta(days=1)
    two_months_ago = two_months_ago.replace(day=1)

    months = []
    for dt in [two_months_ago, last_month, current_month]:
        months.append(dt.strftime('%Y-%m'))

    return months


# 统一的数据筛选函数
def filter_data(data, months=None, regions=None):
    """统一的数据筛选函数"""
    filtered_data = data.copy()

    if months and len(months) > 0:
        filtered_data = filtered_data[filtered_data['所属年月'].isin(months)]

    if regions and len(regions) > 0:
        filtered_data = filtered_data[filtered_data['所属区域'].isin(regions)]

    return filtered_data


# 数据处理和分析函数
def process_data(actual_df, forecast_df, product_info_df):
    """处理数据并计算关键指标"""
    # 按月份、区域、产品码汇总数据
    actual_monthly = actual_df.groupby(['所属年月', '所属区域', '产品代码']).agg({
        '求和项:数量（箱）': 'sum'
    }).reset_index()

    forecast_monthly = forecast_df.groupby(['所属年月', '所属区域', '产品代码']).agg({
        '预计销售量': 'sum'
    }).reset_index()

    # 按销售员细分的预测数据
    forecast_by_salesperson = forecast_df.groupby(['所属年月', '所属区域', '销售员', '产品代码']).agg({
        '预计销售量': 'sum'
    }).reset_index()

    # 实际按销售员细分的数据
    actual_by_salesperson = actual_df.groupby(['所属年月', '所属区域', '申请人', '产品代码']).agg({
        '求和项:数量（箱）': 'sum'
    }).reset_index()

    # 重命名列，使合并更容易
    actual_by_salesperson = actual_by_salesperson.rename(columns={'申请人': '销售员'})

    # 合并预测和实际数据
    # 按区域和产品级别
    merged_monthly = pd.merge(
        actual_monthly,
        forecast_monthly,
        on=['所属年月', '所属区域', '产品代码'],
        how='outer'
    )

    # 按销售员级别
    merged_by_salesperson = pd.merge(
        actual_by_salesperson,
        forecast_by_salesperson,
        on=['所属年月', '所属区域', '销售员', '产品代码'],
        how='outer'
    )

    # 填充缺失值为0
    for df in [merged_monthly, merged_by_salesperson]:
        df['求和项:数量（箱）'] = df['求和项:数量（箱）'].fillna(0)
        df['预计销售量'] = df['预计销售量'].fillna(0)

    # 计算差异和准确率
    for df in [merged_monthly, merged_by_salesperson]:
        # 差异
        df['数量差异'] = df['求和项:数量（箱）'] - df['预计销售量']

        # 差异率 (避免除以零)
        df['数量差异率'] = np.where(
            df['求和项:数量（箱）'] > 0,
            df['数量差异'] / df['求和项:数量（箱）'] * 100,
            np.where(
                df['预计销售量'] > 0,
                -100,  # 预测有值但实际为0
                0  # 预测和实际都是0
            )
        )

        # 准确率
        df['数量准确率'] = np.where(
            (df['求和项:数量（箱）'] > 0) | (df['预计销售量'] > 0),
            np.maximum(0, 100 - np.abs(df['数量差异率'])) / 100,
            1  # 预测和实际都是0时准确率为100%
        )

    # 计算总体准确率
    national_accuracy = calculate_national_accuracy(merged_monthly)
    regional_accuracy = calculate_regional_accuracy(merged_monthly)

    # 计算占比80%的SKU
    national_top_skus = calculate_top_skus(merged_monthly, by_region=False)
    regional_top_skus = calculate_top_skus(merged_monthly, by_region=True)

    return {
        'actual_monthly': actual_monthly,
        'forecast_monthly': forecast_monthly,
        'merged_monthly': merged_monthly,
        'merged_by_salesperson': merged_by_salesperson,
        'national_accuracy': national_accuracy,
        'regional_accuracy': regional_accuracy,
        'national_top_skus': national_top_skus,
        'regional_top_skus': regional_top_skus
    }


def calculate_national_accuracy(merged_df):
    """计算全国的预测准确率"""
    # 按月份汇总
    monthly_summary = merged_df.groupby('所属年月').agg({
        '求和项:数量（箱）': 'sum',
        '预计销售量': 'sum'
    }).reset_index()

    # 计算差异
    monthly_summary['数量差异'] = monthly_summary['求和项:数量（箱）'] - monthly_summary['预计销售量']

    # 使用统一函数计算准确率
    monthly_summary['数量准确率'] = monthly_summary.apply(
        lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
        axis=1
    )

    # 计算整体平均准确率 (使用安全均值计算)
    overall = {
        '数量准确率': safe_mean(monthly_summary['数量准确率'], 0)
    }

    return {
        'monthly': monthly_summary,
        'overall': overall
    }


def calculate_regional_accuracy(merged_df):
    """计算各区域的预测准确率"""
    # 按月份和区域汇总
    region_monthly_summary = merged_df.groupby(['所属年月', '所属区域']).agg({
        '求和项:数量（箱）': 'sum',
        '预计销售量': 'sum'
    }).reset_index()

    # 计算差异
    region_monthly_summary['数量差异'] = region_monthly_summary['求和项:数量（箱）'] - region_monthly_summary[
        '预计销售量']

    # 使用统一函数计算准确率
    region_monthly_summary['数量准确率'] = region_monthly_summary.apply(
        lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
        axis=1
    )

    # 按区域计算平均准确率 (使用安全均值计算)
    region_overall = region_monthly_summary.groupby('所属区域').agg({
        '数量准确率': lambda x: safe_mean(x, 0)
    }).reset_index()

    return {
        'region_monthly': region_monthly_summary,
        'region_overall': region_overall
    }


@st.cache_data
# 替换现有的calculate_product_growth函数
def calculate_product_growth(actual_monthly, regions=None, months=None, growth_min=-100, growth_max=500):
    """
    计算产品销量增长率，用于生成备货建议

    计算逻辑：
    1. 优先计算同比增长率：当前月与去年同月比较
    2. 若无同比数据，则计算环比增长率：当前月与上月比较
    3. 根据增长率给出备货建议

    参数:
    - actual_monthly: 实际销售数据
    - regions: 区域筛选
    - months: 月份筛选
    - growth_min/max: 增长率异常值截断范围

    返回:
    - all_growth: 所有产品增长率数据
    - latest_growth: 最新月份的增长率数据，包含趋势与备货建议
    """
    # 确保数据按时间排序
    actual_monthly['所属年月'] = pd.to_datetime(actual_monthly['所属年月'])
    actual_monthly = actual_monthly.sort_values('所属年月')

    # 应用区域筛选
    if regions and len(regions) > 0:
        filtered_data = actual_monthly[actual_monthly['所属区域'].isin(regions)]
    else:
        filtered_data = actual_monthly  # 如果没有区域筛选，使用全部数据

    # 应用月份筛选
    if months and len(months) > 0:
        months_datetime = pd.to_datetime(months)
        filtered_data = filtered_data[filtered_data['所属年月'].isin(months_datetime)]

    # 按产品和月份汇总筛选后的区域销量
    filtered_monthly_sales = filtered_data.groupby(['所属年月', '产品代码']).agg({
        '求和项:数量（箱）': 'sum'
    }).reset_index()

    # 创建年和月字段
    filtered_monthly_sales['年'] = filtered_monthly_sales['所属年月'].dt.year
    filtered_monthly_sales['月'] = filtered_monthly_sales['所属年月'].dt.month

    # 准备用于计算增长率的数据结构
    growth_data = []

    # 获取所有产品的唯一列表
    products = filtered_monthly_sales['产品代码'].unique()

    # 获取所有年份和月份
    years = filtered_monthly_sales['年'].unique()
    years.sort()

    # 检查是否有足够的数据进行增长率计算
    if len(filtered_monthly_sales) > 0:
        # 为每个产品计算月度增长率
        for product in products:
            product_data = filtered_monthly_sales[filtered_monthly_sales['产品代码'] == product]

            # 按年月对产品销量进行排序
            product_data = product_data.sort_values(['年', '月'])

            # 如果产品有多个月的数据，计算环比增长率（与上月相比）
            if len(product_data) > 1:
                for i in range(1, len(product_data)):
                    current_row = product_data.iloc[i]
                    prev_row = product_data.iloc[i - 1]

                    # 计算当前月环比增长率
                    current_sales = current_row['求和项:数量（箱）']
                    prev_sales = prev_row['求和项:数量（箱）']

                    if prev_sales > 0:
                        growth_rate = (current_sales - prev_sales) / prev_sales * 100
                        # 限制异常值
                        growth_rate = max(min(growth_rate, growth_max), growth_min)
                    else:
                        growth_rate = 0 if current_sales == 0 else 100

                    # 记录环比增长率数据
                    growth_data.append({
                        '产品代码': product,
                        '年': current_row['年'],
                        '月': current_row['月'],
                        '当月销量': current_sales,
                        '上月销量': prev_sales,
                        '销量增长率': growth_rate,
                        '计算方式': '环比'  # 标记为环比计算
                    })

            # 尝试计算同期同比增长率（如果有前一年的数据）- 优先使用同比数据
            if len(years) > 1:
                for year in years[1:]:  # 从第二年开始
                    prev_year = year - 1

                    # 获取当前年和前一年的数据
                    current_year_data = product_data[product_data['年'] == year]
                    prev_year_data = product_data[product_data['年'] == prev_year]

                    # 为每个月计算同比增长率
                    for _, curr_row in current_year_data.iterrows():
                        curr_month = curr_row['月']
                        curr_sales = curr_row['求和项:数量（箱）']

                        # 寻找前一年同月数据
                        prev_month_data = prev_year_data[prev_year_data['月'] == curr_month]

                        if not prev_month_data.empty:
                            prev_sales = prev_month_data.iloc[0]['求和项:数量（箱）']

                            if prev_sales > 0:
                                yoy_growth_rate = (curr_sales - prev_sales) / prev_sales * 100
                                # 限制异常值
                                yoy_growth_rate = max(min(yoy_growth_rate, growth_max), growth_min)
                            else:
                                yoy_growth_rate = 0 if curr_sales == 0 else 100

                            # 记录同比增长率
                            # 优先使用同比数据（替换之前的环比数据，如果存在）
                            existing_entry = next((item for item in growth_data if
                                                   item['产品代码'] == product and
                                                   item['年'] == year and
                                                   item['月'] == curr_month), None)

                            if existing_entry:
                                existing_entry['销量增长率'] = yoy_growth_rate
                                existing_entry['同比上年销量'] = prev_sales
                                existing_entry['计算方式'] = '同比'  # 更新为同比计算
                            else:
                                growth_data.append({
                                    '产品代码': product,
                                    '年': year,
                                    '月': curr_month,
                                    '当月销量': curr_sales,
                                    '同比上年销量': prev_sales,
                                    '销量增长率': yoy_growth_rate,
                                    '计算方式': '同比'  # 标记为同比计算
                                })

    # 创建增长率DataFrame
    growth_df = pd.DataFrame(growth_data)

    # 如果有增长数据，添加趋势判断和备货建议
    if not growth_df.empty:
        try:
            # 取最近一个月的增长率
            latest_growth = growth_df.sort_values(['年', '月'], ascending=False).groupby(
                '产品代码').first().reset_index()

            # 过滤无效增长率值
            latest_growth = latest_growth[latest_growth['销量增长率'].notna()]
            latest_growth = latest_growth[np.isfinite(latest_growth['销量增长率'])]

            if not latest_growth.empty:
                # 添加趋势判断
                latest_growth['趋势'] = np.where(
                    latest_growth['销量增长率'] > 10, '强劲增长',
                    np.where(
                        latest_growth['销量增长率'] > 0, '增长',
                        np.where(
                            latest_growth['销量增长率'] > -10, '轻微下降',
                            '显著下降'
                        )
                    )
                )

                # 添加备货建议
                latest_growth['备货建议对象'] = latest_growth['销量增长率'].apply(generate_recommendation)
                latest_growth['备货建议'] = latest_growth['备货建议对象'].apply(lambda x: x['建议'])
                latest_growth['调整比例'] = latest_growth['备货建议对象'].apply(lambda x: x['调整比例'])
                latest_growth['建议颜色'] = latest_growth['备货建议对象'].apply(lambda x: x['颜色'])
                latest_growth['建议样式类'] = latest_growth['备货建议对象'].apply(lambda x: x['样式类'])
                latest_growth['建议图标'] = latest_growth['备货建议对象'].apply(lambda x: x['图标'])
            else:
                # 创建空的结果框架
                latest_growth = pd.DataFrame(columns=growth_df.columns)
        except Exception as e:
            # 记录错误但继续执行
            print(f"处理增长率数据时出错: {str(e)}")
            latest_growth = pd.DataFrame(columns=growth_df.columns)

        return {
            'all_growth': growth_df,
            'latest_growth': latest_growth
        }
    else:
        return {
            'all_growth': pd.DataFrame(),
            'latest_growth': pd.DataFrame()
        }


# 替换现有的calculate_top_skus函数
def calculate_top_skus(merged_df, by_region=False):
    """计算占销售量80%的SKU及其准确率 - 修复空区域问题"""
    if merged_df.empty:
        return {} if by_region else pd.DataFrame()

    if by_region:
        # 按区域、产品汇总
        grouped = merged_df.groupby(['所属区域', '产品代码']).agg({
            '求和项:数量（箱）': 'sum',
            '预计销售量': 'sum'
        }).reset_index()

        # 计算准确率
        grouped['数量准确率'] = grouped.apply(
            lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
            axis=1
        )

        # 计算各区域的占比80%SKU
        results = {}
        for region in grouped['所属区域'].unique():
            if pd.isna(region) or region is None or region == 'None':
                continue  # 跳过空区域

            region_data = grouped[grouped['所属区域'] == region].copy()
            if region_data.empty:
                continue  # 跳过没有数据的区域

            total_sales = region_data['求和项:数量（箱）'].sum()
            if total_sales <= 0:
                continue  # 跳过销售量为0的区域

            # 按销售量降序排序
            region_data = region_data.sort_values('求和项:数量（箱）', ascending=False)

            # 计算累计销售量和占比
            region_data['累计销售量'] = region_data['求和项:数量（箱）'].cumsum()
            region_data['累计占比'] = region_data['累计销售量'] / total_sales * 100

            # 筛选占比80%的SKU
            top_skus = region_data[region_data['累计占比'] <= 80].copy()

            # 如果没有SKU达到80%阈值，至少取前3个SKU
            if top_skus.empty:
                top_skus = region_data.head(min(3, len(region_data)))

            results[region] = top_skus

        return results
    else:
        # 全国汇总
        grouped = merged_df.groupby('产品代码').agg({
            '求和项:数量（箱）': 'sum',
            '预计销售量': 'sum'
        }).reset_index()

        # 计算准确率
        grouped['数量准确率'] = grouped.apply(
            lambda row: calculate_unified_accuracy(row['求和项:数量（箱）'], row['预计销售量']),
            axis=1
        )

        total_sales = grouped['求和项:数量（箱）'].sum()
        if total_sales <= 0:
            return pd.DataFrame(columns=grouped.columns)  # 返回空DataFrame但保持列结构

        # 按销售量降序排序
        grouped = grouped.sort_values('求和项:数量（箱）', ascending=False)

        # 计算累计销售量和占比 - 这里修复了列名不匹配的错误
        grouped['累计销售量'] = grouped['求和项:数量（箱）'].cumsum()
        grouped['累计占比'] = grouped['累计销售量'] / total_sales * 100  # 修改这里，使用"累计销售量"而不是"累计销量"

        # 筛选占比80%的SKU
        top_skus = grouped[grouped['累计占比'] <= 80].copy()

        # 如果没有SKU达到80%阈值，至少取前5个SKU
        if top_skus.empty:
            top_skus = grouped.head(min(5, len(grouped)))

        return top_skus


# 图表分页器组件
def display_chart_paginator(df, chart_function, page_size, title, key_prefix):
    """创建图表分页器"""
    total_items = len(df)
    total_pages = (total_items + page_size - 1) // page_size

    if f"{key_prefix}_current_page" not in st.session_state:
        st.session_state[f"{key_prefix}_current_page"] = 0

    # 创建分页控制
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        if st.button("上一页", key=f"{key_prefix}_prev", disabled=st.session_state[f"{key_prefix}_current_page"] <= 0):
            st.session_state[f"{key_prefix}_current_page"] -= 1
            st.rerun()

    with col2:
        st.markdown(
            f"<div style='text-align:center' class='pagination-info'>第 {st.session_state[f'{key_prefix}_current_page'] + 1} 页，共 {total_pages} 页</div>",
            unsafe_allow_html=True)

    with col3:
        if st.button("下一页", key=f"{key_prefix}_next",
                     disabled=st.session_state[f"{key_prefix}_current_page"] >= total_pages - 1):
            st.session_state[f"{key_prefix}_current_page"] += 1
            st.rerun()

    # 确保当前页在有效范围内
    if st.session_state[f"{key_prefix}_current_page"] >= total_pages:
        st.session_state[f"{key_prefix}_current_page"] = total_pages - 1
    if st.session_state[f"{key_prefix}_current_page"] < 0:
        st.session_state[f"{key_prefix}_current_page"] = 0

    # 获取当前页的数据
    start_idx = st.session_state[f"{key_prefix}_current_page"] * page_size
    end_idx = min(start_idx + page_size, total_items)
    page_data = df.iloc[start_idx:end_idx]

    # 显示图表
    chart_function(page_data, title)


# 创建通用图表函数
def create_chart(chart_type, data, x, y, title, color=None, orientation='v', text=None, **kwargs):
    """通用图表创建函数"""
    if chart_type == 'bar':
        fig = px.bar(data, x=x, y=y, color=color, orientation=orientation, text=text, title=title, **kwargs)
    elif chart_type == 'line':
        fig = px.line(data, x=x, y=y, color=color, title=title, **kwargs)
    elif chart_type == 'scatter':
        fig = px.scatter(data, x=x, y=y, color=color, title=title, **kwargs)
    else:
        fig = go.Figure()
        st.warning(f"未支持的图表类型: {chart_type}")

    # 通用样式设置
    fig.update_layout(
        title_font=dict(size=16),
        xaxis_title_font=dict(size=14),
        yaxis_title_font=dict(size=14),
        legend_title_font=dict(size=14),
        plot_bgcolor='white'  # 设置白色背景
    )

    # 添加数字格式设置
    if orientation == 'v' and x is not None:
        fig.update_layout(
            xaxis=dict(
                tickformat=",",  # 使用逗号分隔
                showexponent="none"  # 不使用科学计数法
            )
        )
    elif orientation == 'h' and y is not None:
        fig.update_layout(
            yaxis=dict(
                tickformat=",",  # 使用逗号分隔
                showexponent="none"  # 不使用科学计数法
            )
        )

    return fig


# 创建带备货建议的增长率图表
def plot_growth_with_recommendations(data, title):
    """创建带有内置备货建议的增长率图表 - 优化视觉效果"""
    if data.empty:
        st.warning("没有足够的数据来生成增长率图表。")
        return None

    # 确保数据中有备货建议
    if '备货建议对象' not in data.columns:
        data['备货建议对象'] = data['销量增长率'].apply(generate_recommendation)
        data['备货建议'] = data['备货建议对象'].apply(lambda x: x['建议'])
        data['调整比例'] = data['备货建议对象'].apply(lambda x: x['调整比例'])
        data['建议颜色'] = data['备货建议对象'].apply(lambda x: x['颜色'])
        data['建议图标'] = data['备货建议对象'].apply(lambda x: x['图标'])

    # 准备显示文本
    data['显示文本'] = data.apply(
        lambda row: f"{row['销量增长率']:.1f}% {row['建议图标']}",
        axis=1
    )

    # 创建图表 - 优化颜色方案
    fig = px.bar(
        data,
        y='产品显示',
        x='销量增长率',
        color='趋势',
        title=title,
        text='显示文本',
        orientation='h',
        color_discrete_map={
            '强劲增长': '#1E88E5',  # 深蓝色
            '增长': '#43A047',  # 绿色
            '轻微下降': '#FB8C00',  # 橙色
            '显著下降': '#E53935'  # 红色
        }
    )

    # 更新布局 - 改进视觉效果
    fig.update_layout(
        yaxis_title="产品",
        xaxis_title="增长率 (%)",
        xaxis=dict(tickformat=",", showexponent="none"),
        plot_bgcolor='white',
        margin=dict(l=10, r=10, t=50, b=10)
    )

    # 添加参考线
    fig.add_shape(
        type="line",
        y0=-0.5,
        y1=len(data) - 0.5,
        x0=0,
        x1=0,
        line=dict(color="black", width=1, dash="dash")
    )

    # 优化悬停提示
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>增长率: %{x:.2f}%<br>建议: %{customdata[0]}<br>调整比例: %{customdata[1]}%<extra></extra>',
        customdata=data[['备货建议', '调整比例']].values
    )

    # 改进条形图样式
    fig.update_traces(
        marker_line_width=0.5,
        marker_line_color="white",
        opacity=0.9
    )

    return fig


# 创建优化的散点图/气泡图
def create_improved_scatter(data, x, y, size, color, title, hover_name=None):
    """创建优化的散点/气泡图"""
    # 计算最佳气泡大小范围
    if data[size].max() > 0:
        size_max = min(30, max(15, 30 * data[size].quantile(0.9) / data[size].max()))
    else:
        size_max = 15

    # 创建图表
    fig = px.scatter(
        data,
        x=x,
        y=y,
        size=size,
        color=color,
        hover_name=hover_name if hover_name else None,
        size_max=size_max,  # 动态调整最大气泡大小
        opacity=0.75,  # 增加透明度减少视觉拥挤
        title=title,
        color_discrete_map={
            '强劲增长': '#1E88E5',  # 深蓝色
            '增长': '#43A047',  # 绿色
            '轻微下降': '#FB8C00',  # 橙色
            '显著下降': '#E53935'  # 红色
        }
    )

    # 增强布局
    fig.update_layout(
        plot_bgcolor='white',
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5
        )
    )

    # 改进轴线和网格
    fig.update_xaxes(
        title=f"{x} (箱)",
        showgrid=True,
        gridwidth=0.5,
        gridcolor='rgba(220,220,220,0.5)',
        tickformat=",",  # 使用逗号分隔
        showexponent="none"  # 不使用科学计数法
    )
    fig.update_yaxes(
        title=f"{y} (%)",
        showgrid=True,
        gridwidth=0.5,
        gridcolor='rgba(220,220,220,0.5)'
    )

    # 优化散点样式
    fig.update_traces(
        marker=dict(
            line=dict(width=1, color='white')
        ),
        hovertemplate='<b>%{hovertext}</b><br>销售量: %{x:,.0f}箱<br>增长率: %{y:.2f}%<br>趋势: %{marker.color}<br>建议: %{customdata}<extra></extra>'
    )

    # 添加零线
    fig.add_shape(
        type="line",
        x0=data[x].min() * 0.9,
        x1=data[x].max() * 1.1,
        y0=0,
        y1=0,
        line=dict(color="black", width=1, dash="dash")
    )

    return fig


# 替换现有的display_recommendations_table函数
# 替换现有的display_recommendations_table函数
def display_recommendations_table(latest_growth, product_info):
    """显示产品增长率和备货建议的图表"""
    if latest_growth.empty:
        st.warning("没有足够的数据来生成备货建议图表。")
        return

    # 确保数据中包含必要的列
    if '产品代码' not in latest_growth.columns:
        st.error("数据中缺少产品代码列。")
        return

    # 创建一个副本以避免修改原始数据
    display_data = latest_growth.copy()

    # 添加产品显示名称（如果尚未存在）
    if '产品显示' not in display_data.columns:
        display_data['产品显示'] = display_data.apply(
            lambda row: format_product_code(row['产品代码'], product_info, include_name=True),
            axis=1
        )

    # 按增长率降序排序
    display_data = display_data.sort_values('销量增长率', ascending=False)

    # 显示图表标题和说明
    st.markdown("### 产品备货建议一览")
    st.markdown("""
    <div style="margin-bottom: 1rem; padding: 0.9rem; background-color: rgba(76, 175, 80, 0.1); border-radius: 0.5rem; border-left: 0.5rem solid #4CAF50;">
        <p style="margin: 0; font-size: 0.9rem;">
            <b>图表说明</b>：展示了产品销量的增长趋势与备货建议。计算方法：优先使用同比增长率（当前月份与去年同期相比），如无同期数据则使用环比增长率（与前一月相比）。
            颜色区分了不同趋势：深蓝色表示强劲增长(>10%)，绿色表示增长(0-10%)，橙色表示轻微下降(-10-0%)，红色表示显著下降(<-10%)。
            悬停可查看详细的备货建议和调整幅度。
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 创建趋势的颜色映射
    color_map = {
        '强劲增长': '#1E88E5',  # 深蓝色
        '增长': '#43A047',  # 绿色
        '轻微下降': '#FB8C00',  # 橙色
        '显著下降': '#E53935'  # 红色
    }

    # 准备自定义数据用于悬停提示 - 修复乱码问题和键错误
    custom_data = []
    for _, row in display_data.iterrows():
        # 将所有数值转为字符串，避免格式问题
        # 使用'当月销量'替代'3个月滚动销量'
        sales_value = "0"
        if '当月销量' in row and pd.notna(row['当月销量']):
            sales_value = str(int(row['当月销量']))

        trend = str(row['趋势']) if pd.notna(row['趋势']) else ""
        recommendation = str(row['备货建议']) if pd.notna(row['备货建议']) else ""
        adjust_pct = str(int(row['调整比例'])) + "%" if pd.notna(row['调整比例']) else "0%"
        icon = str(row.get('建议图标', '')) if pd.notna(row.get('建议图标', '')) else ""

        custom_data.append([sales_value, trend, recommendation, adjust_pct, icon])

    # 创建水平条形图
    fig = go.Figure()

    # 添加条形图
    fig.add_trace(go.Bar(
        y=display_data['产品显示'],
        x=display_data['销量增长率'],
        orientation='h',
        marker=dict(
            color=[color_map.get(trend, '#1f3867') for trend in display_data['趋势']],
            line=dict(width=0)
        ),
        customdata=custom_data,
        hovertemplate='<b>%{y}</b><br>' +
                      '增长率: %{x:.1f}%<br>' +
                      '当前销量: %{customdata[0]}箱<br>' +  # 修改悬停信息
                      '趋势: %{customdata[1]}<br>' +
                      '备货建议: %{customdata[2]} %{customdata[4]}<br>' +
                      '调整幅度: %{customdata[3]}<extra></extra>'
    ))

    # 添加零线
    fig.add_shape(
        type="line",
        x0=0,
        x1=0,
        y0=-0.5,
        y1=len(display_data) - 0.5,
        line=dict(color="black", width=1, dash="dash")
    )

    # 更新布局 - 修改图例位置到图表上方
    fig.update_layout(
        title="产品销量增长率与备货建议",
        xaxis=dict(
            title="增长率 (%)",
            zeroline=False
        ),
        yaxis=dict(
            title="产品",
            autorange="reversed"  # 将最高增长率的产品放在顶部
        ),
        height=max(500, len(display_data) * 30),  # 动态调整高度以适应产品数量
        margin=dict(l=10, r=10, t=100, b=10),  # 增加上边距为图例留出空间
        plot_bgcolor='white'
    )

    # 添加标注 - 在条形旁边显示增长率
    for i, row in enumerate(display_data.itertuples()):
        fig.add_annotation(
            x=row.销量增长率,
            y=row.产品显示,
            text=f"{row.销量增长率:.1f}% {row.建议图标 if hasattr(row, '建议图标') and pd.notna(row.建议图标) else ''}",
            showarrow=False,
            xshift=10 if row.销量增长率 >= 0 else -10,
            align="left" if row.销量增长率 >= 0 else "right",
            font=dict(
                color="#43A047" if row.销量增长率 >= 0 else "#E53935",
                size=10
            )
        )

    # 添加图例解释不同颜色的含义 - 修改位置到图表上方
    legend_items = [
        {"name": "强劲增长", "color": "#1E88E5", "description": "> 10%"},
        {"name": "增长", "color": "#43A047", "description": "0% ~ 10%"},
        {"name": "轻微下降", "color": "#FB8C00", "description": "-10% ~ 0%"},
        {"name": "显著下降", "color": "#E53935", "description": "< -10%"}
    ]

    # 在图表上方添加图例
    legend_annotations = []
    for i, item in enumerate(legend_items):
        # 计算x位置，平均分布在图表宽度上
        x_pos = 0.05 + (i * 0.25)
        legend_annotations.append(
            dict(
                x=x_pos,
                y=1.08,  # 放在图表上方
                xref="paper",
                yref="paper",
                text=f"<span style='color:{item['color']};'>■</span> {item['name']} ({item['description']})",
                showarrow=False,
                font=dict(size=10),
                align="left"
            )
        )

    fig.update_layout(annotations=legend_annotations)

    # 显示图表
    st.plotly_chart(fig, use_container_width=True)


# 主程序开始
add_logo()  # 添加Logo

# 标题
st.markdown('<div class="main-header">销售预测与库存管理综合分析平台</div>', unsafe_allow_html=True)

# 侧边栏 - 上传文件区域
st.sidebar.header("📂 数据导入")
use_default_files = st.sidebar.checkbox("使用默认文件", value=True, help="使用指定的默认文件路径")

# 定义默认文件路径
DEFAULT_ACTUAL_FILE = "2409~250224出货数据.xlsx"
DEFAULT_FORECAST_FILE = "2409~2502人工预测.xlsx"
DEFAULT_PRODUCT_FILE = "产品信息.xlsx"
DEFAULT_BATCH_FILE = "含批次库存0221（2）.xlsx"
DEFAULT_PRICE_FILE = "单价.xlsx"

if use_default_files:
    # 使用默认文件路径
    actual_data = load_actual_data(DEFAULT_ACTUAL_FILE)
    forecast_data = load_forecast_data(DEFAULT_FORECAST_FILE)
    product_info = load_product_info(DEFAULT_PRODUCT_FILE)
    batch_data = load_batch_inventory(DEFAULT_BATCH_FILE)
    price_data = load_price_data(DEFAULT_PRICE_FILE)

    if os.path.exists(DEFAULT_ACTUAL_FILE):
        st.sidebar.success(f"已成功加载默认出货数据文件")
    else:
        st.sidebar.warning(f"默认出货数据文件不存在，使用示例数据")

    if os.path.exists(DEFAULT_FORECAST_FILE):
        st.sidebar.success(f"已成功加载默认预测数据文件")
    else:
        st.sidebar.warning(f"默认预测数据文件不存在，使用示例数据")

    if os.path.exists(DEFAULT_PRODUCT_FILE):
        st.sidebar.success(f"已成功加载默认产品信息文件")
    else:
        st.sidebar.warning(f"默认产品信息文件不存在，使用示例数据")

    if os.path.exists(DEFAULT_BATCH_FILE):
        st.sidebar.success(f"已成功加载默认批次库存文件")
    else:
        st.sidebar.warning(f"默认批次库存文件不存在，使用示例数据")

    if os.path.exists(DEFAULT_PRICE_FILE):
        st.sidebar.success(f"已成功加载默认单价文件")
    else:
        st.sidebar.warning(f"默认单价文件不存在，使用默认单价数据")
else:
    # 上传文件
    uploaded_actual = st.sidebar.file_uploader("上传出货数据文件", type=["xlsx", "xls"])
    uploaded_forecast = st.sidebar.file_uploader("上传人工预测数据文件", type=["xlsx", "xls"])
    uploaded_product = st.sidebar.file_uploader("上传产品信息文件", type=["xlsx", "xls"])
    uploaded_batch = st.sidebar.file_uploader("上传批次库存文件", type=["xlsx", "xls"])
    uploaded_price = st.sidebar.file_uploader("上传单价文件", type=["xlsx", "xls"])

    # 加载数据
    actual_data = load_actual_data(uploaded_actual if uploaded_actual else None)
    forecast_data = load_forecast_data(uploaded_forecast if uploaded_forecast else None)
    product_info = load_product_info(uploaded_product if uploaded_product else None)
    batch_data = load_batch_inventory(uploaded_batch if uploaded_batch else None)
    price_data = load_price_data(uploaded_price if uploaded_price else None)

# 创建销售人员与区域映射
sales_person_region_mapping = create_person_region_mapping(actual_data, forecast_data)

# 进行库存风险评估
risk_assessment = assess_batch_risk(batch_data, actual_data, forecast_data, sales_person_region_mapping)

# 创建产品代码到名称的映射
product_names_map = {}
if not product_info.empty:
    for _, row in product_info.iterrows():
        product_names_map[row['产品代码']] = row['产品名称']

# 筛选共有月份数据
common_months = get_common_months(actual_data, forecast_data)
actual_data_filtered = actual_data[actual_data['所属年月'].isin(common_months)]
forecast_data_filtered = forecast_data[forecast_data['所属年月'].isin(common_months)]

# 处理数据
processed_data = process_data(actual_data_filtered, forecast_data_filtered, product_info)

# 获取数据的所有月份
all_months = sorted(processed_data['merged_monthly']['所属年月'].unique())
latest_month = all_months[-1] if all_months else None

# 获取最近3个月
last_three_months = get_last_three_months()
valid_last_three_months = [month for month in last_three_months if month in all_months]

# 创建标签页 - 新增库存风险管理标签页
tabs = st.tabs(["📊 总览与历史", "🔍 预测差异分析", "📈 产品趋势", "🔍 重点SKU分析", "⚠️ 库存风险管理"])

with tabs[0]:  # 总览与历史标签页
    # 在标签页内添加筛选器
    st.markdown("### 📊 分析筛选")
    with st.expander("筛选条件", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            selected_months = st.multiselect(
                "选择分析月份",
                options=all_months,
                default=valid_last_three_months if valid_last_three_months else ([all_months[-1]] if all_months else [])
            )

        with col2:
            all_regions = sorted(processed_data['merged_monthly']['所属区域'].unique())
            selected_regions = st.multiselect(
                "选择区域",
                options=all_regions,
                default=all_regions
            )

    # 根据筛选条件过滤数据
    filtered_monthly = filter_data(processed_data['merged_monthly'], selected_months, selected_regions)
    filtered_salesperson = filter_data(processed_data['merged_by_salesperson'], selected_months, selected_regions)

    # 检查选定月份和区域是否为空
    if not selected_months or not selected_regions:
        st.warning("请选择至少一个月份和一个区域进行分析。")
    else:
        # 计算总览KPI
        total_actual_qty = filtered_monthly['求和项:数量（箱）'].sum()
        total_forecast_qty = filtered_monthly['预计销售量'].sum()
        total_diff = total_actual_qty - total_forecast_qty
        total_diff_percent = (total_diff / total_actual_qty * 100) if total_actual_qty > 0 else 0

        # 根据筛选条件计算准确率 - 使用筛选后的数据
        # 计算全国准确率 - 使用筛选后的数据计算
        filtered_national_accuracy = calculate_national_accuracy(filtered_monthly)
        national_qty_accuracy = filtered_national_accuracy['overall']['数量准确率'] * 100

        # 计算区域准确率 - 使用筛选后的数据
        filtered_regional_accuracy = calculate_regional_accuracy(filtered_monthly)
        selected_regions_accuracy = filtered_regional_accuracy['region_overall']
        selected_regions_qty_accuracy = selected_regions_accuracy['数量准确率'].mean() * 100

        # 指标卡行
        st.markdown("### 🔑 关键绩效指标")
        col1, col2, col3, col4 = st.columns(4)

        # 总销售量
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">实际销售量</p>
                    <p class="card-value">{format_number(total_actual_qty)}</p>
                    <p class="card-text">选定期间内</p>
                </div>
                """, unsafe_allow_html=True)

        # 总预测销售量
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">预测销售量</p>
                    <p class="card-value">{format_number(total_forecast_qty)}</p>
                    <p class="card-text">选定期间内</p>
                </div>
                """, unsafe_allow_html=True)

        # 全国准确率
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">全国销售量准确率</p>
                    <p class="card-value">{national_qty_accuracy:.2f}%</p>
                    <p class="card-text">整体预测精度</p>
                    <p class="card-text" style="font-style: italic; font-size: 0.8rem;">计算逻辑：1-|实际销量-预测销量|/实际销量</p>
                </div>
                """, unsafe_allow_html=True)

        # 选定区域准确率
        with col4:
            st.markdown(f"""
                <div class="metric-card">
                    <p class="card-header">选定区域准确率</p>
                    <p class="card-value">{selected_regions_qty_accuracy:.2f}%</p>
                    <p class="card-text">选定区域预测精度</p>
                    <p class="card-text" style="font-style: italic; font-size: 0.8rem;">计算逻辑：各区域准确率的平均值</p>
                </div>
                """, unsafe_allow_html=True)

        # 库存风险概览 - 从附件二整合
        st.markdown('<div class="sub-header">📊 库存风险概览</div>', unsafe_allow_html=True)

        if not risk_assessment.empty:
            # 计算风险分布
            risk_counts = risk_assessment['风险程度'].value_counts()

            # 创建风险分布展示行
            risk_cols = st.columns(5)

            risk_types = ["极高风险", "高风险", "中风险", "低风险", "极低风险"]
            risk_colors = ["#8B0000", "#FF0000", "#FFA500", "#4CAF50", "#2196F3"]

            for i, (risk_type, color) in enumerate(zip(risk_types, risk_colors)):
                count = risk_counts.get(risk_type, 0)
                with risk_cols[i]:
                    st.markdown(f"""
                        <div class="metric-card" style="border-left: 0.5rem solid {color};">
                            <p class="card-header">{risk_type}批次</p>
                            <p class="card-value">{count}</p>
                            <p class="card-text">需关注批次数量</p>
                        </div>
                        """, unsafe_allow_html=True)

            # 显示风险分布饼图
            display_risk_distribution_chart(risk_assessment)

        else:
            st.warning("未加载库存批次数据，无法显示风险概览")

        # 区域销售分析
        st.markdown('<div class="sub-header">📊 区域销售分析</div>', unsafe_allow_html=True)

        # 计算每个区域的销售量和预测量
        region_sales_comparison = filtered_monthly.groupby('所属区域').agg({
            '求和项:数量（箱）': 'sum',
            '预计销售量': 'sum'
        }).reset_index()

        # 计算差异
        region_sales_comparison['差异'] = region_sales_comparison['求和项:数量（箱）'] - region_sales_comparison[
            '预计销售量']
        region_sales_comparison['差异率'] = region_sales_comparison['差异'] / region_sales_comparison[
            '求和项:数量（箱）'] * 100

        # 创建水平堆叠柱状图
        fig_sales_comparison = go.Figure()

        # 添加实际销售量柱
        fig_sales_comparison.add_trace(go.Bar(
            y=region_sales_comparison['所属区域'],
            x=region_sales_comparison['求和项:数量（箱）'],
            name='实际销售量',
            marker_color='royalblue',
            orientation='h'
        ))

        # 添加预测销售量柱
        fig_sales_comparison.add_trace(go.Bar(
            y=region_sales_comparison['所属区域'],
            x=region_sales_comparison['预计销售量'],
            name='预测销售量',
            marker_color='lightcoral',
            orientation='h'
        ))

        # 添加差异率点
        fig_sales_comparison.add_trace(go.Scatter(
            y=region_sales_comparison['所属区域'],
            x=[region_sales_comparison['求和项:数量（箱）'].max() * 1.05] * len(region_sales_comparison),  # 放在右侧
            mode='markers+text',
            marker=dict(
                color=region_sales_comparison['差异率'].apply(lambda x: 'green' if x > 0 else 'red'),
                size=10
            ),
            text=[f"{x:.1f}%" for x in region_sales_comparison['差异率']],
            textposition='middle right',
            name='差异率 (%)'
        ))

        # 更新布局
        fig_sales_comparison.update_layout(
            title="各区域预测与实际销售对比",
            barmode='group',
            xaxis=dict(
                title="销售量 (箱)",
                tickformat=",",
                showexponent="none"
            ),
            yaxis=dict(title="区域"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor='white'
        )

        # 为每个区域准备详细信息
        region_details = []
        for _, region_row in region_sales_comparison.iterrows():
            region = region_row['所属区域']
            # 获取该区域数据
            region_data = filtered_monthly[filtered_monthly['所属区域'] == region]

            if not region_data.empty:
                # 找出差异最大的产品
                product_diff = region_data.groupby('产品代码').agg({
                    '求和项:数量（箱）': 'sum',
                    '预计销售量': 'sum'
                })
                product_diff['差异'] = product_diff['求和项:数量（箱）'] - product_diff['预计销售量']
                product_diff['差异率'] = product_diff.apply(
                    lambda row: (row['差异'] / row['求和项:数量（箱）'] * 100) if row['求和项:数量（箱）'] > 0 else 0,
                    axis=1
                )

                if not product_diff.empty:
                    # 找出差异率最大的产品
                    max_diff_idx = product_diff['差异率'].abs().idxmax()
                    product_code = max_diff_idx
                    product_name = format_product_code(product_code, product_info, include_name=True)
                    actual = product_diff.loc[max_diff_idx, '求和项:数量（箱）']
                    forecast = product_diff.loc[max_diff_idx, '预计销售量']
                    diff_rate = product_diff.loc[max_diff_idx, '差异率']

                    # 找该产品的主要销售员
                    product_sales = filtered_salesperson[
                        (filtered_salesperson['所属区域'] == region) &
                        (filtered_salesperson['产品代码'] == product_code)
                        ]

                    if not product_sales.empty:
                        sales_by_person = product_sales.groupby('销售员').agg({
                            '求和项:数量（箱）': 'sum'
                        })
                        top_salesperson = sales_by_person[
                            '求和项:数量（箱）'].idxmax() if not sales_by_person.empty else "未知"
                    else:
                        top_salesperson = "未知"

                    detail = f"最大差异产品: {product_name}<br>"
                    detail += f"实际销量: {actual:.0f}箱<br>"
                    detail += f"预测销量: {forecast:.0f}箱<br>"
                    detail += f"差异率: {diff_rate:.1f}%<br>"
                    detail += f"主要销售员: {top_salesperson}"
                else:
                    detail = "无产品差异数据"
            else:
                detail = "无区域数据"

            region_details.append(detail)

        # 更新悬停模板
        fig_sales_comparison.update_traces(
            hovertemplate='<b>%{y}区域</b><br>%{x:,.0f}箱<br><br><b>差异详情:</b><br>%{customdata}<extra>%{name}</extra>',
            customdata=region_details,
            selector=dict(type='bar')
        )

        st.plotly_chart(fig_sales_comparison, use_container_width=True)

        # 生成动态解读
        diff_explanation = f"""
            <b>图表解读：</b> 此图展示了各区域的实际销售量(蓝色)与预测销售量(红色)对比，绿色点表示正差异率(低估)，红色点表示负差异率(高估)。
            差异率越高(绝对值越大)，表明预测偏离实际的程度越大。
            """

        # 添加具体分析
        if not region_sales_comparison.empty:
            # 找出差异最大的项目
            high_diff_regions = region_sales_comparison[abs(region_sales_comparison['差异率']) > 15]
            if not high_diff_regions.empty:
                diff_explanation += "<br><b>需关注区域：</b> "
                for _, row in high_diff_regions.iterrows():
                    if row['差异率'] > 0:
                        diff_explanation += f"{row['所属区域']}区域低估了{row['差异率']:.1f}%，"
                    else:
                        diff_explanation += f"{row['所属区域']}区域高估了{abs(row['差异率']):.1f}%，"

            diff_explanation += f"<br><b>行动建议：</b> "

            # 添加具体建议
            if not high_diff_regions.empty:
                for _, row in high_diff_regions.iterrows():
                    if row['差异率'] > 0:
                        adjust = abs(round(row['差异率']))
                        diff_explanation += f"建议{row['所属区域']}区域提高预测量{adjust}%以满足实际需求；"
                    else:
                        adjust = abs(round(row['差异率']))
                        diff_explanation += f"建议{row['所属区域']}区域降低预测量{adjust}%以避免库存积压；"
            else:
                diff_explanation += "各区域预测与实际销售较为匹配，建议维持当前预测方法。"

        add_chart_explanation(diff_explanation)

        # 添加历史趋势分析部分
        st.markdown('<div class="sub-header">📊 销售与预测历史趋势</div>', unsafe_allow_html=True)

        # 准备历史趋势数据
        monthly_trend = filtered_monthly.groupby(['所属年月', '所属区域']).agg({
            '求和项:数量（箱）': 'sum',
            '预计销售量': 'sum'
        }).reset_index()

        # 使用全国数据，不再提供区域选择器
        selected_region_for_trend = '全国'

        if selected_region_for_trend == '全国':
            # 计算全国趋势
            national_trend = monthly_trend.groupby('所属年月').agg({
                '求和项:数量（箱）': 'sum',
                '预计销售量': 'sum'
            }).reset_index()

            trend_data = national_trend
        else:
            # 筛选区域趋势
            region_trend = monthly_trend[monthly_trend['所属区域'] == selected_region_for_trend]
            trend_data = region_trend

        # 创建销售与预测趋势图
        fig_trend = go.Figure()

        # 添加实际销售线
        fig_trend.add_trace(go.Scatter(
            x=trend_data['所属年月'],
            y=trend_data['求和项:数量（箱）'],
            mode='lines+markers',
            name='实际销售量',
            line=dict(color='royalblue', width=3),
            marker=dict(size=8)
        ))

        # 添加预测销售线
        fig_trend.add_trace(go.Scatter(
            x=trend_data['所属年月'],
            y=trend_data['预计销售量'],
            mode='lines+markers',
            name='预测销售量',
            line=dict(color='lightcoral', width=3, dash='dot'),
            marker=dict(size=8)
        ))

        # 计算差异率
        trend_data['差异率'] = (trend_data['求和项:数量（箱）'] - trend_data['预计销售量']) / trend_data[
            '求和项:数量（箱）'] * 100

        # 添加差异率线
        fig_trend.add_trace(go.Scatter(
            x=trend_data['所属年月'],
            y=trend_data['差异率'],
            mode='lines+markers+text',
            name='差异率 (%)',
            yaxis='y2',
            line=dict(color='green', width=2),
            marker=dict(size=8),
            text=[f"{x:.1f}%" for x in trend_data['差异率']],
            textposition='top center'
        ))

        # 更新布局
        title = f"销售与预测历史趋势分析"  # 删除了"全国"前缀
        fig_trend.update_layout(
            title=title,
            xaxis_title="月份",
            yaxis=dict(
                title="销售量 (箱)",
                tickformat=",",
                showexponent="none"
            ),
            yaxis2=dict(
                title="差异率 (%)",
                overlaying='y',
                side='right'
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor='white'
        )

        # 添加悬停提示
        fig_trend.update_traces(
            hovertemplate='<b>%{x}</b><br>%{name}: %{y:,.0f}箱<extra></extra>',
            selector=dict(name=['实际销售量', '预测销售量'])
        )

        fig_trend.update_traces(
            hovertemplate='<b>%{x}</b><br>%{name}: %{y:.2f}%<extra></extra>',
            selector=dict(name='差异率 (%)')
        )

        # 强调选定月份
        if selected_months:
            for month in selected_months:
                if month in trend_data['所属年月'].values:
                    fig_trend.add_shape(
                        type="rect",
                        x0=month,
                        x1=month,
                        y0=0,
                        y1=trend_data['求和项:数量（箱）'].max() * 1.1,
                        fillcolor="rgba(144, 238, 144, 0.2)",
                        line=dict(width=0)
                    )

        st.plotly_chart(fig_trend, use_container_width=True)

        # 生成动态解读
        trend_explanation = f"""
            <b>图表解读：</b> 此图展示了{selected_region_for_trend}历史销售量(蓝线)与预测销售量(红线)趋势，以及月度差异率(绿线)。
            通过观察趋势可以发现销售的季节性波动、预测与实际的一致性以及差异率的变化趋势。
            """

        # 添加具体分析
        if not trend_data.empty and len(trend_data) > 1:
            # 计算整体趋势
            sales_trend = np.polyfit(range(len(trend_data)), trend_data['求和项:数量（箱）'], 1)[0]
            sales_trend_direction = "上升" if sales_trend > 0 else "下降"

            # 找出差异率最大和最小的月份
            max_diff_month = trend_data.loc[trend_data['差异率'].abs().idxmax()]

            # 计算准确率均值
            accuracy_mean = (100 - abs(trend_data['差异率'])).mean()

            trend_explanation += f"<br><b>趋势分析：</b> "

            trend_explanation += f"{selected_region_for_trend}销售量整体呈{sales_trend_direction}趋势，"
            trend_explanation += f"历史准确率平均为{accuracy_mean:.1f}%，"
            trend_explanation += f"{max_diff_month['所属年月']}月差异率最大，达{max_diff_month['差异率']:.1f}%。"

            # 生成建议
            trend_explanation += f"<br><b>行动建议：</b> "

            # 根据趋势分析生成建议
            if abs(trend_data['差异率']).mean() > 10:
                trend_explanation += f"针对{selected_region_for_trend}的销售预测仍有提升空间，建议分析差异率较大月份的原因；"

                # 检查是否有季节性模式
                month_numbers = [int(m.split('-')[1]) for m in trend_data['所属年月']]
                if len(month_numbers) >= 12:
                    spring_diff = abs(trend_data[trend_data['所属年月'].str.contains(r'-0[345]$')]['差异率']).mean()
                    summer_diff = abs(trend_data[trend_data['所属年月'].str.contains(r'-0[678]$')]['差异率']).mean()
                    autumn_diff = abs(
                        trend_data[trend_data['所属年月'].str.contains(r'-0[9]$|10|11$')]['差异率']).mean()
                    winter_diff = abs(
                        trend_data[trend_data['所属年月'].str.contains(r'-12$|-0[12]$')]['差异率']).mean()

                    seasons = [('春季', spring_diff), ('夏季', summer_diff), ('秋季', autumn_diff),
                               ('冬季', winter_diff)]
                    worst_season = max(seasons, key=lambda x: x[1])

                    trend_explanation += f"特别注意{worst_season[0]}月份的预测，历史上这些月份差异率较大({worst_season[1]:.1f}%)；"

                trend_explanation += "考虑在预测模型中增加季节性因素，提高季节性预测的准确性。"
            else:
                trend_explanation += f"{selected_region_for_trend}的销售预测整体表现良好，建议保持当前预测方法，"
                trend_explanation += "持续监控销售趋势变化，及时调整预测模型。"

        add_chart_explanation(trend_explanation)

with tabs[1]:  # 预测差异分析标签页
    # 在标签页内添加筛选器
    st.markdown("### 📊 预测差异分析筛选")
    with st.expander("筛选条件", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            diff_selected_months = st.multiselect(
                "选择分析月份",
                options=all_months,
                default=valid_last_three_months if valid_last_three_months else (
                    [all_months[-1]] if all_months else []),
                key="diff_months"
            )

        with col2:
            diff_selected_regions = st.multiselect(
                "选择区域",
                options=all_regions,
                default=all_regions,
                key="diff_regions"
            )

        with col3:
            analysis_dimension = st.selectbox(
                "选择分析维度",
                options=['产品', '销售员'],
                key="dimension_select"
            )

    # 筛选数据
    diff_filtered_monthly = filter_data(processed_data['merged_monthly'], diff_selected_months, diff_selected_regions)
    diff_filtered_salesperson = filter_data(processed_data['merged_by_salesperson'], diff_selected_months,
                                            diff_selected_regions)

    # 检查筛选条件是否有效
    if not diff_selected_months or not diff_selected_regions:
        st.warning("请选择至少一个月份和一个区域进行分析。")
    else:
        st.markdown("### 预测差异详细分析")

        # 使用全国数据，不再提供区域选择
        selected_region_for_diff = '全国'

        # 准备数据
        if selected_region_for_diff == '全国':
            # 全国数据，按选定维度汇总
            if analysis_dimension == '产品':
                diff_data = diff_filtered_monthly.groupby(['产品代码', '所属区域']).agg({
                    '求和项:数量（箱）': 'sum',
                    '预计销售量': 'sum',
                }).reset_index()

                # 合并销售员信息(按区域和产品分组)
                sales_info = diff_filtered_salesperson.groupby(['所属区域', '产品代码', '销售员']).agg({
                    '求和项:数量（箱）': 'sum'
                }).reset_index()

                # 对每个产品找出主要销售员(销量最大的)
                top_sales = sales_info.loc[sales_info.groupby(['所属区域', '产品代码'])['求和项:数量（箱）'].idxmax()]
                top_sales = top_sales[['所属区域', '产品代码', '销售员']]

                # 将销售员信息合并到差异数据中
                diff_data = pd.merge(diff_data, top_sales, on=['所属区域', '产品代码'], how='left')

                # 汇总到产品级别
                diff_summary = diff_data.groupby('产品代码').agg({
                    '求和项:数量（箱）': 'sum',
                    '预计销售量': 'sum'
                }).reset_index()

            else:  # 销售员维度
                diff_data = diff_filtered_salesperson.groupby(['销售员', '所属区域', '产品代码']).agg({
                    '求和项:数量（箱）': 'sum',
                    '预计销售量': 'sum'
                }).reset_index()

                # 对每个销售员找出主要产品(销量最大的)
                top_products = diff_data.loc[diff_data.groupby(['销售员', '所属区域'])['求和项:数量（箱）'].idxmax()]
                top_products = top_products[['销售员', '所属区域', '产品代码']]

                # 汇总到销售员级别
                diff_summary = diff_data.groupby('销售员').agg({
                    '求和项:数量（箱）': 'sum',
                    '预计销售量': 'sum'
                }).reset_index()
        else:
            # 选定区域数据，按选定维度汇总
            region_filtered = diff_filtered_monthly[diff_filtered_monthly['所属区域'] == selected_region_for_diff]
            region_filtered_salesperson = diff_filtered_salesperson[
                diff_filtered_salesperson['所属区域'] == selected_region_for_diff]

            if analysis_dimension == '产品':
                diff_data = region_filtered.groupby(['产品代码']).agg({
                    '求和项:数量（箱）': 'sum',
                    '预计销售量': 'sum'
                }).reset_index()

                # 合并销售员信息
                sales_info = region_filtered_salesperson.groupby(['产品代码', '销售员']).agg({
                    '求和项:数量（箱）': 'sum'
                }).reset_index()

                # 对每个产品找出主要销售员(销量最大的)
                top_sales = sales_info.loc[sales_info.groupby('产品代码')['求和项:数量（箱）'].idxmax()]
                top_sales = top_sales[['产品代码', '销售员']]

                # 将销售员信息合并到差异数据中
                diff_data = pd.merge(diff_data, top_sales, on='产品代码', how='left')

                # 汇总和差异数据保持一致
                diff_summary = diff_data.copy()

            else:  # 销售员维度
                diff_data = region_filtered_salesperson.groupby(['销售员', '产品代码']).agg({
                    '求和项:数量（箱）': 'sum',
                    '预计销售量': 'sum'
                }).reset_index()

                # 对每个销售员找出主要产品(销量最大的)
                top_products = diff_data.loc[diff_data.groupby('销售员')['求和项:数量（箱）'].idxmax()]
                top_products = top_products[['销售员', '产品代码']]

                # 汇总到销售员级别
                diff_summary = diff_data.groupby('销售员').agg({
                    '求和项:数量（箱）': 'sum',
                    '预计销售量': 'sum'
                }).reset_index()

        # 计算差异和差异率
        diff_summary['数量差异'] = diff_summary['求和项:数量（箱）'] - diff_summary['预计销售量']
        diff_summary['数量差异率'] = diff_summary['数量差异'] / diff_summary['求和项:数量（箱）'] * 100

        # 处理产品名称显示
        if analysis_dimension == '产品':
            diff_summary['产品名称'] = diff_summary['产品代码'].apply(lambda x: product_names_map.get(x, ''))
            diff_summary['产品显示'] = diff_summary.apply(
                lambda row: format_product_code(row['产品代码'], product_info, include_name=True),
                axis=1
            )
            dimension_column = '产品显示'
        else:
            dimension_column = '销售员'

        # 按差异率绝对值降序排序（差异最大的排在前面）
        diff_summary = diff_summary.sort_values('数量差异率', key=abs, ascending=False)

        # 显示所有数据，不再限制数量
        top_diff_items = diff_summary

        # 准备详细信息用于悬停显示
        hover_data = []
        for idx, row in top_diff_items.iterrows():
            if analysis_dimension == '产品':
                # 找到该产品的详细信息
                if selected_region_for_diff == '全国':
                    # 查找该产品在所有选定月份的数据
                    product_details = diff_filtered_monthly[diff_filtered_monthly['产品代码'] == row['产品代码']]
                    product_details = product_details.sort_values('所属年月')

                    # 按月份汇总
                    monthly_info = []
                    for month, month_data in product_details.groupby('所属年月'):
                        actual = month_data['求和项:数量（箱）'].sum()
                        forecast = month_data['预计销售量'].sum()
                        diff_rate = (actual - forecast) / actual * 100 if actual > 0 else 0
                        monthly_info.append(
                            f"{month}月: 实际 {actual:.0f}箱, 预测 {forecast:.0f}箱, 差异 {diff_rate:.1f}%"
                        )

                    # 分析区域和销售员
                    region_info = []
                    for region, region_data in product_details.groupby('所属区域'):
                        region_actual = region_data['求和项:数量（箱）'].sum()
                        region_forecast = region_data['预计销售量'].sum()
                        region_diff = (
                                              region_actual - region_forecast) / region_actual * 100 if region_actual > 0 else 0

                        # 找出该区域主要销售员
                        region_salesperson = diff_filtered_salesperson[
                            (diff_filtered_salesperson['产品代码'] == row['产品代码']) &
                            (diff_filtered_salesperson['所属区域'] == region)
                            ]

                        if not region_salesperson.empty:
                            top_salesperson = region_salesperson.groupby('销售员')['求和项:数量（箱）'].sum().idxmax()
                            region_info.append(
                                f"{region}区域: 差异 {region_diff:.1f}%, 主要销售员: {top_salesperson}"
                            )

                    # 备货建议
                    recent_sales = product_details.sort_values('所属年月', ascending=False)
                    recent_trend = 0
                    if len(recent_sales) >= 2:
                        recent_values = recent_sales.groupby('所属年月')['求和项:数量（箱）'].sum()
                        if len(recent_values) >= 2:
                            latest_values = recent_values.iloc[:2].values
                            if latest_values[1] > 0:  # 避免除以零
                                recent_trend = (latest_values[0] - latest_values[1]) / latest_values[1] * 100

                    recommendation = "<b>备货建议:</b><br>"
                    if recent_trend > 15:
                        recommendation += f"销量呈上升趋势(+{recent_trend:.1f}%)，建议增加备货{min(50, round(abs(recent_trend)))}%"
                    elif recent_trend < -15:
                        recommendation += f"销量呈下降趋势({recent_trend:.1f}%)，建议减少备货{min(30, abs(round(recent_trend)))}%"
                    else:
                        recommendation += "销量较稳定，建议维持当前备货水平，关注区域差异"

                    # 合并所有信息
                    hover_info = "<br>".join(monthly_info) + "<br><br>" + "<br>".join(
                        region_info) + "<br><br>" + recommendation

                else:
                    # 区域内该产品的销售员差异情况
                    sales_details = region_filtered_salesperson[
                        region_filtered_salesperson['产品代码'] == row['产品代码']]

                    if not sales_details.empty:
                        # 计算销售员差异
                        sales_grouped = sales_details.groupby('销售员').agg({
                            '求和项:数量（箱）': 'sum',
                            '预计销售量': 'sum'
                        })
                        sales_grouped['数量差异'] = sales_grouped['求和项:数量（箱）'] - sales_grouped['预计销售量']
                        sales_grouped['数量差异率'] = sales_grouped.apply(
                            lambda x: (x['数量差异'] / x['求和项:数量（箱）'] * 100) if x['求和项:数量（箱）'] > 0 else 0,
                            axis=1
                        )
                        sales_grouped = sales_grouped.sort_values(by='数量差异率', key=abs, ascending=False)

                        # 构建悬停信息
                        sales_info = []
                        for salesperson, detail in sales_grouped.iterrows():
                            sales_info.append(
                                f"销售员 {salesperson}: 差异 {detail['数量差异率']:.1f}%, "
                                f"实际 {detail['求和项:数量（箱）']:.0f}箱, 预测 {detail['预计销售量']:.0f}箱"
                            )

                        # 备货建议
                        recommendation = "<b>备货建议:</b><br>"
                        overestimated = sales_grouped[sales_grouped['数量差异率'] < -10]
                        underestimated = sales_grouped[sales_grouped['数量差异率'] > 10]

                        if len(sales_grouped) > 0:
                            if len(overestimated) > len(underestimated) * 1.5:
                                recommendation += f"整体预测偏高，建议下调{min(30, round(abs(sales_grouped['数量差异率'].mean())))}%"
                            elif len(underestimated) > len(overestimated) * 1.5:
                                recommendation += f"整体预测偏低，建议上调{min(30, round(abs(sales_grouped['数量差异率'].mean())))}%"
                            else:
                                recommendation += "需针对具体销售员调整"
                        else:
                            recommendation += "数据不足，无法提供建议"

                        hover_info = "<br>".join(sales_info) + "<br><br>" + recommendation
                    else:
                        hover_info = "无详细销售员数据"

            else:  # 销售员维度
                if selected_region_for_diff == '全国':
                    # 查找该销售员的所有产品差异
                    salesperson_products = diff_data[diff_data['销售员'] == row['销售员']]

                    # 按产品分组并计算差异
                    product_grouped = salesperson_products.groupby('产品代码').agg({
                        '求和项:数量（箱）': 'sum',
                        '预计销售量': 'sum'
                    })
                    product_grouped['数量差异'] = product_grouped['求和项:数量（箱）'] - product_grouped['预计销售量']
                    product_grouped['数量差异率'] = product_grouped.apply(
                        lambda x: (x['数量差异'] / x['求和项:数量（箱）'] * 100) if x['求和项:数量（箱）'] > 0 else 0,
                        axis=1
                    )
                    # 按差异率绝对值排序
                    product_grouped = product_grouped.sort_values(by='数量差异率', key=abs, ascending=False)

                    # 构建产品详情（最多显示10个）
                    products_info = []
                    for product_code, detail in product_grouped.head(10).iterrows():
                        product_name = format_product_code(product_code, product_info, include_name=True)
                        products_info.append(
                            f"{product_name}: 差异率 {detail['数量差异率']:.1f}%, "
                            f"实际 {detail['求和项:数量（箱）']:.0f}箱, 预测 {detail['预计销售量']:.0f}箱"
                        )

                    # 生成备货建议
                    recommendation = "<b>备货建议:</b><br>"
                    overestimated = product_grouped[product_grouped['数量差异率'] < -10]
                    underestimated = product_grouped[product_grouped['数量差异率'] > 10]

                    if len(product_grouped) > 0:
                        if len(overestimated) > len(underestimated) * 1.5:
                            recommendation += f"该销售员整体高估趋势，建议下调预测10-15%<br>"
                        elif len(underestimated) > len(overestimated) * 1.5:
                            recommendation += f"该销售员整体低估趋势，建议上调预测10-15%<br>"
                        else:
                            recommendation += "需针对具体产品调整:<br>"

                        # 添加最需要调整的3个产品建议
                        top_products = 0
                        for product_code, detail in product_grouped.head(5).iterrows():
                            if abs(detail['数量差异率']) > 10 and top_products < 3:
                                product_name = format_product_code(product_code, product_info, include_name=True)
                                adjustment = min(50, abs(round(detail['数量差异率'])))

                                if detail['数量差异率'] > 10:
                                    recommendation += f"· {product_name}: 上调预测{adjustment}%<br>"
                                else:
                                    recommendation += f"· {product_name}: 下调预测{adjustment}%<br>"

                                top_products += 1
                    else:
                        recommendation += "数据不足，无法提供建议"

                    hover_info = "<br>".join(products_info) + "<br><br>" + recommendation

                else:
                    # 区域内该销售员的产品差异情况
                    product_details = diff_data[diff_data['销售员'] == row['销售员']]
                    if not product_details.empty:
                        # 计算产品差异
                        product_details['数量差异'] = product_details['求和项:数量（箱）'] - product_details['预计销售量']
                        product_details['数量差异率'] = product_details.apply(
                            lambda x: (x['数量差异'] / x['求和项:数量（箱）'] * 100) if x['求和项:数量（箱）'] > 0 else 0,
                            axis=1
                        )
                        product_details = product_details.sort_values(by='数量差异率', key=abs, ascending=False)

                        # 构建悬停信息（最多10个产品）
                        products_info = []
                        for _, detail in product_details.head(10).iterrows():
                            product_name = format_product_code(detail['产品代码'], product_info, include_name=True)
                            products_info.append(
                                f"{product_name}: 差异率 {detail['数量差异率']:.1f}%, "
                                f"实际 {detail['求和项:数量（箱）']:.0f}箱, 预测 {detail['预计销售量']:.0f}箱"
                            )

                        # 备货建议
                        recommendation = "<b>备货建议:</b><br>"
                        overestimated = product_details[product_details['数量差异率'] < -10]
                        underestimated = product_details[product_details['数量差异率'] > 10]

                        if len(overestimated) > len(underestimated) * 1.5:
                            recommendation += f"该销售员在{selected_region_for_diff}区域整体高估，建议下调预测{min(30, round(abs(product_details['数量差异率'].mean())))}%"
                        elif len(underestimated) > len(overestimated) * 1.5:
                            recommendation += f"该销售员在{selected_region_for_diff}区域整体低估，建议上调预测{min(30, round(abs(product_details['数量差异率'].mean())))}%"
                        else:
                            recommendation += "需针对具体产品调整:<br>"
                            # 添加前3个差异最大产品的建议
                            for idx, detail in enumerate(product_details.head(3).itertuples()):
                                if hasattr(detail, '数量差异率') and abs(detail.数量差异率) > 10:
                                    product_name = format_product_code(detail.产品代码, product_info, include_name=True)
                                    adjustment = min(50, abs(round(detail.数量差异率)))
                                    if detail.数量差异率 > 10:
                                        recommendation += f"· {product_name}: 上调预测{adjustment}%<br>"
                                    else:
                                        recommendation += f"· {product_name}: 下调预测{adjustment}%<br>"

                        hover_info = "<br>".join(products_info) + "<br><br>" + recommendation
                    else:
                        hover_info = "无详细产品数据"

            hover_data.append(hover_info)

        # 创建水平堆叠柱状图
        fig_diff = go.Figure()

        # 添加实际销售量柱
        fig_diff.add_trace(go.Bar(
            y=top_diff_items[dimension_column],
            x=top_diff_items['求和项:数量（箱）'],
            name='实际销售量',
            marker_color='royalblue',
            orientation='h',
            customdata=hover_data,
            hovertemplate='<b>%{y}</b><br>实际销售量: %{x:,.0f}箱<br><br><b>详细差异来源:</b><br>%{customdata}<extra></extra>'
        ))

        # 添加预测销售量柱
        fig_diff.add_trace(go.Bar(
            y=top_diff_items[dimension_column],
            x=top_diff_items['预计销售量'],
            name='预测销售量',
            marker_color='lightcoral',
            orientation='h',
            hovertemplate='<b>%{y}</b><br>预测销售量: %{x:,.0f}箱<extra></extra>'
        ))

        # 添加差异率点
        fig_diff.add_trace(go.Scatter(
            y=top_diff_items[dimension_column],
            x=[top_diff_items['求和项:数量（箱）'].max() * 1.05] * len(top_diff_items),  # 放在右侧
            mode='markers+text',
            marker=dict(
                color=top_diff_items['数量差异率'].apply(lambda x: 'green' if x > 0 else 'red'),
                size=10
            ),
            text=[f"{x:.1f}%" for x in top_diff_items['数量差异率']],
            textposition='middle right',
            name='差异率 (%)',
            hovertemplate='<b>%{y}</b><br>差异率: %{text}<extra></extra>'
        ))

        # 更新布局
        title = f"{selected_region_for_diff}预测与实际销售对比 (按{analysis_dimension}维度，差异率降序)"
        fig_diff.update_layout(
            title=title,
            xaxis=dict(
                title="销售量 (箱)",
                tickformat=",",
                showexponent="none"
            ),
            yaxis=dict(title=analysis_dimension),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            barmode='group',
            plot_bgcolor='white',
            hoverlabel=dict(
                bgcolor="white",
                font_size=12
            ),
            height=max(600, len(top_diff_items) * 25)  # 动态调整高度以适应数据量
        )

        st.plotly_chart(fig_diff, use_container_width=True)

        # 生成动态解读
        diff_explanation = f"""
            <b>图表解读：</b> 此图展示{selected_region_for_diff}的{analysis_dimension}维度预测差异情况，蓝色代表实际销售量，红色代表预测销售量，点的颜色表示差异率(绿色为低估，红色为高估)。
            悬停在"实际销售量"条形上，可以查看详细的差异来源，包括区域、销售员或产品的具体信息。这有助于精确定位预测不准确的具体原因。
            """

        # 添加数据钻取分析建议
        diff_explanation += f"<br><b>差异分析建议：</b> "

        if analysis_dimension == '产品':
            diff_explanation += "对于差异较大的产品，建议分析产品在不同区域和销售员间的表现差异，识别特定产品预测准确性的影响因素；"
            if selected_region_for_diff == '全国':
                diff_explanation += "可进一步选择特定区域，深入分析该区域内产品的销售员层面差异。"
            else:
                diff_explanation += "可切换到销售员维度，分析本区域内销售员对产品预测的准确程度。"
        else:  # 销售员维度
            diff_explanation += "对于差异较大的销售员，建议分析其销售的产品组合和区域分布，识别特定销售员预测准确性的影响因素；"
            if selected_region_for_diff == '全国':
                diff_explanation += "可进一步选择特定区域，深入分析该区域内销售员的产品层面差异。"
            else:
                diff_explanation += "可切换到产品维度，分析本区域内产品的销售员层面差异。"

        add_chart_explanation(diff_explanation)

with tabs[2]:  # 产品趋势标签页
    # 在标签页内添加筛选器
    st.markdown("### 📊 分析筛选")
    with st.expander("筛选条件", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            trend_selected_months = st.multiselect(
                "选择分析月份",
                options=all_months,
                default=valid_last_three_months if valid_last_three_months else (
                    [all_months[-1]] if all_months else []),
                key="trend_months"
            )

        with col2:
            trend_selected_regions = st.multiselect(
                "选择区域",
                options=all_regions,
                default=all_regions,
                key="trend_regions"
            )

    # 筛选数据
    trend_filtered_monthly = filter_data(processed_data['merged_monthly'], trend_selected_months,
                                         trend_selected_regions)
    trend_filtered_salesperson = filter_data(processed_data['merged_by_salesperson'], trend_selected_months,
                                             trend_selected_regions)

    # 检查筛选条件是否有效
    if not trend_selected_months or not trend_selected_regions:
        st.warning("请选择至少一个月份和一个区域进行分析。")
    else:
        st.markdown("### 产品销售趋势分析")

        # 动态计算所选区域的产品增长率 - 移除缓存装饰器确保响应筛选
        product_growth = calculate_product_growth(actual_monthly=actual_data, regions=trend_selected_regions,
                                                  months=trend_selected_months)

        if 'latest_growth' in product_growth and not product_growth['latest_growth'].empty:
            # 简要统计
            latest_growth = product_growth['latest_growth']
            growth_stats = {
                '强劲增长': len(latest_growth[latest_growth['趋势'] == '强劲增长']),
                '增长': len(latest_growth[latest_growth['趋势'] == '增长']),
                '轻微下降': len(latest_growth[latest_growth['趋势'] == '轻微下降']),
                '显著下降': len(latest_growth[latest_growth['趋势'] == '显著下降'])
            }

            # 统计指标卡
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(f"""
                    <div class="metric-card" style="border-left: 0.5rem solid #2E8B57;">
                        <p class="card-header">强劲增长产品</p>
                        <p class="card-value">{growth_stats['强劲增长']}</p>
                        <p class="card-text">增长率 > 10%</p>
                    </div>
                    """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                    <div class="metric-card" style="border-left: 0.5rem solid #4CAF50;">
                        <p class="card-header">增长产品</p>
                        <p class="card-value">{growth_stats['增长']}</p>
                        <p class="card-text">增长率 0% ~ 10%</p>
                    </div>
                    """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                    <div class="metric-card" style="border-left: 0.5rem solid #FFA500;">
                        <p class="card-header">轻微下降产品</p>
                        <p class="card-value">{growth_stats['轻微下降']}</p>
                        <p class="card-text">增长率 -10% ~ 0%</p>
                    </div>
                    """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                    <div class="metric-card" style="border-left: 0.5rem solid #F44336;">
                        <p class="card-header">显著下降产品</p>
                        <p class="card-value">{growth_stats['显著下降']}</p>
                        <p class="card-text">增长率 < -10%</p>
                    </div>
                    """, unsafe_allow_html=True)

            # 显示备货建议表格 - 使用修改后的函数避免乱码
            display_recommendations_table(latest_growth, product_info)

            # 添加库存清理预测：显示对增长下降产品的清库预测
            if not risk_assessment.empty:
                st.markdown('<div class="sub-header">📊 增长趋势与库存清理预测</div>', unsafe_allow_html=True)

                # 合并增长率数据和风险评估数据
                if 'latest_growth' in product_growth and not product_growth['latest_growth'].empty:
                    # 准备增长率数据
                    growth_data = product_growth['latest_growth'][['产品代码', '销量增长率', '趋势']].copy()

                    # 合并风险评估数据
                    combined_data = pd.merge(
                        risk_assessment[['物料', '批次库存', '库龄', '日均出货', '预计清库天数', '风险程度']],
                        growth_data,
                        left_on='物料',
                        right_on='产品代码',
                        how='inner'
                    )

                    if not combined_data.empty:
                        # 选择销量下降的产品，因为这些产品可能需要特别注意库存清理
                        declining_products = combined_data[combined_data['趋势'].isin(['轻微下降', '显著下降'])].copy()

                        if not declining_products.empty:
                            # 按预计清库天数排序
                            declining_products['清库天数值'] = declining_products['预计清库天数'].apply(
                                lambda x: 365 if x == float('inf') else float(x)
                            )
                            declining_products = declining_products.sort_values('清库天数值', ascending=False).head(10)

                            # 创建图表
                            fig = go.Figure()

                            # 添加销量增长率条形图
                            fig.add_trace(go.Bar(
                                x=declining_products['物料'],
                                y=declining_products['销量增长率'],
                                name='销量增长率(%)',
                                marker_color='#E53935',
                                text=[f"{x:.1f}%" for x in declining_products['销量增长率']],
                                textposition='outside'
                            ))

                            # 添加预计清库天数曲线
                            fig.add_trace(go.Scatter(
                                x=declining_products['物料'],
                                y=declining_products['清库天数值'],
                                name='预计清库天数',
                                mode='lines+markers',
                                line=dict(color='#1E88E5', width=3),
                                marker=dict(size=8),
                                yaxis='y2'
                            ))

                            # 更新布局
                            fig.update_layout(
                                title='销量下降产品的清库预测',
                                xaxis_title='产品代码',
                                yaxis=dict(
                                    title='销量增长率(%)',
                                    side='left'
                                ),
                                yaxis2=dict(
                                    title='预计清库天数',
                                    side='right',
                                    overlaying='y',
                                    rangemode='tozero'
                                ),
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=1.02,
                                    xanchor="right",
                                    x=1
                                ),
                                plot_bgcolor='white',
                                barmode='group'
                            )

                            # 添加90天风险阈值参考线
                            fig.add_shape(
                                type="line",
                                y0=90, y1=90,
                                x0=-0.5, x1=len(declining_products) - 0.5,
                                yref='y2',
                                line=dict(color="red", width=2, dash="dash"),
                                name="风险阈值(90天)"
                            )

                            # 添加悬停信息
                            hover_texts = [
                                f"产品: {row['物料']}<br>" +
                                f"销量增长率: {row['销量增长率']:.1f}%<br>" +
                                f"批次库存: {row['批次库存']}件<br>" +
                                f"日均出货: {row['日均出货']:.1f}件<br>" +
                                f"预计清库天数: {row['清库天数值'] if row['清库天数值'] < 365 else '无法预计'}<br>" +
                                f"风险程度: {row['风险程度']}"
                                for _, row in declining_products.iterrows()
                            ]

                            fig.update_traces(
                                hovertemplate='%{text}<extra></extra>',
                                text=hover_texts
                            )

                            st.plotly_chart(fig, use_container_width=True)

                            # 添加解释
                            explanation = f"""
                                <b>图表解读：</b> 此图展示了销量下降产品的库存清理预测。红色柱形表示销量增长率(负值表示下降)，蓝色线条表示预计清库天数。
                                红色虚线表示90天的风险阈值，超过该阈值的产品应优先处理。销量下降趋势与较长的清库时间组合，表明这些产品面临库存积压的高风险。
                                建议针对这些产品制定专门的库存清理计划，如促销活动或库存转移。
                                """
                            add_chart_explanation(explanation)
                        else:
                            st.info("未发现销量下降的产品，无需特别关注库存清理")
                    else:
                        st.info("未找到可用于分析的增长率与库存数据")
                else:
                    st.info("未发现产品增长率数据，无法进行增长趋势与库存清理预测分析")

        else:
            st.warning("没有足够的历史数据来计算产品增长率。需要至少两年的销售数据才能计算同比增长。")

with tabs[3]:  # 重点SKU分析标签页
    # 添加筛选器 - 增加月份筛选
    st.markdown("### 📊 分析筛选")
    with st.expander("筛选条件", expanded=True):
        col1, col2 = st.columns(2)

        # 获取当前系统月份作为默认值
        current_month = datetime.now().strftime('%Y-%m')
        current_month_in_data = False

        # 检查当前月份是否在数据集中
        if current_month in all_months:
            current_month_in_data = True
            default_month = [current_month]
        else:
            # 如果当前月份不在数据中，使用数据中的最新月份
            default_month = [all_months[-1]] if all_months else []

        with col1:
            sku_selected_months = st.multiselect(
                "选择分析月份",
                options=all_months,
                default=default_month,
                key="sku_months"
            )
        with col2:
            sku_selected_regions = st.multiselect(
                "选择区域",
                options=all_regions,
                default=all_regions,
                key="sku_regions"
            )

    # 筛选数据
    sku_filtered_monthly = filter_data(processed_data['merged_monthly'], sku_selected_months, sku_selected_regions)
    sku_filtered_salesperson = filter_data(processed_data['merged_by_salesperson'], sku_selected_months,
                                           sku_selected_regions)

    # 重新计算重点SKU，而非使用预计算的结果
    filtered_national_top_skus = calculate_top_skus(sku_filtered_monthly, by_region=False)
    filtered_regional_top_skus = calculate_top_skus(sku_filtered_monthly, by_region=True)

    # 使用新计算的结果
    national_top_skus = filtered_national_top_skus
    regional_top_skus = filtered_regional_top_skus

    # 检查筛选条件是否有效
    if not sku_selected_months or not sku_selected_regions:
        st.warning("请选择至少一个月份和一个区域进行分析。")
    else:
        st.markdown("### 销售量占比80%重点SKU分析")

        # 默认使用全国数据，不再提供选择器
        selected_scope = "全国"

        # 根据用户选择显示相应数据
        if selected_scope == "全国":
            # 显示全国重点SKU分析
            if not national_top_skus.empty:
                # 格式化准确率为百分比
                national_top_skus['数量准确率'] = national_top_skus['数量准确率'] * 100

                # 添加产品名称
                national_top_skus['产品名称'] = national_top_skus['产品代码'].apply(
                    lambda x: product_names_map.get(x, '') if product_names_map else ''
                )
                national_top_skus['产品显示'] = national_top_skus.apply(
                    lambda row: format_product_code(row['产品代码'], product_info, include_name=True),
                    axis=1
                )

                # 合并增长率数据和备货建议
                try:
                    # 使用当前选择的区域和月份计算增长率
                    product_growth_data = calculate_product_growth(
                        actual_monthly=actual_data,
                        regions=sku_selected_regions,
                        months=sku_selected_months
                    ).get('latest_growth', pd.DataFrame())

                    if not product_growth_data.empty:
                        national_top_skus = pd.merge(
                            national_top_skus,
                            product_growth_data[
                                ['产品代码', '销量增长率', '趋势', '备货建议', '调整比例', '建议样式类', '建议图标']],
                            on='产品代码',
                            how='left'
                        )
                except Exception as e:
                    print(f"合并备货建议数据时出错: {str(e)}")

                # 创建水平条形图
                fig_top_skus = go.Figure()

                # 添加销售量条
                fig_top_skus.add_trace(go.Bar(
                    y=national_top_skus['产品显示'],
                    x=national_top_skus['求和项:数量（箱）'],
                    name='销售量',
                    marker=dict(
                        color=national_top_skus['数量准确率'],
                        colorscale='RdYlGn',
                        cmin=0,
                        cmax=100,
                        colorbar=dict(
                            title='准确率 (%)',
                            x=1.05
                        )
                    ),
                    orientation='h'
                ))

                # 添加准确率和备货建议标记
                for i, row in national_top_skus.iterrows():
                    accuracy_text = f"{row['数量准确率']:.0f}%"

                    # 如果有备货建议，添加到文本
                    if 'backup_suggestion' in row and pd.notna(row['备货建议']):
                        accuracy_text += f" {row['建议图标']}"

                    fig_top_skus.add_annotation(
                        y=row['产品显示'],
                        x=row['求和项:数量（箱）'] * 1.05,
                        text=accuracy_text,
                        showarrow=False,
                        font=dict(
                            color="black" if row['数量准确率'] > 70 else "red",
                            size=10
                        )
                    )

                # 更新布局
                fig_top_skus.update_layout(
                    title=f"重点SKU及其准确率",
                    xaxis=dict(
                        title="销售量 (箱)",
                        tickformat=",",
                        showexponent="none"
                    ),
                    yaxis=dict(title="产品"),
                    showlegend=False,
                    plot_bgcolor='white',
                    height=max(700, len(national_top_skus) * 40),  # 增加高度
                    margin=dict(l=20, r=40, t=60, b=30)  # 增加边距
                )

                # 添加悬停提示
                hover_template = '<b>%{y}</b><br>销售量: %{x:,.0f}箱<br>准确率: %{marker.color:.1f}%<br>累计占比: %{customdata[0]:.2f}%'

                # 如果有备货建议数据，添加到悬停提示
                if '备货建议' in national_top_skus.columns:
                    hover_template += '<br>建议: %{customdata[1]}'
                    customdata = national_top_skus[['累计占比', '备货建议']].fillna('未知').values
                else:
                    customdata = national_top_skus[['累计占比']].values

                fig_top_skus.update_traces(
                    hovertemplate=hover_template + '<extra></extra>',
                    customdata=customdata,
                    selector=dict(type='bar')
                )

                # 突出显示准确率低的产品
                low_accuracy_products = national_top_skus[national_top_skus['数量准确率'] < 70]
                if not low_accuracy_products.empty:
                    for product in low_accuracy_products['产品显示']:
                        fig_top_skus.add_shape(
                            type="rect",
                            y0=list(national_top_skus['产品显示']).index(product) - 0.45,
                            y1=list(national_top_skus['产品显示']).index(product) + 0.45,
                            x0=0,
                            x1=national_top_skus['求和项:数量（箱）'].max() * 1.05,
                            line=dict(color="#F44336", width=2),
                            fillcolor="rgba(244, 67, 54, 0.1)"
                        )

                # 保留这个st.plotly_chart调用，这是添加低准确率产品标记后的显示
                st.plotly_chart(fig_top_skus, use_container_width=True)

                # 生成动态解读
                explanation = """
                    <b>图表解读：</b> 此图展示了销售量累计占比达到80%的重点SKU及其准确率，条形长度表示销售量，颜色深浅表示准确率(深绿色表示高准确率，红色表示低准确率)。
                    框线标记的产品准确率低于70%，需要特别关注。
                    """

                # 添加具体产品建议
                if not national_top_skus.empty:
                    top_product = national_top_skus.iloc[0]
                    lowest_accuracy_product = national_top_skus.loc[national_top_skus['数量准确率'].idxmin()]

                    explanation += f"<br><b>产品分析：</b> "
                    explanation += f"{top_product['产品显示']}是销售量最高的产品({format_number(top_product['求和项:数量（箱）'])})，累计占比{top_product['累计占比']:.2f}%，准确率{top_product['数量准确率']:.1f}%；"

                    if lowest_accuracy_product['数量准确率'] < 80:
                        explanation += f"{lowest_accuracy_product['产品显示']}准确率最低，仅为{lowest_accuracy_product['数量准确率']:.1f}%。"

                    # 生成预测建议
                    explanation += "<br><b>行动建议：</b> "

                    low_accuracy = national_top_skus[national_top_skus['数量准确率'] < 70]
                    if not low_accuracy.empty:
                        if len(low_accuracy) <= 3:
                            for _, product in low_accuracy.iterrows():
                                explanation += f"重点关注{product['产品显示']}的预测准确性，目前准确率仅为{product['数量准确率']:.1f}%；"
                        else:
                            explanation += f"共有{len(low_accuracy)}个重点SKU准确率低于70%，需安排专项预测改进计划；"
                    else:
                        explanation += "重点SKU预测准确率良好，建议保持当前预测方法；"

                    # 添加备货建议
                    if '备货建议' in national_top_skus.columns:
                        growth_products = national_top_skus[national_top_skus['销量增长率'] > 10]
                        if not growth_products.empty:
                            top_growth = growth_products.iloc[0]
                            explanation += f"增加{top_growth['产品显示']}的备货量{top_growth['调整比例']}%，其增长率达{top_growth['销量增长率']:.1f}%。"

                add_chart_explanation(explanation)

                # 重点SKU的库存风险分析
                if not risk_assessment.empty:
                    st.markdown('<div class="sub-header">📊 重点SKU库存风险分析</div>', unsafe_allow_html=True)

                    # 合并重点SKU和风险评估数据
                    top_skus_risk = pd.merge(
                        national_top_skus[['产品代码', '产品显示', '求和项:数量（箱）', '累计占比', '数量准确率']],
                        risk_assessment[['物料', '批次库存', '库龄', '预计清库天数', '风险程度', '责任人']],
                        left_on='产品代码',
                        right_on='物料',
                        how='inner'
                    )

                    if not top_skus_risk.empty:
                        # 对数据排序
                        top_skus_risk['风险排序'] = top_skus_risk['风险程度'].map({
                            "极高风险": 0,
                            "高风险": 1,
                            "中风险": 2,
                            "低风险": 3,
                            "极低风险": 4
                        })
                        top_skus_risk = top_skus_risk.sort_values(['风险排序', '累计占比'], ascending=[True, True])

                        # 创建表格显示
                        risk_colors = {
                            "极高风险": "#8B0000",
                            "高风险": "#FF0000",
                            "中风险": "#FFA500",
                            "低风险": "#4CAF50",
                            "极低风险": "#2196F3"
                        }

                        for _, sku in top_skus_risk.iterrows():
                            risk_color = risk_colors.get(sku['风险程度'], "#777777")

                            # 清库天数显示
                            clearance_days = sku['预计清库天数']
                            if clearance_days == float('inf'):
                                clearance_display = "∞ (无法预计)"
                                clearance_class = "clearance-warning"
                            else:
                                clearance_display = f"{clearance_days:.1f}天"
                                clearance_class = "clearance-warning" if clearance_days > 90 else "clearance-ok"

                            # 库龄样式
                            age_class = "batch-age-high" if sku['库龄'] > 90 else "batch-age-medium" if sku[
                                                                                                            '库龄'] > 60 else "batch-age-low"

                            st.markdown(f"""
                                <div class="risk-card" style="border-left: 0.5rem solid {risk_color};">
                                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                        <div>
                                            <h3 style="margin: 0;">{sku['产品显示']}</h3>
                                            <p style="margin: 0.2rem 0;">累计占比: {sku['累计占比']:.2f}% | 准确率: {sku['数量准确率']:.1f}%</p>
                                        </div>
                                        <div style="text-align: right;">
                                            <span style="font-weight: bold; color: {risk_color};">{sku['风险程度']}</span>
                                        </div>
                                    </div>
                                    <div style="display: flex; margin-top: 0.5rem;">
                                        <div style="flex: 1;">
                                            <p style="margin: 0.2rem 0;">批次库存: {sku['批次库存']}件</p>
                                            <p style="margin: 0.2rem 0;">库龄: <span class="{age_class}">{sku['库龄']}天</span></p>
                                        </div>
                                        <div style="flex: 1;">
                                            <p style="margin: 0.2rem 0;">预计清库: <span class="{clearance_class}">{clearance_display}</span></p>
                                            <p style="margin: 0.2rem 0;">责任人: {sku['责任人']}</p>
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)

                        # 添加解释
                        explanation = f"""
                            <b>图表解读：</b> 此图展示了重点SKU的库存风险状况。颜色边框表示风险程度，从红色(极高风险)到蓝色(极低风险)。
                            需特别关注高风险和极高风险的重点SKU，这些产品既在销售中占据重要地位，又面临库存积压风险，应优先处理。
                            """
                        add_chart_explanation(explanation)
                    else:
                        st.info("未找到重点SKU的库存风险数据")
            else:
                st.warning("没有足够的数据来计算全国重点SKU。")
        else:  # 显示特定区域数据
            # 获取所选区域的重点SKU数据
            if selected_scope in regional_top_skus and not regional_top_skus[selected_scope].empty:
                region_top = regional_top_skus[selected_scope].copy()

                # 格式化准确率为百分比
                region_top['数量准确率'] = region_top['数量准确率'] * 100

                # 添加产品名称
                region_top['产品名称'] = region_top['产品代码'].apply(
                    lambda x: product_names_map.get(x, '') if product_names_map else ''
                )
                region_top['产品显示'] = region_top.apply(
                    lambda row: format_product_code(row['产品代码'], product_info, include_name=True),
                    axis=1
                )

                # 合并增长率数据和备货建议
                try:
                    # 使用当前选择的区域和月份计算增长率
                    product_growth_data = calculate_product_growth(
                        actual_monthly=actual_data,
                        regions=[selected_scope],  # 只使用所选区域
                        months=sku_selected_months
                    ).get('latest_growth', pd.DataFrame())

                    if not product_growth_data.empty:
                        region_top = pd.merge(
                            region_top,
                            product_growth_data[
                                ['产品代码', '销量增长率', '趋势', '备货建议', '调整比例', '建议样式类', '建议图标']],
                            on='产品代码',
                            how='left'
                        )
                except Exception as e:
                    print(f"合并区域备货建议数据时出错: {str(e)}")

                # 创建水平条形图
                fig_top_skus = go.Figure()

                # 添加销售量条
                fig_top_skus.add_trace(go.Bar(
                    y=region_top['产品显示'],
                    x=region_top['求和项:数量（箱）'],
                    name='销售量',
                    marker=dict(
                        color=region_top['数量准确率'],
                        colorscale='RdYlGn',
                        cmin=0,
                        cmax=100,
                        colorbar=dict(
                            title='准确率 (%)',
                            x=1.05
                        )
                    ),
                    orientation='h'
                ))

                # 添加准确率标记和备货建议
                for i, row in region_top.iterrows():
                    accuracy_text = f"{row['数量准确率']:.0f}%"

                    # 如果有备货建议，添加到文本
                    if '备货建议' in row and pd.notna(row['备货建议']) and pd.notna(row['建议图标']):
                        accuracy_text += f" {row['建议图标']}"

                    fig_top_skus.add_annotation(
                        y=row['产品显示'],
                        x=row['求和项:数量（箱）'] * 1.05,
                        text=accuracy_text,
                        showarrow=False,
                        font=dict(
                            color="black" if row['数量准确率'] > 70 else "red",
                            size=10
                        )
                    )

                # 更新布局
                fig_top_skus.update_layout(
                    title=f"{selected_scope}区域重点SKU及其准确率",
                    xaxis=dict(
                        title="销售量 (箱)",
                        tickformat=",",
                        showexponent="none"
                    ),
                    yaxis=dict(title="产品"),
                    showlegend=False,
                    plot_bgcolor='white'
                )

                # 添加悬停提示
                hover_template = '<b>%{y}</b><br>销售量: %{x:,.0f}箱<br>准确率: %{marker.color:.1f}%<br>累计占比: %{customdata[0]:.2f}%'

                # 如果有备货建议数据，添加到悬停提示
                if '备货建议' in region_top.columns:
                    hover_template += '<br>建议: %{customdata[1]}'
                    customdata = region_top[['累计占比', '备货建议']].fillna('未知').values
                else:
                    customdata = region_top[['累计占比']].values

                fig_top_skus.update_traces(
                    hovertemplate=hover_template + '<extra></extra>',
                    customdata=customdata,
                    selector=dict(type='bar')
                )

                # 突出显示准确率低的产品
                low_accuracy_products = region_top[region_top['数量准确率'] < 70]
                if not low_accuracy_products.empty:
                    for product in low_accuracy_products['产品显示']:
                        fig_top_skus.add_shape(
                            type="rect",
                            y0=list(region_top['产品显示']).index(product) - 0.45,
                            y1=list(region_top['产品显示']).index(product) + 0.45,
                            x0=0,
                            x1=region_top['求和项:数量（箱）'].max() * 1.05,
                            line=dict(color="#F44336", width=2),
                            fillcolor="rgba(244, 67, 54, 0.1)"
                        )

                st.plotly_chart(fig_top_skus, use_container_width=True)

                # 生成动态解读
                explanation = f"""
                    <b>图表解读：</b> 此图展示了{selected_scope}区域销售量累计占比达到80%的重点SKU及其准确率，条形长度表示销售量，颜色深浅表示准确率。框线标记的产品准确率低于70%，需要特别关注。
                    """

                # 添加具体产品建议
                if not region_top.empty:
                    top_product = region_top.iloc[0]

                    explanation += f"<br><b>产品分析：</b> "
                    explanation += f"{top_product['产品显示']}是{selected_scope}区域销售量最高的产品({format_number(top_product['求和项:数量（箱）'])})，"

                    if len(region_top) > 1:
                        second_product = region_top.iloc[1]
                        explanation += f"其次是{second_product['产品显示']}({format_number(second_product['求和项:数量（箱）'])})。"

                    # 检查准确率
                    low_accuracy = region_top[region_top['数量准确率'] < 70]
                    if not low_accuracy.empty:
                        lowest = low_accuracy.iloc[0]
                        explanation += f"{lowest['产品显示']}准确率最低，仅为{lowest['数量准确率']:.1f}%。"

                    # 生成预测建议
                    explanation += "<br><b>行动建议：</b> "

                    if not low_accuracy.empty:
                        if len(low_accuracy) <= 2:
                            for _, product in low_accuracy.iterrows():
                                explanation += f"{selected_scope}区域应重点关注{product['产品显示']}的预测准确性；"
                        else:
                            explanation += f"{selected_scope}区域有{len(low_accuracy)}个重点SKU准确率低于70%，需安排区域预测培训；"
                    else:
                        explanation += f"{selected_scope}区域重点SKU预测准确率良好；"

                    # 添加备货建议
                    if '备货建议' in region_top.columns:
                        growth_products = region_top[region_top['销量增长率'] > 0]
                        decline_products = region_top[region_top['销量增长率'] < -10]

                        if not growth_products.empty:
                            top_growth = growth_products.iloc[0]
                            explanation += f"建议增加{top_growth['产品显示']}的备货量{top_growth['调整比例']}%；"

                        if not decline_products.empty:
                            top_decline = decline_products.iloc[0]
                            adjust = top_decline['调整比例']
                            explanation += f"建议减少{top_decline['产品显示']}的备货量{adjust}%以避免库存积压。"

                add_chart_explanation(explanation)
            else:
                st.warning(f"没有足够的数据来计算{selected_scope}区域的重点SKU。")

        # 区域与全国重点SKU对比（保留这部分，因为它提供了不同的分析维度）
        if selected_scope != "全国":  # 只有在选择特定区域时才显示对比分析
            st.markdown("### 区域与全国重点SKU对比")

            # 获取区域和全国的SKU列表
            region_top = regional_top_skus[selected_scope] if selected_scope in regional_top_skus else pd.DataFrame()
            if not region_top.empty and not national_top_skus.empty:
                region_skus = set(region_top['产品代码'])
                national_skus = set(national_top_skus['产品代码'])

                # 计算共有和特有SKU
                common_skus = region_skus.intersection(national_skus)
                region_unique_skus = region_skus - national_skus
                national_unique_skus = national_skus - region_skus

                # 创建区域和全国重点SKU的名称映射
                common_sku_names = [format_product_code(code, product_info, include_name=True) for code in common_skus]
                region_unique_sku_names = [format_product_code(code, product_info, include_name=True) for code in
                                           region_unique_skus]
                national_unique_sku_names = [format_product_code(code, product_info, include_name=True) for code in
                                             national_unique_skus]

                # 完整显示所有SKU，不限制数量
                hover_texts = [
                    f"共有SKU ({len(common_skus)}个):<br>" +
                    '<br>- '.join(
                        [''] + [format_product_code(code, product_info, include_name=True) for code in common_skus]),

                    f"区域特有SKU ({len(region_unique_skus)}个):<br>" +
                    '<br>- '.join([''] + [format_product_code(code, product_info, include_name=True) for code in
                                          region_unique_skus]),

                    f"全国重点非区域SKU ({len(national_unique_skus)}个):<br>" +
                    '<br>- '.join([''] + [format_product_code(code, product_info, include_name=True) for code in
                                          national_unique_skus])
                ]

                # 创建饼图
                fig_sku_comparison = go.Figure()

                # 添加区域特有SKU占比
                fig_sku_comparison.add_trace(go.Pie(
                    labels=['区域与全国共有SKU', '区域特有SKU', '全国重点但区域非重点SKU'],
                    values=[len(common_skus), len(region_unique_skus), len(national_unique_skus)],
                    hole=.3,
                    marker_colors=['#4CAF50', '#2196F3', '#F44336'],
                    textinfo='label+percent',
                    hoverinfo='text',
                    hovertext=hover_texts,
                    customdata=[common_sku_names, region_unique_sku_names, national_unique_sku_names]
                ))

                fig_sku_comparison.update_layout(
                    title=f"{selected_scope}区域与全国重点SKU对比",
                    plot_bgcolor='white',
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=12,
                        font_family="Arial"
                    )
                )

                st.plotly_chart(fig_sku_comparison, use_container_width=True)

                # 修改图表解读，删除SKU详情部分
                sku_comparison_explanation = f"""
                    <b>图表解读：</b> 此饼图展示了{selected_scope}区域重点SKU与全国重点SKU的对比情况。共有SKU(绿色)表示同时是区域和全国重点的产品；区域特有SKU(蓝色)表示只在该区域是重点的产品；全国重点但区域非重点SKU(红色)表示在全国范围内是重点但在该区域不是重点的产品。
                    <br><b>建议：</b> 关注区域特有SKU表明区域市场特性；注意全国重点但区域非重点的SKU可能有开发空间。
                    """

                add_chart_explanation(sku_comparison_explanation)
            else:
                st.warning("缺少对比所需的数据。")

with tabs[4]:  # 库存风险管理标签页
    st.markdown("### ⚠️ 批次库存风险管理")

    # 风险过滤选项
    risk_options = ["全部", "极高风险", "高风险", "中风险", "低风险", "极低风险"]
    selected_risk = st.selectbox("选择风险等级", options=risk_options, index=0)

    if not risk_assessment.empty:
        # 风险分布概览
        st.markdown('<div class="sub-header">📊 库存风险分布</div>', unsafe_allow_html=True)

        # 显示风险分布饼图
        display_risk_distribution_chart(risk_assessment)

        # 高风险批次库龄分析
        st.markdown('<div class="sub-header">📊 批次库龄分析</div>', unsafe_allow_html=True)

        # 显示高风险批次库龄分布图
        display_high_risk_age_chart(risk_assessment)

        # 清库预测分析
        st.markdown('<div class="sub-header">📊 清库预测分析</div>', unsafe_allow_html=True)

        # 显示清库预测图
        display_clearance_forecast_chart(risk_assessment)

        # 责任分析
        st.markdown('<div class="sub-header">📊 责任分析</div>', unsafe_allow_html=True)

        # 显示责任分析图
        display_responsibility_analysis(risk_assessment)

        # 风险批次详情列表
        st.markdown('<div class="sub-header">📋 批次风险详情</div>', unsafe_allow_html=True)

        # 显示风险批次详情列表
        display_risk_detail_list(risk_assessment, selected_risk)
    else:
        st.warning("未加载批次库存数据，无法进行风险分析")

# 添加页脚 - 显示数据更新日期
st.markdown(f"""
    <div style="text-align: center; margin-top: 2rem; padding: 1rem; background-color: #f5f5f5; border-radius: 0.5rem;">
        <p style="margin: 0; color: #666; font-size: 0.8rem;">数据更新日期: {datetime.now().strftime('%Y-%m-%d')} | 
        销售预测与库存管理综合分析平台 v2.0</p>
    </div>
    """, unsafe_allow_html=True)