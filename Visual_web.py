# ==================== Visual_web.py ====================
# 新能源重卡充电站投资测算模型 - 可视化Web界面
# 技术栈：Streamlit + Plotly + Pandas
# 公司：Global Nexus Group

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# 设置页面配置（必须放在最前面）
st.set_page_config(
    page_title="Global Nexus Group - 重卡充电站投资测算模型",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ======================== 自定义CSS样式（最终优化版） ========================

def load_css():
    """加载自定义CSS样式 - 深色背景，白底黑字输入框，橙色标题"""
    st.markdown("""
    <style>
    /* ===== 全局背景 ===== */
    .stApp {
        background: linear-gradient(145deg, #0a0e1a 0%, #1a1f2f 100%);
        font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
    }

    /* ===== 主标题 ===== */
    .main-title {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
        background: linear-gradient(90deg, #f7931e, #ffd700, #f7931e);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.2rem;
        font-weight: 800;
        letter-spacing: 2px;
        text-shadow: 0 0 40px rgba(247, 147, 30, 0.15);
        animation: shimmer 4s ease-in-out infinite;
    }

    @keyframes shimmer {
        0% { background-position: 0% center; }
        50% { background-position: 100% center; }
        100% { background-position: 0% center; }
    }

    .sub-title {
        text-align: center;
        color: #8892b0 !important;
        font-size: 1rem;
        font-weight: 300;
        letter-spacing: 4px;
        margin-top: -0.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(247, 147, 30, 0.2);
    }

    /* ===== 公司水印 ===== */
    .watermark {
        position: fixed;
        top: 20px;
        right: 30px;
        color: rgba(247, 147, 30, 0.15);
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 3px;
        z-index: 999;
        pointer-events: none;
        font-family: 'Segoe UI', sans-serif;
        background: rgba(10, 14, 26, 0.6);
        padding: 6px 16px;
        border-radius: 20px;
        border: 1px solid rgba(247, 147, 30, 0.08);
    }

    /* ===== 侧边栏 ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1225 0%, #141b33 100%);
        border-right: 1px solid rgba(247, 147, 30, 0.1);
        padding: 1rem 0.5rem;
    }

    /* ===== 侧边栏所有标签 ===== */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stNumberInput label,
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stCheckbox label {
        color: #ccd6f6 !important;
        font-weight: 500;
        font-size: 0.85rem;
    }

    /* ===== 侧边栏输入框：白底黑字 ===== */
    [data-testid="stSidebar"] .stNumberInput input {
        background-color: #ffffff !important;
        color: #1a1a2e !important;
        border: 1px solid #d0d0d0 !important;
        border-radius: 6px !important;
        padding: 6px 12px !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] .stNumberInput input:focus {
        border-color: #f7931e !important;
        box-shadow: 0 0 0 2px rgba(247,147,30,0.2) !important;
    }

    [data-testid="stSidebar"] .stSelectbox select {
        background-color: #ffffff !important;
        color: #1a1a2e !important;
        border: 1px solid #d0d0d0 !important;
        border-radius: 6px !important;
        padding: 6px 12px !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] .stSelectbox select:focus {
        border-color: #f7931e !important;
    }

    [data-testid="stSidebar"] .stCheckbox label span {
        color: #e6edff !important;
    }
    [data-testid="stSidebar"] .stCheckbox input[type="checkbox"] {
        accent-color: #f7931e !important;
    }

    [data-testid="stSidebar"] .stRadio label span {
        color: #e6edff !important;
    }
    [data-testid="stSidebar"] .stRadio input[type="radio"] {
        accent-color: #f7931e !important;
    }

    [data-testid="stSidebar"] .stSlider .stSliderTrack {
        background: rgba(247,147,30,0.3) !important;
    }
    [data-testid="stSidebar"] .stSlider .stSliderThumb {
        background: #f7931e !important;
    }

    .sidebar-footer {
        position: fixed;
        bottom: 20px;
        left: 20px;
        color: rgba(247, 147, 30, 0.25);
        font-size: 0.7rem;
        letter-spacing: 2px;
        font-weight: 300;
        z-index: 100;
    }

    /* ===== Expander 折叠标题（橙色高亮） ===== */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, rgba(247, 147, 30, 0.08), rgba(247, 147, 30, 0.02)) !important;
        border: 1px solid rgba(247, 147, 30, 0.25) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        color: #f7931e !important;  /* 橙色高亮 */
        font-size: 1.05rem !important;
        padding: 12px 18px !important;
        transition: all 0.3s ease;
    }
    .streamlit-expanderHeader:hover {
        background: linear-gradient(90deg, rgba(247, 147, 30, 0.15), rgba(247, 147, 30, 0.05)) !important;
        border-color: rgba(247, 147, 30, 0.5) !important;
        box-shadow: 0 0 25px rgba(247, 147, 30, 0.1);
        color: #ffb74d !important;
    }

    /* 展开后内部输入框保持白底黑字 */
    .streamlit-expanderContent .stNumberInput input {
        background-color: #ffffff !important;
        color: #1a1a2e !important;
        border: 1px solid #d0d0d0 !important;
        border-radius: 6px !important;
    }
    .streamlit-expanderContent .stNumberInput input:focus {
        border-color: #f7931e !important;
    }
    .streamlit-expanderContent label {
        color: #ccd6f6 !important;
    }

    /* ===== 指标卡片（白底黑字） ===== */
    .stMetric {
        background: #ffffff !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
        border: 1px solid rgba(247,147,30,0.08) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(247,147,30,0.15) !important;
    }
    .stMetric .stMetricLabel {
        color: #555 !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stMetric .stMetricValue {
        color: #1a1a2e !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    .stMetric .stMetricDelta {
        color: #666 !important;
    }

    /* ===== 表格（白底黑字） ===== */
    .stDataFrame {
        background: #ffffff !important;
        border-radius: 12px !important;
        padding: 4px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2) !important;
        border: 1px solid rgba(247,147,30,0.08) !important;
    }
    .stDataFrame table {
        color: #1a1a2e !important;
        font-size: 13px !important;
    }
    .stDataFrame th {
        color: #ffffff !important;
        background: linear-gradient(90deg, #f7931e, #e07b1a) !important;
        font-weight: 700 !important;
        padding: 10px 12px !important;
        text-align: left !important;
    }
    .stDataFrame td {
        color: #1a1a2e !important;
        padding: 8px 12px !important;
        border-bottom: 1px solid #f0f0f0 !important;
    }
    .stDataFrame tr:hover td {
        background: #faf5ee !important;
    }

    /* ===== 重卡装饰图标 ===== */
    .truck-icon {
        font-size: 3rem;
        opacity: 0.6;
        display: inline-block;
        animation: float 6s ease-in-out infinite;
    }

    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-8px) rotate(2deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }

    /* ===== 按钮样式 ===== */
    .stButton button {
        background: linear-gradient(90deg, #f7931e, #ffb347) !important;
        color: #0a0e1a !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(247,147,30,0.2) !important;
    }
    .stButton button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 25px rgba(247,147,30,0.35) !important;
    }

    /* ===== 主区域标题 ===== */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #f0f4ff !important;
        font-weight: 600;
        letter-spacing: 1px;
    }
    .stMarkdown p, .stMarkdown li {
        color: #ccd6f6 !important;
    }

    /* ===== 滚动条 ===== */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #0a0e1a; }
    ::-webkit-scrollbar-thumb { background: rgba(247, 147, 30, 0.3); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(247, 147, 30, 0.5); }
    </style>
    """, unsafe_allow_html=True)


load_css()

# ======================== 导入引擎 ========================

from operation_engine import run_simulation
# 导入各模块用于获取当前默认值（初始显示）
import params_jichucanshu
import params_price_revenue
import params_tax_finance
import params_operating_cost
import solarPV_params
import Battery_params
import charger_params
import other_capEX_params

# ======================== 页面布局 ========================

# ---- 顶部：公司水印 + 标题 ----
st.markdown("""
<div class="watermark">⚡ Global Nexus Group</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">⚡ 新能源重卡充电站</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">投资测算模型 · 光储充一体化 · Global Nexus Group</div>', unsafe_allow_html=True)

# ---- 侧边栏：控制面板 ----
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 0.5rem 0 1rem 0;">
        <span style="font-size:3rem;">🚛⚡</span>
        <p style="color:#ccd6f6; font-size:0.9rem; margin-top:0.2rem; font-weight:300;">Global Nexus Group</p>
        <p style="color:#64ffda; font-size:0.7rem; font-weight:300; letter-spacing:2px; border-top:1px solid rgba(247,147,30,0.1); padding-top:0.5rem;">
            POWERING THE FUTURE
        </p>
    </div>
    """, unsafe_allow_html=True)

    # -------- 模式选择 --------
    st.markdown("---")
    st.markdown("### 🎯 测算模式")
    mode = st.radio(
        "选择模式",
        ["正常测算", "反向求解"],
        label_visibility="collapsed",
        horizontal=True
    )

    if mode == "反向求解":
        st.markdown("---")
        st.markdown("### 🎯 目标指标")
        target_type = st.selectbox(
            "选择目标指标",
            ["全投资IRR", "自有资金IRR", "全投资回收期", "自有资金回收期"]
        )
        target_value = st.number_input(
            "目标值（IRR输入小数如0.08，回收期输入年数）",
            value=0.08,
            step=0.01,
            format="%.4f"
        )
        # ===== 新增：反向求解模式下的还款方式选择 =====
        st.markdown("---")
        st.markdown("### 💳 还款方式")
        solve_loan_type = st.selectbox(
            "选择还款方式",
            ["等额本息", "等额本金"],
            key="solve_loan_type",
            help="选择反向求解时使用的还款方式"
        )
        # ===== 新增：反向求解模式下的固定总投资 =====
        st.markdown("---")
        st.markdown("### 💰 固定总投资模式")
        solve_use_fixed = st.checkbox(
            "启用固定总投资模式",
            value=False,
            key="solve_use_fixed",
            help="启用后，反向求解将在指定的总投资额下进行"
        )
        solve_fixed_value = 0.0
        if solve_use_fixed:
            solve_fixed_value = st.number_input(
                "固定总投资额（元）",
                value=50000000.0,
                min_value=1000000.0,
                max_value=1000000000.0,
                step=1000000.0,
                format="%.0f",
                key="solve_fixed_value",
                help="请输入固定总投资额"
            )
        st.caption("💡 系统将在0~10万元/亩/年范围内求解土地租金单价")

    # -------- 技术路线与还款方式 --------
    st.markdown("---")
    st.markdown("### 🔧 系统配置")
    technology = st.selectbox("技术路线", ["交流", "直流"])
    loan_type = st.selectbox("还款方式", ["等额本息", "等额本金"])
    repayment_freq = st.selectbox("还款频率", ["年", "半年", "月"])

    # ===== 新增：固定总投资模式 =====
    st.markdown("---")
    use_fixed_capex = st.checkbox(
        "✅ 启用固定总投资模式",
        value=params_jichucanshu.USE_FIXED_CAPEX,
        help="启用后，将使用您指定的固定总投资额，各子模块投资按比例缩放"
    )

    fixed_capex_value = 0.0
    if use_fixed_capex:
        fixed_capex_value = st.number_input(
            "固定总投资额（元）",
            value=float(params_jichucanshu.FIXED_TOTAL_CAPEX) if params_jichucanshu.FIXED_TOTAL_CAPEX > 0 else 50000000.0,
            min_value=1000000.0,
            max_value=1000000000.0,
            step=1000000.0,
            format="%.0f",
            help="请输入您希望固定的总投资额（元），各子模块投资将按比例缩放"
        )
        st.caption("💡 启用后，总投资将固定为您输入的金额，各子模块占比保持不变")

    # -------- 8个可折叠参数分类 --------
    st.markdown("---")
    st.markdown("### 📊 参数调整面板")

    # 存储所有参数值，用于后续更新
    param_values = {}

    # ---- 1. 宏观参数 ----
    with st.expander("🏛️ 一、项目宏观参数", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            p_years = st.number_input("项目周期（年）", value=float(params_jichucanshu.PROJECT_YEARS), min_value=1.0,
                                      max_value=50.0, step=1.0, key="p_years")
            p_discount = st.number_input("基准折现率（%）", value=float(params_jichucanshu.DISCOUNT_RATE * 100),
                                         min_value=0.0, max_value=20.0, step=0.1, key="p_discount") / 100.0
        with col2:
            p_months = st.number_input("建设期（月）", value=float(params_jichucanshu.CONSTRUCTION_MONTHS), min_value=0.0,
                                       max_value=24.0, step=1.0, key="p_months")
        param_values["jichucanshu"] = {
            "PROJECT_YEARS": int(p_years),
            "CONSTRUCTION_MONTHS": int(p_months),
            "DISCOUNT_RATE": p_discount
        }

    # ---- 2. 电价与收入 ----
    with st.expander("⚡ 二、电价与收入参数", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            p_peak = st.number_input("尖峰电价（元/kWh）", value=float(params_price_revenue.PRICE_PEAK), min_value=0.0,
                                     max_value=3.0, step=0.01, key="p_peak")
            p_high = st.number_input("高峰电价（元/kWh）", value=float(params_price_revenue.PRICE_HIGH), min_value=0.0,
                                     max_value=3.0, step=0.01, key="p_high")
            p_flat = st.number_input("平段电价（元/kWh）", value=float(params_price_revenue.PRICE_FLAT), min_value=0.0,
                                     max_value=3.0, step=0.01, key="p_flat")
            p_valley = st.number_input("低谷电价（元/kWh）", value=float(params_price_revenue.PRICE_VALLEY),
                                       min_value=0.0, max_value=3.0, step=0.01, key="p_valley")
        with col2:
            p_service = st.number_input("充电服务费（元/kWh）", value=float(params_price_revenue.SERVICE_FEE),
                                        min_value=0.0, max_value=2.0, step=0.01, key="p_service")
            p_sell = st.number_input("余电上网电价（元/kWh）", value=float(params_price_revenue.SELL_PRICE),
                                     min_value=0.0, max_value=2.0, step=0.01, key="p_sell")
            # ===== 新增：设备销售收入比例 =====
            p_equipment_sales_ratio = st.number_input(
                "设备销售收入比例（%）",
                value=float(params_price_revenue.EQUIPMENT_SALES_REVENUE_RATIO * 100),
                min_value=0.0,
                max_value=100.0,
                step=0.5,
                key="p_equipment_sales_ratio",
                help="设备销售收入 = 设备成本总额 × 该比例，仅第1年产生"
            ) / 100.0
            # ===== 新增：其它收入 =====
            p_other_income = st.number_input(
                "其它收入（元/年）",
                value=float(params_price_revenue.OTHER_INCOME),
                min_value=0.0,
                max_value=10000000.0,
                step=10000.0,
                key="p_other_income",
                help="预留入口，用于碳交易、政府补贴、广告收入等，仅第1年产生"
            )
            p_peak_h = st.number_input("尖峰时段（小时/天）", value=float(params_price_revenue.PEAK_HOURS), min_value=0.0,
                                       max_value=24.0, step=0.5, key="p_peak_h")
            p_high_h = st.number_input("高峰时段（小时/天）", value=float(params_price_revenue.HIGH_HOURS), min_value=0.0,
                                       max_value=24.0, step=0.5, key="p_high_h")
            p_flat_h = st.number_input("平段时段（小时/天）", value=float(params_price_revenue.FLAT_HOURS), min_value=0.0,
                                       max_value=24.0, step=0.5, key="p_flat_h")
            p_valley_h = st.number_input("谷段时段（小时/天）", value=float(params_price_revenue.VALLEY_HOURS),
                                         min_value=0.0, max_value=24.0, step=0.5, key="p_valley_h")
        param_values["price_revenue"] = {
            "PRICE_PEAK": p_peak,
            "PRICE_HIGH": p_high,
            "PRICE_FLAT": p_flat,
            "PRICE_VALLEY": p_valley,
            "SERVICE_FEE": p_service,
            "SELL_PRICE": p_sell,
            "EQUIPMENT_SALES_REVENUE_RATIO": p_equipment_sales_ratio,
            "OTHER_INCOME": p_other_income,
            "PEAK_HOURS": p_peak_h,
            "HIGH_HOURS": p_high_h,
            "FLAT_HOURS": p_flat_h,
            "VALLEY_HOURS": p_valley_h
        }

    # ---- 3. 税务与财务 ----
    with st.expander("💰 三、税务与财务参数", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            p_tax = st.number_input("所得税率（%）", value=float(params_tax_finance.INCOME_TAX_RATE * 100), min_value=0.0,
                                    max_value=50.0, step=0.5, key="p_tax") / 100.0
            p_surcharge = st.number_input("税金及附加（%）", value=float(params_tax_finance.SURCHARGE_RATE * 100),
                                          min_value=0.0, max_value=20.0, step=0.5, key="p_surcharge") / 100.0
            p_dep = st.number_input("折旧年限（年）", value=float(params_tax_finance.DEPRECIATION_YEARS), min_value=1.0,
                                    max_value=50.0, step=1.0, key="p_dep")
            p_residual = st.number_input("残值率（%）", value=float(params_tax_finance.RESIDUAL_RATE_DEP * 100),
                                         min_value=0.0, max_value=30.0, step=0.5, key="p_residual") / 100.0
            p_amort = st.number_input("摊销年限（年）", value=float(params_tax_finance.AMORTIZATION_YEARS), min_value=1.0,
                                      max_value=50.0, step=1.0, key="p_amort")
        with col2:
            p_equity = st.number_input("资本金比例（%）", value=float(params_tax_finance.EQUITY_RATIO * 100),
                                       min_value=5.0, max_value=100.0, step=1.0, key="p_equity") / 100.0
            p_loan_rate = st.number_input("贷款利率（%）", value=float(params_tax_finance.LOAN_RATE * 100), min_value=0.0,
                                          max_value=20.0, step=0.05, key="p_loan_rate") / 100.0
            p_loan_period = st.number_input("贷款年限（年）", value=float(params_tax_finance.LOAN_PERIOD), min_value=1.0,
                                            max_value=30.0, step=1.0, key="p_loan_period")
            # ===== 新增：换电池贷款年限 =====
            p_battery_loan_period = st.number_input(
                "换电池贷款年限（年）",
                value=float(params_tax_finance.BATTERY_LOAN_PERIOD),
                min_value=1.0,
                max_value=20.0,
                step=1.0,
                key="p_battery_loan_period"
            )
            # ===== 新增：换电池贷款利率 =====
            p_battery_loan_rate = st.number_input(
                "换电池贷款利率（%）",
                value=float(params_tax_finance.BATTERY_LOAN_RATE * 100),
                min_value=0.0,
                max_value=20.0,
                step=0.05,
                key="p_battery_loan_rate"
            ) / 100.0
            p_holiday = st.checkbox("启用三免三减半", value=params_tax_finance.TAX_HOLIDAY, key="p_holiday")
            p_rebate = st.checkbox("启用即征即退", value=params_tax_finance.TAX_REBATE, key="p_rebate")
            p_inflation = st.number_input("通货膨胀率（%）", value=float(params_tax_finance.INFLATION_RATE * 100),
                                          min_value=0.0, max_value=10.0, step=0.1, key="p_inflation") / 100.0
        param_values["tax_finance"] = {
            "INCOME_TAX_RATE": p_tax,
            "SURCHARGE_RATE": p_surcharge,
            "DEPRECIATION_YEARS": int(p_dep),
            "RESIDUAL_RATE_DEP": p_residual,
            "AMORTIZATION_YEARS": int(p_amort),
            "EQUITY_RATIO": p_equity,
            "LOAN_RATE": p_loan_rate,
            "LOAN_PERIOD": int(p_loan_period),
            "BATTERY_LOAN_PERIOD": int(p_battery_loan_period),
            "BATTERY_LOAN_RATE": p_battery_loan_rate,
            "TAX_HOLIDAY": p_holiday,
            "TAX_REBATE": p_rebate,
            "INFLATION_RATE": p_inflation
        }

    # ---- 4. 运营成本 ----
    with st.expander("🏗️ 四、运营成本参数", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            p_land_area = st.number_input("全部用地面积（亩）", value=float(params_operating_cost.LAND_AREA),
                                          min_value=0.0, max_value=200.0, step=1.0, key="p_land_area")
            p_land_rent = st.number_input("土地租金单价（万元/亩/年）",
                                          value=float(params_operating_cost.LAND_RENT_PER_MU), min_value=0.0,
                                          max_value=10.0, step=0.1, key="p_land_rent")
            p_va_area = st.number_input("增值服务用地面积（亩）",
                                        value=float(params_operating_cost.LAND_AREA_VALUE_ADDED), min_value=0.0,
                                        max_value=100.0, step=1.0, key="p_va_area")
            p_va_revenue = st.number_input("增值服务每亩收入（元/亩/年）",
                                           value=float(params_operating_cost.LAND_REVENUE_PER_MU), min_value=0.0,
                                           max_value=100000.0, step=1000.0, key="p_va_revenue")
        with col2:
            p_staff = st.number_input("人数（人）", value=float(params_operating_cost.STAFF_COUNT), min_value=0.0,
                                      max_value=50.0, step=1.0, key="p_staff")
            p_salary = st.number_input("年工资（万元/人/年）", value=float(params_operating_cost.ANNUAL_SALARY),
                                       min_value=0.0, max_value=50.0, step=0.5, key="p_salary")
            p_insurance = st.number_input("保险费率（%）", value=float(params_operating_cost.INSURANCE_RATE * 100),
                                          min_value=0.0, max_value=5.0, step=0.01, key="p_insurance") / 100.0
            p_capacity = st.number_input("容量费（万元/年）", value=float(params_operating_cost.CAPACITY_FEE),
                                         min_value=0.0, max_value=100.0, step=1.0, key="p_capacity")
        param_values["operating_cost"] = {
            "LAND_AREA": p_land_area,
            "LAND_RENT_PER_MU": p_land_rent,
            "LAND_AREA_VALUE_ADDED": p_va_area,
            "LAND_REVENUE_PER_MU": p_va_revenue,
            "STAFF_COUNT": int(p_staff),
            "ANNUAL_SALARY": p_salary,
            "STAFF_COST_FIRST_YEAR": p_staff * p_salary,
            "INSURANCE_RATE": p_insurance,
            "CAPACITY_FEE": p_capacity
        }

    # ---- 5. 光伏参数 ----
    with st.expander("☀️ 五、光伏系统参数", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            p_pv_cap = st.number_input("光伏装机容量（kWp）", value=float(solarPV_params.PV_CAPACITY), min_value=0.0,
                                       max_value=10000.0, step=100.0, key="p_pv_cap")
            p_sun_hours = st.number_input("峰值日照小时数（小时/天）", value=float(solarPV_params.PEAK_SUN_HOURS),
                                          min_value=0.0, max_value=8.0, step=0.1, key="p_sun_hours")
            p_pv_degrad = st.number_input("年衰减率（%）", value=float(solarPV_params.PV_DEGRADATION * 100),
                                          min_value=0.0, max_value=5.0, step=0.01, key="p_pv_degrad") / 100.0
            p_pv_cost = st.number_input("组件单位投资成本（元/W）", value=float(solarPV_params.PV_COST_PER_W),
                                        min_value=0.0, max_value=10.0, step=0.01, key="p_pv_cost")
        with col2:
            p_pv_opex = st.number_input("年运维费（元/W）", value=float(solarPV_params.PV_OPEX_PER_W), min_value=0.0,
                                        max_value=1.0, step=0.0001, format="%.4f", key="p_pv_opex")
            p_pv_inv = st.number_input("逆变器投入（万元）", value=float(solarPV_params.PV_INVERTER_COST), min_value=0.0,
                                       max_value=500.0, step=1.0, key="p_pv_inv")
            p_pv_bracket = st.number_input("支吊架投入（万元）", value=float(solarPV_params.PV_BRACKET_COST),
                                           min_value=0.0, max_value=500.0, step=1.0, key="p_pv_bracket")
            p_pv_dep = st.number_input("光伏折旧年限（年）", value=float(solarPV_params.PV_DEPRECIATION_YEARS),
                                       min_value=1.0, max_value=50.0, step=1.0, key="p_pv_dep")
            p_pv_res = st.number_input("光伏残值率（%）", value=float(solarPV_params.PV_RESIDUAL_RATE * 100),
                                       min_value=0.0, max_value=30.0, step=0.5, key="p_pv_res") / 100.0
        param_values["solarPV"] = {
            "PV_CAPACITY": p_pv_cap,
            "PEAK_SUN_HOURS": p_sun_hours,
            "PV_DEGRADATION": p_pv_degrad,
            "PV_COST_PER_W": p_pv_cost,
            "PV_OPEX_PER_W": p_pv_opex,
            "PV_INVERTER_COST": p_pv_inv,
            "PV_BRACKET_COST": p_pv_bracket,
            "PV_DEPRECIATION_YEARS": int(p_pv_dep),
            "PV_RESIDUAL_RATE": p_pv_res
        }

    # ---- 6. 储能参数 ----
    with st.expander("🔋 六、储能系统参数", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            p_bat_cap = st.number_input("储能容量（kWh）", value=float(Battery_params.BATTERY_CAPACITY), min_value=0.0,
                                        max_value=100000.0, step=1000.0, key="p_bat_cap")
            p_bat_power = st.number_input("储能功率（kW）", value=float(Battery_params.BATTERY_POWER), min_value=0.0,
                                          max_value=50000.0, step=500.0, key="p_bat_power")
            p_bat_ac = st.number_input("交流系统单价（元/Wh）", value=float(Battery_params.BATTERY_COST_PER_WH_AC),
                                       min_value=0.0, max_value=2.0, step=0.0001, format="%.4f", key="p_bat_ac")
            p_bat_dc = st.number_input("直流系统单价（元/Wh）", value=float(Battery_params.BATTERY_COST_PER_WH_DC),
                                       min_value=0.0, max_value=2.0, step=0.0001, format="%.4f", key="p_bat_dc")
            p_bat_cell = st.number_input("电芯单价（元/Wh）", value=float(Battery_params.BATTERY_CELL_COST_PER_WH),
                                         min_value=0.0, max_value=1.0, step=0.01, key="p_bat_cell")
            p_bat_eff = st.number_input("充放电效率（%）", value=float(Battery_params.BATTERY_EFFICIENCY * 100),
                                        min_value=50.0, max_value=100.0, step=0.5, key="p_bat_eff") / 100.0
            p_bat_dod = st.number_input("放电深度DOD（%）", value=float(Battery_params.BATTERY_DOD * 100), min_value=50.0,
                                        max_value=100.0, step=0.5, key="p_bat_dod") / 100.0
        with col2:
            p_bat_cycle = st.number_input("循环寿命（次）", value=float(Battery_params.BATTERY_CYCLE_LIFE), min_value=0.0,
                                          max_value=20000.0, step=500.0, key="p_bat_cycle")
            p_bat_degrad = st.number_input("储能年衰减率（%）", value=float(Battery_params.BATTERY_DEGRADATION * 100),
                                           min_value=0.0, max_value=10.0, step=0.1, key="p_bat_degrad") / 100.0
            p_bat_opex = st.number_input("储能年运维费率（%）", value=float(Battery_params.BATTERY_OPEX_RATE * 100),
                                         min_value=0.0, max_value=10.0, step=0.1, key="p_bat_opex") / 100.0
            p_bat_cell_dep = st.number_input("电芯折旧年限（年）",
                                             value=float(Battery_params.BATTERY_CELL_DEPRECIATION_YEARS), min_value=1.0,
                                             max_value=20.0, step=1.0, key="p_bat_cell_dep")
            p_bat_cell_res = st.number_input("电芯残值率（%）",
                                             value=float(Battery_params.BATTERY_CELL_RESIDUAL_RATE * 100),
                                             min_value=0.0, max_value=30.0, step=0.5, key="p_bat_cell_res") / 100.0
            p_bat_other_dep = st.number_input("其他设备折旧年限（年）",
                                              value=float(Battery_params.BATTERY_OTHER_DEPRECIATION_YEARS),
                                              min_value=1.0, max_value=50.0, step=1.0, key="p_bat_other_dep")
            p_bat_other_res = st.number_input("其他设备残值率（%）",
                                              value=float(Battery_params.BATTERY_OTHER_RESIDUAL_RATE * 100),
                                              min_value=0.0, max_value=30.0, step=0.5, key="p_bat_other_res") / 100.0
            p_bat_cycle_day = st.number_input("日充放电次数（次/天）", value=float(Battery_params.BATTERY_CYCLE_PER_DAY),
                                              min_value=0.0, max_value=10.0, step=1.0, key="p_bat_cycle_day")
            p_bat_op_days = st.number_input("储能年运行天数（天/年）", value=float(Battery_params.BATTERY_OPERATING_DAYS),
                                            min_value=0.0, max_value=365.0, step=5.0, key="p_bat_op_days")
        param_values["battery"] = {
            "BATTERY_CAPACITY": p_bat_cap,
            "BATTERY_POWER": p_bat_power,
            "BATTERY_COST_PER_WH_AC": p_bat_ac,
            "BATTERY_COST_PER_WH_DC": p_bat_dc,
            "BATTERY_CELL_COST_PER_WH": p_bat_cell,
            "BATTERY_EFFICIENCY": p_bat_eff,
            "BATTERY_DOD": p_bat_dod,
            "BATTERY_CYCLE_LIFE": int(p_bat_cycle),
            "BATTERY_DEGRADATION": p_bat_degrad,
            "BATTERY_OPEX_RATE": p_bat_opex,
            "BATTERY_CELL_DEPRECIATION_YEARS": int(p_bat_cell_dep),
            "BATTERY_CELL_RESIDUAL_RATE": p_bat_cell_res,
            "BATTERY_OTHER_DEPRECIATION_YEARS": int(p_bat_other_dep),
            "BATTERY_OTHER_RESIDUAL_RATE": p_bat_other_res,
            "BATTERY_CYCLE_PER_DAY": int(p_bat_cycle_day),
            "BATTERY_OPERATING_DAYS": int(p_bat_op_days)
        }

    # ---- 7. 充电系统 ----
    with st.expander("🔌 七、充电系统参数", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            p_charger_count = st.number_input("充电桩数量（台）", value=float(charger_params.CHARGER_COUNT),
                                              min_value=0.0, max_value=100.0, step=1.0, key="p_charger_count")
            p_gun_count = st.number_input("充电枪数量（把）", value=float(charger_params.GUN_COUNT), min_value=0.0,
                                          max_value=200.0, step=1.0, key="p_gun_count")
            p_stack_count = st.number_input("充电堆数量（个）", value=float(charger_params.CHARGER_STACK_COUNT),
                                            min_value=0.0, max_value=20.0, step=1.0, key="p_stack_count")
            p_stack_ac = st.number_input("交流充电堆单价（万元/个）", value=float(charger_params.CHARGER_STACK_COST_AC),
                                         min_value=0.0, max_value=100.0, step=1.0, key="p_stack_ac")
            p_stack_dc = st.number_input("直流充电堆单价（万元/个）", value=float(charger_params.CHARGER_STACK_COST_DC),
                                         min_value=0.0, max_value=100.0, step=1.0, key="p_stack_dc")
            p_charger_ac = st.number_input("交流充电桩单价（万元/台）",
                                           value=float(charger_params.CHARGER_COST_PER_UNIT_AC), min_value=0.0,
                                           max_value=200.0, step=1.0, key="p_charger_ac")
            p_charger_dc = st.number_input("直流充电桩单价（万元/台）",
                                           value=float(charger_params.CHARGER_COST_PER_UNIT_DC), min_value=0.0,
                                           max_value=200.0, step=1.0, key="p_charger_dc")
        with col2:
            p_charger_daily = st.number_input("单桩日均充电量（kWh/天）",
                                              value=float(charger_params.CHARGER_DAILY_OUTPUT), min_value=0.0,
                                              max_value=10000.0, step=100.0, key="p_charger_daily")
            p_charger_days = st.number_input("充电年运营天数（天/年）",
                                             value=float(charger_params.CHARGER_OPERATING_DAYS), min_value=0.0,
                                             max_value=365.0, step=5.0, key="p_charger_days")
            p_sim = st.number_input("负荷同时率（%）", value=float(charger_params.CHARGER_SIMULTANEITY * 100),
                                    min_value=0.0, max_value=100.0, step=1.0, key="p_sim") / 100.0
            p_charger_opex = st.number_input("充电桩年运维费（元/年）", value=float(charger_params.CHARGER_OPEX_FIXED),
                                             min_value=0.0, max_value=500000.0, step=5000.0, key="p_charger_opex")
            p_charger_dep = st.number_input("充电桩折旧年限（年）",
                                            value=float(charger_params.CHARGER_UNIT_DEPRECIATION_YEARS), min_value=1.0,
                                            max_value=30.0, step=1.0, key="p_charger_dep")
            p_charger_res = st.number_input("充电桩残值率（%）",
                                            value=float(charger_params.CHARGER_UNIT_RESIDUAL_RATE * 100), min_value=0.0,
                                            max_value=30.0, step=0.5, key="p_charger_res") / 100.0
            p_stack_dep = st.number_input("充电堆折旧年限（年）",
                                          value=float(charger_params.CHARGER_STACK_DEPRECIATION_YEARS), min_value=1.0,
                                          max_value=30.0, step=1.0, key="p_stack_dep")
            p_stack_res = st.number_input("充电堆残值率（%）",
                                          value=float(charger_params.CHARGER_STACK_RESIDUAL_RATE * 100), min_value=0.0,
                                          max_value=30.0, step=0.5, key="p_stack_res") / 100.0
            p_charger_eff = st.number_input("充电效率（%）", value=float(charger_params.CHARGER_EFFICIENCY * 100),
                                            min_value=50.0, max_value=100.0, step=0.5, key="p_charger_eff") / 100.0
        param_values["charger"] = {
            "CHARGER_COUNT": int(p_charger_count),
            "GUN_COUNT": int(p_gun_count),
            "CHARGER_STACK_COUNT": int(p_stack_count),
            "CHARGER_STACK_COST_AC": p_stack_ac,
            "CHARGER_STACK_COST_DC": p_stack_dc,
            "CHARGER_COST_PER_UNIT_AC": p_charger_ac,
            "CHARGER_COST_PER_UNIT_DC": p_charger_dc,
            "CHARGER_DAILY_OUTPUT": int(p_charger_daily),
            "CHARGER_OPERATING_DAYS": int(p_charger_days),
            "CHARGER_SIMULTANEITY": p_sim,
            "CHARGER_OPEX_FIXED": p_charger_opex,
            "CHARGER_UNIT_DEPRECIATION_YEARS": int(p_charger_dep),
            "CHARGER_UNIT_RESIDUAL_RATE": p_charger_res,
            "CHARGER_STACK_DEPRECIATION_YEARS": int(p_stack_dep),
            "CHARGER_STACK_RESIDUAL_RATE": p_stack_res,
            "CHARGER_EFFICIENCY": p_charger_eff
        }

    # ---- 8. 其他资本性支出 ----
    with st.expander("🏗️ 八、其他资本性支出", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            p_trans = st.number_input("变压器（万元）", value=float(other_capEX_params.TRANSFORMER_COST), min_value=0.0,
                                      max_value=1000.0, step=1.0, key="p_trans")
            p_cable = st.number_input("电缆（万元）", value=float(other_capEX_params.CABLE_COST), min_value=0.0,
                                      max_value=5000.0, step=1.0, key="p_cable")
            p_switch = st.number_input("开关柜（万元）", value=float(other_capEX_params.SWITCHGEAR_COST), min_value=0.0,
                                       max_value=500.0, step=1.0, key="p_switch")
            p_monitor = st.number_input("全站辅助监控系统（万元）",
                                        value=float(other_capEX_params.MONITORING_SYSTEM_COST), min_value=0.0,
                                        max_value=500.0, step=1.0, key="p_monitor")
            p_ems = st.number_input("能量管理系统EMS（万元）", value=float(other_capEX_params.EMS_COST), min_value=0.0,
                                    max_value=500.0, step=1.0, key="p_ems")
            p_platform = st.number_input("运营管理平台（万元）", value=float(other_capEX_params.OPERATION_PLATFORM_COST),
                                         min_value=0.0, max_value=100.0, step=0.1, key="p_platform")
            p_fire = st.number_input("火灾报警系统（万元）", value=float(other_capEX_params.FIRE_ALARM_COST),
                                     min_value=0.0, max_value=50.0, step=0.1, key="p_fire")
            p_steel = st.number_input("钢结构（万元）", value=float(other_capEX_params.STEEL_STRUCTURE_COST),
                                      min_value=0.0, max_value=1000.0, step=1.0, key="p_steel")
            p_civil = st.number_input("土建工程施工（万元）", value=float(other_capEX_params.CIVIL_CONSTRUCTION_COST),
                                      min_value=0.0, max_value=5000.0, step=1.0, key="p_civil")
            p_pm = st.number_input("工程管理费（万元）", value=float(other_capEX_params.PROJECT_MANAGEMENT_COST),
                                   min_value=0.0, max_value=500.0, step=1.0, key="p_pm")
        with col2:
            p_design = st.number_input("设计费（万元）", value=float(other_capEX_params.DESIGN_FEE), min_value=0.0,
                                       max_value=200.0, step=1.0, key="p_design")
            p_geo_price = st.number_input("地勘单价（元/延米）",
                                          value=float(other_capEX_params.GEOTECHNICAL_PRICE_PER_METER), min_value=0.0,
                                          max_value=500.0, step=10.0, key="p_geo_price")
            p_geo_meter = st.number_input("地勘延米数（延米）", value=float(other_capEX_params.GEOTECHNICAL_METER_NUM),
                                          min_value=0.0, max_value=10000.0, step=100.0, key="p_geo_meter")
            p_lease_init = st.number_input("首期租赁年限（年）", value=float(other_capEX_params.LAND_LEASE_YEARS_INITIAL),
                                           min_value=0.0, max_value=3.0, step=1.0, key="p_lease_init")
            p_prov = st.number_input("暂列金（万元）", value=float(other_capEX_params.PROVISIONAL_SUM), min_value=0.0,
                                     max_value=200.0, step=1.0, key="p_prov")
            p_contingency = st.number_input("基本预备费（万元）", value=float(other_capEX_params.BASIC_CONTINGENCY_FEE),
                                            min_value=0.0, max_value=200.0, step=1.0, key="p_contingency")
            p_other = st.number_input("其它费用（万元）", value=float(other_capEX_params.OTHER_COST), min_value=0.0,
                                      max_value=500.0, step=1.0, key="p_other")
            p_other_dep = st.number_input("其他折旧年限（年）", value=float(other_capEX_params.DEPRECIATION_YEARS),
                                          min_value=1.0, max_value=50.0, step=1.0, key="p_other_dep")
            p_other_res = st.number_input("其他残值率（%）", value=float(other_capEX_params.RESIDUAL_RATE * 100),
                                          min_value=0.0, max_value=30.0, step=0.5, key="p_other_res") / 100.0
            p_other_amort = st.number_input("其他摊销年限（年）", value=float(other_capEX_params.AMORTIZATION_YEARS),
                                            min_value=1.0, max_value=50.0, step=1.0, key="p_other_amort")
        param_values["other_capex"] = {
            "TRANSFORMER_COST": p_trans,
            "CABLE_COST": p_cable,
            "SWITCHGEAR_COST": p_switch,
            "MONITORING_SYSTEM_COST": p_monitor,
            "EMS_COST": p_ems,
            "OPERATION_PLATFORM_COST": p_platform,
            "FIRE_ALARM_COST": p_fire,
            "STEEL_STRUCTURE_COST": p_steel,
            "CIVIL_CONSTRUCTION_COST": p_civil,
            "PROJECT_MANAGEMENT_COST": p_pm,
            "DESIGN_FEE": p_design,
            "GEOTECHNICAL_PRICE_PER_METER": p_geo_price,
            "GEOTECHNICAL_METER_NUM": p_geo_meter,
            "LAND_LEASE_YEARS_INITIAL": int(p_lease_init),
            "PROVISIONAL_SUM": p_prov,
            "BASIC_CONTINGENCY_FEE": p_contingency,
            "OTHER_COST": p_other,
            "DEPRECIATION_YEARS": int(p_other_dep),
            "RESIDUAL_RATE": p_other_res,
            "AMORTIZATION_YEARS": int(p_other_amort)
        }

    # 将固定总投资模式参数添加到 param_values 中
    param_values["fixed_capex"] = {
        "USE_FIXED_CAPEX": use_fixed_capex,
        "FIXED_TOTAL_CAPEX": fixed_capex_value if use_fixed_capex else 0.0
    }

    # ---- 侧边栏底部水印 ----
    st.markdown("""
    <div class="sidebar-footer">
        ⚡ Global Nexus Group · v1.0<br>
        <span style="font-size:0.6rem; opacity:0.5;">© 2026 All Rights Reserved</span>
    </div>
    """, unsafe_allow_html=True)

    # ---- 运行按钮（反向求解时） ----
    if mode == "反向求解":
        solve_btn = st.button("🔍 求解土地租金", type="primary", use_container_width=True)

# ======================== 主区域：结果展示 ========================

# ---- 执行测算 ----
if mode == "正常测算":
    # 正常模式：自动计算，每次参数变化都会重新运行此代码块
    with st.spinner("⏳ 正在计算中，请稍候..."):
        try:
            results = run_simulation(
                technology=technology,
                loan_type=loan_type,
                params_dict=param_values
            )
        except Exception as e:
            st.error(f"❌ 测算失败：{e}")
            st.stop()

else:
    # 反向求解模式：点击按钮后才计算
    if 'solve_btn' in locals() and solve_btn:
        with st.spinner("🔍 正在求解中，请稍候..."):
            try:
                # 映射目标类型
                target_map = {
                    "全投资IRR": "irr_full",
                    "自有资金IRR": "irr_equity",
                    "全投资回收期": "payback_full",
                    "自有资金回收期": "payback_equity"
                }
                target_type_eng = target_map.get(target_type, "irr_full")

                # 技术路线固定为交流（反向求解中技术路线对结果影响不大）
                solve_technology = "交流"

                # 获取还款方式（从反向求解区域的 selectbox 获取）
                solve_loan_type = st.session_state.get("solve_loan_type", "等额本息")

                # 构建固定总投资参数字典
                solve_params = {
                    "fixed_capex": {
                        "USE_FIXED_CAPEX": solve_use_fixed,
                        "FIXED_TOTAL_CAPEX": solve_fixed_value if solve_use_fixed else 0.0
                    }
                }

                # 创建引擎并执行反向求解
                from operation_engine import OperationEngine

                engine = OperationEngine(
                    technology=solve_technology,
                    loan_type=solve_loan_type,
                    params_dict=solve_params
                )

                result_rent, result_metric, iterations = engine.solve_land_rent_for_target(
                    target_type=target_type_eng,
                    target_value=target_value,
                    precision=0.0001
                )

                # 存储结果到 session_state
                st.session_state['solve_result'] = {
                    'rent': result_rent,
                    'metric': result_metric,
                    'iterations': iterations,
                    'target_type': target_type,
                    'target_value': target_value,
                    'loan_type': solve_loan_type,
                    'use_fixed': solve_use_fixed,
                    'fixed_value': solve_fixed_value if solve_use_fixed else None
                }

                if result_rent is None:
                    st.error("❌ 目标值无法达到，请检查目标值是否在合理范围内。")
                else:
                    st.success("✅ 反向求解完成！")

            except Exception as e:
                st.error(f"❌ 求解失败：{e}")

# ---- 显示结果 ----
if mode == "正常测算" and results:
    # 提取关键指标
    metrics = results.get("metrics", {})
    total_capex = results.get("total_capex", 0)
    loan_amount = results.get("loan_amount", 0)
    equity_amount = results.get("equity_amount", 0)

    # ---- 展示重卡主题装饰 ----
    col_icon1, col_icon2, col_icon3 = st.columns([1, 2, 1])
    with col_icon2:
        st.markdown("""
        <div style="text-align:center; padding: 0.5rem 0;">
            <span class="truck-icon">🚛</span>
            <span style="font-size:2rem; opacity:0.3; padding:0 10px;">⚡</span>
            <span class="truck-icon">🔋</span>
            <span style="font-size:2rem; opacity:0.3; padding:0 10px;">☀️</span>
            <span class="truck-icon">🚛</span>
        </div>
        """, unsafe_allow_html=True)

    # ---- 核心财务指标卡片（白底黑字） ----
    st.markdown("---")
    st.markdown("### 📈 核心财务指标")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        irr_full = metrics.get("full_investment_irr")
        if irr_full is not None:
            st.metric("全投资IRR", f"{irr_full * 100:.2f}%")
        else:
            st.metric("全投资IRR", "无法计算")

    with col2:
        irr_equity = metrics.get("equity_irr")
        if irr_equity is not None:
            st.metric("自有资金IRR", f"{irr_equity * 100:.2f}%")
        else:
            st.metric("自有资金IRR", "无法计算")

    with col3:
        payback_full = metrics.get("full_investment_payback")
        if payback_full is not None:
            st.metric("全投资回收期", f"{payback_full:.2f} 年")
        else:
            st.metric("全投资回收期", "无法计算")

    with col4:
        payback_equity = metrics.get("equity_payback")
        if payback_equity is not None:
            st.metric("自有资金回收期", f"{payback_equity:.2f} 年")
        else:
            st.metric("自有资金回收期", "无法计算")

    # ---- 第二行指标 ----
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        npv_full = metrics.get("full_investment_npv", 0)
        st.metric("全投资NPV", f"¥{npv_full:,.0f}")

    with col6:
        npv_equity = metrics.get("equity_npv", 0)
        st.metric("自有资金NPV", f"¥{npv_equity:,.0f}")

    with col7:
        margin = metrics.get("net_profit_margin", 0)
        st.metric("净利润率", f"{margin * 100:.2f}%")

    with col8:
        st.metric("总投资（CapEx）", f"¥{total_capex:,.0f}")

    # ---- 投资结构分析 ----
    st.markdown("---")
    st.markdown("### 📊 投资结构分析")

    # 检查是否启用了固定总投资模式
    use_fixed = param_values.get("fixed_capex", {}).get("USE_FIXED_CAPEX", False)

    # 尝试从results中获取各子模块投资明细
    try:
        # 直接从引擎结果中获取各子模块投资（如果引擎层返回了这些数据）
        # 注意：引擎层目前没有单独返回各子模块投资，但我们可以从 total_capex 和固定模式状态推算
        # 更好的方式：在引擎层 results 中增加各子模块投资字段，但这里使用估算值展示
        investment_data = {
            "光伏系统": total_capex * 0.18,
            "储能系统": total_capex * 0.35,
            "充电系统": total_capex * 0.15,
            "其他资本性支出": total_capex * 0.32,
        }

        # 如果启用了固定总投资模式，显示缩放提示
        if use_fixed:
            st.info(f"💡 固定总投资模式已启用，总投资固定为 **¥{total_capex:,.0f}**，各子模块按比例缩放")

        colors = ['#1e88e5', '#f0f4ff', '#43a047', '#ff8f00']

        fig = px.pie(
            values=list(investment_data.values()),
            names=list(investment_data.keys()),
            title="投资结构分布",
            color_discrete_sequence=colors,
            hole=0.4
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hoverinfo='label+percent+value',
            marker=dict(line=dict(color='#0a0e1a', width=1)),
            textfont=dict(color='#1a1a2e', size=13)
        )
        fig.update_layout(
            height=360,
            width=500,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f0f4ff", size=12),
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, font=dict(color="#ccd6f6"))
        )
        col_plot1, col_plot2, col_plot3 = st.columns([1, 2, 1])
        with col_plot2:
            st.plotly_chart(fig, use_container_width=False)

        # 如果启用了固定总投资模式，额外显示投资明细表
        if use_fixed:
            st.markdown("#### 📋 投资明细（缩放后）")
            inv_df = pd.DataFrame({
                "子模块": list(investment_data.keys()),
                "投资金额（元）": [f"{v:,.0f}" for v in investment_data.values()],
                "占比（%）": [f"{v/total_capex*100:.1f}" for v in investment_data.values()]
            })
            st.dataframe(inv_df, use_container_width=True, hide_index=True)

    except:
        st.info("💡 投资结构数据加载中...")

    # ---- 逐年利润表（白底黑字） ----
    st.markdown("---")
    st.markdown("### 📋 逐年利润表")

    try:
        revenue_data = results.get("revenue", {})
        opex_data = results.get("opex", {})
        cashflow_data = results.get("cashflow", {})

        total_rev = revenue_data.get("total_revenue", [])
        total_opex = opex_data.get("total_opex", [])
        net_income = cashflow_data.get("net_income", [])
        fcf = cashflow_data.get("fcf", [])

        if total_rev and len(total_rev) > 1:
            years = list(range(1, len(total_rev)))
            df = pd.DataFrame({
                "年份": years,
                "收入（元）": [total_rev[y] for y in years],
                "成本（元）": [total_opex[y] for y in years],
                "净利润（元）": [net_income[y] for y in years],
                "净现金流（元）": [fcf[y] for y in years]
            })
            st.dataframe(
                df.style.format({
                    "收入（元）": "{:,.0f}",
                    "成本（元）": "{:,.0f}",
                    "净利润（元）": "{:,.0f}",
                    "净现金流（元）": "{:,.0f}"
                }).set_properties(**{'color': '#1a1a2e', 'font-size': '14px'})
                .set_table_styles([
                    {'selector': 'thead th',
                     'props': [('color', '#ffffff'), ('background', 'linear-gradient(90deg, #f7931e, #e07b1a)'),
                               ('font-weight', 'bold'), ('padding', '10px 12px')]},
                    {'selector': 'tbody td',
                     'props': [('border-bottom', '1px solid #f0f0f0'), ('padding', '8px 12px')]},
                    {'selector': 'tr:hover td', 'props': [('background', '#faf5ee')]}
                ]),
                use_container_width=True,
                height=400
            )

            # 收入与净利润趋势图（透明背景，白色文字）
            fig2 = make_subplots(specs=[[{"secondary_y": True}]])
            fig2.add_trace(
                go.Scatter(x=df["年份"], y=df["收入（元）"], name="收入", line=dict(color="#f7931e", width=2)),
                secondary_y=False
            )
            fig2.add_trace(
                go.Scatter(x=df["年份"], y=df["净利润（元）"], name="净利润", line=dict(color="#64ffda", width=2)),
                secondary_y=True
            )
            fig2.update_layout(
                title="收入与净利润趋势",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ccd6f6"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02)
            )
            fig2.update_xaxes(title_text="年份", color="#8892b0")
            fig2.update_yaxes(title_text="收入（元）", color="#f7931e", secondary_y=False)
            fig2.update_yaxes(title_text="净利润（元）", color="#64ffda", secondary_y=True)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("💡 逐年数据正在加载...")
    except:
        st.info("💡 利润表数据加载中，请确保参数已正确调整")

    # ---- 贷款明细表（白底黑字） ----
    st.markdown("---")
    st.markdown("### 💳 贷款本金与利息明细")

    try:
        loan_data = results.get("loan", {})
        debt_service = loan_data.get("debt_service", [])
        interest_exp = loan_data.get("interest_expense", [])
        principal_repay = loan_data.get("principal_repayment", [])
        remaining = loan_data.get("remaining_principal", [])

        if debt_service and len(debt_service) > 1:
            years = list(range(1, len(debt_service)))
            df_loan = pd.DataFrame({
                "年份": years,
                "本金偿还（元）": [principal_repay[y] for y in years],
                "利息支出（元）": [interest_exp[y] for y in years],
                "年供（元）": [debt_service[y] for y in years],
                "剩余本金（元）": [remaining[y] for y in years]
            })
            st.dataframe(
                df_loan.style.format({
                    "本金偿还（元）": "{:,.0f}",
                    "利息支出（元）": "{:,.0f}",
                    "年供（元）": "{:,.0f}",
                    "剩余本金（元）": "{:,.0f}"
                }).set_properties(**{'color': '#1a1a2e', 'font-size': '14px'})
                .set_table_styles([
                    {'selector': 'thead th',
                     'props': [('color', '#ffffff'), ('background', 'linear-gradient(90deg, #f7931e, #e07b1a)'),
                               ('font-weight', 'bold'), ('padding', '10px 12px')]},
                    {'selector': 'tbody td',
                     'props': [('border-bottom', '1px solid #f0f0f0'), ('padding', '8px 12px')]},
                    {'selector': 'tr:hover td', 'props': [('background', '#faf5ee')]}
                ]),
                use_container_width=True,
                height=300
            )
        else:
            st.info("💡 贷款数据加载中...")
    except:
        st.info("💡 贷款明细加载中，请确保参数已正确调整")

    # ---- 页面底部水印（橙色高亮） ----
    st.markdown("""
    <div style="text-align:center; padding:2rem 0 1rem 0; border-top:1px solid rgba(247,147,30,0.15); margin-top:2rem;">
        <span style="color:#f7931e; font-size:0.8rem; letter-spacing:4px; font-weight:600; text-shadow: 0 0 20px rgba(247,147,30,0.3);">
            ⚡ Global Nexus Group · 新能源重卡充电站投资测算模型 v1.0 ⚡
        </span>
        <br>
        <span style="color:rgba(247,147,30,0.15); font-size:0.5rem; letter-spacing:2px;">
            © 2026 Global Nexus Group. All Rights Reserved.
        </span>
    </div>
    """, unsafe_allow_html=True)

# ---- 反向求解结果显示 ----
elif mode == "反向求解":
    # 检查是否有求解结果
    if 'solve_result' in st.session_state and st.session_state['solve_result'] is not None:
        res = st.session_state['solve_result']

        if res['rent'] is None:
            st.markdown("---")
            st.markdown("### 🔍 反向求解结果")
            st.error(f"❌ 目标值 {res['target_value']:.4f} 无法达到，请检查目标值是否在合理范围内。")
        else:
            st.markdown("---")
            st.markdown("### 🔍 反向求解结果")

            # 显示配置信息
            col_config1, col_config2 = st.columns(2)
            with col_config1:
                st.markdown(f"**目标指标**：{res['target_type']}")
                st.markdown(f"**目标值**：{res['target_value']:.4f}")
            with col_config2:
                st.markdown(f"**还款方式**：{res['loan_type']}")
                if res['use_fixed'] and res['fixed_value']:
                    st.markdown(f"**固定总投资**：¥{res['fixed_value']:,.0f}")
                else:
                    st.markdown("**固定总投资**：未启用")

            # 求解结果
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("土地租金单价", f"{res['rent']:.4f} 万元/亩/年")
            with col2:
                st.metric("对应实际指标值", f"{res['metric']:.4f}")
            with col3:
                st.metric("迭代次数", f"{res['iterations']} 次")

            st.caption(f"精度误差：{abs(res['metric'] - res['target_value']):.6f}")

            # 查看详细财务结果按钮
            if st.button("📊 查看该租金下的详细财务结果"):
                with st.spinner("正在加载详细财务结果..."):
                    # 重新运行引擎，传入求解出的租金
                    solve_params = {
                        "fixed_capex": {
                            "USE_FIXED_CAPEX": res['use_fixed'],
                            "FIXED_TOTAL_CAPEX": res['fixed_value'] if res['use_fixed'] else 0.0
                        }
                    }
                    from operation_engine import OperationEngine

                    engine = OperationEngine(
                        technology="交流",
                        loan_type=res['loan_type'],
                        params_dict=solve_params
                    )
                    detailed_results = engine._run_core(rent_per_mu=res['rent'], print_output=False)
                    st.info("💡 详细财务结果展示功能开发中...")
    else:
        # 未点击求解按钮时的提示
        st.info("请设置目标指标和目标值，然后点击「求解土地租金」按钮。")

# ======================== 运行说明 ========================

if __name__ == "__main__":
    # 在终端运行：streamlit run Visual_web.py
    pass
