import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import io
import base64
import math
import time
from datetime import datetime, timedelta
# 在import部分确保导入了re模块
# 确保导入re模块
import re

def get_simplified_product_name(product_code, product_name):
    """从产品名称中提取简化产品名称"""
    try:
        # 确保输入是字符串类型
        if not isinstance(product_name, str):
            return str(product_code)  # 返回产品代码作为备选

        if '口力' in product_name:
            # 提取"口力"之后的产品类型
            name_parts = product_name.split('口力')
            if len(name_parts) > 1:
                name_part = name_parts[1]
                if '-' in name_part:
                    name_part = name_part.split('-')[0].strip()

                # 进一步简化，只保留主要部分（去掉规格和包装形式）
                for suffix in ['G分享装袋装', 'G盒装', 'G袋装', 'KG迷你包', 'KG随手包']:
                    if suffix in name_part:
                        name_part = name_part.split(suffix)[0]
                        break

                # 去掉可能的数字和单位
                simple_name = re.sub(r'\d+\w*\s*', '', name_part).strip()

                if simple_name:  # 确保简化名称不为空
                    return f"{simple_name} ({product_code})"

        # 如果无法提取或处理中出现错误，则返回产品代码
        return str(product_code)
    except Exception as e:
        # 捕获任何异常，确保函数始终返回一个字符串
        print(f"简化产品名称时出错: {str(e)}，产品代码: {product_code}")
        return str(product_code)

# 设置页面配置
st.set_page_config(
    page_title="SAL异常与预警",
    page_icon="⚠️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# 加载自定义CSS样式
# 替换现有的load_css函数
# 替换现有的load_css函数
def load_css():
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
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #f8f9fa;
            border-radius: 4px 4px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1f3867;
            color: white;
        }
        .hover-info {
            background-color: rgba(0,0,0,0.7);
            color: white;
            padding: 8px;
            border-radius: 4px;
            font-size: 0.9rem;
        }
    </style>
    """, unsafe_allow_html=True)


#################################################
# 认证模块
#################################################

def initialize_auth():
    """初始化认证状态"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False


