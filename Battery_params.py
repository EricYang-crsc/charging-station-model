# ==================== battery_params.py ====================
# 储能系统参数

# ---------- 容量与功率 ----------
BATTERY_CAPACITY = 20000                # 储能容量（kWh），20MWh = 20000kWh
BATTERY_POWER = 5000                    # 储能功率（kW），5MW = 5000kW

# ---------- 技术路线选择 ----------
# 说明：电站建设前需选择技术路线，本模型支持两种：
#   1. 交流储能系统：0.6185 元/Wh
#   2. 直流储能系统：0.535 元/Wh
# 引擎层需提醒用户选择，两种系统电芯单价相同
BATTERY_TECHNOLOGY = "交流"              # 可选："交流" 或 "直流"

# ---------- 储能系统单价（元/Wh） ----------
BATTERY_COST_PER_WH_AC = 0.6185         # 交流储能系统单价（元/Wh）
BATTERY_COST_PER_WH_DC = 0.535          # 直流储能系统单价（元/Wh）

# ---------- 电芯单价 ----------
BATTERY_CELL_COST_PER_WH = 0.30         # 电芯更换成本（元/Wh），两种系统通用

# ---------- 设备性能 ----------
BATTERY_EFFICIENCY = 0.92               # 充放电综合效率（92%）
BATTERY_DOD = 0.90                      # 放电深度（90%）
BATTERY_CYCLE_LIFE = 6000               # 循环寿命（次），在DOD条件下
BATTERY_DEGRADATION = 0.02              # 年衰减率（2%/年）
BATTERY_LIFETIME = 8                    # 使用寿命（年）

# ---------- 投资与成本 ----------
BATTERY_OPEX_RATE = 0.02                # 年运维费率（2%），按初始投资计算

# ---------- 折旧与残值 ----------
# 电芯：折旧8年，残值率8%
BATTERY_CELL_DEPRECIATION_YEARS = 8
BATTERY_CELL_RESIDUAL_RATE = 0.08
# 除电芯外设备：折旧20年，残值率5%
BATTERY_OTHER_DEPRECIATION_YEARS = 20
BATTERY_OTHER_RESIDUAL_RATE = 0.05

# ---------- 运行策略 ----------
BATTERY_CYCLE_PER_DAY = 2               # 日充放电次数（次/天）
BATTERY_OPERATING_DAYS = 350            # 年运行天数（天/年）