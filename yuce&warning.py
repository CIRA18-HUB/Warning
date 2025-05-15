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
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
from matplotlib.ticker import MaxNLocator
from matplotlib.gridspec import GridSpec

warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="销售预测与库存风险管理一体化仪表盘",
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
    .risk-extreme-high {
        color: #8B0000;
        font-weight: bold;
    }
    .risk-high {
        color: #FF0000;
        font-weight: bold;
    }
    .risk-medium {
        color: #FFA500;
    }
    .risk-low {
        color: #008000;
    }
    .risk-extreme-low {
        color: #0000FF;
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# 登录界面
if not st.session_state.authenticated:
    st.markdown(
        '<div style="font-size: 1.5rem; color: #1f3867; text-align: center; margin-bottom: 1rem;">销售预测与库存风险管理一体化仪表盘 | 登录</div>',
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


# 函数：加载Logo
def add_logo():
    st.markdown(
        """
        <div class="logo-container">
            <img src="https://www.example.com/logo.png" class="logo-img">
        </div>
        """,
        unsafe_allow_html=True
    )


# 函数：格式化数值
def format_number(value):
    """格式化数量显示为逗号分隔的完整数字"""
    return f"{int(value):,} 箱"


# 函数：添加图表解释
def add_chart_explanation(explanation_text):
    """添加图表解释"""
    st.markdown(f'<div class="chart-explanation">{explanation_text}</div>', unsafe_allow_html=True)


# 函数：简化产品名称
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


# 函数：安全计算均值
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


# 函数：计算准确率
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


# 函数：生成备货建议
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


# 函数：计算风险百分比
def calculate_risk_percentage(days_to_clear, batch_age, target_days):
    """
    计算风险百分比，基于清库天数和库龄

    参数:
    days_to_clear (float): 预计清库天数
    batch_age (int): 批次库龄（天数）
    target_days (int): 目标清库天数（30/60/90天）

    返回:
    float: 风险百分比，范围0-100
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


# 函数：加载单价数据
@st.cache_data
def load_price_data(file_path=None):
    """加载产品单价数据"""
    price_data = {}

    # 指定的产品单价信息（默认值，防止文件不存在或读取失败）
    specified_prices = {
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
        'F0104J': 216.96
    }

    try:
        if file_path and os.path.exists(file_path):
            price_df = pd.read_excel(file_path)
            # 查找包含"单价"的列
            unit_price_col = [col for col in price_df.columns if '单价' in col]
            product_code_col = [col for col in price_df.columns if '产品代码' in col or '编号' in col]

            if unit_price_col and product_code_col:
                # 使用找到的列名
                code_col = product_code_col[0]
                price_col = unit_price_col[0]

                # 处理可能的前缀如"型号"或"编号："
                for _, row in price_df.iterrows():
                    code = str(row[code_col])
                    # 提取产品代码 - 查找形如F开头后跟字母和数字的模式
                    code_match = re.search(r'(F[0-9A-Z]+)', code)
                    if code_match:
                        code = code_match.group(1)
                        price_data[code] = row[price_col]
            else:
                # 尝试查找产品代码和单价列，不管列名是什么
                if len(price_df.columns) >= 2:  # 至少有两列：代码和单价
                    code_col = price_df.columns[0]  # 假设第一列是代码
                    price_col = price_df.columns[1]  # 假设第二列是单价

                    for _, row in price_df.iterrows():
                        code = str(row[code_col])
                        # 提取产品代码 - 查找形如F开头后跟字母和数字的模式
                        code_match = re.search(r'(F[0-9A-Z]+)', code)
                        if code_match:
                            code = code_match.group(1)
                            price_data[code] = row[price_col]

            # 如果成功读取了数据，返回
            if price_data:
                return price_data

        # 如果单价文件加载失败或未提供路径，使用指定的价格
        return specified_prices

    except Exception as e:
        # 出错时使用指定的价格
        return specified_prices


# 函数：加载产品信息数据
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


# 函数：创建示例产品信息数据
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


# 函数：格式化产品代码
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


# 函数：加载实际销售数据
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

        # 尝试匹配列名
        renamed_columns = {}
        for req_col in required_columns:
            matched_cols = [col for col in df.columns if req_col in col]
            if matched_cols:
                renamed_columns[matched_cols[0]] = req_col

        # 如果找到匹配列，重命名
        if renamed_columns:
            df = df.rename(columns=renamed_columns)

        # 检查是否有缺失列
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


# 函数：加载预测数据
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

        # 尝试匹配列名
        renamed_columns = {}
        for req_col in required_columns:
            matched_cols = [col for col in df.columns if req_col in col]
            if matched_cols:
                renamed_columns[matched_cols[0]] = req_col

        # 如果找到匹配列，重命名
        if renamed_columns:
            df = df.rename(columns=renamed_columns)

        # 检查是否有缺失列
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


# 函数：创建示例销售数据
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


# 函数：创建示例预测数据
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
                            '所属区域': region,
                            '销售员': sales_person,
                            '所属年月': month_str,
                            '产品代码': product_code,
                            '预计销售量': round(forecast)
                        })

    # 创建DataFrame
    df = pd.DataFrame(data)
    return df


# 函数：加载库存数据
@st.cache_data
def load_inventory_data(file_path=None):
    """加载库存数据和批次信息"""
    try:
        # 默认路径或示例数据
        if file_path is None or not os.path.exists(file_path):
            # 创建示例数据
            return load_sample_inventory_data()

        # 加载数据
        inventory_raw = pd.read_excel(file_path, header=0)

        # 确定列名形式
        expected_columns = ['物料', '描述', '现有库存', '已分配量', '现有库存可订量', '待入库量', '本月剩余可订量',
                            '库位', '生产日期', '生产批号', '数量']

        # 检查列名是否存在
        missing_main_columns = [col for col in expected_columns[:7] if
                                not any(col in str(c) for c in inventory_raw.columns)]
        if missing_main_columns:
            st.error(f"库存文件缺少必要的主要列: {', '.join(missing_main_columns)}。使用示例数据进行演示。")
            return load_sample_inventory_data()

        # 处理第一层数据（产品信息）
        product_rows = inventory_raw[inventory_raw.iloc[:, 0].notna()]
        inventory_data = product_rows.iloc[:, :7].copy()
        inventory_data.columns = ['产品代码', '描述', '现有库存', '已分配量',
                                  '现有库存可订量', '待入库量', '本月剩余可订量']

        # 创建批次信息
        batch_with_product = []
        product_code = None
        product_description = None

        for i, row in inventory_raw.iterrows():
            if pd.notna(row.iloc[0]):
                # 这是产品行
                product_code = row.iloc[0]
                product_description = row.iloc[1]
            elif i < len(inventory_raw) - 1 and pd.notna(row.iloc[7]):
                # 这是批次行
                batch_row = row.iloc[7:].copy()
                batch_row_with_product = pd.Series([product_code, product_description] + batch_row.tolist())
                batch_with_product.append(batch_row_with_product)

        # 创建批次数据DataFrame
        if batch_with_product:
            batch_data = pd.DataFrame(batch_with_product)
            batch_data.columns = ['产品代码', '描述', '库位', '生产日期', '生产批号', '数量']

            # 转换日期列
            batch_data['生产日期'] = pd.to_datetime(batch_data['生产日期'], errors='coerce')

            # 转换数量列为数字
            batch_data['数量'] = pd.to_numeric(batch_data['数量'], errors='coerce')

            # 计算批次价值和库龄
            today = datetime.now().date()
            batch_data['库龄'] = batch_data['生产日期'].apply(
                lambda x: (today - x.date()).days if pd.notna(x) else 0
            )

            return inventory_data, batch_data

        return inventory_data, pd.DataFrame(
            columns=['产品代码', '描述', '库位', '生产日期', '生产批号', '数量', '库龄'])

    except Exception as e:
        st.error(f"加载库存数据时出错: {str(e)}。使用示例数据进行演示。")
        return load_sample_inventory_data()


# 函数：创建示例库存数据
def load_sample_inventory_data():
    """创建示例库存数据和批次信息"""
    # 产品代码列表
    product_codes = [
        'F0101P', 'F0104J', 'F0104L', 'F0104M', 'F0104P',
        'F0110A', 'F0110C', 'F01C5D', 'F01E4B', 'F01A3C'
    ]

    # 描述列表
    descriptions = [
        '口力汉堡90G直立袋装-中国', '口力比萨XXL45G盒装-中国', '口力比萨68G袋装-中国',
        '口力比萨1KG散装-中国', '口力比萨24片盒装-中国', '口力薯条65g-中国',
        '口力奶酪90g-中国', '口力欢乐派对100G袋装（永旺专供）-中国',
        '口力汉堡137g-中国', '口力芝士蛋糕24片盒装-中国'
    ]

    # 创建库存数据
    inventory_data = []
    for code, desc in zip(product_codes, descriptions):
        current_stock = np.random.randint(200, 3000)
        allocated = np.random.randint(0, 300)
        available = current_stock - allocated
        pending = np.random.randint(0, 500)
        remaining = available + pending

        inventory_data.append({
            '产品代码': code,
            '描述': desc,
            '现有库存': current_stock,
            '已分配量': allocated,
            '现有库存可订量': available,
            '待入库量': pending,
            '本月剩余可订量': remaining
        })

    # 创建批次数据
    batch_data = []
    today = datetime.now().date()

    for i, (code, desc) in enumerate(zip(product_codes, descriptions)):
        # 为每个产品生成2-5个批次
        num_batches = np.random.randint(2, 6)

        for j in range(num_batches):
            # 生成随机的生产日期
            days_ago = np.random.randint(10, 300)  # 10-300天前的批次
            production_date = today - timedelta(days=days_ago)

            # 生成批号
            batch_number = f"{production_date.strftime('%Y%m%d')}L:0{75000 + i * 100 + j}"

            # 生成随机数量
            quantity = np.random.randint(20, 1000)

            batch_data.append({
                '产品代码': code,
                '描述': desc,
                '库位': f"DC-{np.random.randint(0, 10):03d}",
                '生产日期': production_date,
                '生产批号': batch_number,
                '数量': quantity,
                '库龄': days_ago
            })

    # 创建DataFrames
    inventory_df = pd.DataFrame(inventory_data)
    batch_df = pd.DataFrame(batch_data)

    # 特别处理F0101P的数据，让它符合附件三中的例子
    if 'F0101P' in inventory_df['产品代码'].values:
        # 找到F0101P的索引
        idx = inventory_df[inventory_df['产品代码'] == 'F0101P'].index[0]
        inventory_df.loc[idx, '现有库存'] = 2581
        inventory_df.loc[idx, '已分配量'] = 20
        inventory_df.loc[idx, '现有库存可订量'] = 2561
        inventory_df.loc[idx, '本月剩余可订量'] = 2561

        # 为F0101P创建特定批次
        f0101p_batches = [
            {
                '产品代码': 'F0101P',
                '描述': '口力汉堡90G直立袋装-中国',
                '库位': 'DC-000',
                '生产日期': datetime(2025, 3, 5),
                '生产批号': '20250305L:075064',
                '数量': 654,
                '库龄': 68
            }
        ]

        # 找到并替换F0101P批次
        batch_df = batch_df[batch_df['产品代码'] != 'F0101P']
        for batch in f0101p_batches:
            batch_df = pd.concat([batch_df, pd.DataFrame([batch])], ignore_index=True)

    # 特别处理F01C5D的数据，让它符合附件三中的例子
    if 'F01C5D' in inventory_df['产品代码'].values:
        # 为F01C5D创建特定批次
        f01c5d_batches = [
            {
                '产品代码': 'F01C5D',
                '描述': '口力欢乐派对100G袋装（永旺专供）-中国',
                '库位': 'DC-000',
                '生产日期': datetime(2024, 9, 10),
                '生产批号': '20240910L:074123',
                '数量': 252,
                '库龄': 244
            }
        ]

        # 找到并替换F01C5D批次
        batch_df = batch_df[batch_df['产品代码'] != 'F01C5D']
        for batch in f01c5d_batches:
            batch_df = pd.concat([batch_df, pd.DataFrame([batch])], ignore_index=True)

    # 特别处理F01A3C的数据，让它符合附件三中的例子
    if 'F01A3C' in inventory_df['产品代码'].values:
        # 为F01A3C创建特定批次
        f01a3c_batches = [
            {
                '产品代码': 'F01A3C',
                '描述': '口力芝士蛋糕24片盒装-中国',
                '库位': 'DC-000',
                '生产日期': datetime(2024, 10, 7),
                '生产批号': '20241007L:074234',
                '数量': 16,
                '库龄': 217
            }
        ]

        # 找到并替换F01A3C批次
        batch_df = batch_df[batch_df['产品代码'] != 'F01A3C']
        for batch in f01a3c_batches:
            batch_df = pd.concat([batch_df, pd.DataFrame([batch])], ignore_index=True)

    return inventory_df, batch_df


# 函数：获取共同月份
def get_common_months(actual_df, forecast_df):
    """获取两个数据集共有的月份"""
    actual_months = set(actual_df['所属年月'].unique())
    forecast_months = set(forecast_df['所属年月'].unique())
    common_months = sorted(list(actual_months.intersection(forecast_months)))
    return common_months


# 函数：获取最近3个月
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


# 函数：筛选数据
def filter_data(data, months=None, regions=None):
    """统一的数据筛选函数"""
    filtered_data = data.copy()

    if months and len(months) > 0:
        filtered_data = filtered_data[filtered_data['所属年月'].isin(months)]

    if regions and len(regions) > 0:
        filtered_data = filtered_data[filtered_data['所属区域'].isin(regions)]

    return filtered_data


# 函数：处理和分析数据
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


# 函数：计算全国准确率
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


# 函数：计算区域准确率
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


# 函数：计算产品增长率
@st.cache_data
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
                    latest_growth['销量增长率'] > 15, '强劲增长',
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


# 函数：计算重点SKU
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


# 函数：分析批次风险
def analyze_batch_risk(batch_data, actual_data, forecast_data, prices, min_daily_sales=0.5, min_seasonal_index=0.3):
    """
    分析批次风险，计算批次的风险等级、清库天数和积压风险等

    参数:
    batch_data (DataFrame): 批次数据
    actual_data (DataFrame): 实际销售数据
    forecast_data (DataFrame): 预测数据
    prices (dict): 产品单价字典
    min_daily_sales (float): 最小日均销量阈值，防止清库天数计算为无穷大
    min_seasonal_index (float): 季节性指数下限，防止季节性太低导致调整后销量接近零

    返回:
    DataFrame: 批次风险分析结果
    """
    if batch_data.empty:
        return pd.DataFrame()

    batch_analysis = []
    today = datetime.now().date()

    # 计算每个产品的销售指标
    product_sales_metrics = {}
    for product_code in batch_data['产品代码'].unique():
        # 获取该产品的销售记录
        product_sales = actual_data[actual_data['产品代码'] == product_code]

        if len(product_sales) == 0:
            # 无销售记录
            product_sales_metrics[product_code] = {
                'daily_avg_sales': 0,
                'sales_std': 0,
                'coefficient_of_variation': float('inf'),
                'total_sales': 0,
                'last_90_days_sales': 0,
                'region_sales': {},
                'person_sales': {}
            }
        else:
            # 计算日均销量
            total_sales = product_sales['求和项:数量（箱）'].sum()

            # 计算过去90天的销量
            ninety_days_ago = today - timedelta(days=90)
            recent_sales = product_sales[product_sales['订单日期'].dt.date >= ninety_days_ago]
            recent_sales_total = recent_sales['求和项:数量（箱）'].sum() if len(recent_sales) > 0 else 0

            # 计算日均销量
            # 使用从最早订单到今天的天数作为分母
            days_range = (today - product_sales['订单日期'].min().date()).days + 1
            daily_avg_sales = total_sales / days_range if days_range > 0 else 0

            # 计算日销量标准差
            # 首先构建每日销量时间序列
            daily_sales = product_sales.groupby(product_sales['订单日期'].dt.date)['求和项:数量（箱）'].sum()

            # 计算标准差
            sales_std = daily_sales.std() if len(daily_sales) > 1 else 0

            # 计算变异系数（波动系数）
            coefficient_of_variation = sales_std / daily_avg_sales if daily_avg_sales > 0 else float('inf')

            # 按区域和销售人员分组统计
            region_sales = product_sales.groupby('所属区域')['求和项:数量（箱）'].sum().to_dict()
            person_sales = product_sales.groupby('申请人')['求和项:数量（箱）'].sum().to_dict()

            # 存储结果
            product_sales_metrics[product_code] = {
                'daily_avg_sales': daily_avg_sales,
                'sales_std': sales_std,
                'coefficient_of_variation': coefficient_of_variation,
                'total_sales': total_sales,
                'last_90_days_sales': recent_sales_total,
                'region_sales': region_sales,
                'person_sales': person_sales
            }

    # 计算每个产品的季节性指数
    seasonal_indices = {}
    for product_code in batch_data['产品代码'].unique():
        product_sales = actual_data[actual_data['产品代码'] == product_code]

        if len(product_sales) > 0:
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
                else:
                    seasonal_index = 1.0  # 无数据时默认为1
            else:
                seasonal_index = 1.0  # 只有一个月的数据，无法计算季节性
        else:
            seasonal_index = 1.0  # 无销售数据默认为1

        # 应用季节性指数下限，避免因季节性极低导致的问题
        seasonal_index = max(seasonal_index, min_seasonal_index)
        seasonal_indices[product_code] = seasonal_index

    # 为每个批次计算风险指标
    for _, batch in batch_data.iterrows():
        product_code = batch['产品代码']
        batch_date = batch['生产日期']
        batch_qty = batch['数量']
        batch_age = batch['库龄'] if '库龄' in batch.index else (today - batch_date.date()).days

        # 获取销售指标
        sales_metrics = product_sales_metrics.get(product_code, {
            'daily_avg_sales': 0,
            'sales_std': 0,
            'coefficient_of_variation': float('inf'),
            'total_sales': 0,
            'last_90_days_sales': 0,
            'region_sales': {},
            'person_sales': {}
        })

        # 获取季节性指数
        seasonal_index = seasonal_indices.get(product_code, 1.0)

        # 获取产品单价并计算批次价值
        unit_price = prices.get(product_code, 50.0)
        batch_value = batch_qty * unit_price

        # 计算预计清库天数
        daily_avg_sales = sales_metrics['daily_avg_sales']

        # 考虑季节性调整，并应用最小销量阈值
        daily_avg_sales_adjusted = max(daily_avg_sales * seasonal_index, min_daily_sales)

        # 计算清库天数和积压风险
        if daily_avg_sales_adjusted > 0:
            days_to_clear = batch_qty / daily_avg_sales_adjusted

            # 计算风险百分比
            one_month_risk = calculate_risk_percentage(days_to_clear, batch_age, 30)
            two_month_risk = calculate_risk_percentage(days_to_clear, batch_age, 60)
            three_month_risk = calculate_risk_percentage(days_to_clear, batch_age, 90)
        else:
            days_to_clear = float('inf')
            one_month_risk = 100
            two_month_risk = 100
            three_month_risk = 100

        # 根据复杂的风险评估逻辑确定风险等级和风险得分
        # 改进风险等级评估逻辑 - 使用综合评分方法
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

        # 获取责任区域和责任人
        responsible_region, responsible_person, responsibility_summary = analyze_responsibility(
            product_code, batch_date, sales_metrics, forecast_data, actual_data, batch_qty
        )

        # 添加批次分析结果
        batch_analysis.append({
            '产品代码': product_code,
            '描述': batch['描述'],
            '批次日期': batch_date.date(),
            '批次库存': batch_qty,
            '库龄': batch_age,
            '批次价值': batch_value,
            '日均出货': round(daily_avg_sales, 2),
            '出货波动系数': round(sales_metrics['coefficient_of_variation'], 2),
            '预计清库天数': days_to_clear if days_to_clear != float('inf') else float('inf'),
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

    # 创建DataFrame并排序
    batch_df = pd.DataFrame(batch_analysis)

    # 按照风险程度和库龄排序
    risk_order = {
        "极高风险": 0,
        "高风险": 1,
        "中风险": 2,
        "低风险": 3,
        "极低风险": 4
    }

    if not batch_df.empty:
        batch_df['风险排序'] = batch_df['风险程度'].map(risk_order)
        batch_df = batch_df.sort_values(by=['风险排序', '库龄'], ascending=[True, False])
        batch_df = batch_df.drop(columns=['风险排序'])

    return batch_df


# 函数：分析责任归属
def analyze_responsibility(product_code, batch_date, sales_metrics, forecast_df, actual_df, batch_qty):
    """
    分析批次库存的责任归属

    参数:
    product_code (str): 产品代码
    batch_date (datetime): 批次生产日期
    sales_metrics (dict): 产品销售指标
    forecast_df (DataFrame): 预测数据
    actual_df (DataFrame): 实际销售数据
    batch_qty (float): 批次库存数量

    返回:
    tuple: (责任区域, 责任人, 责任分析摘要)
    """
    today = datetime.now().date()
    batch_date = batch_date.date()
    default_region = "未知"
    default_person = "系统管理员"

    # 建立销售人员-区域映射
    sales_person_region_mapping = {}
    person_region_data = actual_df[['申请人', '所属区域']].drop_duplicates()
    for _, row in person_region_data.iterrows():
        person = row['申请人']
        region = row['所属区域']
        sales_person_region_mapping[person] = region

    # 获取产品责任分配的默认映射
    product_responsibility = {}
    product_region_counts = actual_df[actual_df['产品代码'] == product_code].groupby('所属区域')[
        '求和项:数量（箱）'].sum()
    product_person_counts = actual_df[actual_df['产品代码'] == product_code].groupby('申请人')['求和项:数量（箱）'].sum()

    if not product_region_counts.empty:
        default_region = product_region_counts.idxmax()
    if not product_person_counts.empty:
        default_person = product_person_counts.idxmax()

    # 定义时间窗口
    forecast_start_date = batch_date - timedelta(days=90)
    forecast_end_date = batch_date + timedelta(days=30)
    sales_start_date = batch_date
    sales_end_date = min(today, batch_date + timedelta(days=90))

    # 获取相关预测记录
    forecast_df['所属年月'] = pd.to_datetime(forecast_df['所属年月'])
    product_forecasts = forecast_df[
        (forecast_df['产品代码'] == product_code) &
        (forecast_df['所属年月'].dt.date >= forecast_start_date) &
        (forecast_df['所属年月'].dt.date <= forecast_end_date)
        ]

    # 获取相关实际销售记录
    product_sales = actual_df[
        (actual_df['产品代码'] == product_code) &
        (actual_df['订单日期'].dt.date >= sales_start_date) &
        (actual_df['订单日期'].dt.date <= sales_end_date)
        ]

    # 初始化责任评分
    person_scores = {}
    region_scores = {}

    # 计算预测未兑现量
    person_allocations = {}
    forecast_responsibility = {}

    if not product_forecasts.empty:
        # 按销售人员分组统计预测总量
        person_forecast_totals = product_forecasts.groupby('销售员')['预计销售量'].sum()

        # 按销售人员统计实际销售总量
        person_sales_data = {}
        for person in person_forecast_totals.index:
            person_actual_sales = product_sales[product_sales['申请人'] == person]['求和项:数量（箱）'].sum() \
                if not product_sales.empty else 0
            person_sales_data[person] = person_actual_sales

            # 计算未兑现预测量
            forecast_qty = person_forecast_totals[person]
            if forecast_qty > 0:
                unfulfilled = max(0, forecast_qty - person_actual_sales)
                if unfulfilled > 0:
                    forecast_responsibility[person] = {
                        "forecast_quantity": forecast_qty,
                        "actual_sales": person_actual_sales,
                        "unfulfilled": unfulfilled,
                        "fulfillment_rate": person_actual_sales / forecast_qty
                    }

        # 如果有未兑现预测，按未兑现量分配库存责任
        if forecast_responsibility:
            total_unfulfilled = sum(detail["unfulfilled"] for person, detail in forecast_responsibility.items())

            if total_unfulfilled > 0:
                # 按未兑现预测量比例分配库存
                for person, detail in forecast_responsibility.items():
                    allocation = int(batch_qty * (detail["unfulfilled"] / total_unfulfilled))
                    person_allocations[person] = max(1, allocation)

                    # 计算责任得分
                    # 预测差异得分 (60%)
                    forecast_score = 0.6 * (1 - detail["fulfillment_rate"])
                    # 分配总得分
                    person_scores[person] = forecast_score

                    # 设置区域得分
                    person_region = sales_person_region_mapping.get(person, default_region)
                    region_scores[person_region] = region_scores.get(person_region, 0) + forecast_score

                # 确保所有库存都被分配
                allocated_total = sum(person_allocations.values())
                if allocated_total < batch_qty and person_allocations:
                    # 将剩余库存分配给未兑现预测量最大的人
                    top_unfulfilled_person = max(forecast_responsibility.items(),
                                                 key=lambda x: x[1]["unfulfilled"])[0]
                    person_allocations[top_unfulfilled_person] += (batch_qty - allocated_total)

    # 如果没有人有预测未兑现，使用默认责任人
    if not person_scores:
        person_scores[default_person] = 1.0
        region_scores[default_region] = 1.0
        person_allocations[default_person] = batch_qty

    # 确定最终责任人
    if person_allocations:
        responsible_person = max(person_allocations.items(), key=lambda x: x[1])[0]

        # 获取责任区域
        if responsible_person in sales_person_region_mapping:
            responsible_region = sales_person_region_mapping[responsible_person]
        else:
            responsible_region = default_region
    else:
        responsible_person = default_person
        responsible_region = default_region

    # 构建责任分析摘要
    responsibility_summary = generate_responsibility_summary(
        responsible_person, forecast_responsibility, person_allocations, batch_qty
    )

    return responsible_region, responsible_person, responsibility_summary


# 函数：生成责任分析摘要
def generate_responsibility_summary(responsible_person, forecast_responsibility, person_allocations, batch_qty):
    """
    生成责任分析摘要

    参数:
    responsible_person (str): 主要责任人
    forecast_responsibility (dict): 预测责任详情
    person_allocations (dict): 人员库存分配情况
    batch_qty (float): 批次库存数量

    返回:
    str: 责任分析摘要
    """
    if not person_allocations:
        return "无法确定责任"

    # 确定主要责任人的责任原因
    main_reasons = []

    if responsible_person in forecast_responsibility:
        detail = forecast_responsibility[responsible_person]
        forecast_qty = detail["forecast_quantity"]
        actual_sales = detail["actual_sales"]
        fulfillment_rate = detail["fulfillment_rate"] * 100
        unfulfilled = detail["unfulfilled"]

        main_reasons.append(f"预测{forecast_qty:.0f}件但仅销售{actual_sales:.0f}件(履行率{fulfillment_rate:.0f}%)")
        main_reasons.append(f"未兑现预测{unfulfilled:.0f}件")
    else:
        main_reasons.append("综合预测与销售因素")

    # 获取主要责任人应承担的库存数量
    main_allocation = person_allocations.get(responsible_person, 0)

    # 构建主要责任人部分
    main_reason = "、".join(main_reasons)
    main_part = f"{responsible_person}主要责任({main_reason}，承担{main_allocation}件)"

    # 构建共同责任部分
    other_persons = []
    for person, allocation in person_allocations.items():
        if person != responsible_person and allocation > 0:
            if person in forecast_responsibility:
                unfulfilled = forecast_responsibility[person]["unfulfilled"]
                other_persons.append(f"{person}(未兑现预测{unfulfilled:.0f}件，承担{allocation}件)")
            else:
                other_persons.append(f"{person}(责任共担，承担{allocation}件)")

    # 组合最终摘要
    if other_persons:
        return f"{main_part}，共同责任：{', '.join(other_persons)}"
    else:
        return main_part


# 函数：创建图表分页器
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


# 函数：创建通用图表
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


# 函数：创建带备货建议的增长率图表
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


# 函数：创建批次风险分布饼图
def create_risk_distribution_chart(batch_analysis):
    """创建批次风险分布饼图"""
    if batch_analysis.empty:
        st.warning("没有批次数据可供分析")
        return None

    # 计算各风险等级的批次数量
    risk_counts = batch_analysis['风险程度'].value_counts()

    # 为饼图准备数据
    labels = risk_counts.index
    values = risk_counts.values

    # 设置颜色映射
    color_map = {
        '极高风险': '#8B0000',  # 深红色
        '高风险': '#FF0000',  # 红色
        '中风险': '#FFA500',  # 橙色
        '低风险': '#4CAF50',  # 绿色
        '极低风险': '#2196F3'  # 蓝色
    }
    colors = [color_map.get(level, '#CCCCCC') for level in labels]

    # 设置分离值
    explode = [0.1 if level == '极高风险' else 0.05 if level == '高风险' else 0 for level in labels]

    # 创建饼图
    fig = go.Figure()

    # 添加饼图
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=colors),
        textinfo='percent',
        hoverinfo='label+value+percent',
        textfont=dict(size=14),
        pull=explode
    ))

    # 更新布局
    fig.update_layout(
        title='库存批次风险分布',
        title_font=dict(size=18, family='Arial', color='#1f3867'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5,
            font=dict(size=12)
        ),
        margin=dict(t=60, b=100, l=20, r=20),
        height=500,
        width=700,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    # 添加注释 - 显示批次总数
    total_batches = sum(values)
    high_risk_batches = risk_counts.get('极高风险', 0) + risk_counts.get('高风险', 0)

    fig.add_annotation(
        x=0.5,
        y=0.5,
        text=f"总批次: {total_batches}<br>高风险批次: {high_risk_batches}",
        font=dict(size=14, color='#1f3867'),
        showarrow=False
    )

    return fig


# 函数：创建高风险批次库龄分布图
def create_high_risk_batches_chart(batch_analysis):
    """创建高风险批次库龄分布图"""
    if batch_analysis.empty:
        st.warning("没有批次数据可供分析")
        return None

    # 筛选高风险批次
    high_risk_batches = batch_analysis[batch_analysis['风险程度'].isin(['极高风险', '高风险'])]

    if high_risk_batches.empty:
        st.info("没有高风险批次数据")
        return None

    # 排序批次数据，按库龄降序
    high_risk_batches = high_risk_batches.sort_values('库龄', ascending=False)

    # 只显示前10个批次，避免图表过于拥挤
    top_batches = high_risk_batches.head(10)

    # 创建批次标签 - 更加清晰的格式
    batch_labels = [f"{code} ({date})" for code, date in
                    zip(top_batches['产品代码'], top_batches['批次日期'].astype(str))]

    # 设置颜色 - 使用风险程度区分
    bar_colors = ['#8B0000' if x == '极高风险' else '#FF5252' for x in top_batches['风险程度']]

    # 创建水平条形图
    fig = go.Figure()

    # 添加库龄条形图
    fig.add_trace(go.Bar(
        y=batch_labels,
        x=top_batches['库龄'],
        orientation='h',
        marker=dict(color=bar_colors),
        text=top_batches['库龄'].apply(lambda x: f"{int(x)}天"),
        textposition='outside',
        name='库龄(天)'
    ))

    # 添加风险阈值参考线
    fig.add_shape(
        type="line",
        x0=90, x1=90,
        y0=-0.5, y1=len(batch_labels) - 0.5,
        line=dict(color="red", width=1, dash="dash"),
        name="高风险阈值(90天)"
    )

    fig.add_shape(
        type="line",
        x0=60, x1=60,
        y0=-0.5, y1=len(batch_labels) - 0.5,
        line=dict(color="orange", width=1, dash="dash"),
        name="中风险阈值(60天)"
    )

    fig.add_shape(
        type="line",
        x0=30, x1=30,
        y0=-0.5, y1=len(batch_labels) - 0.5,
        line=dict(color="green", width=1, dash="dash"),
        name="低风险阈值(30天)"
    )

    # 添加图例注释
    fig.add_annotation(x=90, y=len(batch_labels), text="高风险(90天)",
                       showarrow=False, xanchor="left", yanchor="bottom",
                       font=dict(color="red"))

    fig.add_annotation(x=60, y=len(batch_labels), text="中风险(60天)",
                       showarrow=False, xanchor="left", yanchor="bottom",
                       font=dict(color="orange"))

    fig.add_annotation(x=30, y=len(batch_labels), text="低风险(30天)",
                       showarrow=False, xanchor="left", yanchor="bottom",
                       font=dict(color="green"))

    # 更新布局
    fig.update_layout(
        title='高风险批次库龄分布分析',
        title_font=dict(size=18, family='Arial', color='#1f3867'),
        xaxis=dict(
            title='库龄(天)',
            tickformat=",",
            showexponent="none"
        ),
        yaxis=dict(title='批次'),
        margin=dict(t=60, b=50, l=20, r=20),
        height=max(500, len(batch_labels) * 40),
        width=800,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    # 添加悬停信息
    hover_texts = []
    for _, batch in top_batches.iterrows():
        hover_text = (
            f"产品代码: {batch['产品代码']}<br>"
            f"批次日期: {batch['批次日期']}<br>"
            f"库龄: {batch['库龄']}天<br>"
            f"批次库存: {batch['批次库存']}件<br>"
            f"批次价值: ¥{batch['批次价值']:,.2f}<br>"
            f"风险等级: {batch['风险程度']}<br>"
            f"责任人: {batch['责任人']}"
        )
        hover_texts.append(hover_text)

    fig.update_traces(
        hovertemplate='%{text}',
        text=hover_texts
    )

    return fig


# 函数：创建预测偏差分析图
def create_forecast_bias_chart(batch_analysis, actual_data, forecast_data):
    """创建预测偏差分析图"""
    if batch_analysis.empty:
        st.warning("没有批次数据可供分析")
        return None

    # 筛选高风险批次
    high_risk_batches = batch_analysis[batch_analysis['风险程度'].isin(['极高风险', '高风险'])]

    if high_risk_batches.empty:
        st.info("没有高风险批次数据")
        return None

    # 计算产品预测偏差
    forecast_bias_data = []

    for _, batch in high_risk_batches.iterrows():
        product_code = batch['产品代码']
        batch_date = batch['批次日期']

        # 获取相关预测和实际销售数据
        three_months_before = pd.to_datetime(batch_date) - pd.DateOffset(months=3)
        product_forecast = forecast_data[
            (forecast_data['产品代码'] == product_code) &
            (pd.to_datetime(forecast_data['所属年月']).dt.date >= three_months_before)
            ]

        product_sales = actual_data[
            (actual_data['产品代码'] == product_code) &
            (actual_data['订单日期'].dt.date >= three_months_before)
            ]

        if not product_forecast.empty and not product_sales.empty:
            forecast_qty = product_forecast['预计销售量'].sum()
            actual_qty = product_sales['求和项:数量（箱）'].sum()

            if actual_qty > 0:
                bias_pct = (forecast_qty - actual_qty) / actual_qty * 100
            elif forecast_qty > 0:
                bias_pct = 100  # 预测有值但实际为0
            else:
                bias_pct = 0  # 预测和实际都是0

            # 限制偏差在合理范围内，便于可视化
            bias_pct = max(min(bias_pct, 200), -100)

            forecast_bias_data.append({
                '产品代码': product_code,
                '描述': batch['描述'],
                '批次日期': batch_date,
                '预测量': forecast_qty,
                '实际销量': actual_qty,
                '预测偏差': bias_pct,
                '风险程度': batch['风险程度']
            })

    if not forecast_bias_data:
        st.info("无法计算预测偏差数据")
        return None

    # 创建预测偏差DataFrame
    bias_df = pd.DataFrame(forecast_bias_data)

    # 按偏差绝对值排序
    bias_df = bias_df.reindex(bias_df['预测偏差'].abs().sort_values(ascending=False).index)

    # 限制显示前8个偏差最大的产品
    bias_df = bias_df.head(8)

    # 创建水平条形图
    fig = go.Figure()

    # 创建产品标签
    products = []
    for code, desc in zip(bias_df['产品代码'], bias_df['描述']):
        short_desc = desc[:20] + '...' if len(desc) > 20 else desc
        products.append(f"{code}: {short_desc}")

    # 设置颜色 - 正偏差(预测过高)为红色，负偏差(预测过低)为蓝色
    bar_colors = ['#FF5252' if x > 0 else '#4682B4' for x in bias_df['预测偏差']]

    # 添加预测偏差条形图
    fig.add_trace(go.Bar(
        y=products,
        x=bias_df['预测偏差'].abs(),
        orientation='h',
        marker=dict(color=bar_colors),
        text=bias_df['预测偏差'].apply(
            lambda x: f"{abs(x):.1f}% ({'预测过高' if x > 0 else '预测过低'})"
        ),
        textposition='outside',
        name='预测偏差(%)'
    ))

    # 更新布局
    fig.update_layout(
        title='批次预测偏差分析',
        title_font=dict(size=18, family='Arial', color='#1f3867'),
        xaxis=dict(
            title='预测偏差百分比(绝对值)',
            tickformat=",",
            showexponent="none"
        ),
        yaxis=dict(title='产品'),
        margin=dict(t=60, b=50, l=20, r=20),
        height=max(500, len(products) * 40),
        width=800,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    # 添加图例
    fig.add_shape(
        type="rect",
        xref="paper", yref="paper",
        x0=0.8, y0=0.9, x1=0.82, y1=0.92,
        fillcolor="#FF5252",
        line_width=0,
        layer="below"
    )

    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.83, y=0.91,
        text="预测过高 - 导致库存积压",
        showarrow=False,
        font=dict(size=12),
        align="left"
    )

    fig.add_shape(
        type="rect",
        xref="paper", yref="paper",
        x0=0.8, y0=0.85, x1=0.82, y1=0.87,
        fillcolor="#4682B4",
        line_width=0,
        layer="below"
    )

    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.83, y=0.86,
        text="预测过低 - 可能导致缺货",
        showarrow=False,
        font=dict(size=12),
        align="left"
    )

    # 添加悬停信息
    hover_texts = []
    for _, row in bias_df.iterrows():
        hover_text = (
            f"产品代码: {row['产品代码']}<br>"
            f"预测量: {row['预测量']:.0f}件<br>"
            f"实际销量: {row['实际销量']:.0f}件<br>"
            f"预测偏差: {row['预测偏差']:.1f}%<br>"
            f"风险程度: {row['风险程度']}"
        )
        hover_texts.append(hover_text)

    fig.update_traces(
        hovertemplate='%{text}',
        text=hover_texts
    )

    return fig


# 函数：创建清库预测图
def create_clearance_forecast_chart(batch_analysis):
    """创建清库预测图"""
    if batch_analysis.empty:
        st.warning("没有批次数据可供分析")
        return None

    # 筛选高风险批次
    high_risk_batches = batch_analysis[batch_analysis['风险程度'].isin(['极高风险', '高风险'])]

    if high_risk_batches.empty:
        st.info("没有高风险批次数据")
        return None

    # 处理清库天数数值
    high_risk_batches['清库天数值'] = high_risk_batches['预计清库天数'].apply(
        lambda x: 365 if x == float('inf') else float(x)
    )

    # 按清库天数排序
    sorted_batches = high_risk_batches.sort_values('清库天数值', ascending=False).head(8)

    # 创建批次标签
    batch_labels = []
    for code, desc in zip(sorted_batches['产品代码'], sorted_batches['描述']):
        short_desc = desc[:20] + '...' if len(desc) > 20 else desc
        batch_labels.append(f"{code}: {short_desc}")

    # 创建柱状图
    fig = go.Figure()

    # 添加清库天数柱
    fig.add_trace(go.Bar(
        y=batch_labels,
        x=sorted_batches['清库天数值'],
        orientation='h',
        marker=dict(color='#FF5252'),
        text=sorted_batches['清库天数值'].apply(
            lambda x: f"{int(x)}天" if x < 365 else "∞"
        ),
        textposition='outside',
        name='预计清库天数'
    ))

    # 添加库龄柱
    fig.add_trace(go.Bar(
        y=batch_labels,
        x=sorted_batches['库龄'],
        orientation='h',
        marker=dict(color='#4682B4'),
        text=sorted_batches['库龄'].apply(lambda x: f"{int(x)}天"),
        textposition='outside',
        name='当前库龄'
    ))

    # 添加风险阈值参考线
    fig.add_shape(
        type="line",
        x0=90, x1=90,
        y0=-0.5, y1=len(batch_labels) - 0.5,
        line=dict(color="red", width=1, dash="dash"),
        name="高风险阈值(90天)"
    )

    fig.add_shape(
        type="line",
        x0=60, x1=60,
        y0=-0.5, y1=len(batch_labels) - 0.5,
        line=dict(color="orange", width=1, dash="dash"),
        name="中风险阈值(60天)"
    )

    fig.add_shape(
        type="line",
        x0=30, x1=30,
        y0=-0.5, y1=len(batch_labels) - 0.5,
        line=dict(color="green", width=1, dash="dash"),
        name="低风险阈值(30天)"
    )

    # 更新布局
    fig.update_layout(
        title='高风险批次清库预测分析',
        title_font=dict(size=18, family='Arial', color='#1f3867'),
        xaxis=dict(
            title='天数',
            tickformat=",",
            showexponent="none"
        ),
        yaxis=dict(title='产品'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=80, b=50, l=20, r=20),
        height=max(500, len(batch_labels) * 50),
        width=800,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    # 添加悬停信息
    clearance_hover_texts = []
    age_hover_texts = []
    for _, batch in sorted_batches.iterrows():
        clearance_text = (
            f"产品代码: {batch['产品代码']}<br>"
            f"预计清库天数: {batch['清库天数值']:.0f if batch['清库天数值'] < 365 else '∞'}天<br>"
            f"日均出货: {batch['日均出货']:.2f}箱<br>"
            f"批次库存: {batch['批次库存']}件<br>"
            f"风险程度: {batch['风险程度']}"
        )
        clearance_hover_texts.append(clearance_text)

        age_text = (
            f"产品代码: {batch['产品代码']}<br>"
            f"当前库龄: {batch['库龄']}天<br>"
            f"批次日期: {batch['批次日期']}<br>"
            f"批次价值: ¥{batch['批次价值']:,.2f}"
        )
        age_hover_texts.append(age_text)

    fig.update_traces(
        hovertemplate='%{text}',
        text=clearance_hover_texts,
        selector=dict(name='预计清库天数')
    )

    fig.update_traces(
        hovertemplate='%{text}',
        text=age_hover_texts,
        selector=dict(name='当前库龄')
    )

    return fig


# 函数：创建责任区域分布图
def create_responsibility_region_chart(batch_analysis):
    """创建责任区域分布图"""
    if batch_analysis.empty:
        st.warning("没有批次数据可供分析")
        return None

    # 筛选高风险批次
    high_risk_batches = batch_analysis[batch_analysis['风险程度'].isin(['极高风险', '高风险'])]

    if high_risk_batches.empty:
        st.info("没有高风险批次数据")
        return None

    # 计算各区域的高风险批次数量
    region_counts = high_risk_batches['责任区域'].value_counts()

    # 计算各区域的高风险批次价值总和
    region_values = high_risk_batches.groupby('责任区域')['批次价值'].sum()

    # 创建柱状图
    fig = go.Figure()

    # 添加批次数量柱
    fig.add_trace(go.Bar(
        x=region_counts.index,
        y=region_counts.values,
        name='批次数量',
        marker=dict(color='#4682B4'),
        text=region_counts.values,
        textposition='outside'
    ))

    # 添加批次价值线
    fig.add_trace(go.Scatter(
        x=region_values.index,
        y=region_values.values,
        mode='lines+markers',
        name='批次价值(元)',
        yaxis='y2',
        marker=dict(size=10, color='#FF5252'),
        line=dict(width=3, color='#FF5252')
    ))

    # 更新布局
    fig.update_layout(
        title='高风险批次责任区域分布',
        title_font=dict(size=18, family='Arial', color='#1f3867'),
        xaxis=dict(title='责任区域'),
        yaxis=dict(
            title='批次数量',
            titlefont=dict(color='#4682B4'),
            tickfont=dict(color='#4682B4')
        ),
        yaxis2=dict(
            title='批次价值(元)',
            titlefont=dict(color='#FF5252'),
            tickfont=dict(color='#FF5252'),
            overlaying='y',
            side='right',
            tickformat=',',
            showexponent='none'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=80, b=50, l=50, r=100),
        height=500,
        width=800,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    # 添加悬停信息
    region_details = {}
    for region in region_counts.index:
        region_batches = high_risk_batches[high_risk_batches['责任区域'] == region]
        top_products = region_batches.groupby('产品代码').size().sort_values(ascending=False).head(3)

        details = f"区域: {region}<br>批次数: {region_counts[region]}<br>批次价值: ¥{region_values.get(region, 0):,.2f}<br><br>主要产品:<br>"
        for product, count in top_products.items():
            details += f"- {product}: {count}个批次<br>"

        region_details[region] = details

    hover_texts = []
    for region in region_counts.index:
        hover_texts.append(region_details[region])

    fig.update_traces(
        hovertemplate='%{text}',
        text=hover_texts,
        selector=dict(name='批次数量')
    )

    fig.update_traces(
        hovertemplate='%{text}',
        text=hover_texts,
        selector=dict(name='批次价值(元)')
    )

    return fig


# 函数：创建责任人分布图
def create_responsibility_person_chart(batch_analysis):
    """创建责任人分布图"""
    if batch_analysis.empty:
        st.warning("没有批次数据可供分析")
        return None

    # 筛选高风险批次
    high_risk_batches = batch_analysis[batch_analysis['风险程度'].isin(['极高风险', '高风险'])]

    if high_risk_batches.empty:
        st.info("没有高风险批次数据")
        return None

    # 计算各责任人的高风险批次数量
    person_counts = high_risk_batches['责任人'].value_counts().head(10)  # 只显示前10位责任人

    # 计算各责任人的高风险批次价值总和
    person_values = high_risk_batches.groupby('责任人')['批次价值'].sum()
    person_values = person_values[person_counts.index]  # 保持与counts相同顺序

    # 创建柱状图
    fig = go.Figure()

    # 添加批次数量柱
    fig.add_trace(go.Bar(
        x=person_counts.index,
        y=person_counts.values,
        name='批次数量',
        marker=dict(color='#4682B4'),
        text=person_counts.values,
        textposition='outside'
    ))

    # 添加批次价值线
    fig.add_trace(go.Scatter(
        x=person_values.index,
        y=person_values.values,
        mode='lines+markers',
        name='批次价值(元)',
        yaxis='y2',
        marker=dict(size=10, color='#FF5252'),
        line=dict(width=3, color='#FF5252')
    ))

    # 更新布局
    fig.update_layout(
        title='高风险批次责任人分布(前10位)',
        title_font=dict(size=18, family='Arial', color='#1f3867'),
        xaxis=dict(
            title='责任人',
            tickangle=45
        ),
        yaxis=dict(
            title='批次数量',
            titlefont=dict(color='#4682B4'),
            tickfont=dict(color='#4682B4')
        ),
        yaxis2=dict(
            title='批次价值(元)',
            titlefont=dict(color='#FF5252'),
            tickfont=dict(color='#FF5252'),
            overlaying='y',
            side='right',
            tickformat=',',
            showexponent='none'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=80, b=100, l=50, r=100),
        height=600,
        width=800,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    # 添加悬停信息
    person_details = {}
    for person in person_counts.index:
        person_batches = high_risk_batches[high_risk_batches['责任人'] == person]
        top_products = person_batches.groupby('产品代码').size().sort_values(ascending=False).head(3)
        regions = person_batches['责任区域'].unique()

        details = f"责任人: {person}<br>批次数: {person_counts[person]}<br>批次价值: ¥{person_values.get(person, 0):,.2f}<br>"
        details += f"所属区域: {', '.join(regions)}<br><br>主要产品:<br>"

        for product, count in top_products.items():
            details += f"- {product}: {count}个批次<br>"

        person_details[person] = details

    hover_texts = []
    for person in person_counts.index:
        hover_texts.append(person_details[person])

    fig.update_traces(
        hovertemplate='%{text}',
        text=hover_texts,
        selector=dict(name='批次数量')
    )

    fig.update_traces(
        hovertemplate='%{text}',
        text=hover_texts,
        selector=dict(name='批次价值(元)')
    )

    return fig


# 函数：显示备货建议表格
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
    legend_spacing = 0.25  # 图例项之间的间距

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
st.markdown('<div class="main-header">销售预测与库存风险管理一体化仪表盘</div>', unsafe_allow_html=True)

# 侧边栏 - 上传文件区域
st.sidebar.header("📂 数据导入")
use_default_files = st.sidebar.checkbox("使用默认文件", value=True, help="使用指定的默认文件路径")

# 定义默认文件路径
DEFAULT_ACTUAL_FILE = "2409~250224出货数据.xlsx"
DEFAULT_FORECAST_FILE = "2409~2502人工预测.xlsx"
DEFAULT_PRODUCT_FILE = "产品信息.xlsx"
DEFAULT_INVENTORY_FILE = "含批次库存0221（2）.xlsx"
DEFAULT_PRICE_FILE = "单价.xlsx"

if use_default_files:
    # 使用默认文件路径
    actual_data = load_actual_data(DEFAULT_ACTUAL_FILE)
    forecast_data = load_forecast_data(DEFAULT_FORECAST_FILE)
    product_info = load_product_info(DEFAULT_PRODUCT_FILE)
    inventory_data, batch_data = load_inventory_data(DEFAULT_INVENTORY_FILE)
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

    if os.path.exists(DEFAULT_INVENTORY_FILE):
        st.sidebar.success(f"已成功加载默认库存数据文件")
    else:
        st.sidebar.warning(f"默认库存数据文件不存在，使用示例数据")

    if os.path.exists(DEFAULT_PRICE_FILE):
        st.sidebar.success(f"已成功加载默认单价数据文件")
    else:
        st.sidebar.warning(f"默认单价数据文件不存在，使用默认单价")
else:
    # 上传文件
    uploaded_actual = st.sidebar.file_uploader("上传出货数据文件", type=["xlsx", "xls"])
    uploaded_forecast = st.sidebar.file_uploader("上传人工预测数据文件", type=["xlsx", "xls"])
    uploaded_product = st.sidebar.file_uploader("上传产品信息文件", type=["xlsx", "xls"])
    uploaded_inventory = st.sidebar.file_uploader("上传库存数据文件", type=["xlsx", "xls"])
    uploaded_price = st.sidebar.file_uploader("上传单价数据文件", type=["xlsx", "xls"])

    # 加载数据
    actual_data = load_actual_data(uploaded_actual if uploaded_actual else None)
    forecast_data = load_forecast_data(uploaded_forecast if uploaded_forecast else None)
    product_info = load_product_info(uploaded_product if uploaded_product else None)
    inventory_data, batch_data = load_inventory_data(uploaded_inventory if uploaded_inventory else None)
    price_data = load_price_data(uploaded_price if uploaded_price else None)

# 分析批次风险
batch_risk_analysis = analyze_batch_risk(batch_data, actual_data, forecast_data, price_data)

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

# 创建标签页 - 更新标签页结构
tabs = st.tabs(["📊 总览与历史", "🔍 预测差异分析", "📈 产品趋势", "🔍 重点SKU分析", "🚨 库存风险管理"])

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

        # 计算库存风险分布
        risk_counts = {'极高风险': 0, '高风险': 0, '中风险': 0, '低风险': 0, '极低风险': 0}
        if not batch_risk_analysis.empty:
            risk_distribution = batch_risk_analysis['风险程度'].value_counts().to_dict()
            for level, count in risk_distribution.items():
                if level in risk_counts:
                    risk_counts[level] = count

        # 计算高风险批次占比
        high_risk_count = risk_counts['极高风险'] + risk_counts['高风险']
        total_batches = sum(risk_counts.values())
        high_risk_percent = (high_risk_count / total_batches * 100) if total_batches > 0 else 0

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

        # 库存风险指标
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">高风险库存批次</p>
                <p class="card-value">{high_risk_count} <span style="font-size: 1rem;">({high_risk_percent:.1f}%)</span></p>
                <p class="card-text">需紧急处理的库存批次</p>
                <p class="card-text" style="font-style: italic; font-size: 0.8rem;">包括极高风险({risk_counts['极高风险']})和高风险({risk_counts['高风险']})批次</p>
            </div>
            """, unsafe_allow_html=True)

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

        # 库存风险分布概览
        st.markdown('<div class="sub-header">🚨 库存风险概览</div>', unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])

        with col1:
            # 创建风险分布饼图
            risk_chart = create_risk_distribution_chart(batch_risk_analysis)
            if risk_chart:
                st.plotly_chart(risk_chart, use_container_width=True)
            else:
                st.info("没有足够的批次数据来生成风险分布图")

        with col2:
            # 高风险批次库龄分布图
            high_risk_chart = create_high_risk_batches_chart(batch_risk_analysis)
            if high_risk_chart:
                st.plotly_chart(high_risk_chart, use_container_width=True)
            else:
                st.info("没有高风险批次数据来生成库龄分布图")

        # 风险解读
        risk_explanation = f"""
        <b>风险分布解读：</b> 左图展示了所有库存批次按风险等级的分布情况，右图显示了高风险批次的库龄分布。
        风险评估基于库龄、清库天数、销量波动等因素综合计算，分为极高风险、高风险、中风险、低风险和极低风险五个等级。
        """

        # 添加具体分析
        high_risk_batches = batch_risk_analysis[batch_risk_analysis['风险程度'].isin(['极高风险', '高风险'])]
        if not high_risk_batches.empty:
            avg_age = high_risk_batches['库龄'].mean()
            oldest_batch = high_risk_batches.iloc[high_risk_batches['库龄'].idxmax()]
            total_value = high_risk_batches['批次价值'].sum()

            risk_explanation += f"<br><b>高风险批次分析：</b> "
            risk_explanation += f"共有{len(high_risk_batches)}个高风险批次，平均库龄{avg_age:.1f}天，最长库龄批次为{oldest_batch['产品代码']}({oldest_batch['库龄']}天)。"
            risk_explanation += f"这些批次总价值{total_value:,.2f}元，占用仓储资源和资金成本。"

            risk_explanation += f"<br><b>行动建议：</b> "
            risk_explanation += f"优先处理极高风险批次，考虑折价促销或转仓调配；对高风险批次制定清库计划；加强预测准确性，减少未来库存积压风险。"
        else:
            risk_explanation += "<br><b>当前无高风险批次，库存状况良好。继续保持当前库存管理水平。</b>"

        add_chart_explanation(risk_explanation)
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
                    spring_diff = abs(trend_data[trend_data['所属年月'].str.contains(r'-0[345])]['
                    差异率
                    ']).mean()
                    summer_diff = abs(trend_data[trend_data['所属年月'].str.contains(r'-0[678])]['
                    差异率
                    ']).mean()
                    autumn_diff = abs(
                        trend_data[trend_data['所属年月'].str.contains(r'-0[9]$|10|11)]['
                    差异率
                    ']).mean()
                    winter_diff = abs(
                        trend_data[trend_data['所属年月'].str.contains(r'-12$|-0[12])]['
                    差异率
                    ']).mean()

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
                    diff_filtered_monthly = filter_data(processed_data['merged_monthly'], diff_selected_months,
                                                        diff_selected_regions)
                    diff_filtered_salesperson = filter_data(processed_data['merged_by_salesperson'],
                                                            diff_selected_months,
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
                        if
                    analysis_dimension == '产品':
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
                    region_filtered = diff_filtered_monthly[
                        diff_filtered_monthly['所属区域'] == selected_region_for_diff]
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
                        diff_summary['产品名称'] = diff_summary['产品代码'].apply(
                            lambda x: product_names_map.get(x, ''))
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
                        if
                    analysis_dimension == '产品':
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

                    # 添加库存风险信息
                    if not batch_risk_analysis.empty:
                        product_batches = batch_risk_analysis[batch_risk_analysis['产品代码'] == row['产品代码']]
                    if not product_batches.empty:
                        high_risk_batches = product_batches[product_batches['风险程度'].isin(['极高风险', '高风险'])]
                    if not high_risk_batches.empty:
                        avg_age = high_risk_batches['库龄'].mean()
                    total_qty = high_risk_batches['批次库存'].sum()
                    total_value = high_risk_batches['批次价值'].sum()

                    recommendation += f"<br><b>库存风险警示:</b><br>"
                    recommendation += f"有{len(high_risk_batches)}个高风险批次，共{total_qty}箱，价值{total_value:,.2f}元，平均库龄{avg_age:.1f}天"
                    recommendation += f"<br>建议采取积极清库措施，减少库存积压"

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
                        if
                    len(overestimated) > len(underestimated) * 1.5:
                    recommendation += f"整体预测偏高，建议下调{min(30, round(abs(sales_grouped['数量差异率'].mean())))}%"
                    elif len(underestimated) > len(overestimated) * 1.5:
                    recommendation += f"整体预测偏低，建议上调{min(30, round(abs(sales_grouped['数量差异率'].mean())))}%"
                    else:
                    recommendation += "需针对具体销售员调整"
                    else:
                    recommendation += "数据不足，无法提供建议"

                    # 添加库存风险信息
                    if not batch_risk_analysis.empty:
                        product_batches = batch_risk_analysis[batch_risk_analysis['产品代码'] == row['产品代码']]
                    if not product_batches.empty:
                        high_risk_batches = product_batches[product_batches['风险程度'].isin(['极高风险', '高风险'])]
                    if not high_risk_batches.empty:
                        avg_age = high_risk_batches['库龄'].mean()
                    total_qty = high_risk_batches['批次库存'].sum()
                    total_value = high_risk_batches['批次价值'].sum()

                    recommendation += f"<br><b>库存风险警示:</b><br>"
                    recommendation += f"有{len(high_risk_batches)}个高风险批次，共{total_qty}箱，价值{total_value:,.2f}元，平均库龄{avg_age:.1f}天"
                    recommendation += f"<br>建议采取积极清库措施，减少库存积压"

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
                        if
                    len(overestimated) > len(underestimated) * 1.5:
                    recommendation += f"该销售员整体高估趋势，建议下调预测10-15%<br>"
                    elif len(underestimated) > len(overestimated) * 1.5:
                    recommendation += f"该销售员整体低估趋势，建议上调预测10-15%<br>"
                    else:
                    recommendation += "需针对具体产品调整:<br>"

                    # 添加最需要调整的3个产品建议
                    top_products = 0
                    for product_code, detail in product_grouped.head(5).iterrows():
                        if
                    abs(detail['数量差异率']) > 10 and top_products < 3:
                    product_name = format_product_code(product_code, product_info, include_name=True)
                    adjustment = min(50, abs(round(detail['数量差异率'])))

                    if detail['数量差异率'] > 10:
                        recommendation += f"· {product_name}: 上调预测{adjustment}%<br>"
                    else:
                        recommendation += f"· {product_name}: 下调预测{adjustment}%<br>"

                    top_products += 1
                    else:
                    recommendation += "数据不足，无法提供建议"

                    # 添加库存风险责任信息
                    if not batch_risk_analysis.empty:
                        person_responsibility = batch_risk_analysis[batch_risk_analysis['责任人'] == row['销售员']]
                    if not person_responsibility.empty:
                        high_risk_count =
                        person_responsibility[person_responsibility['风险程度'].isin(['极高风险', '高风险'])].shape[0]
                    if high_risk_count > 0:
                        total_value =
                        person_responsibility[person_responsibility['风险程度'].isin(['极高风险', '高风险'])][
                            '批次价值'].sum()

                    recommendation += f"<br><b>库存责任警示:</b><br>"
                    recommendation += f"该销售员负责{high_risk_count}个高风险批次，价值{total_value:,.2f}元"
                    recommendation += f"<br>建议提高预测准确性，减少未来库存积压"

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
                        if
                    hasattr(detail, '数量差异率') and abs(detail.数量差异率) > 10:
                    product_name = format_product_code(detail.产品代码, product_info, include_name=True)
                    adjustment = min(50, abs(round(detail.数量差异率)))
                    if detail.数量差异率 > 10:
                        recommendation += f"· {product_name}: 上调预测{adjustment}%<br>"
                    else:
                        recommendation += f"· {product_name}: 下调预测{adjustment}%<br>"

                    # 添加库存风险责任信息
                    if not batch_risk_analysis.empty:
                        person_responsibility = batch_risk_analysis[
                            (batch_risk_analysis['责任人'] == row['销售员']) &
                            (batch_risk_analysis['责任区域'] == selected_region_for_diff)
                            ]
                    if not person_responsibility.empty:
                        high_risk_count =
                        person_responsibility[person_responsibility['风险程度'].isin(['极高风险', '高风险'])].shape[0]
                    if high_risk_count > 0:
                        total_value =
                        person_responsibility[person_responsibility['风险程度'].isin(['极高风险', '高风险'])][
                            '批次价值'].sum()

                    recommendation += f"<br><b>库存责任警示:</b><br>"
                    recommendation += f"该销售员在此区域负责{high_risk_count}个高风险批次，价值{total_value:,.2f}元"
                    recommendation += f"<br>建议提高预测准确性，减少未来库存积压"

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

                    # 预测偏差与库存风险关系分析
                    st.markdown('<div class="sub-header">📊 预测偏差与库存风险关系分析</div>', unsafe_allow_html=True)

                    # 创建预测偏差分析图
                    bias_chart = create_forecast_bias_chart(batch_risk_analysis, actual_data, forecast_data)
                    if bias_chart:
                        st.plotly_chart(bias_chart, use_container_width=True)
                    else:
                        st.info("没有足够的数据来生成预测偏差分析图")

                    # 预测偏差与库存风险关系解读
                    bias_explanation = """
        <b>图表解读：</b> 此图分析了预测准确性对库存积压的影响。红色表示预测过高(实际销量低于预测)，导致不必要的库存积压；蓝色表示预测过低(实际销量高于预测)，可能导致缺货和销售机会损失。图表按偏差绝对值大小排序，展示偏差最显著的批次。
        """

                    # 添加具体分析
                    if not batch_risk_analysis.empty:
                        high_risk_batches = batch_risk_analysis[
                            batch_risk_analysis['风险程度'].isin(['极高风险', '高风险'])]
                    if not high_risk_batches.empty:
                        high_pred_count = sum(
                            1 for bias in high_risk_batches['日均出货'] / high_risk_batches['批次库存'] * 100 if
                            bias < 30)
                    bias_explanation += f"<br><b>关键发现：</b> {high_pred_count}个高风险批次的日均出货量不到批次库存的30%，表明预测过高导致库存积压。"
                    bias_explanation += f"预测准确性与库存健康度密切相关，提高预测准确性是减少库存积压的关键。"

                    # 重点人员分析
                    top_persons = high_risk_batches['责任人'].value_counts().head(3)
                    if not top_persons.empty:
                        persons_list = [f"{person}({count}个批次)" for person, count in top_persons.items()]
                    bias_explanation += f"<br><b>重点关注人员：</b> {', '.join(persons_list)}的预测准确性问题是库存积压的主要来源，应优先提高这些人员的预测能力。"

                    add_chart_explanation(bias_explanation)

                    # 动态解读
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
                    trend_filtered_salesperson = filter_data(processed_data['merged_by_salesperson'],
                                                             trend_selected_months,
                                                             trend_selected_regions)

                    # 检查筛选条件是否有效
                    if not trend_selected_months or not trend_selected_regions:
                        st.warning("请选择至少一个月份和一个区域进行分析。")
                    else:
                        st.markdown("### 产品销售趋势分析")

                    # 动态计算所选区域的产品增长率 - 移除缓存装饰器确保响应筛选
                    product_growth = calculate_product_growth(actual_monthly=actual_data,
                                                              regions=trend_selected_regions,
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

                    # 清库预测分析
                    st.markdown('<div class="sub-header">📊 产品清库预测分析</div>', unsafe_allow_html=True)

                    # 创建清库预测图
                    clearance_chart = create_clearance_forecast_chart(batch_risk_analysis)
                    if clearance_chart:
                        st.plotly_chart(clearance_chart, use_container_width=True)
                    else:
                        st.info("没有高风险批次数据来生成清库预测图")

                    # 清库预测解读
                    clearance_explanation = """
            <b>图表解读：</b> 此图对比展示了高风险批次的预计清库天数(红色)和当前库龄(蓝色)。预计清库天数基于当前日均销量计算，表示在当前销售速度下消化完该批次库存所需的时间。垂直红线表示90天高风险阈值。
            """

                    # 添加具体分析
                    if not batch_risk_analysis.empty:
                        high_risk_batches = batch_risk_analysis[
                            batch_risk_analysis['风险程度'].isin(['极高风险', '高风险'])]
                    if not high_risk_batches.empty:
                        avg_clearance = high_risk_batches['预计清库天数'].replace(float('inf'), 365).mean()
                    infinite_count = sum(1 for x in high_risk_batches['预计清库天数'] if x == float('inf'))

                    clearance_explanation += f"<br><b>关键发现：</b> 分析显示高风险批次平均清库时间约{avg_clearance:.1f}天，远超90天风险阈值。"
                    if infinite_count > 0:
                        clearance_explanation += f"有{infinite_count}个批次因无销量导致清库天数为无穷大，这类批次需要特别干预措施。"

                    clearance_explanation += f"<br>库存处理优先级应是：无销量批次 > 清库天数超过180天批次 > 其余高风险批次。建议采取促销、转仓、调配或特价处理等措施加速库存周转。"

                    add_chart_explanation(clearance_explanation)
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
                    sku_filtered_monthly = filter_data(processed_data['merged_monthly'], sku_selected_months,
                                                       sku_selected_regions)
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
                        if
                    not national_top_skus.empty:
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

                    # 添加库存风险信息
                    if not batch_risk_analysis.empty:
                        high_risk_products = []
                        for _, product in national_top_skus.iterrows():
                            product_code = product['产品代码']
                            product_batches = batch_risk_analysis[batch_risk_analysis['产品代码'] == product_code]
                            high_risk_count = \
                            product_batches[product_batches['风险程度'].isin(['极高风险', '高风险'])].shape[0]
                            if high_risk_count > 0:
                                high_risk_products.append(f"{product['产品显示']}({high_risk_count}个批次)")

                        if high_risk_products:
                            explanation += f"<br><b>库存风险警示：</b> 重点SKU中{', '.join(high_risk_products[:3])}等产品存在高风险库存，需要特别关注清库进度。"

                add_chart_explanation(explanation)
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

                    # 添加库存风险信息
                    if not batch_risk_analysis.empty:
                        high_risk_products = []
                        for _, product in region_top.iterrows():
                            product_code = product['产品代码']
                            product_batches = batch_risk_analysis[
                                (batch_risk_analysis['产品代码'] == product_code) &
                                (batch_risk_analysis['责任区域'] == selected_scope)
                                ]
                            high_risk_count = \
                            product_batches[product_batches['风险程度'].isin(['极高风险', '高风险'])].shape[0]
                            if high_risk_count > 0:
                                high_risk_products.append(f"{product['产品显示']}({high_risk_count}个批次)")

                        if high_risk_products:
                            explanation += f"<br><b>库存风险警示：</b> 区域重点SKU中{', '.join(high_risk_products[:3])}等产品存在高风险库存，需要特别关注清库进度。"

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
    # 在标签页内添加筛选器
    st.markdown("### 📊 库存风险分析筛选")
    with st.expander("筛选条件", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            risk_filter = st.multiselect(
                "按风险程度筛选",
                options=['极高风险', '高风险', '中风险', '低风险', '极低风险'],
                default=['极高风险', '高风险'],
                key="risk_filter"
            )

        with col2:
            responsibility_regions = sorted(batch_risk_analysis['责任区域'].unique())
            region_filter = st.multiselect(
                "按责任区域筛选",
                options=responsibility_regions,
                default=responsibility_regions,
                key="region_filter"
            )

        with col3:
            all_persons = sorted(batch_risk_analysis['责任人'].unique())
            person_filter = st.multiselect(
                "按责任人筛选",
                options=all_persons,
                default=[],
                key="person_filter"
            )

    # 应用筛选条件
    filtered_risk_data = batch_risk_analysis

    if risk_filter:
        filtered_risk_data = filtered_risk_data[filtered_risk_data['风险程度'].isin(risk_filter)]

    if region_filter:
        filtered_risk_data = filtered_risk_data[filtered_risk_data['责任区域'].isin(region_filter)]

    if person_filter:
        filtered_risk_data = filtered_risk_data[filtered_risk_data['责任人'].isin(person_filter)]

    # 检查筛选后的数据是否为空
    if filtered_risk_data.empty:
        st.warning("筛选条件下没有符合条件的批次数据。")
    else:
        # 库存风险概览
        st.markdown("### 库存风险总览")

        # 风险批次统计和汇总信息
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_batches = len(filtered_risk_data)
            high_risk_batches = filtered_risk_data[filtered_risk_data['风险程度'].isin(['极高风险', '高风险'])].shape[0]
            high_risk_pct = (high_risk_batches / total_batches * 100) if total_batches > 0 else 0

            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">风险批次数量</p>
                <p class="card-value">{total_batches}</p>
                <p class="card-text">其中高风险{high_risk_batches}个({high_risk_pct:.1f}%)</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            total_value = filtered_risk_data['批次价值'].sum()
            high_risk_value = filtered_risk_data[filtered_risk_data['风险程度'].isin(['极高风险', '高风险'])][
                '批次价值'].sum()
            value_pct = (high_risk_value / total_value * 100) if total_value > 0 else 0

            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">库存价值总额</p>
                <p class="card-value">¥{total_value:,.2f}</p>
                <p class="card-text">高风险价值占比{value_pct:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            avg_age = filtered_risk_data['库龄'].mean()
            max_age = filtered_risk_data['库龄'].max()

            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">平均库龄</p>
                <p class="card-value">{avg_age:.1f}天</p>
                <p class="card-text">最长库龄{max_age}天</p>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            # 计算无清库天数的批次数量
            inf_clearance = sum(1 for x in filtered_risk_data['预计清库天数'] if x == float('inf'))
            clearance_pct = (inf_clearance / total_batches * 100) if total_batches > 0 else 0

            st.markdown(f"""
            <div class="metric-card">
                <p class="card-header">无法清库批次</p>
                <p class="card-value">{inf_clearance}个</p>
                <p class="card-text">占总批次{clearance_pct:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)

        # 库存风险分布可视化
        st.markdown('<div class="sub-header">🚨 风险分布与责任分析</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            # 创建风险分布饼图
            risk_chart = create_risk_distribution_chart(filtered_risk_data)
            if risk_chart:
                st.plotly_chart(risk_chart, use_container_width=True)

        with col2:
            # 责任区域分布
            region_chart = create_responsibility_region_chart(filtered_risk_data)
            if region_chart:
                st.plotly_chart(region_chart, use_container_width=True)

        # 责任人分析
        st.markdown('<div class="sub-header">👤 责任人库存风险分析</div>', unsafe_allow_html=True)

        # 责任人分布图
        person_chart = create_responsibility_person_chart(filtered_risk_data)
        if person_chart:
            st.plotly_chart(person_chart, use_container_width=True)

        # 责任分析解读
        responsibility_explanation = """
        <b>图表解读：</b> 上方图表展示了高风险批次的责任区域和责任人分布情况。蓝色柱表示批次数量，红色线表示批次价值。负责批次数量最多或批次价值最高的区域和人员应优先关注。
        """

        # 添加具体分析
        if not filtered_risk_data.empty:
            # 区域分析
            top_regions = filtered_risk_data['责任区域'].value_counts().head(3)
            if not top_regions.empty:
                regions_str = ', '.join([f"{region}({count}个批次)" for region, count in top_regions.items()])
                responsibility_explanation += f"<br><b>重点责任区域：</b> {regions_str}需要优先处理高风险库存。"

            # 责任人分析
            top_persons = filtered_risk_data['责任人'].value_counts().head(3)
            if not top_persons.empty:
                persons_str = ', '.join([f"{person}({count}个批次)" for person, count in top_persons.items()])
                responsibility_explanation += f"<br><b>重点责任人员：</b> {persons_str}负责的批次风险较高，需要重点关注其预测准确性。"

            # 风险批次成因分析
            if '积压原因' in filtered_risk_data.columns:
                reason_counts = filtered_risk_data['积压原因'].value_counts()
                top_reasons = reason_counts.head(3)
                if not top_reasons.empty:
                    reasons_str = ', '.join([f"{reason}({count}个批次)" for reason, count in top_reasons.items()])
                    responsibility_explanation += f"<br><b>主要积压原因：</b> {reasons_str}，应针对不同原因采取差异化措施。"

            # 添加清库建议
            responsibility_explanation += f"<br><b>行动建议：</b> 针对高风险批次，应优先考虑折价促销或转仓调配；"
            responsibility_explanation += f"加强销售预测培训，尤其是对责任人数量较多的人员；定期进行库存健康度分析，减少库存积压风险。"

        add_chart_explanation(responsibility_explanation)

        # 显示批次详情表格
        st.markdown('<div class="sub-header">📋 批次风险详情表</div>', unsafe_allow_html=True)

        # 显示筛选后的批次风险数据
        if not filtered_risk_data.empty:
            # 选择要显示的列
            display_columns = [
                '产品代码', '批次日期', '批次库存', '库龄', '批次价值', '日均出货',
                '预计清库天数', '风险程度', '责任区域', '责任人', '建议措施'
            ]

            # 确保所有要显示的列都存在于数据中
            display_columns = [col for col in display_columns if col in filtered_risk_data.columns]

            # 格式化预计清库天数列
            filtered_risk_data_display = filtered_risk_data.copy()
            filtered_risk_data_display['预计清库天数'] = filtered_risk_data_display['预计清库天数'].apply(
                lambda x: "无法清库" if x == float('inf') else f"{int(x)}天"
            )


            # 创建带有颜色标记的风险等级列
            def highlight_risk(risk_level):
                if risk_level == '极高风险':
                    return f'<span class="risk-extreme-high">{risk_level}</span>'
                elif risk_level == '高风险':
                    return f'<span class="risk-high">{risk_level}</span>'
                elif risk_level == '中风险':
                    return f'<span class="risk-medium">{risk_level}</span>'
                elif risk_level == '低风险':
                    return f'<span class="risk-low">{risk_level}</span>'
                else:
                    return f'<span class="risk-extreme-low">{risk_level}</span>'


            filtered_risk_data_display['风险程度'] = filtered_risk_data_display['风险程度'].apply(highlight_risk)

            # 显示表格
            st.markdown(filtered_risk_data_display[display_columns].to_html(
                escape=False, index=False, formatters={
                    '批次价值': lambda x: f"¥{x:,.2f}",
                    '日均出货': lambda x: f"{x:.2f}箱/天"
                }
            ), unsafe_allow_html=True)

            # 提供CSV下载功能
            csv_download = filtered_risk_data[display_columns].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="下载风险批次数据CSV",
                data=csv_download,
                file_name="库存风险批次数据.csv",
                mime="text/csv",
                key="download-risk-csv"
            )

            # 添加批次数据解读
            batch_explanation = f"""
            <b>表格说明：</b> 此表格展示了所有符合筛选条件的{len(filtered_risk_data)}个批次的详细风险信息，
            包括产品代码、批次日期、库存量、库龄、批次价值、日均出货量、预计清库天数、风险程度、责任区域、责任人和建议措施。
            可以通过点击表头对任意列进行排序，以便更好地分析和处理库存风险。
            """

            add_chart_explanation(batch_explanation)
        else:
            st.info("没有符合条件的批次数据")

# 页面运行
if __name__ == "__main__":
    # 页面已成功加载，不需要额外的处理
    pass