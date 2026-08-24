# ==================== other_capEX_systems.py ====================
# 其他资本性支出运算逻辑

from other_capEX_params import (
    # 电气设备
    TRANSFORMER_COST,
    CABLE_COST,
    SWITCHGEAR_COST,
    MONITORING_SYSTEM_COST,
    EMS_COST,
    OPERATION_PLATFORM_COST,
    FIRE_ALARM_COST,
    # 工程建设
    STEEL_STRUCTURE_COST,
    CIVIL_CONSTRUCTION_COST,
    PROJECT_MANAGEMENT_COST,
    # 设计咨询
    DESIGN_FEE,
    GEOTECHNICAL_PRICE_PER_METER,
    GEOTECHNICAL_METER_NUM,
    # 监理审图
    SUPERVISION_FEE,
    PLAN_REVIEW_FEE,
    # 暂列金
    PROVISIONAL_SUM,
    # 土地首期租赁
    LAND_LEASE_YEARS_INITIAL,
    # 折旧与摊销
    DEPRECIATION_YEARS,
    RESIDUAL_RATE,
    AMORTIZATION_YEARS,
    # 基本预备费
    BASIC_CONTINGENCY_FEE,
    # 其它费用
    OTHER_COST
)
from params_jichucanshu import PROJECT_YEARS
from params_operating_cost import LAND_AREA, LAND_RENT_PER_MU


