# ==================== charger_system.py ====================
# 充电系统单元 - 完整运算逻辑（支持交流/直流技术路线，动态读取参数）

import charger_params
from params_jichucanshu import PROJECT_YEARS


class ChargerSystem:
    """
    充电系统类
    负责计算充电系统的：
    - 每年充电量（重卡实际用电量）
    - 每年电网取电量（含效率损耗）
    - 初始投资（CapEx）= 充电桩投资 + 充电堆投资
    - 更换投资（第8年末，仅更换充电桩，充电堆不换）
    - 每年运维成本（OpEx）- 固定5万元/年
    - 每年折旧额（充电桩初始8年折旧，更换后折旧到项目最后一年；充电堆固定8年折旧）
    - 残值（旧桩第8年末回收，新桩第20年末残值 + 充电堆残值）

    技术路线支持：
    - 交流技术路线：交流充电桩 + 交流充电堆
    - 直流技术路线：直流充电桩 + 直流充电堆

    所有参数动态从 charger_params 模块读取，修改参数文件后无需修改本文件
    """

    def __init__(self, technology="交流"):
        """
        初始化充电系统

        :param technology: 技术路线，可选 "交流" 或 "直流"，默认"交流"
        """
        # ---------- 从参数模块动态读取所有参数 ----------
        # 充电桩规模
        self.charger_count = charger_params.CHARGER_COUNT
        self.gun_count = charger_params.GUN_COUNT

        # 充电堆
        self.stack_count = charger_params.CHARGER_STACK_COUNT

        # 技术路线选择
        self.technology = technology

        # 根据技术路线选择对应的单价
        if technology == "交流":
            self.cost_per_unit = charger_params.CHARGER_COST_PER_UNIT_AC
            self.stack_cost = charger_params.CHARGER_STACK_COST_AC
        elif technology == "直流":
            self.cost_per_unit = charger_params.CHARGER_COST_PER_UNIT_DC
            self.stack_cost = charger_params.CHARGER_STACK_COST_DC
        else:
            raise ValueError(f"未知的技术路线：{technology}，请选择'交流'或'直流'")

        # 运营负荷
        self.daily_output = charger_params.CHARGER_DAILY_OUTPUT
        self.operating_days = charger_params.CHARGER_OPERATING_DAYS
        self.simultaneity = charger_params.CHARGER_SIMULTANEITY

        # 投资与成本
        self.opex_fixed = charger_params.CHARGER_OPEX_FIXED

        # ---------- 折旧与残值（充电桩） ----------
        self.charger_lifetime = charger_params.CHARGER_UNIT_LIFETIME
        self.charger_dep_years = charger_params.CHARGER_UNIT_DEPRECIATION_YEARS
        self.charger_residual_rate = charger_params.CHARGER_UNIT_RESIDUAL_RATE

        # ---------- 折旧与残值（充电堆） ----------
        self.stack_lifetime = charger_params.CHARGER_STACK_LIFETIME
        self.stack_dep_years = charger_params.CHARGER_STACK_DEPRECIATION_YEARS
        self.stack_residual_rate = charger_params.CHARGER_STACK_RESIDUAL_RATE

        # 效率
        self.efficiency = charger_params.CHARGER_EFFICIENCY

        self.years = PROJECT_YEARS

    # ======================== 投资计算 ========================

    def get_charger_investment(self):
        """
        计算充电桩投资

        计算公式：
        充电桩投资（元）= 充电桩单价（万元/台）× 充电桩数量（台）× 10000

        :return: float，充电桩投资（元）
        """
        investment = self.cost_per_unit * self.charger_count * 10000
        return round(investment, 0)

    def get_stack_investment(self):
        """
        计算充电堆投资

        计算公式：
        充电堆投资（元）= 充电堆单价（万元/个）× 充电堆数量（个）× 10000

        :return: float，充电堆投资（元）
        """
        investment = self.stack_cost * self.stack_count * 10000
        return round(investment, 0)

    def get_capex(self):
        """
        计算充电系统初始投资（CapEx）

        计算公式：
        初始投资（元）= 充电桩投资 + 充电堆投资

        :return: float，初始投资金额（元）
        """
        capex = self.get_charger_investment() + self.get_stack_investment()
        return round(capex, 0)

    def get_replacement_cost(self):
        """
        计算充电桩更换成本（第8年末）

        说明：仅更换充电桩，充电堆不更换

        计算公式：
        更换成本（元）= 充电桩单价（万元/台）× 充电桩数量（台）× 10000

        :return: float，更换成本（元）
        """
        return self.get_charger_investment()

    def get_replacement_year(self):
        """
        计算充电桩更换年份

        逻辑说明：
        - 设计寿命8年，第8年末更换
        - 第9年启用新桩
        - 更换后不再更换（项目周期20年，新桩用12年）

        :return: int，更换年份（第8年）
        """
        return self.charger_lifetime  # 8

    # ======================== 电量计算 ========================

    def calc_annual_throughput(self):
        """
        计算充电系统每年吞吐量

        逻辑说明：
        - 第0年（建设期）：充电量为0
        - 第1~20年：正常运行（更换不影响充电量）

        计算公式：
        年充电量（kWh）= 单桩日均充电量（kWh/天）× 充电桩数量（台）× 年运行天数（天/年）
        年取电量（kWh）= 年充电量（kWh）/ 充电效率

        :return: tuple (output_list, grid_purchase_list)
                output_list: 重卡实际用电量（kWh）
                grid_purchase_list: 电网取电量（kWh），含效率损耗
        """
        output_list = []
        grid_purchase_list = []

        annual_output = self.daily_output * self.charger_count * self.operating_days
        annual_grid_purchase = annual_output / self.efficiency

        for year in range(self.years + 1):
            if year == 0:
                output_list.append(0)
                grid_purchase_list.append(0)
            else:
                output_list.append(round(annual_output, 0))
                grid_purchase_list.append(round(annual_grid_purchase, 0))

        return output_list, grid_purchase_list

    # ======================== 成本计算 ========================

    def get_opex(self):
        """
        计算充电系统年运维成本（OpEx）

        说明：年运维费固定为5万元/年，每年不变

        :return: float，每年运维成本（元）
        """
        return self.opex_fixed

    # ======================== 折旧计算 ========================

    def get_depreciation(self):
        """
        计算充电系统每年折旧额（直线折旧法）

        折旧逻辑：
        1. 充电桩：
           - 初始：第1~8年计提折旧，残值率8%
           - 第8年末更换，更换成本 = 充电桩初始投资
           - 更换后：从第9年开始，折旧到项目最后一年（第20年）
             折旧年限 = 项目周期 - 更换年份
             年折旧额 = 更换成本 × (1 - 残值率) / 折旧年限
        2. 充电堆：
           - 第1~8年计提折旧，残值率8%，之后不再计提（不更换）

        :return: dict，包含充电桩折旧、充电堆折旧、总折旧
        """
        # 充电桩投资
        charger_inv = self.get_charger_investment()
        # 充电堆投资
        stack_inv = self.get_stack_investment()

        # ---------- 充电桩折旧 ----------
        # 初始折旧（8年，残值率8%）
        charger_residual = charger_inv * self.charger_residual_rate
        charger_depreciable = charger_inv - charger_residual
        charger_annual_dep_initial = charger_depreciable / self.charger_dep_years

        # 更换后折旧（折旧到项目最后一年）
        replacement_year = self.get_replacement_year()
        if replacement_year is not None and replacement_year < self.years:
            remaining_years_after_replacement = self.years - replacement_year
            charger_annual_dep_after = (
                charger_inv * (1 - self.charger_residual_rate) / remaining_years_after_replacement
            )
        else:
            charger_annual_dep_after = 0

        # ---------- 充电堆折旧（8年，残值率8%，不更换）----------
        stack_residual = stack_inv * self.stack_residual_rate
        stack_depreciable = stack_inv - stack_residual
        stack_annual_dep = stack_depreciable / self.stack_dep_years

        # ---------- 生成逐年折旧列表 ----------
        charger_dep_schedule = []
        stack_dep_schedule = []
        total_dep_schedule = []

        for year in range(self.years + 1):
            if year == 0:
                charger_dep_schedule.append(0)
                stack_dep_schedule.append(0)
                total_dep_schedule.append(0)
                continue

            # ===== 充电桩折旧 =====
            if replacement_year is not None and year > replacement_year:
                # 更换后：从第9年到第20年，使用新的年折旧额
                charger_dep = round(charger_annual_dep_after, 0)
            else:
                # 未更换（第1~8年）：按初始折旧年限折旧
                if year <= self.charger_dep_years:
                    charger_dep = round(charger_annual_dep_initial, 0)
                else:
                    charger_dep = 0

            # ===== 充电堆折旧（第1~8年折旧，之后不再计提）=====
            if year <= self.stack_dep_years:
                stack_dep = round(stack_annual_dep, 0)
            else:
                stack_dep = 0

            charger_dep_schedule.append(charger_dep)
            stack_dep_schedule.append(stack_dep)
            total_dep_schedule.append(charger_dep + stack_dep)

        return {
            "charger_depreciation": charger_dep_schedule,
            "stack_depreciation": stack_dep_schedule,
            "total_depreciation": total_dep_schedule
        }

    # ======================== 残值计算 ========================

    def get_residual_value_first_batch(self):
        """
        计算第一批充电桩在更换时的残值（第8年末）

        :return: float，残值金额（元）
        """
        charger_inv = self.get_charger_investment()
        residual = charger_inv * self.charger_residual_rate
        return round(residual, 0)

    def get_residual_value_second_batch(self):
        """
        计算第二批充电桩在项目期末的残值（第20年末）

        说明：第二批充电桩第9年启用，折旧到第20年，第20年末残值 = 投资 × 残值率

        :return: float，残值金额（元）
        """
        charger_inv = self.get_charger_investment()
        residual = charger_inv * self.charger_residual_rate
        return round(residual, 0)

    def get_residual_value_stack(self):
        """
        计算充电堆在项目期末的残值（第20年末）

        说明：充电堆第1~8年折旧，第20年末残值 = 投资 × 残值率

        :return: float，残值金额（元）
        """
        stack_inv = self.get_stack_investment()
        residual = stack_inv * self.stack_residual_rate
        return round(residual, 0)

    def get_residual_value(self):
        """
        计算充电系统在项目期末的残值（新桩残值 + 充电堆残值）

        :return: float，残值金额（元）
        """
        total = self.get_residual_value_second_batch() + self.get_residual_value_stack()
        return round(total, 0)

    # ======================== 功率计算 ========================

    def get_power_capacity(self):
        """
        计算充电站总功率容量

        计算公式：
        总功率（kW）= 充电桩数量（台）× 单桩最大功率（kW）× 负荷同时率

        :return: float，总功率（kW）
        """
        total_power = self.charger_count * 1200 * self.simultaneity
        return round(total_power, 0)

    def get_technology_info(self):
        """
        获取当前技术路线信息

        :return: dict，包含技术路线、充电桩单价、充电堆单价
        """
        return {
            "technology": self.technology,
            "charger_price": self.cost_per_unit,
            "stack_price": self.stack_cost
        }

    # ======================== 摘要 ========================

    def get_summary(self):
        """输出充电系统摘要信息"""
        capex = self.get_capex()
        charger_inv = self.get_charger_investment()
        stack_inv = self.get_stack_investment()
        replacement_year = self.get_replacement_year()
        replacement_cost = self.get_replacement_cost()
        opex = self.get_opex()
        residual_old = self.get_residual_value_first_batch()
        residual_new = self.get_residual_value_second_batch()
        residual_stack = self.get_residual_value_stack()
        output, grid = self.calc_annual_throughput()
        dep = self.get_depreciation()
        tech_info = self.get_technology_info()

        total_output = sum(output)
        total_grid = sum(grid)
        total_dep = sum(dep["total_depreciation"])

        print("=" * 55)
        print("【充电系统摘要】")
        print("=" * 55)
        print(f"项目周期：              {self.years:>12} 年")
        print(f"技术路线：              {tech_info['technology']:>12}")
        print(f"充电桩数量：            {self.charger_count:>12} 台（单桩单枪）")
        print(f"充电枪数量：            {self.gun_count:>12} 把")
        print(f"充电堆数量：            {self.stack_count:>12} 个")
        print(f"充电桩单价：            {tech_info['charger_price']:>12} 万元/台")
        print(f"充电堆单价：            {tech_info['stack_price']:>12} 万元/个")
        print(f"单桩日均充电量：        {self.daily_output:>12} kWh/天")
        print(f"场站日均充电量：        {self.daily_output * self.charger_count:>12,.0f} kWh/天")
        print(f"年运营天数：            {self.operating_days:>12} 天/年")
        print(f"负荷同时率：            {self.simultaneity * 100:>11.2f} %")
        print(f"充电效率：              {self.efficiency * 100:>11.2f} %")
        print(f"充电桩设计寿命：        {self.charger_lifetime:>12} 年")
        print(f"充电桩折旧年限/残值率： {self.charger_dep_years:>8}年 / {self.charger_residual_rate*100:>5.1f}%")
        print(f"充电堆折旧年限/残值率： {self.stack_dep_years:>8}年 / {self.stack_residual_rate*100:>5.1f}%")
        print(f"年运维费（固定）：      {self.opex_fixed:>12,.0f} 元/年")
        print("-" * 55)
        print(f"充电桩投资：            {charger_inv:>12,.0f} 元")
        print(f"充电堆投资：            {stack_inv:>12,.0f} 元")
        print(f"初始投资（CapEx）：     {capex:>12,.0f} 元")
        print(f"更换年份：              {replacement_year:>12} 年末（仅更换充电桩）")
        print(f"更换成本：              {replacement_cost:>12,.0f} 元")
        print(f"旧桩残值（第8年末）：   {residual_old:>12,.0f} 元")
        print(f"新桩残值（第20年末）：  {residual_new:>12,.0f} 元")
        print(f"充电堆残值（第20年末）：{residual_stack:>12,.0f} 元")
        print(f"总残值（第20年末）：    {self.get_residual_value():>12,.0f} 元")
        print(f"年运维成本（OpEx）：    {opex:>12,.0f} 元/年")
        print(f"生命周期总折旧：        {total_dep:>12,.0f} 元")
        print(f"生命周期总充电量：      {total_output:>12,.0f} kWh")
        print(f"生命周期总取电量：      {total_grid:>12,.0f} kWh")
        print("=" * 55)


# ---------- 测试代码 ----------
if __name__ == "__main__":
    print("=" * 55)
    print("测试交流充电系统：")
    print("=" * 55)
    charger_ac = ChargerSystem(technology="交流")
    charger_ac.get_summary()

    print("\n" + "=" * 55 + "\n")

    print("=" * 55)
    print("测试直流充电系统：")
    print("=" * 55)
    charger_dc = ChargerSystem(technology="直流")
    charger_dc.get_summary()

    print("\n【交流充电系统 - 逐年折旧额】")
    dep_ac = charger_ac.get_depreciation()
    print("年份\t充电桩折旧（元）\t充电堆折旧（元）\t合计（元）")
    for year in range(1, 21):
        print(f"  {year:>2}年\t{dep_ac['charger_depreciation'][year]:>14,.0f}\t{dep_ac['stack_depreciation'][year]:>14,.0f}\t{dep_ac['total_depreciation'][year]:>14,.0f}")
