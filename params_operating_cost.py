# ==================== params_operating_cost.py ====================
# 运营成本参数（OPEX Parameters）

# ---------- 土地租金 ----------
LAND_AREA = 30                  # 全部土地面积（亩），用于计算土地租金
LAND_RENT_PER_MU = 1.6          # 租金价格（万元/亩/年）
# 租赁年限 = DEPRECIATION_YEARS（从 financial_params 中读取，20年）

# ---------- 增值服务用地（在全部用地中划分） ----------
# 说明：全部用地面积 = 实际用地面积 + 增值服务用地面积
#       实际用地面积用于重卡充电主营业务（充电桩、设备、道路等）
#       增值服务用地面积用于司机之家、夜市小摊、休息区等增值服务
#       土地租金按全部用地面积计算（已在 LAND_AREA 中体现）
#       增值服务用地面积仅用于计算增值服务收入，不参与租金计算
LAND_AREA_VALUE_ADDED = 5       # 增值服务用地面积（亩），用户根据实际情况填写
LAND_REVENUE_PER_MU = 20000     # 增值服务用地收入（元/亩/年）

# 实际用地面积（亩）= LAND_AREA - LAND_AREA_VALUE_ADDED（在引擎层动态计算）

# ---------- 人员支出 ----------
STAFF_COUNT = 2                 # 人数（人）
ANNUAL_SALARY = 10              # 年工资（万元/人/年），含福利费
STAFF_COST_FIRST_YEAR = 20      # 首年人员支出（万元/年）

# ---------- 保险费 ----------
# 费率 = 0.1%，基数为电气设备总价值
# 电气设备包括：光伏系统、储能系统、充电桩、电缆、变压器、开关柜
# 保险基数在 run_model.py 中汇总计算
INSURANCE_RATE = 0.001          # 保险费率（0.1%）

# ---------- 容量费 ----------
CAPACITY_FEE = 0                # 容量费（万元/年），暂列为0

# ---------- 换算为元（用于统一单位） ----------
LAND_RENT_PER_MU_YUAN = LAND_RENT_PER_MU * 10000      # 元/亩/年
STAFF_COST_FIRST_YEAR_YUAN = STAFF_COST_FIRST_YEAR * 10000  # 元/年
CAPACITY_FEE_YUAN = CAPACITY_FEE * 10000              # 元/年