class OtherCapEXSystem:
    """
    其他资本性支出类
    负责计算除光伏、储能、充电桩以外的所有投资：
    - 电气设备（变压器、电缆、开关柜、监控、EMS、平台、火灾报警）
    - 工程建设（钢结构、土建施工、工程管理费）
    - 设计咨询（设计费、地勘费）
    - 监理审图（监理费、审图费）
    - 暂列金
    - 土地首期租赁费用（期初一次性支付，计入固定资产，参与折旧）
    - 其它费用（预留入口，计入固定资产，参与折旧）

    输出：
    - 各分类投资额
    - 总投资（CapEx）
    - 每年折旧额（固定资产，20年，残值率5%）
    - 每年摊销额（无形资产及其他，20年）
    - 残值
    """

    def __init__(self):
        """初始化其他资本性支出，所有参数从对应文件读取"""
        # ---------- 电气设备 ----------
        self.transformer = TRANSFORMER_COST
        self.cable = CABLE_COST
        self.switchgear = SWITCHGEAR_COST
        self.monitoring = MONITORING_SYSTEM_COST
        self.ems = EMS_COST
        self.platform = OPERATION_PLATFORM_COST
        self.fire_alarm = FIRE_ALARM_COST

        # ---------- 工程建设 ----------
        self.steel = STEEL_STRUCTURE_COST
        self.civil = CIVIL_CONSTRUCTION_COST
        self.project_management = PROJECT_MANAGEMENT_COST

        # ---------- 设计咨询 ----------
        self.design = DESIGN_FEE
        self.geotech_price_per_meter = GEOTECHNICAL_PRICE_PER_METER    # 地勘单价：元/延米
        self.geotech_meter_num = GEOTECHNICAL_METER_NUM                # 地勘总延米数

        # ---------- 监理审图 ----------
        self.supervision = SUPERVISION_FEE
        self.plan_review = PLAN_REVIEW_FEE

        # ---------- 暂列金 ----------
        self.provisional = PROVISIONAL_SUM

        # ---------- 土地首期租赁 ----------
        # 首期租赁年限（用户自定义，1~3年）
        self.land_lease_years_initial = LAND_LEASE_YEARS_INITIAL
        # 首期租赁费用由引擎层动态计算，不在此处硬编码
        # 计算公式：首期租赁费（万元）= LAND_AREA × LAND_RENT_PER_MU × LAND_LEASE_YEARS_INITIAL
        # 首期租赁费计入固定资产，按20年折旧，残值率5%

        # ---------- 其它费用（预留入口） ----------
        self.other_cost = OTHER_COST

        # ---------- 基本预备费 ----------
        self.contingency = BASIC_CONTINGENCY_FEE

        # ---------- 折旧与摊销 ----------
        self.dep_years = DEPRECIATION_YEARS
        self.residual_rate = RESIDUAL_RATE
        self.amort_years = AMORTIZATION_YEARS

        # ---------- 土地参数（从运营成本参数读取） ----------
        self.land_area = LAND_AREA
        self.land_rent_per_mu = LAND_RENT_PER_MU

        self.years = PROJECT_YEARS

    # ======================== 分类投资汇总 ========================

    def get_electrical_cost(self):
        """
        计算电气设备类投资总额

        计算公式：
        电气设备投资 = 变压器 + 电缆 + 开关柜 + 监控系统 + EMS + 运营平台 + 火灾报警

        :return: float，电气设备投资（万元）
        """
        total = (
            self.transformer +
            self.cable +
            self.switchgear +
            self.monitoring +
            self.ems +
            self.platform +
            self.fire_alarm
        )
        return round(total, 2)

    def get_construction_cost(self):
        """
        计算工程建设类投资总额

        计算公式：
        工程建设投资 = 钢结构 + 土建施工 + 工程管理费

        :return: float，工程建设投资（万元）
        """
        total = (
            self.steel +
            self.civil +
            self.project_management
        )
        return round(total, 2)

    def get_geotech_cost(self):
        """
        计算地勘费（万元）

        计算公式：
        地勘费（万元）= 地勘单价（元/延米）× 延米数 / 10000

        :return: float，地勘费（万元）
        """
        cost = self.geotech_price_per_meter * self.geotech_meter_num / 10000
        return round(cost, 2)

    def get_design_consulting_cost(self):
        """
        计算设计咨询类投资总额

        计算公式：
        设计咨询投资 = 设计费 + 地勘费

        :return: float，设计咨询投资（万元）
        """
        total = (
            self.design +
            self.get_geotech_cost()
        )
        return round(total, 2)

    def get_supervision_cost(self):
        """
        计算监理审图类投资总额

        计算公式：
        监理审图投资 = 监理费 + 审图费

        :return: float，监理审图投资（万元）
        """
        total = (
            self.supervision +
            self.plan_review
        )
        return round(total, 2)

    def get_land_rent_initial_cost(self):
        """
        计算首期一次性支付的土地租金（万元）

        计算公式：
        首期土地租金（万元）= 土地面积（亩）× 租金单价（万元/亩/年）× 首期租赁年限（年）

        :return: float，首期土地租金（万元）
        """
        cost = self.land_area * self.land_rent_per_mu * self.land_lease_years_initial
        return round(cost, 2)

    def get_other_cost_total(self):
        """
        计算其它费用总额（万元）

        说明：此处仅返回用户在参数文件中填写的 OTHER_COST
        如需追加其它临时费用，可直接在参数文件中修改

        :return: float，其它费用（万元）
        """
        return round(self.other_cost, 2)

    def get_provisional_sum(self):
        """
        计算暂列金（万元）

        :return: float，暂列金（万元）
        """
        return round(self.provisional, 2)

    # ======================== 总投资 ========================

    def get_capex(self):
        """
        计算其他资本性支出总投资（CapEx）

        计算公式：
        总投资 = 电气设备 + 工程建设 + 设计咨询 + 监理审图 + 暂列金 + 首期土地租金 + 其它费用 + 基本预备费

        :return: float，总投资（万元）
        """
        total = (
            self.get_electrical_cost() +
            self.get_construction_cost() +
            self.get_design_consulting_cost() +
            self.get_supervision_cost() +
            self.get_provisional_sum() +
            self.get_land_rent_initial_cost() +
            self.get_other_cost_total() +
            self.contingency
        )
        return round(total, 2)

    def get_capex_yuan(self):
        """
        计算其他资本性支出总投资（元）

        :return: float，总投资（元）
        """
        return self.get_capex() * 10000

    # ======================== 固定资产折旧 ========================

    def get_depreciable_assets(self):
        """
        计算需要计提折旧的固定资产总额

        属于固定资产的科目：
        - 电气设备类：变压器、电缆、开关柜、监控系统、EMS、运营平台、火灾报警
        - 工程建设类：钢结构、土建施工、工程管理费
        - 首期土地租金（期初一次性支付的租金，计入固定资产）
        - 其它费用（预留入口，计入固定资产）

        :return: float，固定资产总额（万元）
        """
        total = (
            self.get_electrical_cost() +
            self.get_construction_cost() +
            self.get_land_rent_initial_cost() +
            self.get_other_cost_total()
        )
        return round(total, 2)

    def get_depreciation_schedule(self):
        """
        计算每年折旧额（直线折旧法，20年，残值率5%）

        计算公式：
        年折旧额（万元）= 固定资产总额 × (1 - 残值率) / 折旧年限

        逻辑说明：
        - 第0年（建设期）：不计提折旧
        - 第1~20年：每年计提折旧

        :return: list，每年折旧额（万元），长度=项目周期+1
        """
        depreciable_base = self.get_depreciable_assets() * (1 - self.residual_rate)
        annual_depreciation = depreciable_base / self.dep_years

        dep_schedule = []
        for year in range(self.years + 1):
            if year == 0:
                dep_schedule.append(0)
            else:
                dep_schedule.append(round(annual_depreciation, 2))

        return dep_schedule

    # ======================== 无形资产摊销 ========================

    def get_amortizable_assets(self):
        """
        计算需要摊销的资产总额

        属于摊销的科目：
        - 设计咨询类：设计费、地勘费
        - 监理审图类：监理费、审图费
        - 暂列金

        注意：
        - 基本预备费不属于摊销，已在总投资中体现
        - 首期土地租金属于固定资产（计提折旧），不属于摊销资产

        :return: float，摊销资产总额（万元）
        """
        total = (
            self.get_design_consulting_cost() +
            self.get_supervision_cost() +
            self.get_provisional_sum()
        )
        return round(total, 2)

    def get_amortization_schedule(self):
        """
        计算每年摊销额（直线法，20年）

        计算公式：
        年摊销额（万元）= 摊销资产总额 / 摊销年限

        逻辑说明：
        - 第0年（建设期）：不计提摊销
        - 第1~20年：每年计提摊销

        :return: list，每年摊销额（万元），长度=项目周期+1
        """
        amortizable_base = self.get_amortizable_assets()
        annual_amortization = amortizable_base / self.amort_years

        amort_schedule = []
        for year in range(self.years + 1):
            if year == 0:
                amort_schedule.append(0)
            else:
                amort_schedule.append(round(annual_amortization, 2))

        return amort_schedule

    # ======================== 残值 ========================

    def get_residual_value(self):
        """
        计算固定资产在项目期末的残值

        计算公式：
        残值（万元）= 固定资产总额 × 残值率

        :return: float，残值（万元）
        """
        residual = self.get_depreciable_assets() * self.residual_rate
        return round(residual, 2)

    def get_residual_value_yuan(self):
        """
        计算固定资产在项目期末的残值（元）

        :return: float，残值（元）
        """
        return self.get_residual_value() * 10000

    # ======================== 摘要 ========================

    def get_summary(self):
        """
        输出其他资本性支出摘要信息
        """
        print("=" * 55)
        print("【其他资本性支出摘要】")
        print("=" * 55)

        print("\n一、电气设备类（合计：%.2f 万元）" % self.get_electrical_cost())
        print(f"  变压器：              {self.transformer:>12.2f} 万元")
        print(f"  电缆：                {self.cable:>12.2f} 万元")
        print(f"  开关柜：              {self.switchgear:>12.2f} 万元")
        print(f"  全站辅助监控系统：    {self.monitoring:>12.2f} 万元")
        print(f"  能量管理系统（EMS）： {self.ems:>12.2f} 万元")
        print(f"  运营管理平台：        {self.platform:>12.2f} 万元")
        print(f"  全站火灾报警系统：    {self.fire_alarm:>12.2f} 万元")

        print("\n二、工程建设类（合计：%.2f 万元）" % self.get_construction_cost())
        print(f"  钢结构：              {self.steel:>12.2f} 万元")
        print(f"  土建工程施工：        {self.civil:>12.2f} 万元")
        print(f"  工程管理费：          {self.project_management:>12.2f} 万元")

        print("\n三、设计&地勘咨询费（合计：%.2f 万元）" % self.get_design_consulting_cost())
        print(f"  设计费：              {self.design:>12.2f} 万元")
        print(f"  地勘单价：            {self.geotech_price_per_meter:>12} 元/延米")
        print(f"  地勘总延米数：        {self.geotech_meter_num:>12} 延米")
        print(f"  地勘费：              {self.get_geotech_cost():>12.2f} 万元")
        print(f"  （计算公式：{self.geotech_price_per_meter} × {self.geotech_meter_num} / 10000 = {self.get_geotech_cost():.2f} 万元）")

        print("\n四、监理与审图咨询费（合计：%.2f 万元）" % self.get_supervision_cost())
        print(f"  监理费：              {self.supervision:>12.2f} 万元")
        print(f"  审图费：              {self.plan_review:>12.2f} 万元")

        print("\n五、暂列金：")
        print(f"  暂列金：              {self.get_provisional_sum():>12.2f} 万元")

        print("\n六、土地首期租赁费用：")
        print(f"  首期租赁年限：        {self.land_lease_years_initial:>12} 年")
        print(f"  首期租赁面积：        {self.land_area:>12} 亩")
        print(f"  租金单价：            {self.land_rent_per_mu:>12.2f} 万元/亩/年")
        print(f"  首期租赁费用：        {self.get_land_rent_initial_cost():>12.2f} 万元")
        print(f"  （计算公式：{self.land_area} × {self.land_rent_per_mu} × {self.land_lease_years_initial} = {self.get_land_rent_initial_cost():.2f} 万元）")

        print("\n七、基本预备费：")
        print(f"  基本预备费：          {self.contingency:>12.2f} 万元")

        print("\n八、其它费用（预留）：")
        print(f"  其它费用：            {self.get_other_cost_total():>12.2f} 万元")

        print("-" * 55)
        print(f"【总投资（CapEx）】    {self.get_capex():>12.2f} 万元")
        print(f"                     {self.get_capex_yuan():>12,.0f} 元")

        print("\n【折旧与摊销】")
        print(f"  折旧年限：            {self.dep_years:>12} 年")
        print(f"  摊销年限：            {self.amort_years:>12} 年")
        print(f"  残值率：              {self.residual_rate * 100:>11.2f} %")
        print(f"  固定资产总额：        {self.get_depreciable_assets():>12.2f} 万元")
        print(f"  摊销资产总额：        {self.get_amortizable_assets():>12.2f} 万元")
        print(f"  年折旧额：            {self.get_depreciation_schedule()[1]:>12.2f} 万元/年")
        print(f"  年摊销额：            {self.get_amortization_schedule()[1]:>12.2f} 万元/年")
        print(f"  残值（第20年末）：    {self.get_residual_value():>12.2f} 万元")
        print("=" * 55)


# ---------- 测试代码 ----------
if __name__ == "__main__":
    # 实例化
    other = OtherCapEXSystem()

    # 打印摘要
    other.get_summary()

    # 打印逐年折旧
    dep_schedule = other.get_depreciation_schedule()
    amort_schedule = other.get_amortization_schedule()

    print("\n【逐年折旧与摊销】")
    print("年份\t折旧（万元）\t摊销（万元）\t合计（万元）")
    for year in range(1, 21):
        total = dep_schedule[year] + amort_schedule[year]
        print(f"  {year:>2}年\t{dep_schedule[year]:>11.2f}\t{amort_schedule[year]:>11.2f}\t{total:>11.2f}")