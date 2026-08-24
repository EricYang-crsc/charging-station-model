# ==================== charger_params.py ====================
# 充电系统参数

# ---------- 充电桩规模 ----------
CHARGER_COUNT = 16                  # 充电桩数量（台），单桩单枪，共16枪
GUN_COUNT = 16                      # 充电枪数量（把）

# ---------- 充电堆 ----------
CHARGER_STACK_COUNT = 2             # 充电堆数量（个）

# 充电堆单价（按技术路线区分）
CHARGER_STACK_COST_AC = 32          # 交流充电堆单价（万元/个）
CHARGER_STACK_COST_DC = 32          # 直流充电堆单价（万元/个）

# ---------- 充电桩单价（按技术路线区分） ----------
CHARGER_COST_PER_UNIT_AC = 1.72       # 交流充电桩单价（万元/台）
CHARGER_COST_PER_UNIT_DC = 1.72       # 直流充电桩单价（万元/台）

# ---------- 运营负荷 ----------
CHARGER_DAILY_OUTPUT = 2500         # 单桩日均充电量（kWh/天）
CHARGER_OPERATING_DAYS = 350        # 年运营天数（天/年）
CHARGER_SIMULTANEITY = 0.7          # 负荷同时率（70%）

# ---------- 投资与成本 ----------
CHARGER_OPEX_FIXED = 50000          # 年运维费（元/年），固定5万元/年

# ---------- 折旧与残值 ----------
# 充电桩：初始折旧8年，残值率8%，第8年末更换后折旧到项目最后一年
CHARGER_UNIT_LIFETIME = 8           # 充电桩设计寿命（年）
CHARGER_UNIT_DEPRECIATION_YEARS = 8 # 充电桩初始折旧年限（年）
CHARGER_UNIT_RESIDUAL_RATE = 0.08   # 充电桩残值率（8%）

# 充电堆：折旧8年，残值率8%，不更换
CHARGER_STACK_LIFETIME = 8          # 充电堆设计寿命（年）
CHARGER_STACK_DEPRECIATION_YEARS = 8 # 充电堆折旧年限（年）
CHARGER_STACK_RESIDUAL_RATE = 0.08  # 充电堆残值率（8%）

# ---------- 效率 ----------
CHARGER_EFFICIENCY = 0.95           # 充电效率（95%）