def login_ui():
    """显示登录界面"""
    st.markdown(
        '<div style="font-size: 1.5rem; color: #1f3867; text-align: center; margin-bottom: 1rem;">SAL异常与预警 | 登录</div>',
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
            if password == 'SAL':
                st.session_state.authenticated = True
                st.success("登录成功！")
                st.rerun()
            else:
                st.error("密码错误，请重试！")


def check_authentication():
    """检查用户是否已认证"""
    initialize_auth()

    if not st.session_state.authenticated:
        login_ui()
        return False
    return True


#################################################
# 数据加载器
#################################################

class DataLoader:
    """数据加载和处理类"""

    def __init__(self, data_dir="."):
        """
        初始化数据加载器

        参数:
        data_dir (str): 数据文件目录路径
        """
        self.data_dir = data_dir

        # 文件路径
        self.inventory_file = os.path.join(data_dir, "含批次库存0221(2).xlsx")
        self.shipping_file = os.path.join(data_dir, "2409~250224出货数据.xlsx")
        self.forecast_file = os.path.join(data_dir, "2409~2502人工预测.xlsx")
        self.price_file = os.path.join(data_dir, "单价.xlsx")

        # 数据存储
        self.inventory_data = None
        self.batch_data = None
        self.shipping_data = None
        self.forecast_data = None
        self.price_data = {}
        self.sales_person_region_mapping = {}
        self.product_responsibility = {}

        # 默认区域和责任人
        self.default_regions = ['东', '南', '西', '北', '中']
        self.default_region = '东'
        self.default_person = '系统管理员'

    @st.cache_data
    def load_all_data(_self):
        """加载并预处理所有数据文件"""
        _self.load_inventory_data()
        _self.load_shipping_data()
        _self.load_forecast_data()
        _self.load_price_data()
        _self.create_person_region_mapping()
        _self.create_product_responsibility_mapping()

        return {
            "inventory_data": _self.inventory_data,
            "batch_data": _self.batch_data,
            "shipping_data": _self.shipping_data,
            "forecast_data": _self.forecast_data,
            "price_data": _self.price_data,
            "sales_person_region_mapping": _self.sales_person_region_mapping,
            "product_responsibility": _self.product_responsibility
        }

    def load_inventory_data(self):
        """加载库存数据"""
        try:
            inventory_raw = pd.read_excel(self.inventory_file, header=0)

            # 处理第一层数据（产品信息）
            product_rows = inventory_raw[inventory_raw.iloc[:, 0].notna()]
            self.inventory_data = product_rows.iloc[:, :7].copy()
            self.inventory_data.columns = ['产品代码', '描述', '现有库存', '已分配量',
                                           '现有库存可订量', '待入库量', '本月剩余可订量']

            # 添加简化产品名称
            self.inventory_data['简化产品名称'] = self.inventory_data.apply(
                lambda row: get_simplified_product_name(row['产品代码'], row['描述']),
                axis=1
            )

            # 处理第二层数据（批次信息）
            batch_with_product = []
            product_code = None
            product_description = None
            simplified_name = None

            for i, row in inventory_raw.iterrows():
                if pd.notna(row.iloc[0]):
                    # 这是产品行
                    product_code = row.iloc[0]
                    product_description = row.iloc[1]
                    simplified_name = get_simplified_product_name(product_code, product_description)
                elif pd.notna(row.iloc[7]):
                    # 这是批次行
                    batch_row = row.iloc[7:].copy()
                    batch_row_with_product = pd.Series(
                        [product_code, product_description, simplified_name] + batch_row.tolist())
                    batch_with_product.append(batch_row_with_product)

            self.batch_data = pd.DataFrame(batch_with_product)
            self.batch_data.columns = ['产品代码', '描述', '简化产品名称', '库位', '生产日期', '生产批号', '数量']

            # 转换日期列
            self.batch_data['生产日期'] = pd.to_datetime(self.batch_data['生产日期'])

            return True
        except Exception as e:
            st.error(f"加载库存数据失败: {str(e)}")
            return False

    def load_shipping_data(self):
        """加载出货数据"""
        try:
            self.shipping_data = pd.read_excel(self.shipping_file, header=0)
            self.shipping_data.columns = ['订单日期', '所属区域', '申请人', '产品代码', '数量']

            # 转换日期列
            self.shipping_data['订单日期'] = pd.to_datetime(self.shipping_data['订单日期'])

            # 确保所有数值列为数字类型
            self.shipping_data['数量'] = pd.to_numeric(self.shipping_data['数量'], errors='coerce')
            self.shipping_data = self.shipping_data.dropna(subset=['数量'])

            # 将空的申请人替换为默认责任人
            self.shipping_data['申请人'] = self.shipping_data['申请人'].fillna(self.default_person)

            # 将空的区域替换为默认区域
            self.shipping_data['所属区域'] = self.shipping_data['所属区域'].fillna(self.default_region)

            # 添加简化产品名称 - 需要与inventory_data关联
            if not self.inventory_data is None and not self.inventory_data.empty:
                # 创建产品代码到简化名称的映射
                product_name_map = dict(zip(self.inventory_data['产品代码'], self.inventory_data['简化产品名称']))

                # 应用映射到shipping_data
                self.shipping_data['简化产品名称'] = self.shipping_data['产品代码'].map(
                    lambda x: product_name_map.get(x, get_simplified_product_name(x, ""))
                )
            else:
                # 如果没有库存数据，直接使用产品代码
                self.shipping_data['简化产品名称'] = self.shipping_data['产品代码']

            return True
        except Exception as e:
            st.error(f"加载出货数据失败: {str(e)}")
            return False

    def load_forecast_data(self):
        """加载预测数据"""
        try:
            self.forecast_data = pd.read_excel(self.forecast_file, header=0)

            # 调整预测数据的格式
            if len(self.forecast_data.columns) == 1:
                # 如果是单列，尝试拆分
                columns = ['所属大区', '销售员', '所属年月', '产品代码', '预计销售量']
                self.forecast_data = pd.DataFrame([
                    row.split() for row in self.forecast_data.iloc[:, 0]
                ], columns=columns)
                self.forecast_data['预计销售量'] = self.forecast_data['预计销售量'].astype(float)
            else:
                self.forecast_data.columns = ['所属大区', '销售员', '所属年月', '产品代码', '预计销售量']

            # 转换日期列
            self.forecast_data['所属年月'] = pd.to_datetime(self.forecast_data['所属年月'])

            # 确保预计销售量为数字类型
            self.forecast_data['预计销售量'] = pd.to_numeric(self.forecast_data['预计销售量'], errors='coerce')
            self.forecast_data = self.forecast_data.dropna(subset=['预计销售量'])

            # 将空的大区替换为默认区域
            self.forecast_data['所属大区'] = self.forecast_data['所属大区'].fillna(self.default_region)

            # 将空的销售员替换为默认责任人
            self.forecast_data['销售员'] = self.forecast_data['销售员'].fillna(self.default_person)

            # 添加简化产品名称 - 需要与inventory_data关联
            if not self.inventory_data is None and not self.inventory_data.empty:
                # 创建产品代码到简化名称的映射
                product_name_map = dict(zip(self.inventory_data['产品代码'], self.inventory_data['简化产品名称']))

                # 应用映射到forecast_data
                self.forecast_data['简化产品名称'] = self.forecast_data['产品代码'].map(
                    lambda x: product_name_map.get(x, get_simplified_product_name(x, ""))
                )
            else:
                # 如果没有库存数据，直接使用产品代码
                self.forecast_data['简化产品名称'] = self.forecast_data['产品代码']

            return True
        except Exception as e:
            st.error(f"加载预测数据失败: {str(e)}")
            return False

    def load_price_data(self):
        """加载单价数据"""
        try:
            if os.path.exists(self.price_file):
                price_df = pd.read_excel(self.price_file)
                # 将单价数据转换为字典
                for _, row in price_df.iterrows():
                    self.price_data[row['产品代码']] = row['单价']
            else:
                # 指定的产品单价信息
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
                self.price_data = specified_prices

            return True
        except Exception as e:
            st.error(f"加载单价数据失败: {str(e)}")
            return False

    def create_person_region_mapping(self):
        """创建销售人员与区域的对应关系"""
        # 从出货数据中提取销售人员-区域对应关系
        person_region_counts = self.shipping_data.groupby(['申请人', '所属区域']).size().unstack(fill_value=0)

        # 初始化映射字典
        self.sales_person_region_mapping = {}

        # 对于每个销售人员，找出他们最常用的区域
        for person in self.shipping_data['申请人'].unique():
            # 修改：系统管理员对应区域为空字符串
            if person == self.default_person:
                self.sales_person_region_mapping[person] = ""
            elif person in person_region_counts.index:
                # 找出该人员最常见的区域
                most_common_region = person_region_counts.loc[person].idxmax()
                self.sales_person_region_mapping[person] = most_common_region
            else:
                # 如果没有记录，使用默认区域
                self.sales_person_region_mapping[person] = self.default_region

        # 对预测数据中的销售员也添加区域映射
        for person in self.forecast_data['销售员'].unique():
            # 跳过已处理的系统管理员
            if person == self.default_person:
                continue

            if person not in self.sales_person_region_mapping:
                # 在预测数据中查找该销售员的区域
                person_regions = self.forecast_data[self.forecast_data['销售员'] == person]['所属大区'].unique()
                if len(person_regions) > 0:
                    self.sales_person_region_mapping[person] = person_regions[0]
                else:
                    self.sales_person_region_mapping[person] = self.default_region

        # 确保系统管理员的区域为空字符串
        self.sales_person_region_mapping[self.default_person] = ""

    def create_product_responsibility_mapping(self):
        """创建产品与责任区域、责任人的映射关系"""
        self.product_responsibility = {}

        # 基于出货数据创建产品-区域-责任人映射
        product_region_counts = self.shipping_data.groupby(['产品代码', '所属区域']).size().unstack(fill_value=0)
        product_person_counts = self.shipping_data.groupby(['产品代码', '申请人']).size().unstack(fill_value=0)

        # 对于每个产品，找出最频繁的区域和责任人
        for product_code in self.inventory_data['产品代码'].unique():
            if product_code in product_region_counts.index:
                # 找出该产品最常见的区域
                top_region = product_region_counts.loc[product_code].idxmax()

                # 找出该产品中，该区域最常见的责任人
                region_persons = self.shipping_data[
                    (self.shipping_data['产品代码'] == product_code) &
                    (self.shipping_data['所属区域'] == top_region)
                    ]['申请人'].value_counts()

                if not region_persons.empty:
                    top_person = region_persons.index[0]
                elif product_code in product_person_counts.index:
                    # 如果没找到该区域的责任人，则使用该产品最常见的责任人
                    top_person = product_person_counts.loc[product_code].idxmax()
                else:
                    # 如果没有任何相关记录，使用默认值
                    top_person = self.default_person
            else:
                # 如果产品没有出货记录，使用默认值
                top_region = self.default_region
                top_person = self.default_person

            # 保存映射关系
            # 修改：如果责任人是系统管理员，区域设为空字符串
            if top_person == self.default_person:
                self.product_responsibility[product_code] = {
                    "region": "",
                    "person": top_person
                }
            else:
                self.product_responsibility[product_code] = {
                    "region": top_region,
                    "person": top_person
                }

                # 确保责任人与区域一致（使用我们之前建立的映射）
                if top_person in self.sales_person_region_mapping:
                    # 更新为标准化后的区域
                    self.product_responsibility[product_code]["region"] = self.sales_person_region_mapping[top_person]


#################################################
# 分析引擎
#################################################

class AnalysisEngine:
    """
    批次级别库存积压预警系统分析引擎
    用于分析库存数据、销售数据和预测数据，提供库存积压预警
    集成了责任归属分析，以识别造成库存积压的主要责任人或区域
    """

    def __init__(self, data_dict):
        """
        初始化分析引擎

        参数:
        data_dict (dict): 包含所有加载的数据
        """
        # 从数据字典中提取数据
        self.inventory_data = data_dict["inventory_data"]
        self.batch_data = data_dict["batch_data"]
        self.shipping_data = data_dict["shipping_data"]
        self.forecast_data = data_dict["forecast_data"]
        self.price_data = data_dict["price_data"]
        self.sales_person_region_mapping = data_dict["sales_person_region_mapping"]
        self.product_responsibility = data_dict["product_responsibility"]

        # 设置风险参数
        self.high_stock_days = 90  # 库存超过90天视为高风险
        self.medium_stock_days = 60  # 库存超过60天视为中风险
        self.low_stock_days = 30  # 库存超过30天视为低风险
        self.high_volatility_threshold = 1.0  # 出货波动系数超过1.0视为高波动
        self.medium_volatility_threshold = 0.8  # 出货波动系数超过0.8视为中等波动

        # 预测偏差阈值
        self.high_forecast_bias_threshold = 0.3  # 预测偏差超过30%视为高偏差
        self.medium_forecast_bias_threshold = 0.15  # 预测偏差超过15%视为中等偏差
        self.max_forecast_bias = 1.0  # 预测偏差最大值

        # 清库天数阈值
        self.high_clearance_days = 90  # 预计清库天数超过90天视为高风险
        self.medium_clearance_days = 60  # 预计清库天数超过60天视为中风险
        self.low_clearance_days = 30  # 预计清库天数超过30天视为低风险

        # 最小日均销量阈值，防止清库天数计算为无穷大
        self.min_daily_sales = 0.5  # 每天至少0.5件的销售量
        # 季节性指数下限，防止由于季节性太低导致调整后销量接近零
        self.min_seasonal_index = 0.3  # 季节性指数最低为0.3

        # 责任归属分析权重参数
        self.forecast_accuracy_weight = 0.25  # 预测准确性在责任判定中的权重
        self.recent_sales_weight = 0.30  # 最近销售在责任判定中的权重
        self.ordering_history_weight = 0.25  # 历史订货在责任判定中的权重
        self.market_performance_weight = 0.20  # 市场表现权重

        # 订单历史数据（直接使用出货数据）
        self.orders_data = self.shipping_data.copy()
        self.orders_data['订单数量'] = self.orders_data['数量']

        # 分析结果存储
        self.batch_analysis = None
        self.risk_assessment = None

        # 颜色定义
        self.risk_colors = {
            '极高风险': '#FF0000',  # 红色
            '高风险': '#FF5252',  # 浅红色
            '中风险': '#FFC107',  # 黄色
            '低风险': '#4CAF50',  # 绿色
            '极低风险': '#2196F3'  # 蓝色
        }

        # 风险等级排序
        self.risk_order = {
            "极高风险": 0,
            "高风险": 1,
            "中风险": 2,
            "低风险": 3,
            "极低风险": 4
        }

    def calculate_risk_percentage(self, days_to_clear, batch_age, target_days):
        """
        计算风险百分比

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

    def calculate_forecast_bias(self, forecast_quantity, actual_sales):
        """
        计算预测偏差

        参数:
        forecast_quantity (float): 预测销量
        actual_sales (float): 实际销量

        返回:
        float: 预测偏差比例（正值表示预测高于实际，负值表示预测低于实际）
        """
        # 当前期间的预测偏差计算
        if actual_sales == 0 and forecast_quantity == 0:
            return 0.0  # 无预测无销售，无偏差
        elif actual_sales == 0:
            # 有预测无销售，根据预测量大小返回有上限的偏差
            return min(math.sqrt(forecast_quantity) / (forecast_quantity), self.max_forecast_bias)
        elif forecast_quantity == 0:
            # 无预测有销售，返回负偏差
            return -min(math.sqrt(actual_sales) / (actual_sales), self.max_forecast_bias)
        else:
            # 使用均方根百分比误差(RMSPE)变体，对大小误差更敏感
            if forecast_quantity > actual_sales:
                # 预测过高
                normalized_error = (forecast_quantity - actual_sales) / actual_sales
                # 使用非线性衰减函数，降低大数值效应
                return min(math.tanh(normalized_error), self.max_forecast_bias)
            else:
                # 预测过低
                normalized_error = (actual_sales - forecast_quantity) / forecast_quantity
                # 同样使用非线性衰减
                return -min(math.tanh(normalized_error), self.max_forecast_bias)

    def analyze_responsibility_collaborative(self, product_code, batch_date, batch_qty=0):
        """
        责任归属分析

        参数:
        product_code (str): 产品代码
        batch_date (datetime): 批次生产日期
        batch_qty (float): 批次库存数量

        返回:
        tuple: (主要责任区域, 主要责任人, 责任分析详情)
        """
        today = datetime.now().date()
        batch_date = batch_date.date()

        # 获取产品的默认责任映射
        default_mapping = self.product_responsibility.get(product_code,
                                                          {"region": "", "person": "系统管理员"})

        # 1. 获取相关数据
        # ===============================

        # 1.1 获取批次生产前后的预测记录
        forecast_start_date = batch_date - timedelta(days=90)
        forecast_end_date = batch_date + timedelta(days=30)

        product_forecasts = self.forecast_data[
            (self.forecast_data['产品代码'] == product_code) &
            (self.forecast_data['所属年月'].dt.date >= forecast_start_date) &
            (self.forecast_data['所属年月'].dt.date <= forecast_end_date)
            ]

        # 1.2 获取批次生产后的实际销售记录
        sales_start_date = batch_date
        sales_end_date = min(today, batch_date + timedelta(days=90))

        product_sales = self.shipping_data[
            (self.shipping_data['产品代码'] == product_code) &
            (self.shipping_data['订单日期'].dt.date >= sales_start_date) &
            (self.shipping_data['订单日期'].dt.date <= sales_end_date)
            ]

        # 2. 初始化责任评分系统
        # ===============================
        person_scores = {}
        region_scores = {}
        responsibility_details = {}

        # 3. 预测与销售差异分析 (60%)
        # ===============================
        forecast_sales_discrepancy_weight = 0.60
        forecast_responsibility_details = {}

        if not product_forecasts.empty:
            # 计算批次相关的总预测量 (所有人员)
            total_forecast = product_forecasts['预计销售量'].sum()

            # 计算批次相关的总实际销量
            total_actual_sales = product_sales['数量'].sum() if not product_sales.empty else 0

            # 总体履行率
            overall_fulfillment_rate = total_actual_sales / total_forecast if total_forecast > 0 else 1.0

            # 按销售人员分组统计预测总量
            person_forecast_totals = product_forecasts.groupby('销售员')['预计销售量'].sum()

            # 按销售人员分组统计实际销售总量
            person_sales = {}
            for person in person_forecast_totals.index:
                # 获取该销售人员的实际销售记录
                person_actual_sales = product_sales[product_sales['申请人'] == person]['数量'].sum() \
                    if not product_sales.empty else 0
                person_sales[person] = person_actual_sales

            # 如果整体履行率低于80%，说明存在库存积压问题
            if overall_fulfillment_rate < 0.8:
                # 为每个预测者分配责任
                for person, forecast_qty in person_forecast_totals.items():
                    # 该人员的预测占总预测的比例
                    forecast_proportion = forecast_qty / total_forecast

                    # 该人员的实际销售量
                    actual_sales = person_sales.get(person, 0)

                    # 该人员的销售履行率
                    fulfillment_rate = actual_sales / forecast_qty if forecast_qty > 0 else 1.0

                    # 计算基础责任分数
                    base_score = (1 - fulfillment_rate) * forecast_proportion

                    # 根据预测量大小和履行率调整责任权重
                    if forecast_proportion > 0.5:  # 主要预测者
                        if fulfillment_rate < 0.6:  # 履行率很低
                            adjusted_score = base_score * 2.0
                        else:  # 履行率尚可
                            adjusted_score = base_score * 1.5
                    elif forecast_proportion > 0.2:  # 重要预测者
                        if fulfillment_rate < 0.6:  # 履行率很低
                            adjusted_score = base_score * 1.5
                        else:  # 履行率尚可
                            adjusted_score = base_score * 1.2
                    else:  # 次要预测者
                        adjusted_score = base_score * 1.0

                    # 计算最终责任分数
                    final_score = adjusted_score * forecast_sales_discrepancy_weight

                    # 更新人员责任分数
                    person_scores[person] = person_scores.get(person, 0) + final_score

                    # 获取该人员的区域
                    person_region = self.sales_person_region_mapping.get(person, default_mapping["region"])
                    region_scores[person_region] = region_scores.get(person_region, 0) + (final_score * 0.8)

                    # 记录详细计算过程
                    forecast_responsibility_details[person] = {
                        "forecast_quantity": forecast_qty,
                        "forecast_proportion": forecast_proportion,
                        "actual_sales": actual_sales,
                        "fulfillment_rate": fulfillment_rate,
                        "responsibility_score": final_score,
                        "calculation_factors": {
                            "base_score": base_score,
                            "adjustment_factor": adjusted_score / base_score if base_score > 0 else 1.0
                        }
                    }

            responsibility_details["forecast_responsibility"] = forecast_responsibility_details

        # 4. 销售响应及时性分析 (25%)
        # ===============================
        sales_response_weight = 0.25
        response_responsibility_details = {}

        if not product_sales.empty:
            # 计算从批次生产到首次销售的响应时间
            first_sales_dates = product_sales.groupby('申请人')['订单日期'].min()

            for person in first_sales_dates.index:
                first_sale_date = first_sales_dates[person].date()
                response_days = (first_sale_date - batch_date).days

                # 销售响应及时性评分 - 响应越慢责任越大
                if response_days > 45:  # 45天以上才有首次销售
                    timeliness_score = sales_response_weight * 1.0
                elif response_days > 30:  # 30-45天有首次销售
                    timeliness_score = sales_response_weight * 0.8
                elif response_days > 15:  # 15-30天有首次销售
                    timeliness_score = sales_response_weight * 0.5
                else:  # 15天内有销售响应
                    timeliness_score = sales_response_weight * 0.2

                # 更新人员责任分数
                person_scores[person] = person_scores.get(person, 0) + timeliness_score

                # 获取该人员的区域
                person_region = self.sales_person_region_mapping.get(person, default_mapping["region"])
                region_scores[person_region] = region_scores.get(person_region, 0) + (timeliness_score * 0.8)

                # 记录详细信息
                response_responsibility_details[person] = {
                    "first_sale_date": first_sale_date,
                    "response_days": response_days,
                    "timeliness_score": timeliness_score
                }

        responsibility_details["response_responsibility"] = response_responsibility_details

        # 5. 订单历史与批次关联度 (15%)
        # ===============================
        ordering_relation_weight = 0.15
        order_responsibility_details = {}

        # 获取批次生产前的订单记录
        pre_batch_orders = self.orders_data[
            (self.orders_data['产品代码'] == product_code) &
            (self.orders_data['订单日期'].dt.date <= batch_date) &
            (self.orders_data['订单日期'].dt.date >= batch_date - timedelta(days=60))
            ]

        if not pre_batch_orders.empty:
            # 按人员统计订单量
            person_order_totals = pre_batch_orders.groupby('申请人')['订单数量'].sum()
            total_orders = person_order_totals.sum()

            for person, order_qty in person_order_totals.items():
                # 订单占比
                order_proportion = order_qty / total_orders

                # 责任评分 - 订单比例越高，责任越大
                order_score = ordering_relation_weight * order_proportion

                # 更新人员责任分数
                person_scores[person] = person_scores.get(person, 0) + order_score

                # 获取该人员的区域
                person_region = self.sales_person_region_mapping.get(person, default_mapping["region"])
                region_scores[person_region] = region_scores.get(person_region, 0) + (order_score * 0.8)

                # 记录详细信息
                order_responsibility_details[person] = {
                    "order_quantity": order_qty,
                    "order_proportion": order_proportion,
                    "order_score": order_score
                }

        responsibility_details["order_responsibility"] = order_responsibility_details

        # 6. 责任共担机制 - 计算库存责任分配
        # ===============================

        # 如果没有找到足够责任信息，使用默认责任
        if not person_scores:
            person_scores[default_mapping["person"]] = 1.0
            region_scores[default_mapping["region"]] = 1.0

        # 计算库存责任分配
        person_allocations = {}
        if forecast_responsibility_details and batch_qty > 0:
            # 1. 创建预测差值字典：计算每人预测与实际销售的差额
            forecast_deltas = {}
            total_delta = 0
            for person, details in forecast_responsibility_details.items():
                forecast_qty = details.get("forecast_quantity", 0)
                actual_sales = details.get("actual_sales", 0)
                # 计算"未兑现的预测"，即预测量超出实际销售的部分
                delta = max(0, forecast_qty - actual_sales)

                # 只有预测大于实际销售的人才承担直接责任
                if delta > 0:
                    forecast_deltas[person] = delta
                    total_delta += delta

            # 2. 按预测差值分配库存（基于"谁预测谁负责"原则）
            if total_delta > 0:
                # 第一轮：按未兑现的预测量分配库存
                allocated_total = 0
                for person, delta in forecast_deltas.items():
                    # 按差值比例分配
                    proportion = delta / total_delta
                    allocation = int(batch_qty * proportion)
                    # 确保结果合理
                    allocation = max(1, allocation)
                    allocation = min(allocation, batch_qty - allocated_total)

                    person_allocations[person] = allocation
                    allocated_total += allocation

                # 检查是否还有剩余库存未分配
                remaining_qty = batch_qty - allocated_total

                # 如果所有有预测的人分配完后还有剩余，将剩余部分按比例再分配给有预测的人
                if remaining_qty > 0 and forecast_deltas:
                    # 按比例分配剩余部分
                    remaining_allocated = 0
                    sorted_forecast_persons = sorted(forecast_deltas.items(), key=lambda x: x[1], reverse=True)

                    for i, (person, _) in enumerate(sorted_forecast_persons):
                        if i == len(sorted_forecast_persons) - 1:
                            # 最后一人获得所有剩余
                            person_allocations[person] += (remaining_qty - remaining_allocated)
                        else:
                            additional = int(remaining_qty * (forecast_deltas[person] / total_delta))
                            additional = max(0, additional)
                            additional = min(additional, remaining_qty - remaining_allocated)
                            person_allocations[person] += additional
                            remaining_allocated += additional
            else:
                # 如果没有正的预测差值，找出有预测的人按预测量比例分配
                forecasters = {p: details.get("forecast_quantity", 0)
                               for p, details in forecast_responsibility_details.items()
                               if details.get("forecast_quantity", 0) > 0}

                if forecasters:
                    total_forecast = sum(forecasters.values())
                    allocated_total = 0

                    for person, forecast_qty in sorted(forecasters.items(), key=lambda x: x[1], reverse=True):
                        if len(forecasters) == 1:
                            # 只有一个预测者，获得全部数量
                            person_allocations[person] = batch_qty
                        else:
                            # 按预测比例分配
                            proportion = forecast_qty / total_forecast
                            allocation = int(batch_qty * proportion)
                            # 确保结果合理
                            allocation = max(1, allocation)
                            allocation = min(allocation, batch_qty - allocated_total)

                            person_allocations[person] = allocation
                            allocated_total += allocation

                    # 确保所有库存都分配完毕
                    if allocated_total < batch_qty and forecasters:
                        # 将剩余库存分配给预测量最高的人
                        top_forecaster = max(forecasters.items(), key=lambda x: x[1])[0]
                        person_allocations[top_forecaster] += (batch_qty - allocated_total)
                else:
                    # 如果完全没有预测者，分配给主要责任人
                    person_allocations[default_mapping["person"]] = batch_qty
        else:
            # 如果没有预测数据或批次数量为0
            max_person = max(person_scores.items(), key=lambda x: x[1])[0] if person_scores else default_mapping[
                "person"]
            person_allocations[max_person] = batch_qty

        # 7. 确定主要责任人和区域
        # ===============================

        # 根据应承担库存数量确定主要责任人
        if person_allocations:
            # 找出应承担库存数量最多的人作为主要责任人
            responsible_person = max(person_allocations.items(), key=lambda x: x[1])[0]

            # 获取该人员的标准区域
            if responsible_person in self.sales_person_region_mapping:
                # 如果是系统管理员，区域留空
                if responsible_person == "系统管理员":  # 使用默认名称
                    responsible_region = ""
                else:
                    responsible_region = self.sales_person_region_mapping[responsible_person]
            else:
                # 如果找不到映射，使用得分最高的区域
                responsible_region = max(region_scores.items(), key=lambda x: x[1])[0] if region_scores else ""
                # 如果是系统管理员，区域留空
                if responsible_person == "系统管理员":  # 使用默认名称
                    responsible_region = ""
        else:
            responsible_person = default_mapping["person"]
            # 如果是系统管理员，区域留空
            if responsible_person == "系统管理员":  # 使用默认名称
                responsible_region = ""
            else:
                responsible_region = default_mapping["region"]

        # 8. 构建最终责任分析详情
        # ===============================

        # 确定共同责任人 - 得分超过最高分60%的人员都算共同责任人
        responsible_persons = list(person_allocations.keys())

        # 限制共同责任人数量，但确保至少包含得分最高的人
        if len(responsible_persons) > 5:
            # 按库存分配量排序
            sorted_persons = sorted([(p, person_allocations[p]) for p in responsible_persons],
                                    key=lambda x: x[1], reverse=True)
            responsible_persons = [p[0] for p in sorted_persons[:5]]

        # 次要责任人 - 主要责任人之外的其他责任人
        secondary_persons = [p for p in responsible_persons if p != responsible_person]

        # 区域责任
        responsible_regions = []
        for p in responsible_persons:
            if p == "系统管理员":  # 使用默认名称
                # 系统管理员不添加区域
                continue
            region = self.sales_person_region_mapping.get(p, default_mapping["region"])
            if region and region not in responsible_regions:
                responsible_regions.append(region)

        # 次要责任区域
        secondary_regions = [r for r in responsible_regions if r != responsible_region]

        # 构建完整的责任分析结果
        responsibility_analysis = {
            "responsible_person": responsible_person,
            "responsible_region": responsible_region,
            "responsible_persons": responsible_persons,
            "secondary_persons": secondary_persons,
            "responsible_regions": responsible_regions,
            "secondary_regions": secondary_regions,
            "person_scores": person_scores,
            "region_scores": region_scores,
            "responsibility_details": responsibility_details,
            "quantity_allocation": {
                "batch_qty": batch_qty,
                "person_allocations": person_allocations,
                "allocation_logic": "责任库存严格基于预测未兑现量(预测-实际销量)分配，预测量为0的人不承担任何库存责任"
            },
            "batch_info": {
                "batch_date": batch_date,
                "batch_age": (today - batch_date).days,
                "batch_qty": batch_qty
            }
        }

        return (responsible_region, responsible_person, responsibility_analysis)

    def generate_responsibility_summary(self, responsibility_analysis):
        """
        根据责任分析详情生成摘要

        参数:
        responsibility_analysis (dict): 责任分析详情

        返回:
        str: 责任分析摘要
        """
        if not responsibility_analysis:
            return "无法确定责任"

        responsible_person = responsibility_analysis.get("responsible_person", "系统管理员")
        secondary_persons = responsibility_analysis.get("secondary_persons", [])
        person_allocations = responsibility_analysis.get("quantity_allocation", {}).get("person_allocations", {})
        responsibility_details = responsibility_analysis.get("responsibility_details", {})

        # 构建主要责任人的责任原因
        main_person_reasons = []

        # 检查主要责任人的预测情况
        forecast_responsibility = responsibility_details.get("forecast_responsibility", {})
        if responsible_person in forecast_responsibility:
            person_forecast = forecast_responsibility[responsible_person]
            forecast_qty = person_forecast.get("forecast_quantity", 0)
            actual_sales = person_forecast.get("actual_sales", 0)
            fulfillment = person_forecast.get("fulfillment_rate", 1.0) * 100
            unfulfilled = max(0, forecast_qty - actual_sales)

            if forecast_qty > 0:
                main_person_reasons.append(
                    f"预测{forecast_qty:.0f}件但仅销售{actual_sales:.0f}件(履行率{fulfillment:.0f}%)")

            if unfulfilled > 0:
                main_person_reasons.append(f"未兑现预测{unfulfilled:.0f}件")

        # 如果没有预测但有其他责任原因
        if not main_person_reasons:
            # 检查响应及时性
            response_responsibility = responsibility_details.get("response_responsibility", {})
            if responsible_person in response_responsibility:
                days = response_responsibility[responsible_person].get("response_days", 0)
                if days > 30:
                    main_person_reasons.append(f"销售响应延迟({days}天)")

            # 检查订单历史
            order_responsibility = responsibility_details.get("order_responsibility", {})
            if responsible_person in order_responsibility:
                order_pct = order_responsibility[responsible_person].get("order_proportion", 0) * 100
                if order_pct > 20:
                    main_person_reasons.append(f"订单占比高({order_pct:.0f}%)")

        # 如果没有特定原因，添加一个通用原因
        if not main_person_reasons:
            main_person_reasons.append("综合预测与销售因素")

        # 构建其他责任人的摘要
        other_persons_data = []

        # 处理次要责任人
        for person in secondary_persons:
            if person != responsible_person:
                allocated_qty = person_allocations.get(person, 0)

                # 获取责任原因
                reason = ""

                # 检查预测情况
                if person in forecast_responsibility:
                    forecast_info = forecast_responsibility[person]
                    forecast_qty = forecast_info.get("forecast_quantity", 0)
                    actual_sales = forecast_info.get("actual_sales", 0)
                    fulfillment = forecast_info.get("fulfillment_rate", 1.0) * 100
                    unfulfilled = max(0, forecast_qty - actual_sales)

                    if unfulfilled > 0:
                        reason = f"未兑现预测{unfulfilled:.0f}件"
                    elif forecast_qty > 0 and fulfillment < 100:
                        reason = f"履行率低({fulfillment:.0f}%)"
                # 检查响应及时性
                elif person in response_responsibility:
                    days = response_responsibility[person].get("response_days", 0)
                    if days > 30:
                        reason = f"响应延迟({days}天)"
                    else:
                        reason = "有销售记录"
                # 检查订单历史
                elif person in order_responsibility:
                    reason = "订单关联"
                # 如果都没有，使用通用原因
                else:
                    reason = "责任共担"

                # 添加到待排序列表
                other_persons_data.append((person, reason, allocated_qty))

        # 确保也包括那些不在 secondary_persons 但在 person_allocations 中的人
        for person, allocated_qty in person_allocations.items():
            if person != responsible_person and person not in secondary_persons and allocated_qty > 0:
                # 获取责任原因，逻辑同上
                reason = ""
                if person in forecast_responsibility:
                    forecast_info = forecast_responsibility[person]
                    forecast_qty = forecast_info.get("forecast_quantity", 0)
                    actual_sales = forecast_info.get("actual_sales", 0)
                    fulfillment = forecast_info.get("fulfillment_rate", 1.0) * 100
                    unfulfilled = max(0, forecast_qty - actual_sales)

                    if unfulfilled > 0:
                        reason = f"未兑现预测{unfulfilled:.0f}件"
                    elif forecast_qty > 0 and fulfillment < 100:
                        reason = f"履行率低({fulfillment:.0f}%)"
                elif person in response_responsibility:
                    days = response_responsibility[person].get("response_days", 0)
                    if days > 30:
                        reason = f"响应延迟({days}天)"
                    else:
                        reason = "有销售记录"
                elif person in order_responsibility:
                    reason = "订单关联"
                else:
                    reason = "责任共担"

                other_persons_data.append((person, reason, allocated_qty))

        # 严格按照应承担库存数量降序排序
        other_persons_data.sort(key=lambda x: x[2], reverse=True)

        # 转换为摘要文本
        other_persons_summary = [f"{person}({reason}，承担{qty}件)" for person, reason, qty in other_persons_data]

        # 生成最终摘要
        main_reason = "、".join(main_person_reasons)

        # 添加主要责任人需要承担的库存数量信息
        if responsible_person in person_allocations and person_allocations[responsible_person] > 0:
            main_responsibility_qty = person_allocations[responsible_person]
            main_person_with_qty = f"{responsible_person}主要责任({main_reason}，承担{main_responsibility_qty}件)"
        else:
            # 即使没有库存分配也添加0件
            main_person_with_qty = f"{responsible_person}主要责任({main_reason}，承担0件)"

        if other_persons_summary:
            others_text = "，".join(other_persons_summary)
            summary = f"{main_person_with_qty}，共同责任：{others_text}"
        else:
            summary = main_person_with_qty

        return summary

    @st.cache_data
    def analyze_data(_self, filtered_data=None):
        """
        分析数据并生成指标

        参数:
        filtered_data (tuple): 包含筛选后的批次数据和出货数据，格式为(filtered_batch_data, filtered_shipping_data)

        返回:
        DataFrame: 批次分析结果
        """
        # 使用原始数据或筛选后的数据
        batch_data_to_analyze = _self.batch_data
        shipping_data_to_analyze = _self.shipping_data

        if filtered_data and isinstance(filtered_data, tuple) and len(filtered_data) == 2:
            filtered_batch_data, filtered_shipping_data = filtered_data
            if filtered_batch_data is not None and not filtered_batch_data.empty:
                batch_data_to_analyze = filtered_batch_data
            if filtered_shipping_data is not None and not filtered_shipping_data.empty:
                shipping_data_to_analyze = filtered_shipping_data

        # 为每个产品批次计算关键指标
        batch_analysis = []
        today = datetime.now().date()

        # 计算每个产品的销售指标
        product_sales_metrics = {}
        for product_code in _self.inventory_data['产品代码'].unique():
            # 获取该产品的销售记录
            product_sales = shipping_data_to_analyze[shipping_data_to_analyze['产品代码'] == product_code]

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
                total_sales = product_sales['数量'].sum()

                # 计算过去90天的销量
                ninety_days_ago = today - timedelta(days=90)
                recent_sales = product_sales[product_sales['订单日期'].dt.date >= ninety_days_ago]
                recent_sales_total = recent_sales['数量'].sum() if len(recent_sales) > 0 else 0

                # 计算日均销量
                # 使用从最早订单到今天的天数作为分母
                days_range = (today - product_sales['订单日期'].min().date()).days + 1
                daily_avg_sales = total_sales / days_range if days_range > 0 else 0

                # 计算日销量标准差
                # 首先构建每日销量时间序列
                daily_sales = product_sales.groupby(product_sales['订单日期'].dt.date)['数量'].sum()

                # 计算标准差
                sales_std = daily_sales.std() if len(daily_sales) > 1 else 0

                # 计算变异系数（波动系数）
                coefficient_of_variation = sales_std / daily_avg_sales if daily_avg_sales > 0 else float('inf')

                # 按区域和销售人员分组统计
                region_sales = product_sales.groupby('所属区域')['数量'].sum().to_dict()
                person_sales = product_sales.groupby('申请人')['数量'].sum().to_dict()

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
        for product_code in _self.inventory_data['产品代码'].unique():
            product_sales = shipping_data_to_analyze[shipping_data_to_analyze['产品代码'] == product_code]

            if len(product_sales) > 0:
                # 按月分组销量 - 修复SettingWithCopyWarning
                product_sales_copy = product_sales.copy()
                product_sales_copy.loc[:, '月份'] = product_sales_copy['订单日期'].dt.month
                monthly_sales = product_sales_copy.groupby('月份')['数量'].sum()

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
            seasonal_index = max(seasonal_index, _self.min_seasonal_index)
            seasonal_indices[product_code] = seasonal_index

        # 计算每个产品的预测准确度
        forecast_accuracy = {}
        for product_code in _self.inventory_data['产品代码'].unique():
            product_forecast = _self.forecast_data[_self.forecast_data['产品代码'] == product_code]

            if len(product_forecast) > 0:
                # 获取预测销量
                forecast_quantity = product_forecast['预计销售量'].sum()

                # 获取实际销量（最近一个月）
                one_month_ago = today - timedelta(days=30)
                product_recent_sales = shipping_data_to_analyze[
                    (shipping_data_to_analyze['产品代码'] == product_code) &
                    (shipping_data_to_analyze['订单日期'].dt.date >= one_month_ago)
                    ]

                # 确保实际销量有合理值
                actual_sales = product_recent_sales['数量'].sum() if not product_recent_sales.empty else 0

                # 计算预测偏差
                forecast_bias = _self.calculate_forecast_bias(forecast_quantity, actual_sales)

                # 按区域分组的预测
                region_forecast = product_forecast.groupby('所属大区')['预计销售量'].sum().to_dict()

                # 按销售员分组的预测
                person_forecast = product_forecast.groupby('销售员')['预计销售量'].sum().to_dict()

                # 计算每个销售员的预测偏差
                person_bias = {}
                for person, forecast_qty in person_forecast.items():
                    # 获取该人员的最近销售记录
                    person_recent_sales = product_recent_sales[product_recent_sales['申请人'] == person]['数量'].sum() \
                        if not product_recent_sales.empty else 0

                    # 计算个人预测偏差
                    person_bias[person] = _self.calculate_forecast_bias(forecast_qty, person_recent_sales)
            else:
                # 无预测数据时
                forecast_bias = 0.0  # 默认无偏差
                region_forecast = {}
                person_forecast = {}
                person_bias = {}

            forecast_accuracy[product_code] = {
                'forecast_bias': forecast_bias,
                'region_forecast': region_forecast,
                'person_forecast': person_forecast,
                'person_bias': person_bias
            }

        # 计算每个批次的指标
        for _, batch in batch_data_to_analyze.iterrows():
            product_code = batch['产品代码']
            description = batch['描述']

            # 获取简化产品名称
            if '简化产品名称' in batch.index:
                simplified_name = batch['简化产品名称']
            else:
                # 如果批次数据中没有简化名称，尝试从inventory_data获取
                product_in_inventory = _self.inventory_data[_self.inventory_data['产品代码'] == product_code]
                if not product_in_inventory.empty and '简化产品名称' in product_in_inventory.columns:
                    simplified_name = product_in_inventory['简化产品名称'].iloc[0]
                else:
                    # 如果找不到，使用get_simplified_product_name函数生成
                    simplified_name = get_simplified_product_name(product_code, description)

            batch_date = batch['生产日期']
            batch_qty = batch['数量']

            # 计算库龄（从生产日期到今天的天数）
            batch_age = (today - batch_date.date()).days

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

            # 获取预测准确度
            forecast_info = forecast_accuracy.get(product_code, {
                'forecast_bias': 0.0,
                'region_forecast': {},
                'person_forecast': {},
                'person_bias': {}
            })

            # 获取产品单价并计算批次价值
            unit_price = _self.price_data.get(product_code, 50.0)
            batch_value = batch_qty * unit_price

            # 计算预计清库天数
            daily_avg_sales = sales_metrics['daily_avg_sales']

            # 考虑季节性调整，并应用最小销量阈值
            daily_avg_sales_adjusted = max(daily_avg_sales * seasonal_index, _self.min_daily_sales)

            # 计算清库天数和积压风险
            if daily_avg_sales_adjusted > 0:
                days_to_clear = batch_qty / daily_avg_sales_adjusted

                # 使用改进的风险计算方法
                one_month_risk = _self.calculate_risk_percentage(days_to_clear, batch_age, 30)
                two_month_risk = _self.calculate_risk_percentage(days_to_clear, batch_age, 60)
                three_month_risk = _self.calculate_risk_percentage(days_to_clear, batch_age, 90)
            else:
                days_to_clear = float('inf')
                one_month_risk = 100
                two_month_risk = 100
                three_month_risk = 100

            # 使用基于多人责任共担的责任归属分析方法，传递批次库存数量
            responsible_region, responsible_person, responsibility_details = _self.analyze_responsibility_collaborative(
                product_code, batch_date, batch_qty
            )

            # 生成责任分析摘要
            responsibility_summary = _self.generate_responsibility_summary(responsibility_details)

            # 计算销量占比（该产品销量在所有产品中的占比）
            total_all_sales = sum([metrics['total_sales'] for metrics in product_sales_metrics.values()])
            product_total_sales = sales_metrics['total_sales']
            sales_proportion = (product_total_sales / total_all_sales * 100) if total_all_sales > 0 else 0

            # 确定积压原因
            stocking_reasons = []
            if batch_age > 60:
                stocking_reasons.append("库龄过长")
            if sales_metrics['coefficient_of_variation'] > _self.high_volatility_threshold:
                stocking_reasons.append("销量波动大")
            if seasonal_index < 0.8:
                stocking_reasons.append("季节性影响")
            if abs(forecast_info['forecast_bias']) > _self.high_forecast_bias_threshold:
                stocking_reasons.append("预测偏差大")
            if not stocking_reasons:
                stocking_reasons.append("正常库存")

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

            # 预测偏差 (0-10分) - 使用绝对值评估偏差大小
            if abs(forecast_info['forecast_bias']) > 0.5:  # 50%以上偏差
                risk_score += 10
            elif abs(forecast_info['forecast_bias']) > 0.3:  # 30%以上偏差
                risk_score += 8
            elif abs(forecast_info['forecast_bias']) > 0.15:  # 15%以上偏差
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

            # 格式化预测偏差为百分比
            forecast_bias_value = forecast_info['forecast_bias']
            if forecast_bias_value == float('inf'):
                forecast_bias_pct = "无穷大"
            elif forecast_bias_value == 0:
                forecast_bias_pct = "0%"
            else:
                # 转换为易于理解的百分比格式，正负值表示方向
                forecast_bias_pct = f"{round(forecast_bias_value * 100, 1)}%"

            # 将分析结果添加到列表
            batch_analysis.append({
                '物料': product_code,
                '描述': description,
                '简化产品名称': simplified_name,  # 添加简化产品名称
                '批次日期': batch_date.date(),
                '批次库存': batch_qty,
                '库龄': batch_age,
                '批次价值': batch_value,
                '日均出货': round(daily_avg_sales, 2),
                '出货标准差': round(sales_metrics['sales_std'], 2),
                '出货波动系数': round(sales_metrics['coefficient_of_variation'], 2),
                '预计清库天数': days_to_clear if days_to_clear != float('inf') else float('inf'),
                '一个月积压风险': f"{round(one_month_risk, 1)}%",
                '两个月积压风险': f"{round(two_month_risk, 1)}%",
                '三个月积压风险': f"{round(three_month_risk, 1)}%",
                '积压原因': '，'.join(stocking_reasons),
                '季节性指数': round(seasonal_index, 2),
                '预测偏差': forecast_bias_pct,
                '责任区域': responsible_region,
                '责任人': responsible_person,
                '责任详情': responsibility_details,
                '责任分析摘要': responsibility_summary,
                '风险程度': risk_level,
                '风险得分': risk_score,
                '建议措施': recommendation
            })

        # 转换为DataFrame
        batch_analysis_df = pd.DataFrame(batch_analysis)

        # 按照风险程度和库龄排序
        if not batch_analysis_df.empty:
            batch_analysis_df['风险排序'] = batch_analysis_df['风险程度'].map(_self.risk_order)
            batch_analysis_df = batch_analysis_df.sort_values(by=['风险排序', '库龄'], ascending=[True, False])
            batch_analysis_df = batch_analysis_df.drop(columns=['风险排序'])

        # 缓存分析结果
        _self.batch_analysis = batch_analysis_df

        return batch_analysis_df

    def get_risk_summary(self):
        """获取风险等级分布统计"""
        if self.batch_analysis is None or self.batch_analysis.empty:
            return {
                "极高风险": 0,
                "高风险": 0,
                "中风险": 0,
                "低风险": 0,
                "极低风险": 0
            }

        risk_counts = self.batch_analysis['风险程度'].value_counts().to_dict()

        # 确保所有风险等级都有值
        all_risks = {"极高风险": 0, "高风险": 0, "中风险": 0, "低风险": 0, "极低风险": 0}
        all_risks.update(risk_counts)

        return all_risks

    def get_age_clearance_data(self, risk_filter=None):
        """
        获取库龄和清库分析数据

        参数:
        risk_filter (list): 风险等级筛选列表

        返回:
        DataFrame: 筛选后的数据
        """
        if self.batch_analysis is None or self.batch_analysis.empty:
            return pd.DataFrame()

        # 应用风险筛选
        if risk_filter and isinstance(risk_filter, list) and len(risk_filter) > 0:
            data = self.batch_analysis[self.batch_analysis['风险程度'].isin(risk_filter)]
        else:
            data = self.batch_analysis

        # 处理清库天数为无穷大的情况
        data = data.copy()  # 创建副本以避免SettingWithCopyWarning
        data['清库天数值'] = data['预计清库天数'].apply(
            lambda x: float('inf') if x == '∞' or x == float('inf') else float(x)
        )

        # 排序并返回数据
        return data.sort_values(by=['库龄'], ascending=False)

    # 替换现有的get_forecast_bias_data函数
    def get_forecast_bias_data(self):
        """获取预测偏差分析数据"""
        if self.batch_analysis is None or self.batch_analysis.empty:
            return pd.DataFrame()

        try:
            # 制作预测偏差数据的副本
            bias_data = self.batch_analysis.copy()

            # 确保'预测偏差'列存在
            if '预测偏差' not in bias_data.columns:
                print("Warning: '预测偏差' column not found in batch_analysis")
                return pd.DataFrame()

            # 安全地转换预测偏差为数值
            def safe_convert(x):
                try:
                    if isinstance(x, str) and '%' in x:
                        return float(str(x).rstrip('%')) / 100
                    elif isinstance(x, (int, float)):
                        return float(x)
                    else:
                        return 0.0
                except Exception as e:
                    print(f"无法转换预测偏差值 '{x}': {str(e)}")
                    return 0.0

            bias_data['预测偏差数值'] = bias_data['预测偏差'].apply(safe_convert)

            # 过滤极端值
            bias_data['预测偏差数值'] = bias_data['预测偏差数值'].apply(lambda x: min(max(x, -1), 1))

            # 确保bias_data非空并且包含需要的列后再排序
            if not bias_data.empty and '预测偏差数值' in bias_data.columns:
                # 使用绝对值列排序
                bias_data['预测偏差绝对值'] = bias_data['预测偏差数值'].abs()
                result = bias_data.sort_values(by='预测偏差绝对值', ascending=False)
                if '预测偏差绝对值' in result.columns:
                    result = result.drop(columns=['预测偏差绝对值'])
                return result
            else:
                print("Warning: Empty bias_data or '预测偏差数值' column not created")
                return pd.DataFrame()
        except Exception as e:
            print(f"处理预测偏差数据时出错: {str(e)}")
            return pd.DataFrame()

    def get_responsibility_data(self):
        """获取责任分析数据"""
        if self.batch_analysis is None or self.batch_analysis.empty:
            return pd.DataFrame()

        # 创建责任分析数据
        responsibility_data = self.batch_analysis.copy()

        # 根据批次价值和风险程度排序
        return responsibility_data.sort_values(by=['风险程度', '批次价值'],
                                               ascending=[True, False])

    def get_high_risk_products(self, limit=10):
        """获取高风险产品"""
        if self.batch_analysis is None or self.batch_analysis.empty:
            return pd.DataFrame()

        # 筛选高风险批次
        high_risk = self.batch_analysis[self.batch_analysis['风险程度'].isin(['极高风险', '高风险'])]

        # 按批次价值排序取前N个
        return high_risk.sort_values(by='批次价值', ascending=False).head(limit)

    def filter_data(self, product_filter=None, region_filter=None, person_filter=None, risk_filter=None):
        """
        根据条件筛选数据

        参数:
        product_filter (list): 产品筛选列表
        region_filter (list): 区域筛选列表
        person_filter (list): 责任人筛选列表
        risk_filter (list): 风险等级筛选列表

        返回:
        tuple: (filtered_batch_data, filtered_shipping_data)
        """
        # 初始筛选条件
        batch_filter = True
        shipping_filter = True

        # 应用产品筛选
        if product_filter and isinstance(product_filter, list) and len(product_filter) > 0:
            batch_filter = batch_filter & self.batch_data['产品代码'].isin(product_filter)
            shipping_filter = shipping_filter & self.shipping_data['产品代码'].isin(product_filter)

        # 应用区域筛选
        if region_filter and isinstance(region_filter, list) and len(region_filter) > 0:
            # 对批次数据，需要先找出哪些产品属于选定区域
            region_products = self.shipping_data[self.shipping_data['所属区域'].isin(region_filter)][
                '产品代码'].unique()
            batch_filter = batch_filter & self.batch_data['产品代码'].isin(region_products)

            # 对出货数据直接筛选
            shipping_filter = shipping_filter & self.shipping_data['所属区域'].isin(region_filter)

        # 应用责任人筛选
        if person_filter and isinstance(person_filter, list) and len(person_filter) > 0:
            # 对批次数据，需要先找出哪些产品属于选定责任人
            person_products = self.shipping_data[self.shipping_data['申请人'].isin(person_filter)]['产品代码'].unique()
            batch_filter = batch_filter & self.batch_data['产品代码'].isin(person_products)

            # 对出货数据直接筛选
            shipping_filter = shipping_filter & self.shipping_data['申请人'].isin(person_filter)

        # 应用筛选条件
        filtered_batch_data = self.batch_data[batch_filter] if isinstance(batch_filter, pd.Series) else self.batch_data
        filtered_shipping_data = self.shipping_data[shipping_filter] if isinstance(shipping_filter,
                                                                                   pd.Series) else self.shipping_data

        return (filtered_batch_data, filtered_shipping_data)


#################################################
# 可视化函数
#################################################


def add_chart_explanation(explanation_text):
    """添加图表解释"""
    st.markdown(f'<div class="chart-explanation">{explanation_text}</div>', unsafe_allow_html=True)


def download_excel(data, filename="data.xlsx"):
    """创建Excel下载链接"""
    try:
        # 检查是否安装了xlsxwriter
        import xlsxwriter

        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        data.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.close()

        b64 = base64.b64encode(output.getvalue()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">下载Excel文件</a>'
        return href
    except ImportError:
        # 如果xlsxwriter未安装，使用openpyxl作为备选
        try:
            output = io.BytesIO()
            writer = pd.ExcelWriter(output, engine='openpyxl')
            data.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.close()

            b64 = base64.b64encode(output.getvalue()).decode()
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">下载Excel文件</a>'
            return href
        except Exception as e:
            # 如果仍有问题，退回到CSV导出
            st.warning(f"Excel导出遇到问题: {str(e)}，切换到CSV导出")
            csv = data.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:text/csv;base64,{b64}" download="{filename.replace(".xlsx", ".csv")}">下载CSV文件</a>'
            return href


# 替换现有的create_risk_distribution_chart函数
# 替换现有的create_risk_distribution_chart函数
def create_risk_distribution_chart(batch_analysis):
    """创建风险分布饼图 - 增强悬停效果"""
    if batch_analysis is None or batch_analysis.empty:
        return go.Figure()

    # 计算风险分布
    risk_counts = batch_analysis['风险程度'].value_counts().reset_index()
    risk_counts.columns = ['风险等级', '批次数量']

    # 风险排序
    risk_order = {
        "极高风险": 0,
        "高风险": 1,
        "中风险": 2,
        "低风险": 3,
        "极低风险": 4
    }

    # 计算每个风险等级的批次价值总和
    risk_values = batch_analysis.groupby('风险程度')['批次价值'].sum().reset_index()
    risk_values.columns = ['风险等级', '批次价值总和']

    # 合并批次数量和价值信息
    risk_info = pd.merge(risk_counts, risk_values, on='风险等级')

    # 对风险等级排序
    risk_info['排序'] = risk_info['风险等级'].map(risk_order)
    risk_info = risk_info.sort_values('排序')

    # 设置颜色映射
    color_map = {
        '极高风险': '#FF0000',
        '高风险': '#FF5252',
        '中风险': '#FFC107',
        '低风险': '#4CAF50',
        '极低风险': '#2196F3'
    }

    # 创建自定义悬停文本
    hover_texts = []
    for _, row in risk_info.iterrows():
        top_products = batch_analysis[batch_analysis['风险程度'] == row['风险等级']].nlargest(3, '批次价值')
        product_texts = []
        for _, product in top_products.iterrows():
            if '简化产品名称' in product:
                product_name = product['简化产品名称']
            else:
                product_name = f"{product['物料']} ({product['描述'][:15]}...)"
            product_texts.append(f"- {product_name}: ¥{product['批次价值']:,.2f}")

        hover_text = (f"风险等级: {row['风险等级']}<br>" +
                      f"批次数量: {row['批次数量']}<br>" +
                      f"批次价值总和: ¥{row['批次价值总和']:,.2f}<br>" +
                      f"<br>主要产品:<br>" +
                      "<br>".join(product_texts))
        hover_texts.append(hover_text)

    # 创建饼图
    fig = px.pie(
        risk_info,
        values='批次数量',
        names='风险等级',
        title='库存批次风险分布',
        color='风险等级',
        color_discrete_map=color_map,
        hole=0.4,
        hover_data=['批次价值总和'],
        custom_data=[hover_texts]
    )

    # 添加饼图标签
    fig.update_traces(
        textposition='outside',
        textinfo='percent+label+value',
        marker=dict(line=dict(color='#FFFFFF', width=2)),
        hovertemplate='%{customdata[0]}<extra></extra>'
    )

    # 更新布局
    fig.update_layout(
        legend_title_text='风险等级',
        height=500,
        margin=dict(l=60, r=60, t=80, b=60),
        plot_bgcolor='white',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12
        )
    )

    return fig


# 替换现有的create_risk_value_chart函数
# 替换现有的create_risk_value_chart函数
# 替换现有的create_risk_value_chart函数
def create_risk_value_chart(batch_analysis):
    """创建风险价值条形图 - 增强悬停效果"""
    if batch_analysis is None or batch_analysis.empty:
        return go.Figure()

    # 按风险等级分组计算总价值和批次数量
    risk_value = batch_analysis.groupby('风险程度').agg({
        '批次价值': 'sum',
        '物料': 'count'
    }).reset_index()
    risk_value.columns = ['风险程度', '批次价值', '批次数量']

    # 风险排序
    risk_order = {
        "极高风险": 0,
        "高风险": 1,
        "中风险": 2,
        "低风险": 3,
        "极低风险": 4
    }

    # 对风险等级排序
    risk_value['排序'] = risk_value['风险程度'].map(risk_order)
    risk_value = risk_value.sort_values('排序')

    # 设置颜色映射
    color_map = {
        '极高风险': '#FF0000',
        '高风险': '#FF5252',
        '中风险': '#FFC107',
        '低风险': '#4CAF50',
        '极低风险': '#2196F3'
    }

    # 创建自定义悬停文本
    hover_texts = []
    for _, row in risk_value.iterrows():
        # 找出该风险等级的前3个最高价值批次
        top_batches = batch_analysis[batch_analysis['风险程度'] == row['风险程度']].nlargest(3, '批次价值')
        batch_texts = []
        for _, batch in top_batches.iterrows():
            if '简化产品名称' in batch:
                batch_name = batch['简化产品名称']
            else:
                batch_name = f"{batch['物料']} ({batch['描述'][:15]}...)"

            batch_info = (f"- {batch_name}: ¥{batch['批次价值']:,.2f}, " +
                          f"库龄: {batch['库龄']}天, " +
                          f"责任人: {batch['责任人']}")
            batch_texts.append(batch_info)

        hover_text = (f"风险等级: {row['风险程度']}<br>" +
                      f"批次价值总和: ¥{row['批次价值']:,.2f}<br>" +
                      f"批次数量: {row['批次数量']}<br>" +
                      f"<br>最高价值批次:<br>" +
                      "<br>".join(batch_texts))
        hover_texts.append(hover_text)

    # 创建条形图
    fig = px.bar(
        risk_value,
        x='风险程度',
        y='批次价值',
        title='不同风险等级库存价值分布',
        color='风险程度',
        color_discrete_map=color_map,
        text='批次价值',
        custom_data=[hover_texts]
    )

    # 添加数值标签
    fig.update_traces(
        texttemplate='%{y:,.2f}元',
        textposition='outside',
        hovertemplate='%{customdata[0]}<extra></extra>'
    )

    # 更新轴标签
    fig.update_layout(
        xaxis_title='风险等级',
        yaxis_title='库存价值 (元)',
        yaxis=dict(tickformat=","),
        height=500,
        margin=dict(l=60, r=60, t=80, b=60),
        plot_bgcolor='white',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12
        )
    )

    return fig


# 替换现有的create_age_distribution_chart函数
# 替换现有的create_age_distribution_chart函数
def create_age_distribution_chart(age_data):
    """创建库龄分布条形图 - 显示全部批次而非仅Top N"""
    if age_data is None or age_data.empty:
        return go.Figure()

    # 按库龄降序排序
    sorted_age_data = age_data.sort_values('库龄', ascending=False)

    # 创建标签 - 使用简化产品名称
    if '简化产品名称' in sorted_age_data.columns:
        labels = [f"{name} ({date})" for name, date in
                  zip(sorted_age_data['简化产品名称'], sorted_age_data['批次日期'].astype(str))]
    else:
        labels = [f"{code} ({date})" for code, date in
                  zip(sorted_age_data['物料'], sorted_age_data['批次日期'].astype(str))]

    # 设置颜色 - 使用风险程度区分
    color_map = {
        '极高风险': '#FF0000',
        '高风险': '#FF5252',
        '中风险': '#FFC107',
        '低风险': '#4CAF50',
        '极低风险': '#2196F3'
    }

    # 创建条形图
    fig = px.bar(
        sorted_age_data,
        x='库龄',
        y=labels,
        orientation='h',
        title='批次库龄分布',
        color='风险程度',
        color_discrete_map=color_map,
        text='库龄',
        hover_data=['物料', '描述', '批次日期', '批次库存', '库龄', '风险程度', '预计清库天数', '批次价值', '责任人']
    )

    # 添加阈值参考线
    fig.add_vline(x=90, line_dash="dash", line_color="red", annotation_text="高风险阈值 (90天)")
    fig.add_vline(x=60, line_dash="dash", line_color="orange", annotation_text="中风险阈值 (60天)")
    fig.add_vline(x=30, line_dash="dash", line_color="green", annotation_text="低风险阈值 (30天)")

    # 更新悬停模板，提供更详细的信息
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>' +
                    '物料: %{customdata[0]}<br>' +
                    '描述: %{customdata[1]}<br>' +
                    '批次日期: %{customdata[2]}<br>' +
                    '批次库存: %{customdata[3]} 件<br>' +
                    '库龄: %{x} 天<br>' +
                    '风险程度: %{customdata[4]}<br>' +
                    '预计清库天数: %{customdata[5]} 天<br>' +
                    '批次价值: ¥%{customdata[6]:,.2f}<br>' +
                    '责任人: %{customdata[7]}<extra></extra>'
    )

    # 更新布局
    fig.update_layout(
        xaxis_title='库龄 (天)',
        yaxis_title='批次',
        height=max(800, len(sorted_age_data) * 30),  # 动态调整高度以适应所有批次
        # 增加左边距以显示较长的标签
        margin=dict(l=250, r=100, t=80, b=80),
        plot_bgcolor='white',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12
        )
    )

    # 添加数据标签
    fig.update_traces(
        texttemplate='%{x}天',
        textposition='outside'
    )

    return fig


# 替换现有的create_clearance_chart函数
# 替换现有的create_clearance_chart函数
def create_clearance_chart(clearance_data, max_display=20):
    """创建清库预测图 - 增强悬停效果和可读性"""
    if clearance_data is None or clearance_data.empty:
        return go.Figure()

    # 处理清库天数，创建数值列
    data = clearance_data.copy()
    data['清库天数值'] = data['预计清库天数'].apply(
        lambda x: 500 if x == float('inf') else float(x)  # 将无穷大转换为500天用于显示
    )

    # 选择预计清库天数最长的N个批次
    top_clearance = data.nlargest(max_display, '清库天数值')

    # 创建标签 - 使用简化产品名称
    if '简化产品名称' in top_clearance.columns:
        labels = [f"{name}" for name in top_clearance['简化产品名称']]
    else:
        # 如果没有简化名称，创建一个简短描述
        labels = [f"{code} ({desc[:15]}...)" for code, desc in zip(top_clearance['物料'], top_clearance['描述'])]

    # 设置颜色 - 使用风险程度区分
    color_map = {
        '极高风险': '#FF0000',
        '高风险': '#FF5252',
        '中风险': '#FFC107',
        '低风险': '#4CAF50',
        '极低风险': '#2196F3'
    }

    # 准备自定义数据用于悬停显示
    customdata = []
    for _, row in top_clearance.iterrows():
        hover_data = [
            row['物料'],
            row['描述'],
            row['批次日期'].strftime('%Y-%m-%d') if hasattr(row['批次日期'], 'strftime') else str(row['批次日期']),
            float(row['批次库存']),
            float(row['库龄']),
            '无法预测' if row['预计清库天数'] == float('inf') else f"{float(row['预计清库天数']):.1f}",
            float(row['批次价值']),
            row['责任人'],
            row['责任区域'],
            row['风险程度'],
            row['建议措施'],
            row['责任分析摘要'] if '责任分析摘要' in row else ''
        ]
        customdata.append(hover_data)

    # 创建子图
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 添加清库天数条形图
    fig.add_trace(
        go.Bar(
            x=top_clearance['清库天数值'],
            y=labels,
            orientation='h',
            name='预计清库天数',
            marker_color=[color_map.get(risk, '#777777') for risk in top_clearance['风险程度']],
            text=top_clearance['清库天数值'].apply(lambda x: '无法清库' if x >= 500 else f"{int(x)}天"),
            textposition='outside',
            customdata=customdata,
            hovertemplate='<b>%{y}</b><br>' +
                          '预计清库天数: %{text}<br>' +
                          '物料: %{customdata[0]}<br>' +
                          '描述: %{customdata[1]}<br>' +
                          '批次日期: %{customdata[2]}<br>' +
                          '批次库存: %{customdata[3]:,.0f} 件<br>' +
                          '库龄: %{customdata[4]} 天<br>' +
                          '批次价值: ¥%{customdata[6]:,.2f}<br>' +
                          '责任人: %{customdata[7]}<br>' +
                          '责任区域: %{customdata[8]}<br>' +
                          '风险程度: %{customdata[9]}<br>' +
                          '建议措施: %{customdata[10]}<br>' +
                          '责任分析: %{customdata[11]}<extra></extra>'
        ),
        secondary_y=False
    )

    # 添加库龄点图
    fig.add_trace(
        go.Scatter(
            x=top_clearance['库龄'],
            y=labels,
            mode='markers+text',
            name='当前库龄',
            marker=dict(
                symbol='diamond',
                size=12,
                color='rgba(0, 0, 255, 0.7)'
            ),
            text=top_clearance['库龄'],
            textposition='top center',
            customdata=customdata,
            hovertemplate='<b>%{y}</b><br>' +
                          '当前库龄: %{x} 天<br>' +
                          '物料: %{customdata[0]}<br>' +
                          '描述: %{customdata[1]}<br>' +
                          '批次日期: %{customdata[2]}<br>' +
                          '批次库存: %{customdata[3]:,.0f} 件<br>' +
                          '预计清库天数: %{customdata[5]} 天<br>' +
                          '批次价值: ¥%{customdata[6]:,.2f}<br>' +
                          '责任人: %{customdata[7]}<br>' +
                          '责任区域: %{customdata[8]}<br>' +
                          '风险程度: %{customdata[9]}<br>' +
                          '建议措施: %{customdata[10]}<extra></extra>'
        ),
        secondary_y=True
    )

    # 添加阈值参考线
    fig.add_vline(x=90, line_dash="dash", line_color="red", annotation_text="高风险阈值 (90天)")

    # 更新布局
    fig.update_layout(
        title=f'预计清库天数 vs. 库龄',
        height=max(600, len(top_clearance) * 30),  # 根据显示批次数动态调整高度
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='white',
        # 增加左边距以显示较长的标签
        margin=dict(l=250, r=100, t=80, b=80),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12
        )
    )

    # 更新坐标轴
    fig.update_xaxes(title_text="天数", showgrid=True, gridwidth=0.5, gridcolor='rgba(220,220,220,0.5)')
    fig.update_yaxes(title_text="批次", secondary_y=False)
    fig.update_yaxes(title_text="", secondary_y=True)

    return fig


# 替换现有的create_forecast_bias_chart函数
# 替换现有的create_forecast_bias_chart函数
def create_forecast_bias_chart(bias_data, max_display=20):
    """创建预测偏差图 - 增强悬停效果和可读性"""
    if bias_data is None or bias_data.empty:
        return go.Figure()

    try:
        # 检查是否有预测偏差数值列
        if '预测偏差数值' not in bias_data.columns:
            # 尝试从预测偏差列创建
            if '预测偏差' in bias_data.columns:
                def extract_bias_value(bias_str):
                    try:
                        if isinstance(bias_str, str) and '%' in bias_str:
                            return float(bias_str.rstrip('%')) / 100
                        elif isinstance(bias_str, (int, float)):
                            return float(bias_str)
                        else:
                            return 0
                    except:
                        return 0

                bias_data = bias_data.copy()
                bias_data['预测偏差数值'] = bias_data['预测偏差'].apply(extract_bias_value)
            else:
                # 没有预测偏差相关列，返回空图表
                fig = go.Figure()
                fig.update_layout(title="无法获取预测偏差数据")
                return fig

        # 使用try-except处理nlargest操作
        try:
            # 选择预测偏差最显著的N个批次（按绝对值大小排序）
            top_bias = bias_data.nlargest(max_display, '预测偏差数值', key=lambda x: abs(x))
        except Exception as e:
            # 如果key=abs失败，尝试不使用key参数
            print(f"无法使用key=abs进行排序: {str(e)}，尝试替代方法")
            bias_data['预测偏差绝对值'] = bias_data['预测偏差数值'].apply(abs)
            top_bias = bias_data.nlargest(max_display, '预测偏差绝对值')
            if '预测偏差绝对值' in top_bias.columns:
                top_bias = top_bias.drop(columns=['预测偏差绝对值'])

        # 检查top_bias是否为空
        if top_bias.empty:
            fig = go.Figure()
            fig.update_layout(title="没有足够的预测偏差数据进行分析")
            return fig

        # 创建标签 - 使用简化产品名称（如果有）
        if '简化产品名称' in top_bias.columns:
            labels = [f"{row['简化产品名称']}" for _, row in top_bias.iterrows()]
        else:
            labels = [f"{code}" for code in top_bias['物料']]

        # 创建条形图
        fig = go.Figure()

        # 准备自定义数据用于悬停显示
        customdata = []
        for _, row in top_bias.iterrows():
            # 收集所有可能的悬停数据
            hover_data = [
                row['物料'] if '物料' in row else '',
                row['描述'] if '描述' in row else '',
                row['批次日期'].strftime('%Y-%m-%d') if '批次日期' in row and hasattr(row['批次日期'], 'strftime') else '',
                float(row['批次库存']) if '批次库存' in row else 0,
                float(row['日均出货']) if '日均出货' in row else 0,
                float(row['预计清库天数']) if '预计清库天数' in row and row['预计清库天数'] != float('inf') else '无法预测',
                row['责任人'] if '责任人' in row else '',
                row['责任区域'] if '责任区域' in row else '',
                row['风险程度'] if '风险程度' in row else '',
                row['责任分析摘要'] if '责任分析摘要' in row else ''
            ]
            customdata.append(hover_data)

        # 添加正偏差条形图（预测过高）
        positive_bias = top_bias[top_bias['预测偏差数值'] > 0]
        if not positive_bias.empty:
            pos_customdata = [customdata[i] for i in range(len(top_bias)) if top_bias.iloc[i]['预测偏差数值'] > 0]
            fig.add_trace(go.Bar(
                y=[labels[i] for i in range(len(top_bias)) if top_bias.iloc[i]['预测偏差数值'] > 0],
                x=positive_bias['预测偏差数值'] * 100,
                name='预测过高',
                orientation='h',
                marker_color='rgba(255, 59, 59, 0.8)',
                text=positive_bias['预测偏差'],
                textposition='outside',
                customdata=pos_customdata,
                hovertemplate='<b>%{y}</b><br>' +
                              '预测偏差: %{x:.1f}%<br>' +
                              '物料: %{customdata[0]}<br>' +
                              '描述: %{customdata[1]}<br>' +
                              '批次日期: %{customdata[2]}<br>' +
                              '批次库存: %{customdata[3]:,.0f} 件<br>' +
                              '日均出货: %{customdata[4]:.2f} 件<br>' +
                              '预计清库天数: %{customdata[5]}<br>' +
                              '责任人: %{customdata[6]}<br>' +
                              '责任区域: %{customdata[7]}<br>' +
                              '风险程度: %{customdata[8]}<br>' +
                              '责任分析: %{customdata[9]}<extra></extra>'
            ))

        # 添加负偏差条形图（预测过低）
        negative_bias = top_bias[top_bias['预测偏差数值'] < 0]
        if not negative_bias.empty:
            neg_customdata = [customdata[i] for i in range(len(top_bias)) if top_bias.iloc[i]['预测偏差数值'] < 0]
            fig.add_trace(go.Bar(
                y=[labels[i] for i in range(len(top_bias)) if top_bias.iloc[i]['预测偏差数值'] < 0],
                x=negative_bias['预测偏差数值'] * 100,
                name='预测过低',
                orientation='h',
                marker_color='rgba(59, 89, 255, 0.8)',
                text=negative_bias['预测偏差'],
                textposition='outside',
                customdata=neg_customdata,
                hovertemplate='<b>%{y}</b><br>' +
                              '预测偏差: %{x:.1f}%<br>' +
                              '物料: %{customdata[0]}<br>' +
                              '描述: %{customdata[1]}<br>' +
                              '批次日期: %{customdata[2]}<br>' +
                              '批次库存: %{customdata[3]:,.0f} 件<br>' +
                              '日均出货: %{customdata[4]:.2f} 件<br>' +
                              '预计清库天数: %{customdata[5]}<br>' +
                              '责任人: %{customdata[6]}<br>' +
                              '责任区域: %{customdata[7]}<br>' +
                              '风险程度: %{customdata[8]}<br>' +
                              '责任分析: %{customdata[9]}<extra></extra>'
            ))

        # 添加参考线
        fig.add_vline(x=30, line_dash="dash", line_color="red", annotation_text="高偏差阈值 (30%)")
        fig.add_vline(x=-30, line_dash="dash", line_color="red")
        fig.add_vline(x=15, line_dash="dash", line_color="orange", annotation_text="中偏差阈值 (15%)")
        fig.add_vline(x=-15, line_dash="dash", line_color="orange")

        # 更新布局
        fig.update_layout(
            title='批次预测偏差分析',
            xaxis_title='预测偏差 (%)',
            yaxis_title='批次',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor='white',
            # 增加高度以避免标签拥挤
            height=max(600, len(top_bias) * 30),
            # 增加左边距以显示较长的产品名称
            margin=dict(l=250, r=100, t=80, b=80),
            hoverlabel=dict(
                bgcolor="white",
                font_size=12
            )
        )

        return fig
    except Exception as e:
        print(f"创建预测偏差图表时出错: {str(e)}")
        fig = go.Figure()
        fig.update_layout(title=f"创建图表时出错: {str(e)}")
        return fig


# 替换现有的create_forecast_accuracy_chart函数
def create_forecast_accuracy_chart(bias_data):
    """创建预测准确度散点图 - 增强悬停效果"""
    if bias_data is None or bias_data.empty:
        return go.Figure()

    # 筛选有效数据
    valid_data = bias_data[~bias_data['预测偏差数值'].isna()]

    # 准备自定义数据用于悬停显示
    customdata = []
    for _, row in valid_data.iterrows():
        hover_data = [
            row['物料'],
            row['描述'][:30] + '...' if len(row['描述']) > 30 else row['描述'],
            float(row['批次库存']),
            float(row['日均出货']) if '日均出货' in row else 0,
            float(row['预计清库天数']) if row['预计清库天数'] != float('inf') else '无法预测',
            row['责任人'],
            row['责任区域'] if pd.notna(row['责任区域']) else '无指定区域',
            row['简化产品名称'] if '简化产品名称' in row else row['物料']
        ]
        customdata.append(hover_data)

    # 创建散点图
    fig = px.scatter(
        valid_data,
        x='预测偏差数值',
        y='预计清库天数',
        color='风险程度',
        size='批次价值',
        hover_name='简化产品名称' if '简化产品名称' in valid_data.columns else '物料',
        text='简化产品名称' if '简化产品名称' in valid_data.columns else '物料',
        title='预测准确度与清库关系分析',
        labels={
            '预测偏差数值': '预测偏差',
            '预计清库天数': '预计清库天数 (天)'
        },
        color_discrete_map={
            '极高风险': '#FF0000',
            '高风险': '#FF5252',
            '中风险': '#FFC107',
            '低风险': '#4CAF50',
            '极低风险': '#2196F3'
        },
        custom_data=customdata
    )

    # 更新点显示
    fig.update_traces(
        marker=dict(line=dict(width=1, color='DarkSlateGrey')),
        selector=dict(mode='markers+text'),
        textposition='top center',
        hovertemplate='<b>%{hovertext}</b><br>' +
                      '预测偏差: %{x:.1%}<br>' +
                      '预计清库天数: %{y:,.0f} 天<br>' +
                      '物料: %{customdata[0]}<br>' +
                      '描述: %{customdata[1]}<br>' +
                      '批次库存: %{customdata[2]:,.0f} 件<br>' +
                      '日均出货: %{customdata[3]:.2f} 件/天<br>' +
                      '责任人: %{customdata[5]}<br>' +
                      '责任区域: %{customdata[6]}<br>' +
                      '风险程度: %{marker.color}<extra></extra>'
    )

    # 添加参考线
    fig.add_vline(x=0.3, line_dash="dash", line_color="red")
    fig.add_vline(x=-0.3, line_dash="dash", line_color="red")
    fig.add_hline(y=90, line_dash="dash", line_color="red")

    # 添加象限标签
    fig.add_annotation(x=0.6, y=180, text="预测过高<br>清库困难", showarrow=False, font=dict(size=12, color="red"))
    fig.add_annotation(x=-0.6, y=180, text="预测过低<br>清库困难", showarrow=False, font=dict(size=12, color="red"))
    fig.add_annotation(x=0.6, y=30, text="预测过高<br>清库正常", showarrow=False, font=dict(size=12, color="black"))
    fig.add_annotation(x=-0.6, y=30, text="预测过低<br>清库正常", showarrow=False, font=dict(size=12, color="black"))

    # 转换x轴为百分比格式
    fig.update_xaxes(
        tickformat=".0%",
        range=[-1, 1],
        title_font=dict(size=14),
        showgrid=True,
        gridwidth=0.5,
        gridcolor='rgba(220,220,220,0.5)'
    )

    # 处理预计清库天数为无穷大的情况
    max_clearance = valid_data['预计清库天数'].replace([float('inf')], 200).max()

    # 更新y轴
    fig.update_yaxes(
        range=[0, max(200, max_clearance * 1.1)],
        title_font=dict(size=14),
        showgrid=True,
        gridwidth=0.5,
        gridcolor='rgba(220,220,220,0.5)'
    )

    # 优化图表布局
    fig.update_layout(
        margin=dict(l=80, r=80, t=80, b=80),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        plot_bgcolor='white',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12
        )
    )

    return fig


# 替换现有的create_responsibility_region_chart函数
# 替换现有的create_responsibility_region_chart函数
def create_responsibility_region_chart(batch_analysis):
    """创建责任区域分布图 - 增强悬停效果"""
    if batch_analysis is None or batch_analysis.empty:
        return go.Figure()

    # 计算区域责任分布及价值总和
    region_stats = batch_analysis.groupby('责任区域').agg({
        '物料': 'count',
        '批次价值': 'sum'
    }).reset_index()
    region_stats.columns = ['责任区域', '批次数量', '批次价值总和']

    # 确保空区域显示为"无指定区域"
    region_stats['责任区域'] = region_stats['责任区域'].replace('', '无指定区域')

    # 创建自定义悬停文本
    hover_texts = []
    for _, row in region_stats.iterrows():
        region = row['责任区域']
        # 替换空字符串为"无指定区域"作为过滤条件
        filter_region = '' if region == '无指定区域' else region

        # 找出该区域的主要责任人
        region_batches = batch_analysis[batch_analysis['责任区域'] == filter_region]
        top_persons = region_batches.groupby('责任人').size().nlargest(3)

        person_texts = []
        for person, count in top_persons.items():
            person_value = region_batches[region_batches['责任人'] == person]['批次价值'].sum()
            person_texts.append(f"- {person}: {count}个批次, ¥{person_value:,.2f}")

        # 找出该区域的主要产品
        top_products = region_batches.groupby('物料').agg({'批次价值': 'sum'}).nlargest(3, '批次价值')

        product_texts = []
        for product, value in top_products.iterrows():
            # 尝试获取简化产品名称
            product_row = region_batches[region_batches['物料'] == product].iloc[0] if not region_batches[
                region_batches['物料'] == product].empty else None
            if product_row is not None and '简化产品名称' in product_row:
                product_name = product_row['简化产品名称']
            else:
                product_name = product

            product_texts.append(f"- {product_name}: ¥{value['批次价值']:,.2f}")

        hover_text = (f"责任区域: {region}<br>" +
                      f"批次数量: {row['批次数量']}<br>" +
                      f"批次价值总和: ¥{row['批次价值总和']:,.2f}<br><br>" +
                      f"主要责任人:<br>" +
                      "<br>".join(person_texts) + "<br><br>" +
                      f"主要产品:<br>" +
                      "<br>".join(product_texts))
        hover_texts.append(hover_text)

    # 创建饼图
    fig = px.pie(
        region_stats,
        values='批次数量',
        names='责任区域',
        title='库存批次责任区域分布',
        hole=0.4,
        custom_data=[hover_texts]
    )

    # 添加标签
    fig.update_traces(
        textposition='outside',
        textinfo='percent+label+value',
        hovertemplate='%{customdata[0]}<extra></extra>'
    )

    # 更新布局
    fig.update_layout(
        legend_title_text='责任区域',
        height=500,
        margin=dict(l=60, r=60, t=80, b=60),
        plot_bgcolor='white',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12
        )
    )

    return fig


# 替换现有的create_responsibility_person_chart函数
# 替换现有的create_responsibility_person_chart函数
def create_responsibility_person_chart(batch_analysis, max_display=10):
    """创建责任人风险分析图 - 增强悬停效果"""
    if batch_analysis is None or batch_analysis.empty:
        return go.Figure()

    # 获取每个责任人的批次数量和平均风险得分
    person_stats = batch_analysis.groupby('责任人').agg({
        '物料': 'count',
        '风险得分': 'mean',
        '批次价值': 'sum'
    }).reset_index()
    person_stats.columns = ['责任人', '批次数量', '平均风险得分', '总批次价值']

    # 按平均风险得分排序，选择前N个
    top_persons = person_stats.nlargest(max_display, '平均风险得分')

    # 创建自定义悬停文本
    hover_texts = []
    for _, row in top_persons.iterrows():
        person = row['责任人']

        # 计算该责任人的风险等级分布
        person_batches = batch_analysis[batch_analysis['责任人'] == person]
        risk_distribution = person_batches.groupby('风险程度').size()
        risk_texts = []
        for risk, count in risk_distribution.items():
            risk_value = person_batches[person_batches['风险程度'] == risk]['批次价值'].sum()
            risk_texts.append(f"- {risk}: {count}个批次, ¥{risk_value:,.2f}")

        # 找出该责任人的主要产品
        top_products = person_batches.groupby('物料').agg({'批次价值': 'sum'}).nlargest(3, '批次价值')

        product_texts = []
        for product, value in top_products.iterrows():
            # 尝试获取简化产品名称
            product_row = person_batches[person_batches['物料'] == product].iloc[0] if not person_batches[
                person_batches['物料'] == product].empty else None
            if product_row is not None and '简化产品名称' in product_row:
                product_name = product_row['简化产品名称']
            else:
                product_name = product

            product_texts.append(f"- {product_name}: ¥{value['批次价值']:,.2f}")

        hover_text = (f"责任人: {person}<br>" +
                      f"批次数量: {row['批次数量']}<br>" +
                      f"平均风险得分: {row['平均风险得分']:.1f}<br>" +
                      f"总批次价值: ¥{row['总批次价值']:,.2f}<br><br>" +
                      f"风险分布:<br>" +
                      "<br>".join(risk_texts) + "<br><br>" +
                      f"主要产品:<br>" +
                      "<br>".join(product_texts))
        hover_texts.append(hover_text)

    # 创建条形图
    fig = px.bar(
        top_persons,
        x='责任人',
        y='平均风险得分',
        title=f'责任人风险排名 (Top {len(top_persons)})',
        color='平均风险得分',
        color_continuous_scale='Reds',
        text='平均风险得分',
        hover_data=['批次数量', '总批次价值'],
        custom_data=[hover_texts]
    )

    # 添加数据标签
    fig.update_traces(
        texttemplate='%{y:.1f}',
        textposition='outside',
        hovertemplate='%{customdata[0]}<extra></extra>'
    )

    # 更新布局
    fig.update_layout(
        xaxis_title='责任人',
        yaxis_title='平均风险得分',
        coloraxis_showscale=False,
        height=max(500, len(top_persons) * 30),
        margin=dict(l=60, r=60, t=80, b=100),
        plot_bgcolor='white',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12
        )
    )

    return fig


# 替换现有的create_fulfillment_rate_chart函数
# 替换现有的create_fulfillment_rate_chart函数
def create_fulfillment_rate_chart(batch_analysis):
    """创建预测履行率热力图 - 增强悬停效果"""
    if batch_analysis is None or batch_analysis.empty:
        return go.Figure()

    # 创建责任分析摘要解析函数
    def extract_fulfillment_rate(summary):
        if not isinstance(summary, str):
            return None

        # 尝试从摘要中提取履行率
        import re
        match = re.search(r'履行率(\d+\.?\d*)%', summary)
        if match:
            return float(match.group(1)) / 100
        return None

    # 从摘要中提取履行率
    batch_analysis['履行率'] = batch_analysis['责任分析摘要'].apply(extract_fulfillment_rate)

    # 筛选有效数据
    valid_data = batch_analysis[~batch_analysis['履行率'].isna()]

    if valid_data.empty:
        # 如果没有有效数据，返回空图
        fig = go.Figure()
        fig.update_layout(title='无有效预测履行率数据')
        return fig

    # 按责任人和区域分组计算平均履行率
    fulfillment_by_person_region = valid_data.groupby(['责任人', '责任区域']).agg({
        '履行率': 'mean',
        '物料': 'count',
        '批次价值': 'sum'
    }).reset_index()

    # 添加自定义悬停文本
    hover_texts = []
    for _, row in fulfillment_by_person_region.iterrows():
        person = row['责任人']
        region = row['责任区域']

        # 找出该责任人在该区域的批次
        person_region_batches = valid_data[(valid_data['责任人'] == person) & (valid_data['责任区域'] == region)]

        # 找出履行率最低的3个批次
        lowest_fulfillment = person_region_batches.nsmallest(3, '履行率')

        batch_texts = []
        for _, batch in lowest_fulfillment.iterrows():
            if '简化产品名称' in batch:
                batch_name = batch['简化产品名称']
            else:
                batch_name = f"{batch['物料']} ({batch['描述'][:15]}...)"

            batch_texts.append(f"- {batch_name}: {batch['履行率'] * 100:.1f}%, ¥{batch['批次价值']:,.2f}")

        hover_text = (f"责任人: {person}<br>" +
                      f"区域: {region if region else '无指定区域'}<br>" +
                      f"平均履行率: {row['履行率'] * 100:.1f}%<br>" +
                      f"批次数量: {row['物料']}<br>" +
                      f"总批次价值: ¥{row['批次价值']:,.2f}<br><br>" +
                      f"履行率最低批次:<br>" +
                      "<br>".join(batch_texts))
        hover_texts.append(hover_text)

    fulfillment_by_person_region['hover_text'] = hover_texts

    # 为了热力图，创建数据透视表
    fulfillment_pivot = fulfillment_by_person_region.pivot_table(
        values='履行率',
        index='责任人',
        columns='责任区域',
        fill_value=0
    )

    # 创建数据透视表用于悬停信息
    hover_pivot = fulfillment_by_person_region.pivot_table(
        values='hover_text',
        index='责任人',
        columns='责任区域',
        fill_value=''
    )

    # 创建热力图数据
    z_data = fulfillment_pivot.values
    x_data = fulfillment_pivot.columns
    y_data = fulfillment_pivot.index
    hover_data = hover_pivot.values

    # 创建热力图
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=x_data,
        y=y_data,
        colorscale='RdYlGn',
        text=[[f"{val * 100:.1f}%" for val in row] for row in z_data],
        hoverinfo='text',
        hovertext=hover_data,
        colorbar=dict(
            title='履行率',
            tickformat=".0%",
            tickmode="array",
            tickvals=[0, 0.25, 0.5, 0.75, 1],
            ticktext=["0%", "25%", "50%", "75%", "100%"]
        )
    ))

    # 更新布局
    fig.update_layout(
        title='责任人-区域预测履行率热力图',
        height=max(500, 100 + len(fulfillment_pivot) * 30),  # 根据责任人数量调整高度
        margin=dict(l=150, r=80, t=80, b=80),
        xaxis_title='责任区域',
        yaxis_title='责任人',
        plot_bgcolor='white',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12
        )
    )

    return fig


# 替换现有的format_yuan函数
def format_yuan(value):
    """格式化人民币数值 - 更加清晰的格式"""
    if value >= 100000000:  # 亿元级别
        return f"¥{value / 100000000:.2f}亿元"
    elif value >= 10000:  # 万元级别
        return f"¥{value / 10000:.2f}万元"
    else:
        return f"¥{value:.2f}元"



def create_metric_cards(risk_summary, batch_analysis):
    """创建关键指标卡片 - 改进格式"""
    if batch_analysis is None or batch_analysis.empty:
        total_batches = 0
        total_value = 0
        avg_age = 0
        high_risk_batches = 0
        high_risk_value = 0
    else:
        total_batches = len(batch_analysis)
        total_value = batch_analysis['批次价值'].sum()
        avg_age = batch_analysis['库龄'].mean()
        high_risk_batches = risk_summary.get('极高风险', 0) + risk_summary.get('高风险', 0)
        high_risk_value = batch_analysis[batch_analysis['风险程度'].isin(['极高风险', '高风险'])]['批次价值'].sum()

    # 创建关键指标卡片行
    cols = st.columns(4)

    with cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">总批次数</p>
            <p class="card-value">{total_batches}</p>
            <p class="card-text">监控批次总数</p>
        </div>
        """, unsafe_allow_html=True)

    with cols[1]:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">总库存价值</p>
            <p class="card-value">{format_yuan(total_value)}</p>
            <p class="card-text">全部批次价值</p>
        </div>
        """, unsafe_allow_html=True)

    with cols[2]:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">高风险批次</p>
            <p class="card-value">{high_risk_batches}</p>
            <p class="card-text">需优先处理批次</p>
        </div>
        """, unsafe_allow_html=True)

    with cols[3]:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">平均库龄</p>
            <p class="card-value">{avg_age:.1f}天</p>
            <p class="card-text">全部批次平均库龄</p>
        </div>
        """, unsafe_allow_html=True)

    return high_risk_value


# 替换现有的create_risk_metric_cards函数
def create_risk_metric_cards(risk_summary):
    """创建风险等级指标卡片 - 改进格式"""
    # 获取各风险等级数量
    extreme_high = risk_summary.get('极高风险', 0)
    high = risk_summary.get('高风险', 0)
    medium = risk_summary.get('中风险', 0)
    low = risk_summary.get('低风险', 0)
    extreme_low = risk_summary.get('极低风险', 0)

    # 创建风险等级卡片行
    cols = st.columns(5)

    with cols[0]:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #FF0000;">
            <p class="card-header">极高风险</p>
            <p class="card-value" style="color: #FF0000;">{extreme_high}</p>
            <p class="card-text">紧急处理批次</p>
        </div>
        """, unsafe_allow_html=True)

    with cols[1]:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #FF5252;">
            <p class="card-header">高风险</p>
            <p class="card-value" style="color: #FF5252;">{high}</p>
            <p class="card-text">优先处理批次</p>
        </div>
        """, unsafe_allow_html=True)

    with cols[2]:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #FFC107;">
            <p class="card-header">中风险</p>
            <p class="card-value" style="color: #FFC107;">{medium}</p>
            <p class="card-text">密切监控批次</p>
        </div>
        """, unsafe_allow_html=True)

    with cols[3]:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #4CAF50;">
            <p class="card-header">低风险</p>
            <p class="card-value" style="color: #4CAF50;">{low}</p>
            <p class="card-text">常规管理批次</p>
        </div>
        """, unsafe_allow_html=True)

    with cols[4]:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #2196F3;">
            <p class="card-header">极低风险</p>
            <p class="card-value" style="color: #2196F3;">{extreme_low}</p>
            <p class="card-text">正常库存批次</p>
        </div>
        """, unsafe_allow_html=True)


