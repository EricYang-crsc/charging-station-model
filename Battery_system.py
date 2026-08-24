# ==================== Battery_system.py ====================
# 储能系统单元 - 完整运算逻辑

from Battery_params import (
    BATTERY_CAPACITY,
    BATTERY_POWER,
    BATTERY_TECHNOLOGY,
    BATTERY_COST_PER_WH_AC,
    BATTERY_COST_PER_WH_DC,
    BATTERY_CELL_COST_PER_WH,
    BATTERY_EFFICIENCY,
    BATTERY_DOD,
    BATTERY_CYCLE_LIFE,
    BATTERY_DEGRADATION,
    BATTERY_LIFETIME,
    BATTERY_OPEX_RATE,
    BATTERY_CELL_DEPRECIATION_YEARS,
    BATTERY_CELL_RESIDUAL_RATE,
    BATTERY_OTHER_DEPRECIATION_YEARS,
    BATTERY_OTHER_RESIDUAL_RATE,
    BATTERY_CYCLE_PER_DAY,
    BATTERY_OPERATING_DAYS
)
from params_jichucanshu import PROJECT_YEARS


class BatterySystem:
    """
    储能系统类
    负责计算储能系统的：
    - 每年充放电量
    - 电池更换年份及更换成本
    - 初始投资（CapEx）
    - 每年运维成本（OpEx）- 按初始投资的2%计算
    - 每年折旧额（电芯8年/残值8%，其他设备20年/残值5%）
    - 残值

    技术路线支持：
    - 交流储能系统：0.6185 元/Wh
    - 直流储能系统：0.535 元/Wh
    """

    def __init__(self, technology=None):
        """
        初始化储能系统

        :param technology: 技术路线，可选 "交流" 或 "直流"
                           如不传参，使用 BATTERY_TECHNOLOGY 默认值
        """
        # 容量与功率
        self.capacity = BATTERY_CAPACITY
        self.power = BATTERY_POWER

        # 技术路线选择
        if technology is not None:
            self.technology = technology
        else:
            self.technology = BATTERY_TECHNOLOGY

        if self.technology == "交流":
            self.cost_per_wh = BATTERY_COST_PER_WH_AC
        elif self.technology == "直流":
            self.cost_per_wh = BATTERY_COST_PER_WH_DC
        else:
            raise ValueError(f"未知的技术路线：{self.technology}，请选择'交流'或'直流'")

        # 电芯单价
        self.cell_cost_per_wh = BATTERY_CELL_COST_PER_WH

        # 设备性能
        self.efficiency = BATTERY_EFFICIENCY
        self.dod = BATTERY_DOD
        self.cycle_life = BATTERY_CYCLE_LIFE
        self.degradation = BATTERY_DEGRADATION
        self.lifetime = BATTERY_LIFETIME

        # 投资与成本
        self.opex_rate = BATTERY_OPEX_RATE

        # 折旧与残值
        self.cell_dep_years = BATTERY_CELL_DEPRECIATION_YEARS
        self.cell_residual_rate = BATTERY_CELL_RESIDUAL_RATE
        self.other_dep_years = BATTERY_OTHER_DEPRECIATION_YEARS
        self.other_residual_rate = BATTERY_OTHER_RESIDUAL_RATE

        # 运行策略
        self.cycle_per_day = BATTERY_CYCLE_PER_DAY
        self.operating_days = BATTERY_OPERATING_DAYS

        self.years = PROJECT_YEARS

        # 计算电芯投资占比（用于拆分折旧）
        self._calculate_investment_ratio()

    def _calculate_investment_ratio(self):
        """计算电芯投资占总投资的比重"""
        total_investment = self.capacity * 1000 * self.cost_per_wh
        cell_investment = self.capacity * 1000 * self.cell_cost_per_wh
        self.cell_ratio = cell_investment / total_investment
        self.other_ratio = 1 - self.cell_ratio

    def get_capex(self):
        """计算初始投资（元）"""
        capex = self.capacity * 1000 * self.cost_per_wh
        return round(capex, 0)

    def get_cell_cost(self):
        """计算电芯更换成本（元）"""
        cell_cost = self.capacity * 1000 * self.cell_cost_per_wh
        return round(cell_cost, 0)

    def get_replacement_year(self):
        """计算电池更换年份"""
        cycle_years = self.cycle_life / (self.cycle_per_day * self.operating_days)
        replacement_year = min(cycle_years, self.lifetime)
        if replacement_year < self.years:
            return int(replacement_year)
        else:
            return None

    def calc_annual_throughput(self):
        """计算每年充放电量"""
        discharge_list = []
        charge_list = []
        cycles_per_year = self.cycle_per_day * self.operating_days
        replacement_year = self.get_replacement_year()

        for year in range(self.years + 1):
            if year == 0:
                discharge_list.append(0)
                charge_list.append(0)
                continue

            if replacement_year is not None and year > replacement_year:
                years_after = year - replacement_year
                if years_after == 1:
                    degradation_factor = 1.0
                else:
                    degradation_factor = (1 - self.degradation) ** (years_after - 1)
            else:
                if year == 1:
                    degradation_factor = 1.0
                else:
                    degradation_factor = (1 - self.degradation) ** (year - 1)

            annual_discharge = self.capacity * self.dod * cycles_per_year * degradation_factor
            annual_charge = annual_discharge / self.efficiency
            discharge_list.append(round(annual_discharge, 0))
            charge_list.append(round(annual_charge, 0))

        return discharge_list, charge_list

    def get_opex(self):
        """
        计算储能系统年运维成本（OpEx）

        计算公式：
        年运维成本（元）= 初始投资（元）× 年运维费率（2%）

        :return: float，每年运维成本（元）
        """
        capex = self.get_capex()
        opex = capex * self.opex_rate
        return round(opex, 0)

    def get_depreciation(self):
        """
        计算储能系统每年折旧额

        折旧逻辑：
        1. 电芯部分：
           - 未更换前：按8年直线折旧，残值率8%
           - 更换后：从更换后下一年开始，折旧到项目最后一年（第20年）
             折旧年限 = 项目周期 - 更换年份
             年折旧额 = 更换成本 × (1 - 残值率) / 折旧年限
        2. 其他设备部分：按20年直线折旧，残值率5%（不更换）

        :return: dict，包含电芯折旧、其他设备折旧、总折旧
        """
        capex = self.get_capex()

        # 拆分投资（初始投资）
        cell_investment = capex * self.cell_ratio
        other_investment = capex * self.other_ratio

        # ---- 电芯初始折旧（8年，残值率8%）----
        cell_residual = cell_investment * self.cell_residual_rate
        cell_depreciable = cell_investment - cell_residual
        cell_annual_dep_initial = cell_depreciable / self.cell_dep_years

        # ---- 电芯更换后折旧（折旧到项目最后一年）----
        replacement_year = self.get_replacement_year()
        # 电芯更换成本（即电芯投资额）
        cell_replacement_cost = self.get_cell_cost()

        if replacement_year is not None and replacement_year < self.years:
            # 折旧年限 = 项目周期 - 更换年份（从更换后下一年到项目结束）
            remaining_years_after_replacement = self.years - replacement_year
            cell_annual_dep_after_replacement = (
                cell_replacement_cost * (1 - self.cell_residual_rate) / remaining_years_after_replacement
            )
        else:
            cell_annual_dep_after_replacement = 0

        # ---- 其他设备折旧（20年，残值率5%）----
        other_residual = other_investment * self.other_residual_rate
        other_depreciable = other_investment - other_residual
        other_annual_dep = other_depreciable / self.other_dep_years

        # ---- 生成逐年折旧列表 ----
        cell_dep_schedule = []
        other_dep_schedule = []
        total_dep_schedule = []

        for year in range(self.years + 1):
            if year == 0:
                cell_dep_schedule.append(0)
                other_dep_schedule.append(0)
                total_dep_schedule.append(0)
                continue

            # ---- 电芯折旧 ----
            if replacement_year is not None and year > replacement_year:
                # 更换后：从更换年份的下一年开始，使用新折旧额，一直折到项目结束
                cell_dep = round(cell_annual_dep_after_replacement, 0)
            else:
                # 未更换：按原折旧年限（8年）折旧
                if year <= self.cell_dep_years:
                    cell_dep = round(cell_annual_dep_initial, 0)
                else:
                    cell_dep = 0

            # ---- 其他设备折旧（20年）----
            if year <= self.other_dep_years:
                other_dep = round(other_annual_dep, 0)
            else:
                other_dep = 0

            cell_dep_schedule.append(cell_dep)
            other_dep_schedule.append(other_dep)
            total_dep_schedule.append(round(cell_dep + other_dep, 0))

        return {
            "cell_depreciation": cell_dep_schedule,
            "other_depreciation": other_dep_schedule,
            "total_depreciation": total_dep_schedule
        }

    def get_residual_value(self):
        """计算项目期末残值"""
        capex = self.get_capex()
        cell_investment = capex * self.cell_ratio
        other_investment = capex * self.other_ratio
        cell_residual = cell_investment * self.cell_residual_rate
        other_residual = other_investment * self.other_residual_rate
        return round(cell_residual + other_residual, 0)

    def get_replacement_cost(self):
        """获取电池更换成本"""
        replacement_year = self.get_replacement_year()
        if replacement_year is not None:
            return {"year": replacement_year, "cost": self.get_cell_cost()}
        else:
            return None

    def get_technology_info(self):
        """获取当前技术路线信息"""
        return {"technology": self.technology, "price_per_wh": self.cost_per_wh}

    def get_summary(self):
        """输出摘要信息"""
        capex = self.get_capex()
        opex = self.get_opex()
        residual = self.get_residual_value()
        replacement = self.get_replacement_cost()
        discharge, charge = self.calc_annual_throughput()
        tech_info = self.get_technology_info()

        # 获取折旧信息用于展示
        dep = self.get_depreciation()
        total_dep_sum = sum(dep["total_depreciation"])

        print("=" * 55)
        print("【储能系统摘要】")
        print("=" * 55)
        print(f"项目周期：              {self.years:>12} 年")
        print(f"技术路线：              {tech_info['technology']:>12}")
        print(f"储能系统单价：          {tech_info['price_per_wh']:>12.4f} 元/Wh")
        print(f"电芯单价：              {self.cell_cost_per_wh:>12.4f} 元/Wh")
        print(f"储能容量：              {self.capacity:>12,.0f} kWh")
        print(f"储能功率：              {self.power:>12,.0f} kW")
        print(f"充放电效率：            {self.efficiency * 100:>11.2f} %")
        print(f"放电深度（DOD）：       {self.dod * 100:>11.2f} %")
        print(f"循环寿命：              {self.cycle_life:>12,} 次")
        print(f"年衰减率：              {self.degradation * 100:>11.2f} %")
        print(f"使用寿命：              {self.lifetime:>12} 年")
        print(f"日充放电次数：          {self.cycle_per_day:>12} 次/天")
        print(f"年运行天数：            {self.operating_days:>12} 天/年")
        print(f"电芯折旧年限/残值率：   {self.cell_dep_years:>8}年 / {self.cell_residual_rate*100:>5.1f}%")
        print(f"其他设备折旧年限/残值率：{self.other_dep_years:>8}年 / {self.other_residual_rate*100:>5.1f}%")
        print(f"年运维费率：            {self.opex_rate * 100:>11.2f} %")
        print("-" * 55)
        print(f"电芯投资占比：          {self.cell_ratio * 100:>11.2f} %")
        print(f"其他设备投资占比：      {self.other_ratio * 100:>11.2f} %")
        print(f"初始投资（CapEx）：     {capex:>12,.0f} 元")
        print(f"年运维成本（OpEx）：    {opex:>12,.0f} 元/年")
        print(f"残值：                  {residual:>12,.0f} 元")
        print(f"生命周期总折旧：        {total_dep_sum:>12,.0f} 元")

        if replacement:
            print(f"电池更换年份：          {replacement['year']:>12} 年")
            print(f"电池更换成本：          {replacement['cost']:>12,.0f} 元")
        else:
            print("电池更换年份：          不需要更换")

        total_discharge = sum(discharge)
        total_charge = sum(charge)
        print(f"生命周期总放电量：      {total_discharge:>12,.0f} kWh")
        print(f"生命周期总充电量：      {total_charge:>12,.0f} kWh")
        print("=" * 55)


if __name__ == "__main__":
    print("测试交流储能系统：")
    battery_ac = BatterySystem(technology="交流")
    battery_ac.get_summary()

    print("\n" + "=" * 55 + "\n")

    print("测试直流储能系统：")
    battery_dc = BatterySystem(technology="直流")
    battery_dc.get_summary()