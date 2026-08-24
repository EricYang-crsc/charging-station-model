# ==================== solarPV_system.py ====================
# 光伏系统单元 - 完整运算逻辑

from solarPV_params import (
    PV_CAPACITY,
    PEAK_SUN_HOURS,
    PV_DEGRADATION,
    PV_LIFETIME,
    PV_COST_PER_W,
    PV_INVERTER_COST,
    PV_BRACKET_COST,
    PV_OPEX_PER_W,
    PV_DEPRECIATION_YEARS,
    PV_RESIDUAL_RATE
)
from params_jichucanshu import PROJECT_YEARS


class PVSystem:
    """
    光伏系统类
    负责计算光伏系统的：
    - 每年发电量
    - 初始投资（CapEx）= 光伏组件 + 逆变器 + 支吊架
    - 每年运维成本（OpEx）
    - 每年折旧额
    - 残值
    """

    def __init__(self):
        """初始化光伏系统，所有参数从对应文件读取"""
        self.capacity = PV_CAPACITY                # 装机容量（kWp）
        self.peak_sun_hours = PEAK_SUN_HOURS       # 峰值日照小时数（小时/天）
        self.degradation = PV_DEGRADATION          # 年衰减率
        self.lifetime = PV_LIFETIME                # 使用寿命（年）
        self.cost_per_w = PV_COST_PER_W            # 光伏组件单位投资成本（元/W）
        self.inverter_cost = PV_INVERTER_COST      # 逆变器投入（万元）
        self.bracket_cost = PV_BRACKET_COST        # 支吊架投入（万元）
        self.opex_per_w = PV_OPEX_PER_W            # 年运维费（元/W）
        self.depreciation_years = PV_DEPRECIATION_YEARS  # 折旧年限（年）
        self.residual_rate = PV_RESIDUAL_RATE      # 残值率
        self.years = PROJECT_YEARS                 # 项目周期（年）

    def calc_annual_output(self):
        """
        计算光伏系统每年发电量

        计算公式：
        年发电量（kWh）= 装机容量（kW）× 峰值日照小时数（h/天）× 365天 × (1 - 衰减率)^(年-1)

        逻辑说明：
        - 第0年（建设期）：发电量为0
        - 第1年：满发，无衰减
        - 第2~20年：逐年衰减
        - 超过使用寿命（20年）后：发电量为0（项目周期20年，刚好第20年结束）

        :return: list，长度为21（第0年~第20年），单位kWh
        """
        annual_output = []

        # 第一年初始发电量（无衰减）
        initial_output = self.capacity * self.peak_sun_hours * 365

        for year in range(self.years + 1):  # 0 ~ 20年（共21个数据点）
            if year == 0:
                # 建设期当年发电量为0
                annual_output.append(0)
            elif year == 1:
                # 第1年：无衰减
                output = initial_output
                annual_output.append(round(output, 0))
            else:
                # 第2~20年：逐年衰减
                # 第2年衰减1次，第20年衰减19次
                output = initial_output * (1 - self.degradation) ** (year - 1)
                annual_output.append(round(output, 0))

        return annual_output

    def get_capex(self):
        """
        计算光伏系统初始投资（CapEx）

        计算公式：
        光伏组件投资（元）= 装机容量（kW）× 1000 × 单位投资成本（元/W）
        逆变器投资（元）= 逆变器投入（万元）× 10000
        支吊架投资（元）= 支吊架投入（万元）× 10000
        初始投资（元）= 光伏组件投资 + 逆变器投资 + 支吊架投资

        :return: float，初始投资金额（元）
        """
        # 光伏组件投资
        panel_investment = self.capacity * 1000 * self.cost_per_w
        # 逆变器投资（万元→元）
        inverter_investment = self.inverter_cost * 10000
        # 支吊架投资（万元→元）
        bracket_investment = self.bracket_cost * 10000

        capex = panel_investment + inverter_investment + bracket_investment
        return round(capex, 0)

    def get_opex(self):
        """
        计算光伏系统年运维成本（OpEx）

        计算公式：
        年运维成本（元）= 装机容量（kW）× 1000 × 单位运维费（元/W）

        说明：运维费与装机容量挂钩，每年固定不变

        :return: float，每年运维成本（元）
        """
        opex = self.capacity * 1000 * self.opex_per_w
        return round(opex, 0)

    def get_depreciation(self):
        """
        计算光伏系统每年折旧额（直线折旧法）

        计算公式：
        年折旧额（元）=（初始投资 - 残值）/ 折旧年限
        残值 = 初始投资 × 残值率

        逻辑说明：
        - 折旧从第1年开始，到第20年结束（共20年）
        - 第0年（建设期）不计提折旧

        :return: list，长度为21（第0年~第20年），单位元
        """
        capex = self.get_capex()
        residual_value = capex * self.residual_rate
        depreciable_base = capex - residual_value
        annual_depreciation = depreciable_base / self.depreciation_years

        depreciation_schedule = []
        for year in range(self.years + 1):  # 0 ~ 20年
            if year == 0:
                # 建设期不计提折旧
                depreciation_schedule.append(0)
            else:
                # 第1~20年：每年计提折旧
                depreciation_schedule.append(round(annual_depreciation, 0))

        return depreciation_schedule

    def get_residual_value(self):
        """
        计算光伏系统在项目期末的残值

        计算公式：
        残值（元）= 初始投资 × 残值率

        说明：残值在项目最后一年（第20年）作为现金流入

        :return: float，残值金额（元）
        """
        capex = self.get_capex()
        residual_value = capex * self.residual_rate
        return round(residual_value, 0)

    def get_summary(self):
        """
        输出光伏系统摘要信息
        """
        capex = self.get_capex()
        opex = self.get_opex()
        residual = self.get_residual_value()
        output = self.calc_annual_output()
        total_output = sum(output)

        # 拆解投资构成
        panel_investment = self.capacity * 1000 * self.cost_per_w
        inverter_investment = self.inverter_cost * 10000
        bracket_investment = self.bracket_cost * 10000

        print("=" * 55)
        print("【光伏系统摘要】")
        print("=" * 55)
        print(f"项目周期：              {self.years:>12} 年")
        print(f"装机容量：              {self.capacity:>12,.0f} kWp")
        print(f"峰值日照小时数：        {self.peak_sun_hours:>12.1f} 小时/天")
        print(f"年衰减率：              {self.degradation * 100:>11.2f} %")
        print(f"使用寿命：              {self.lifetime:>12} 年")
        print(f"组件单位投资成本：      {self.cost_per_w:>12.2f} 元/W")
        print(f"逆变器投入：            {self.inverter_cost:>12.2f} 万元")
        print(f"支吊架投入：            {self.bracket_cost:>12.2f} 万元")
        print(f"年运维费：              {self.opex_per_w:>12.3f} 元/W")
        print(f"折旧年限：              {self.depreciation_years:>12} 年")
        print(f"残值率：                {self.residual_rate * 100:>11.2f} %")
        print("-" * 55)
        print(f"组件投资：              {panel_investment:>12,.0f} 元")
        print(f"逆变器投资：            {inverter_investment:>12,.0f} 元")
        print(f"支吊架投资：            {bracket_investment:>12,.0f} 元")
        print(f"初始投资（CapEx）：     {capex:>12,.0f} 元")
        print(f"年运维成本（OpEx）：    {opex:>12,.0f} 元/年")
        print(f"残值：                  {residual:>12,.0f} 元")
        print(f"生命周期总发电量：      {total_output:>12,.0f} kWh")
        print("=" * 55)


# ---------- 测试代码 ----------
if __name__ == "__main__":
    # 实例化光伏系统
    pv = PVSystem()

    # 打印摘要
    pv.get_summary()

    # 打印20年全部发电量
    output = pv.calc_annual_output()
    print("\n【逐年发电量（20年项目周期）】")
    print("年份\t发电量（kWh）")
    for year in range(1, 21):
        print(f"  {year:>2}年\t{output[year]:>12,.0f}")

    # 打印折旧
    dep = pv.get_depreciation()
    print("\n【逐年折旧额】")
    print("年份\t折旧额（元）")
    for year in range(1, 21):
        print(f"  {year:>2}年\t{dep[year]:>12,.0f}")