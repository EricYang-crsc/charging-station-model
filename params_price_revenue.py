# ==================== params_price_revenue.py ====================
# 电价与收入参数（Revenue Parameters）


# ---------- 分时电价（元/kWh） ----------
PRICE_PEAK = 1.01               # 尖峰电价
PRICE_HIGH = 0.82               # 高峰电价
PRICE_FLAT = 0.63               # 平段电价
PRICE_VALLEY = 0.42             # 低谷电价


# ---------- 收入相关 ----------
SERVICE_FEE = 0.40              # 充电服务费（元/kWh），固定值
SELL_PRICE = 0.0                # 余电上网电价（元/kWh），0表示不允许上网

# ---------- 设备销售收入 ----------
# 计算公式：设备销售收入 = 所有设备成本之和 × 该比例
# 设备成本包含：光伏系统、储能系统、充电系统、钢结构、变压器、电缆、开关柜、
#              监控系统、EMS、运营平台、火灾报警系统
# 不含：土建工程、工程管理费、设计费、地勘费、暂列金、基本预备费、其它费用
EQUIPMENT_SALES_REVENUE_RATIO = 0.25  # 设备销售收入比例（25%）

# ---------- 其它收入 ----------
# 预留入口，用于填写项目测算中未单独列项的其它收入
# 例如：碳交易收入、政府补贴、广告收入等
# 按年固定金额计算（元/年），如需按比例计算可自行修改
OTHER_INCOME = 0.0              # 其它收入（元/年），用户根据需要填写


# ---------- 分时时段划分（小时/天） ----------
# 用于电网购电成本计算的时段权重
PEAK_HOURS = 2                  # 尖峰时段（20:00-22:00），2小时/天
HIGH_HOURS = 5                  # 高峰时段（17:00-20:00, 22:00-23:59），5小时/天
FLAT_HOURS = 8                  # 平段时段（06:00-14:00），8小时/天
VALLEY_HOURS = 9                # 低谷时段（00:00-06:00, 14:00-17:00），9小时/天

# 分时时段详细时间（用于参考，暂未被代码引用）
PEAK_TIME = "20:00-22:00"
HIGH_TIME = "17:00-20:00, 22:00-23:59"
FLAT_TIME = "06:00-14:00"
VALLEY_TIME = "00:00-06:00, 14:00-17:00"


# ---------- 充电时段分配（每桩每天） ----------
# 说明：
#   1. 定义每个充电桩每天在各个时段的充电时间分配
#   2. 时段名称必须与上面的电价变量名对应（VALLEY/FLAT/HIGH/PEAK）
#   3. 修改此分配即可调整充电时段策略，无需改动引擎层代码
#   4. 总充电小时数 = 各时段小时数之和 = 6.25 小时/桩/天
CHARGING_SCHEDULE = [
    {"时段": "VALLEY", "小时": 2.0, "电价": PRICE_VALLEY},   # 0:00-06:00 谷段
    {"时段": "FLAT", "小时": 2.0, "电价": PRICE_FLAT},       # 12:00-14:00 平段
    {"时段": "VALLEY", "小时": 2.0, "电价": PRICE_VALLEY},   # 14:00-17:00 谷段
    {"时段": "HIGH", "小时": 0.25, "电价": PRICE_HIGH},      # 22:00-23:59 高峰段
]

# 每日总充电小时数（自动计算，用于校验和加权平均）
TOTAL_CHARGING_HOURS_PER_PILE = sum([s["小时"] for s in CHARGING_SCHEDULE])  # = 6.25 小时/桩/天

# 单桩平均充电功率（kW）
# 配合总充电小时数，计算每桩日均充电量：400kW × 6.25h = 2,500 kWh/天
CHARGER_AVG_POWER = 400          # kW

# 每桩日均充电量（自动校验）
# 2,500 kWh/天 × 16桩 = 40,000 kWh/天
DAILY_CHARGE_PER_PILE = CHARGER_AVG_POWER * TOTAL_CHARGING_HOURS_PER_PILE  # 2,500 kWh/天


# ---------- 计算加权平均电价（用于收入计算） ----------
# 根据充电时段分配，计算每度电的加权平均电价
# 公式：Σ(各时段电价 × 该时段小时数) / 总小时数
def calculate_weighted_avg_price():
    """
    根据 CHARGING_SCHEDULE 计算加权平均电价

    :return: float，加权平均电价（元/kWh）
    """
    total_hours = TOTAL_CHARGING_HOURS_PER_PILE
    weighted_sum = sum([s["电价"] * s["小时"] for s in CHARGING_SCHEDULE])
    return weighted_sum / total_hours


# 加权平均电价（模块加载时自动计算）
WEIGHTED_AVG_PRICE = calculate_weighted_avg_price()

# 加权平均电价计算过程（参考值）：
# (0.42 × 2.0 + 0.63 × 2.0 + 0.42 × 2.0 + 0.82 × 0.25) / 6.25
# = (0.84 + 1.26 + 0.84 + 0.205) / 6.25
# = 3.145 / 6.25
# = 0.5032 元/kWh


# ---------- 调试输出（仅在直接运行本文件时触发） ----------
if __name__ == "__main__":
    print("=" * 55)
    print("【电价与充电时段参数摘要】")
    print("=" * 55)
    print(f"谷段电价：          {PRICE_VALLEY:.2f} 元/kWh")
    print(f"平段电价：          {PRICE_FLAT:.2f} 元/kWh")
    print(f"高峰电价：          {PRICE_HIGH:.2f} 元/kWh")
    print(f"尖峰电价：          {PRICE_PEAK:.2f} 元/kWh")
    print(f"充电服务费：        {SERVICE_FEE:.2f} 元/kWh")
    print("-" * 55)
    print("【设备销售收入】")
    print(f"  设备销售收入比例：  {EQUIPMENT_SALES_REVENUE_RATIO * 100:.0f}%")
    print("  计算公式：设备销售收入 = 设备成本总额 × 该比例")
    print("-" * 55)
    print(f"【其它收入】")
    print(f"  其它收入（年）：    {OTHER_INCOME:>12,.0f} 元/年")
    print("  说明：预留入口，用于碳交易、补贴、广告等未单独列项的收入")
    print("-" * 55)
    print("【充电时段分配】")
    for slot in CHARGING_SCHEDULE:
        print(f"  {slot['时段']}段：{slot['小时']:.2f} 小时/天，电价 {slot['电价']:.2f} 元/kWh")
    print("-" * 55)
    print(f"每日总充电小时数：  {TOTAL_CHARGING_HOURS_PER_PILE:.2f} 小时/桩/天")
    print(f"单桩平均功率：      {CHARGER_AVG_POWER} kW")
    print(f"每桩日均充电量：    {DAILY_CHARGE_PER_PILE:.0f} kWh/天")
    print(f"全站日均充电量：    {DAILY_CHARGE_PER_PILE * 16:.0f} kWh/天")
    print("-" * 55)
    print(f"加权平均电价：      {WEIGHTED_AVG_PRICE:.4f} 元/kWh")
    print(f"加权平均电价+服务费：{WEIGHTED_AVG_PRICE + SERVICE_FEE:.4f} 元/kWh")
    print("=" * 55)