#################################################
# 主函数
#################################################

def main():
    # 加载CSS样式
    load_css()

    # 检查用户是否已登录
    if not check_authentication():
        return

    # 设置页面标题
    st.markdown('<div class="main-header">SAL异常与预警</div>', unsafe_allow_html=True)

    # 侧边栏 - 数据加载与筛选
    with st.sidebar:
        st.header("📂 数据控制")
        st.write("数据文件目录: `./`")

        # 数据加载
        data_loader = DataLoader(data_dir="./")

        # 如果点击刷新按钮，清除缓存并重新加载数据
        if st.button("刷新数据", key="refresh_data"):
            st.cache_data.clear()
            st.success("数据已刷新!")
            time.sleep(1)
            st.rerun()

        try:
            # 加载所有数据
            data = data_loader.load_all_data()

            # 数据加载成功后，显示数据概览
            st.subheader("📊 数据概览")
            st.info(f"产品数量: {len(data['inventory_data'])}")
            st.info(f"批次数量: {len(data['batch_data'])}")
            st.info(f"出货记录数量: {len(data['shipping_data'])}")

            # 创建分析引擎
            analysis_engine = AnalysisEngine(data)

            # 初始分析
            batch_analysis = analysis_engine.analyze_data()

            # 侧边栏 - 筛选器
            st.header("🔍 筛选数据")

            # 风险等级筛选器
            risk_options = ["极高风险", "高风险", "中风险", "低风险", "极低风险"]
            selected_risks = st.multiselect("选择风险等级", risk_options, default=risk_options)

            # 产品筛选器
            all_products = sorted(data_loader.batch_data['产品代码'].unique())
            selected_products = st.multiselect("选择产品", all_products)

            # 区域筛选器
            all_regions = sorted([r for r in data_loader.shipping_data['所属区域'].unique() if r])
            selected_regions = st.multiselect("选择区域", all_regions)

            # 责任人筛选器
            all_persons = sorted(
                [p for p in data_loader.shipping_data['申请人'].unique() if p != data_loader.default_person])
            selected_persons = st.multiselect("选择责任人", all_persons)

            # 应用筛选
            if st.button("应用筛选", key="apply_filter"):
                with st.spinner("正在应用筛选条件..."):
                    # 筛选数据
                    filtered_data = analysis_engine.filter_data(
                        product_filter=selected_products if selected_products else None,
                        region_filter=selected_regions if selected_regions else None,
                        person_filter=selected_persons if selected_persons else None
                    )

                    # 分析筛选后的数据
                    batch_analysis = analysis_engine.analyze_data(filtered_data)

                    # 应用风险等级筛选
                    if selected_risks and len(selected_risks) < len(risk_options):
                        batch_analysis = batch_analysis[batch_analysis['风险程度'].isin(selected_risks)]

                    st.success("筛选条件已应用!")

            # 下载筛选后的数据
            if not batch_analysis.empty:
                st.markdown("### 📥 导出数据")
                st.markdown(download_excel(batch_analysis, "SAL异常与预警分析结果.xlsx"), unsafe_allow_html=True)

        except Exception as e:
            st.error(f"数据加载错误: {str(e)}")
            st.stop()

    # 获取风险等级统计
    risk_summary = analysis_engine.get_risk_summary()

    # 创建选项卡
    tabs = st.tabs(["📊 风险预警概览", "🕗 库龄与清库分析", "🔍 预测偏差分析", "👥 责任分析与跟踪"])

    with tabs[0]:  # 风险预警概览
        # 风险指标卡片
        create_risk_metric_cards(risk_summary)

        # KPI指标卡片
        high_risk_value = create_metric_cards(risk_summary, batch_analysis)

        # 风险分布与价值图表
        st.markdown('<div class="sub-header">风险分布与价值分析</div>', unsafe_allow_html=True)

        cols = st.columns(2)
        with cols[0]:
            risk_dist_fig = create_risk_distribution_chart(batch_analysis)
            st.plotly_chart(risk_dist_fig, use_container_width=True)

            # 添加图表解读
            total_risk_count = sum(risk_summary.values())
            high_risk_percent = (risk_summary.get('极高风险', 0) + risk_summary.get('高风险',
                                                                                    0)) / total_risk_count * 100 if total_risk_count > 0 else 0

            add_chart_explanation(f"""
            <b>图表解读：</b> 饼图展示了所有库存批次的风险分布情况，红色和橙色部分表示需要优先关注的高风险批次。目前高风险和极高风险批次共占{high_risk_percent:.1f}%，需要重点关注。
            <b>行动建议：</b> 关注极高风险和高风险批次，按照库龄和价值优先级制定清库计划；定期跟踪风险分布变化，及时调整库存管理策略。
            """)

        with cols[1]:
            risk_value_fig = create_risk_value_chart(batch_analysis)
            st.plotly_chart(risk_value_fig, use_container_width=True)

            # 添加图表解读
            total_value = batch_analysis['批次价值'].sum() if not batch_analysis.empty else 0
            high_risk_value_percent = high_risk_value / total_value * 100 if total_value > 0 else 0

            add_chart_explanation(f"""
            <b>图表解读：</b> 条形图展示了不同风险等级批次的总库存价值。高风险和极高风险批次共占用资金{format_yuan(high_risk_value)}，占总库存价值的{high_risk_value_percent:.1f}%。
            <b>行动建议：</b> 针对高价值高风险批次，设计专项清库方案，优先释放资金；对中风险批次进行常态化监控，防止升级为高风险。
            """)

        # 高风险产品列表
        st.markdown('<div class="sub-header">高风险产品优先处理清单</div>', unsafe_allow_html=True)

        high_risk_products = analysis_engine.get_high_risk_products(limit=5)
        if not high_risk_products.empty:
            # 创建高风险产品卡片
            for i, product in enumerate(high_risk_products.itertuples()):
                if i % 2 == 0:
                    cols = st.columns(2)

                with cols[i % 2]:
                    risk_color = "#FF0000" if product.风险程度 == "极高风险" else "#FF5252"
                    # 使用简化产品名称（如果有）
                    product_name = product.简化产品名称 if hasattr(product, '简化产品名称') else product.物料
                    st.markdown(f"""
                    <div class="metric-card" style="border-left: 5px solid {risk_color};">
                        <p class="card-header">{product_name} | {product.风险程度}</p>
                        <p class="card-value">{format_yuan(product.批次价值)}</p>
                        <p class="card-text">库龄: {product.库龄}天 | 清库预测: {'无法预测' if product.预计清库天数 == float('inf') else f'{int(product.预计清库天数)}天'}</p>
                        <p class="card-text">建议: {product.建议措施}</p>
                    </div>
                    """, unsafe_allow_html=True)

            # 添加高风险产品列表的解读
            add_chart_explanation(f"""
            <b>卡片解读：</b> 以上显示了库存价值最高的{len(high_risk_products)}个高风险产品，需要优先处理。每个卡片展示了产品名称、风险等级、价值、库龄、清库预测以及建议措施。
            <b>行动建议：</b> 针对这些产品制定专项清库计划，安排专人负责跟进，并定期评估清库进度。对于无法预测清库天数的产品，需要分析销售历史，检查预测模型的准确性。
            """)
        else:
            st.info("没有高风险产品，恭喜！")

    with tabs[1]:  # 库龄与清库分析
        # KPI指标
        create_metric_cards(risk_summary, batch_analysis)

        # 库龄分布图表
        st.markdown('<div class="sub-header">批次库龄分析</div>', unsafe_allow_html=True)

        # 获取库龄分析数据
        age_data = analysis_engine.get_age_clearance_data(
            risk_filter=selected_risks if 'selected_risks' in locals() and selected_risks else None
        )

        if not age_data.empty:
            age_fig = create_age_distribution_chart(age_data)
            st.plotly_chart(age_fig, use_container_width=True)

            # 添加图表解读
            over_90_days_count = sum(age_data['库龄'] > 90)
            over_60_days_count = sum(age_data['库龄'] > 60)
            over_30_days_count = sum(age_data['库龄'] > 30)

            add_chart_explanation(f"""
            <b>图表解读：</b> 此图表展示了所有批次的库龄分布情况，红线表示90天高风险阈值，橙线表示60天中风险阈值，绿线表示30天低风险阈值。
            批次库龄越长，资金占用成本越高，过期风险越大。目前有{over_90_days_count}个批次库龄超过90天，{over_60_days_count}个批次库龄超过60天，{over_30_days_count}个批次库龄超过30天。
            <b>行动建议：</b> 对库龄超过90天的批次实施特别促销计划；60-90天的批次进行常规促销；30-60天的批次密切监控销售情况。建立库龄预警机制，在产品到达60天库龄前干预。
            """)

            # 清库预测图表
            st.markdown('<div class="sub-header">清库预测分析</div>', unsafe_allow_html=True)

            clearance_fig = create_clearance_chart(age_data)
            st.plotly_chart(clearance_fig, use_container_width=True)

            # 添加图表解读
            infinite_count = sum(age_data['预计清库天数'] == float('inf'))
            over_90_count = sum((age_data['预计清库天数'] != float('inf')) & (age_data['预计清库天数'] > 90))
            big_gap_count = sum(
                (age_data['预计清库天数'] != float('inf')) & (age_data['预计清库天数'] > age_data['库龄'] * 2))

            add_chart_explanation(f"""
            <b>图表解读：</b> 此图展示了预计清库天数最长的批次。蓝色菱形点表示当前库龄，横条表示预计清库天数。有{infinite_count}个批次因无销量导致无法预测清库时间，
            另有{over_90_count}个批次预计清库时间超过90天。预计清库天数远大于当前库龄的批次({big_gap_count}个)面临严重的积压风险。
            <b>行动建议：</b> 对无法清库的批次考虑特价处理或转仓；对预计清库天数超过90天的批次，制定阶段性清库目标；结合产品生命周期，评估是否需要调整生产计划。
            """)
        else:
            st.info("没有库龄数据，请调整筛选条件或检查数据源。")

    with tabs[2]:  # 预测偏差分析
        # KPI指标
        create_metric_cards(risk_summary, batch_analysis)

        # 预测偏差分析图表
        st.markdown('<div class="sub-header">预测偏差分析</div>', unsafe_allow_html=True)

        # 获取预测偏差数据
        bias_data = analysis_engine.get_forecast_bias_data()

        if not bias_data.empty:
            bias_fig = create_forecast_bias_chart(bias_data)
            st.plotly_chart(bias_fig, use_container_width=True)

            # 添加图表解读
            positive_bias = sum(bias_data['预测偏差数值'] > 0.3)
            negative_bias = sum(bias_data['预测偏差数值'] < -0.3)
            moderate_bias = sum((bias_data['预测偏差数值'] > 0.15) & (bias_data['预测偏差数值'] <= 0.3))

            add_chart_explanation(f"""
            <b>图表解读：</b> 此图分析了预测偏差最显著的批次。红色表示预测过高(导致库存积压)，蓝色表示预测过低(可能导致缺货)。
            有{positive_bias}个批次预测显著过高(>30%)，{negative_bias}个批次预测显著过低(<-30%)，{moderate_bias}个批次预测中等偏高(15%-30%)。
            <b>行动建议：</b> 针对预测过高的产品，审查预测模型并调整参数；对预测过低的产品，加强市场监控和需求捕捉；建立预测准确率考核机制，提高预测质量。
            """)

            # 预测准确度与清库关系分析
            st.markdown('<div class="sub-header">预测准确度与清库关系分析</div>', unsafe_allow_html=True)

            accuracy_fig = create_forecast_accuracy_chart(bias_data)
            st.plotly_chart(accuracy_fig, use_container_width=True)

            # 添加图表解读
            right_up = sum((bias_data['预测偏差数值'] > 0.3) & (bias_data['预计清库天数'] > 90))
            left_up = sum((bias_data['预测偏差数值'] < -0.3) & (bias_data['预计清库天数'] > 90))

            add_chart_explanation(f"""
            <b>图表解读：</b> 此散点图展示了预测偏差与清库天数的关系，气泡大小表示批次价值。
            右上象限(预测过高、清库困难)的产品是最高风险区域，有{right_up}个批次需要特别关注；
            左上象限(预测过低、清库困难)的产品有{left_up}个，表明市场需求超出预期，建议检查产能；
            右下和左下象限的产品虽有预测偏差但清库天数合理，风险相对较低。
            <b>行动建议：</b> 针对右上象限的产品，进行促销清库并调整下期预测；对左上象限的产品，增加产能或订货量；对下半区产品，保持常规管理即可。
            """)
        else:
            st.info("没有预测偏差数据，请调整筛选条件或检查数据源。")

    with tabs[3]:  # 责任分析与跟踪
        # KPI指标
        create_metric_cards(risk_summary, batch_analysis)

        # 责任分析图表
        st.markdown('<div class="sub-header">责任区域与人员分析</div>', unsafe_allow_html=True)

        # 获取责任分析数据
        responsibility_data = analysis_engine.get_responsibility_data()

        if not responsibility_data.empty:
            cols = st.columns(2)
            with cols[0]:
                region_fig = create_responsibility_region_chart(responsibility_data)
                st.plotly_chart(region_fig, use_container_width=True)

                # 添加图表解读
                region_counts = responsibility_data['责任区域'].value_counts()
                largest_region = region_counts.idxmax() if not region_counts.empty else "无数据"
                largest_count = region_counts.max() if not region_counts.empty else 0

                add_chart_explanation(f"""
                <b>图表解读：</b> 饼图展示了库存批次的责任区域分布情况。区域占比反映了各区域在库存管理中的责任比重。
                责任区域分布不均可能反映区域间的预测准确度和销售执行力差异。{largest_region}区域责任批次最多，共{largest_count}个批次。
                <b>行动建议：</b> 对责任比重高的区域进行重点培训和支持；推广责任占比低的区域的最佳实践；建立区域间的库存管理经验分享机制。
                """)

            with cols[1]:
                person_fig = create_responsibility_person_chart(responsibility_data)
                st.plotly_chart(person_fig, use_container_width=True)

                # 添加图表解读
                if not responsibility_data.empty:
                    person_stats = responsibility_data.groupby('责任人').agg({
                        '风险得分': 'mean',
                        '物料': 'count'
                    }).reset_index()
                    top_risk_person = person_stats.nlargest(1, '风险得分')
                    person_name = top_risk_person['责任人'].iloc[0] if not top_risk_person.empty else "无数据"
                    person_score = top_risk_person['风险得分'].iloc[0] if not top_risk_person.empty else 0

                    add_chart_explanation(f"""
                    <b>图表解读：</b> 条形图展示了责任人的风险评分排名。评分越高表示该责任人管理的批次风险程度越高，可能反映预测准确度和销售执行力的问题。
                    责任人{person_name}的风险评分最高，达到{person_score:.1f}分，表明其管理的批次风险程度较高。
                    <b>行动建议：</b> 对高风险评分的责任人提供针对性培训和支持；组织低风险评分责任人分享经验；将库存管理纳入绩效考核体系。
                    """)
                else:
                    add_chart_explanation("""
                    <b>图表解读：</b> 条形图展示了责任人的风险评分排名。图表无数据，请调整筛选条件或检查数据源。
                    """)

            # 预测履行率热力图
            st.markdown('<div class="sub-header">责任人-区域预测履行率分析</div>', unsafe_allow_html=True)

            fulfillment_fig = create_fulfillment_rate_chart(responsibility_data)
            st.plotly_chart(fulfillment_fig, use_container_width=True)

            # 添加图表解读
            add_chart_explanation(f"""
            <b>图表解读：</b> 热力图展示了不同责任人在不同区域的预测履行率（实际销售/预测销售）。
            颜色越绿表示履行率越高（接近100%），颜色越红表示履行率越低。
            履行率分布反映了预测准确度和销售执行力的组合表现，区域和人员的交叉分析有助于识别系统性问题。
            <b>行动建议：</b> 对红色区域进行重点关注和改进；分析绿色区域的成功因素并推广；建立预测-销售协同机制，提高整体履行率。
            """)

            # 详细批次责任信息
            st.markdown('<div class="sub-header">批次责任详情列表（前10个批次）</div>', unsafe_allow_html=True)

            # 选择前10个高风险批次显示责任详情
            top_risk_batches = responsibility_data.sort_values(
                by=['风险排序' if '风险排序' in responsibility_data.columns else '风险程度', '批次价值'],
                ascending=[True, False]).head(10)

            # 创建表格显示责任详情
            for i, batch in enumerate(top_risk_batches.itertuples()):
                with st.expander(f"批次 {i + 1}: {batch.物料} - {batch.描述[:30]}... (风险: {batch.风险程度})"):
                    st.markdown(f"""
                    **批次信息:**
                    - 批次日期: {batch.批次日期}
                    - 批次库存: {batch.批次库存} 件
                    - 库龄: {batch.库龄} 天
                    - 批次价值: {format_yuan(batch.批次价值)}
                    - 预计清库天数: {'无法预测' if batch.预计清库天数 == float('inf') else f'{int(batch.预计清库天数)}天'}

                    **责任分析:**
                    - 责任区域: {batch.责任区域 if batch.责任区域 else '无指定区域'}
                    - 责任人: {batch.责任人}
                    - 责任摘要: {batch.责任分析摘要}

                    **风险评估:**
                    - 风险程度: {batch.风险程度}
                    - 风险得分: {batch.风险得分}
                    - 建议措施: {batch.建议措施}
                    """)

            # 责任分析总结
            st.markdown('<div class="sub-header">责任分析总结</div>', unsafe_allow_html=True)

            # 计算责任人和区域的总体统计
            person_summary = responsibility_data.groupby('责任人').agg({
                '物料': 'count',
                '批次价值': 'sum',
                '风险得分': 'mean'
            }).sort_values('批次价值', ascending=False).reset_index()

            person_summary.columns = ['责任人', '批次数量', '总批次价值', '平均风险得分']

            region_summary = responsibility_data.groupby('责任区域').agg({
                '物料': 'count',
                '批次价值': 'sum',
                '风险得分': 'mean'
            }).sort_values('批次价值', ascending=False).reset_index()

            region_summary.columns = ['责任区域', '批次数量', '总批次价值', '平均风险得分']

            # 显示表格
            cols = st.columns(2)
            with cols[0]:
                st.subheader("责任人库存概况")
                st.dataframe(person_summary, use_container_width=True)

            with cols[1]:
                st.subheader("责任区域库存概况")
                st.dataframe(region_summary, use_container_width=True)

            add_chart_explanation("""
            <b>结论：</b> 责任分析表明，库存积压的主要原因包括预测偏高、销售履行率低和区域协同不足。通过明确责任人和责任区域，可以更有针对性地进行库存管理。
            <b>建议行动：</b> 
            1. 建立预测-销售协同机制，提高预测准确度和履行率
            2. 将库存管理纳入绩效考核体系，激励责任人积极清库
            3. 开展区域间和责任人间的经验分享，推广最佳实践
            4. 定期进行库存风险评估和责任分析，及时干预高风险批次
            """)
        else:
            st.info("没有责任分析数据，请调整筛选条件或检查数据源。")


if __name__ == "__main__":
    main()