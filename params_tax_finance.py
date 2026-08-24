# ==================== params_tax_finance.py ====================
# 税务与财务参数（Tax & Finance Parameters）

# ---------- 增值税税率 ----------
VAT_EQUIPMENT = 0.13            # 设备费增值税（13%）
VAT_CONSTRUCTION = 0.09         # 建安费增值税（9%）
VAT_OTHER = 0.06                # 其他费用增值税（6%）
VAT_ELECTRICITY = 0.13          # 电费收入增值税（13%）
VAT_SERVICE = 0.10              # 增值服务综合增值税（10%）
VAT_INTEREST = 0.06             # 利息税（6%）
VAT_MATERIAL = 0.13             # 材料费税率（13%）
VAT_MAINTENANCE = 0.06          # 维修费税率（6%）

# ---------- 所得税与附加 ----------
INCOME_TAX_RATE = 0.25          # 所得税（25%）
SURCHARGE_RATE = 0.10           # 税金及附加（10%）

# ---------- 折旧与摊销 ----------
DEPRECIATION_YEARS = 20         # 除电池外设备折旧年限（年）
RESIDUAL_RATE_DEP = 0.08        # 残值率（8%）
AMORTIZATION_YEARS = 20         # 无形资产及其他摊销年限（年）

# ---------- 贷款与资本金 ----------
EQUITY_RATIO = 0.20             # 资本金比例（20%）
LOAN_RATE = 0.0285              # 长期贷款利息（2.85%）
LOAN_PERIOD = 15                # 贷款年限（年）
LOAN_TYPE = "等额本息"           # 贷款方式："等额本息" 或 "等额本金"

# ---------- 还款频率 ----------
# 说明：贷款偿还周期，影响利息计算和每期还款额
#       可选值："年"、"半年"、"月"
#       - "年"：每年偿还一次，按年利率计息
#       - "半年"：每半年偿还一次，按半年利率计息（年利率/2）
#       - "月"：每月偿还一次，按月利率计息（年利率/12）
REPAYMENT_FREQUENCY = "半年"     # 还款频率："年" / "半年" / "月"

# ---------- 换电池贷款 ----------
BATTERY_LOAN_PERIOD = 5         # 换电池借款年限（年）
BATTERY_LOAN_RATE = 0.0285      # 换电池贷款利率（可单独设置，未给则同长期贷款）

# ---------- 税收优惠 ----------
TAX_HOLIDAY = False             # 三免三减半（True/False）
TAX_REBATE = False              # 即征即退（True/False）

# ---------- 其他 ----------
INFLATION_RATE = 0.00           # 通货膨胀率（0%）
PRINCIPAL_GRACE = 0             # 本金宽限期（年）
SUBSIDY_DELAY = 0               # 补贴延迟（年）