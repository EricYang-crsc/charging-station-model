# ==================== operation_engine.py ====================
# 光储充重卡充电站测算模型 - 引擎层
# 功能：整合所有子模块，完成电量耦合、成本收入计算、财务指标测算
# 交互方式：控制台输入选择技术路线（交流/直流）和还款方式（等额本息/等额本金）
# 贷款参数（利率、期限、还款频率）均从 params_tax_finance.py 读取
# 新增反向求解模式：给定目标财务指标，求解土地租金单价

import numpy as np
import numpy_financial as npf
import importlib

# 导入参数模块（不导入具体变量）
import params_jichucanshu
import params_price_revenue
import params_tax_finance
import params_operating_cost
import solarPV_params
import Battery_params
import charger_params
import other_capEX_params

# 导入子模块类（这些类内部也会动态读取参数）
from solarPV_system import PVSystem
from Battery_system import BatterySystem
from charger_system import ChargerSystem
from other_capEX_systems import OtherCapEXSystem


class OperationEngine:
    """
    光储充重卡充电站测算引擎
    整合所有子模块，完成全流程测算
    支持正常测算和反向求解（给定目标指标求土地租金）
    """

    def __init__(self, technology="交流", loan_type=None, params_dict=None):
        """
        初始化引擎

        :param technology: 技术路线，"交流" 或 "直流"
        :param loan_type: 还款方式，"等额本息" 或 "等额本金"，默认从参数文件读取
        :param params_dict: 参数字典，用于覆盖参数文件中的值（由 run_simulation 传入）
        """
        self.technology = technology
        self.loan_type = loan_type if loan_type is not None else params_tax_finance.LOAN_TYPE
        self.years = params_jichucanshu.PROJECT_YEARS

        # 如果传入参数字典，更新各个参数模块
        if params_dict:
            for module_name, module_vars in params_dict.items():
                if module_name == "jichucanshu":
                    for key, value in module_vars.items():
                        setattr(params_jichucanshu, key, value)
                elif module_name == "price_revenue":
                    for key, value in module_vars.items():
                        setattr(params_price_revenue, key, value)
                elif module_name == "tax_finance":
                    for key, value in module_vars.items():
                        setattr(params_tax_finance, key, value)
                elif module_name == "operating_cost":
                    for key, value in module_vars.items():
                        setattr(params_operating_cost, key, value)
                elif module_name == "solarPV":
                    for key, value in module_vars.items():
                        setattr(solarPV_params, key, value)
                elif module_name == "battery":
                    for key, value in module_vars.items():
                        setattr(Battery_params, key, value)
                elif module_name == "charger":
                    for key, value in module_vars.items():
                        setattr(charger_params, key, value)
                elif module_name == "other_capex":
                    for key, value in module_vars.items():
                        setattr(other_capEX_params, key, value)

        # ---------- 实例化所有子模块 ----------
        # 子模块类内部会从其对应的参数模块中读取最新值（因为它们也使用 import 模块方式）
        self.pv = PVSystem()
        self.battery = BatterySystem(technology=technology)
        self.charger = ChargerSystem(technology=technology)
        self.other = OtherCapEXSystem()

        # ---------- 存储计算结果 ----------
        self.results = {}

        print(f"\n✅ 引擎初始化完成")
        print(f"  技术路线：{technology}")
        print(f"  还款方式：{self.loan_type}")
        print(f"  还款频率：{params_tax_finance.REPAYMENT_FREQUENCY}")
        print(f"  贷款利率：{params_tax_finance.LOAN_RATE * 100:.2f}%")
        print(f"  贷款年限：{params_tax_finance.LOAN_PERIOD} 年")
        print(f"  土地租金单价：{params_operating_cost.LAND_RENT_PER_MU:.2f} 万元/亩/年")
        print("=" * 60)

    # ======================== 固定总投资模式 ========================

    def apply_fixed_capex(self):
        """
        应用固定总投资模式：按比例缩放所有子模块投资

        当 USE_FIXED_CAPEX = True 时，将用户指定的固定总投资额按比例
        分配到各子模块，保持各子模块的投资占比不变。
        缩放后的投资会覆盖原有的 pv_capex、battery_capex、charger_capex、other_capex。
        """
        if not params_jichucanshu.USE_FIXED_CAPEX:
            return

        fixed_total = params_jichucanshu.FIXED_TOTAL_CAPEX
        original_total = self.pv_capex + self.battery_capex + self.charger_capex + self.other_capex

        if original_total <= 0:
            print("⚠️ 警告：原始总投资为0，无法应用固定总投资模式")
            return

        scale = fixed_total / original_total

        # 按比例缩放各子模块投资
        self.pv_capex = self.pv_capex * scale
        self.battery_capex = self.battery_capex * scale
        self.charger_capex = self.charger_capex * scale
        self.other_capex = self.other_capex * scale

        # 打印应用信息
        print("\n📊 【固定总投资模式已启用】")
        print(f"  原始总投资：{original_total:>14,.0f} 元")
        print(f"  固定总投资：{fixed_total:>14,.0f} 元")
        print(f"  缩放比例：  {scale * 100:>10.2f} %")
        print("-" * 50)
        print(f"  缩放后光伏投资：{self.pv_capex:>14,.0f} 元")
        print(f"  缩放后储能投资：{self.battery_capex:>14,.0f} 元")
        print(f"  缩放后充电投资：{self.charger_capex:>14,.0f} 元")
        print(f"  缩放后其它投资：{self.other_capex:>14,.0f} 元")
        print("=" * 60)

    # ======================== 核心计算（可被多次调用） ========================

    def _run_core(self, rent_per_mu=None, print_output=True):
        """
        核心计算函数，可被正常测算和反向求解共用

        :param rent_per_mu: 土地租金单价（万元/亩/年），如果传入则覆盖当前值
        :param print_output: 是否打印详细输出
        :return: dict，包含所有结果
        """
        # 更新土地租金单价（如果传入）
        if rent_per_mu is not None:
            # 直接修改参数模块中的值
            setattr(params_operating_cost, "LAND_RENT_PER_MU", rent_per_mu)

        # 重新实例化子模块（确保参数独立）
        self.pv = PVSystem()
        self.battery = BatterySystem(technology=self.technology)
        self.charger = ChargerSystem(technology=self.technology)
        self.other = OtherCapEXSystem()

        # 获取各子模块数据
        self.get_submodule_data()

        # ===== 新增：应用固定总投资模式（如果有） =====
        self.apply_fixed_capex()

        # 电量耦合
        power_balance = self.calculate_power_balance()

        # 计算收入（含增值服务、设备销售收入、其它收入）
        revenue = self.calculate_revenue(power_balance)

        # 计算运营成本（使用更新后的土地租金单价）
        opex = self.calculate_opex(power_balance)

        # 计算折旧摊销
        dep_amort = self.calculate_depreciation_amortization()

        # 总投资（已缩放）
        total_capex = self.pv_capex + self.battery_capex + self.charger_capex + self.other_capex

        # 资本性支出时间表
        capex_schedule = [0] * (self.years + 1)
        capex_schedule[0] = total_capex
        if self.battery_replacement is not None:
            rep_year = self.battery_replacement["year"]
            rep_cost = self.battery_replacement["cost"]
            capex_schedule[rep_year] += rep_cost
        if self.charger_replacement is not None:
            rep_year = self.charger_replacement_year
            rep_cost = self.charger_replacement
            capex_schedule[rep_year] += rep_cost

        # 贷款
        loan = self.calculate_loan(total_capex)

        # 现金流
        cashflow = self.calculate_cashflow(revenue, opex, dep_amort, loan, capex_schedule)

        # 财务指标
        metrics = self.calculate_financial_metrics(cashflow)

        # 保存结果
        self.results = {
            "technology": self.technology,
            "loan_type": self.loan_type,
            "total_capex": total_capex,
            "loan_amount": loan["loan_amount"],
            "equity_amount": loan["equity_amount"],
            "power_balance": power_balance,
            "revenue": revenue,
            "opex": opex,
            "dep_amort": dep_amort,
            "loan": loan,
            "cashflow": cashflow,
            "metrics": metrics
        }

        if print_output:
            self.print_results()
            self.print_detailed_tables()

        return self.results

    # ======================== 第一步：获取各子模块数据 ========================

    def get_submodule_data(self):
        """
        从各子模块获取基础数据
        """
        # 光伏数据
        self.pv_output = self.pv.calc_annual_output()          # 年发电量（kWh），列表
        self.pv_capex = self.pv.get_capex()                    # 初始投资（元）
        self.pv_opex = self.pv.get_opex()                      # 年运维费（元/年）
        self.pv_dep = self.pv.get_depreciation()               # 逐年折旧（元）
        self.pv_residual = self.pv.get_residual_value()        # 残值（元）

        # 储能数据
        self.battery_discharge, self.battery_charge = self.battery.calc_annual_throughput()
        self.battery_capex = self.battery.get_capex()
        self.battery_opex = self.battery.get_opex()
        self.battery_dep = self.battery.get_depreciation()
        self.battery_residual = self.battery.get_residual_value()
        self.battery_replacement = self.battery.get_replacement_cost()

        # 充电桩数据
        self.charger_output, self.charger_grid = self.charger.calc_annual_throughput()
        self.charger_capex = self.charger.get_capex()
        self.charger_opex = self.charger.get_opex()
        self.charger_dep = self.charger.get_depreciation()
        self.charger_residual = self.charger.get_residual_value()
        self.charger_replacement = self.charger.get_replacement_cost()
        self.charger_replacement_year = self.charger.get_replacement_year()

        # 其他资本性支出数据
        self.other_capex = self.other.get_capex_yuan()         # 元
        self.other_dep = self.other.get_depreciation_schedule()  # 逐年折旧（万元）
        self.other_amort = self.other.get_amortization_schedule()  # 逐年摊销（万元）
        self.other_residual = self.other.get_residual_value_yuan()  # 残值（元）
        self.other_dep_yuan = [d * 10000 for d in self.other_dep]   # 折旧（万元→元）
        self.other_amort_yuan = [a * 10000 for a in self.other_amort]  # 摊销（万元→元）

        # 充电需求（每天100辆车 × 400度 = 40,000 kWh/天）
        self.daily_vehicle_count = 100
        self.daily_charge_per_vehicle = 400
        self.daily_charge_demand = self.daily_vehicle_count * self.daily_charge_per_vehicle  # 40,000 kWh/天
        self.annual_charge_demand = self.daily_charge_demand * self.charger.operating_days   # 14,000,000 kWh/年

        # 充电桩单桩日均充电量（校验用）
        self.single_charger_daily = self.daily_charge_demand / self.charger.charger_count    # 2,500 kWh/天

    # ======================== 新增：计算设备成本总额 ========================

    def calculate_equipment_cost(self):
        """
        计算所有设备成本之和（用于设备销售收入计算）

        设备成本包含：
        - 光伏系统（含逆变器、支吊架）
        - 储能系统
        - 充电系统（含充电桩、充电堆）
        - 钢结构
        - 变压器、电缆、开关柜
        - 监控系统、EMS、运营平台、火灾报警系统

        不含：土建工程、工程管理费、设计费、地勘费、暂列金、基本预备费、其它费用

        :return: float，设备成本总额（元）
        """
        equipment_cost = 0.0

        # 1. 光伏系统（已包含逆变器、支吊架）
        equipment_cost += self.pv_capex

        # 2. 储能系统
        equipment_cost += self.battery_capex

        # 3. 充电系统（含充电桩、充电堆）
        equipment_cost += self.charger_capex

        # 4. 其他资本性支出中的设备部分
        # 直接从 other_capEX_params 中读取各项设备成本（均为万元，需转换为元）
        equipment_cost += other_capEX_params.STEEL_STRUCTURE_COST * 10000          # 钢结构
        equipment_cost += other_capEX_params.TRANSFORMER_COST * 10000              # 变压器
        equipment_cost += other_capEX_params.CABLE_COST * 10000                    # 电缆
        equipment_cost += other_capEX_params.SWITCHGEAR_COST * 10000               # 开关柜
        equipment_cost += other_capEX_params.MONITORING_SYSTEM_COST * 10000        # 全站辅助监控系统
        equipment_cost += other_capEX_params.EMS_COST * 10000                      # 能量管理系统
        equipment_cost += other_capEX_params.OPERATION_PLATFORM_COST * 10000       # 运营管理平台
        equipment_cost += other_capEX_params.FIRE_ALARM_COST * 10000               # 全站火灾报警系统

        return equipment_cost

    # ======================== 第二步：电量耦合 ========================

    def calculate_power_balance(self):
        """
        逐年计算电量平衡（核心算法）
        逻辑：
        1. 充电需求优先满足（车辆需要多少电就供多少）
        2. 光伏发电量优先给储能充电
        3. 储能放电满足充电需求
        4. 不足部分从电网购电

        :return: dict，包含逐年各电量数据
        """
        years = self.years
        pv_gen = self.pv_output
        charger_demand = [self.annual_charge_demand] * (years + 1)
        charger_demand[0] = 0

        battery_discharge = self.battery_discharge
        battery_charge_total = self.battery_charge

        pv_to_storage = [0] * (years + 1)
        pv_curtailment = [0] * (years + 1)
        grid_to_storage = [0] * (years + 1)
        storage_to_charger = [0] * (years + 1)
        grid_to_charger = [0] * (years + 1)
        total_grid_purchase = [0] * (years + 1)
        grid_purchase_cost = [0] * (years + 1)

        for year in range(1, years + 1):
            pv_energy = pv_gen[year]
            demand = charger_demand[year]
            batt_discharge = battery_discharge[year]
            batt_charge = battery_charge_total[year]

            # 第一步：光伏给储能充电
            if pv_energy >= batt_charge:
                pv_to_storage[year] = batt_charge
                pv_curtailment[year] = pv_energy - batt_charge
                grid_to_storage[year] = 0
            else:
                pv_to_storage[year] = pv_energy
                pv_curtailment[year] = 0
                grid_to_storage[year] = batt_charge - pv_energy

            # 第二步：储能放电满足充电需求
            if batt_discharge >= demand:
                storage_to_charger[year] = demand
                grid_to_charger[year] = 0
            else:
                storage_to_charger[year] = batt_discharge
                grid_to_charger[year] = demand - batt_discharge

            # 第三步：电网购电
            total_grid_purchase[year] = grid_to_storage[year] + grid_to_charger[year]

            # 第四步：计算电网购电成本
            storage_grid_cost = grid_to_storage[year] * params_price_revenue.PRICE_VALLEY
            charger_grid_cost = grid_to_charger[year] * params_price_revenue.WEIGHTED_AVG_PRICE
            grid_purchase_cost[year] = storage_grid_cost + charger_grid_cost

        return {
            "pv_gen": pv_gen,
            "charger_demand": charger_demand,
            "battery_discharge": battery_discharge,
            "battery_charge": battery_charge_total,
            "pv_to_storage": pv_to_storage,
            "pv_curtailment": pv_curtailment,
            "grid_to_storage": grid_to_storage,
            "storage_to_charger": storage_to_charger,
            "grid_to_charger": grid_to_charger,
            "total_grid_purchase": total_grid_purchase,
            "grid_purchase_cost": grid_purchase_cost
        }

    # ======================== 第三步：计算收入 ========================

    def calculate_revenue(self, power_balance):
        """
        计算逐年收入

        收入来源：
        1. 充电收入 = 充电量 × (加权平均电价 + 服务费) （每年持续）
        2. 增值服务收入 = 增值服务用地面积 × 每亩收入 （每年持续）
        3. 设备销售收入 = 设备成本总额 × 设备销售收入比例 （仅第1年，一次性收入）
        4. 其它收入 = 固定金额 （仅第1年，一次性收入）
        说明：光伏发电不计入收入，只用于降低电网购电成本（已在成本端体现）

        :param power_balance: 电量平衡结果
        :return: dict，逐年收入
        """
        years = self.years
        charger_demand = power_balance["charger_demand"]

        # 1. 充电收入（每年持续）
        unit_price_with_service = params_price_revenue.WEIGHTED_AVG_PRICE + params_price_revenue.SERVICE_FEE
        charging_revenue = [0] * (years + 1)
        for year in range(1, years + 1):
            charging_revenue[year] = charger_demand[year] * unit_price_with_service

        # 2. 增值服务收入（每年持续）
        value_added_revenue = [0] * (years + 1)
        annual_value_added_revenue = params_operating_cost.LAND_AREA_VALUE_ADDED * params_operating_cost.LAND_REVENUE_PER_MU
        for year in range(1, years + 1):
            value_added_revenue[year] = annual_value_added_revenue

        # 3. 设备销售收入（只第1年，一次性收入）
        equipment_sales_revenue = [0] * (years + 1)
        equipment_cost_total = self.calculate_equipment_cost()
        sales_ratio = params_price_revenue.EQUIPMENT_SALES_REVENUE_RATIO
        annual_equipment_sales_revenue = equipment_cost_total * sales_ratio
        if years >= 1:
            equipment_sales_revenue[1] = annual_equipment_sales_revenue

        # 4. 其它收入（只第1年，一次性收入）
        other_income = [0] * (years + 1)
        annual_other_income = params_price_revenue.OTHER_INCOME
        if years >= 1:
            other_income[1] = annual_other_income

        # 5. 总营业收入
        total_revenue = [0] * (years + 1)
        for year in range(1, years + 1):
            total_revenue[year] = (
                charging_revenue[year] +
                value_added_revenue[year] +
                equipment_sales_revenue[year] +
                other_income[year]
            )

        return {
            "charging_revenue": charging_revenue,
            "value_added_revenue": value_added_revenue,
            "equipment_sales_revenue": equipment_sales_revenue,
            "other_income": other_income,
            "total_revenue": total_revenue
        }

    # ======================== 第四步：计算运营成本 ========================

    def calculate_opex(self, power_balance):
        """
        计算逐年运营成本（不含折旧、摊销、利息）

        成本项包括：
        1. 电网购电成本
        2. 各子模块运维费（光伏、储能、充电桩）
        3. 土地租金（按全部用地面积计算，与增值服务用地无关）
        4. 人员工资
        5. 保险费
        6. 容量费

        :param power_balance: 电量平衡结果
        :return: dict，逐年运营成本
        """
        years = self.years

        grid_purchase_cost = power_balance["grid_purchase_cost"]

        pv_opex = [0] * (years + 1)
        battery_opex = [0] * (years + 1)
        charger_opex = [0] * (years + 1)

        for year in range(1, years + 1):
            pv_opex[year] = self.pv_opex
            battery_opex[year] = self.battery_opex
            charger_opex[year] = self.charger_opex

        # 土地租金（按全部用地面积计算，使用 self.rent_per_mu）
        remaining_lease_years = self.years - other_capEX_params.LAND_LEASE_YEARS_INITIAL
        annual_land_rent = params_operating_cost.LAND_AREA * params_operating_cost.LAND_RENT_PER_MU * 10000  # 元/年

        land_rent = [0] * (years + 1)
        for year in range(1, years + 1):
            if year <= remaining_lease_years:
                land_rent[year] = annual_land_rent
            else:
                land_rent[year] = 0

        # 人员工资
        staff_cost = [0] * (years + 1)
        for year in range(1, years + 1):
            if year == 1:
                staff_cost[year] = params_operating_cost.STAFF_COST_FIRST_YEAR * 10000
            else:
                staff_cost[year] = staff_cost[year - 1] * (1 + params_tax_finance.INFLATION_RATE)

        # 保险费（电气设备总价值 × 0.1%）
        electrical_total = self.pv_capex + self.battery_capex + self.charger_capex
        electrical_total += (other_capEX_params.TRANSFORMER_COST + other_capEX_params.CABLE_COST + other_capEX_params.SWITCHGEAR_COST) * 10000

        annual_insurance = electrical_total * params_operating_cost.INSURANCE_RATE

        insurance = [0] * (years + 1)
        for year in range(1, years + 1):
            insurance[year] = annual_insurance

        # 容量费
        capacity_fee = [0] * (years + 1)
        annual_capacity_fee = params_operating_cost.CAPACITY_FEE * 10000
        for year in range(1, years + 1):
            capacity_fee[year] = annual_capacity_fee

        # 汇总
        total_opex = [0] * (years + 1)
        for year in range(1, years + 1):
            total_opex[year] = (
                grid_purchase_cost[year] +
                pv_opex[year] +
                battery_opex[year] +
                charger_opex[year] +
                land_rent[year] +
                staff_cost[year] +
                insurance[year] +
                capacity_fee[year]
            )

        return {
            "grid_purchase_cost": grid_purchase_cost,
            "pv_opex": pv_opex,
            "battery_opex": battery_opex,
            "charger_opex": charger_opex,
            "land_rent": land_rent,
            "staff_cost": staff_cost,
            "insurance": insurance,
            "capacity_fee": capacity_fee,
            "total_opex": total_opex
        }

    # ======================== 第五步：计算折旧和摊销 ========================

    def calculate_depreciation_amortization(self):
        """
        汇总各子模块的折旧和摊销

        :return: dict，逐年总折旧和总摊销
        """
        years = self.years

        pv_dep = self.pv_dep
        battery_dep = self.battery_dep["total_depreciation"]
        charger_dep = self.charger_dep["total_depreciation"]

        other_dep = self.other_dep_yuan
        other_amort = self.other_amort_yuan

        total_dep = [0] * (years + 1)
        total_amort = [0] * (years + 1)

        for year in range(1, years + 1):
            total_dep[year] = pv_dep[year] + battery_dep[year] + charger_dep[year] + other_dep[year]
            total_amort[year] = other_amort[year]

        return {
            "pv_dep": pv_dep,
            "battery_dep": battery_dep,
            "charger_dep": charger_dep,
            "other_dep": other_dep,
            "other_amort": other_amort,
            "total_dep": total_dep,
            "total_amort": total_amort
        }

    # ======================== 第六步：计算贷款和利息 ========================

    def calculate_loan(self, total_investment):
        """
        计算贷款还本付息

        支持等额本息和等额本金两种还款方式
        支持年、半年、月三种还款频率（从 params_tax_finance.py 读取）
        按"期"计算，再汇总到年

        :param total_investment: 总投资（元）
        :return: dict，逐年还本付息、利息
        """
        # 从参数模块动态读取
        loan_rate = params_tax_finance.LOAN_RATE
        loan_period = params_tax_finance.LOAN_PERIOD
        equity_ratio = params_tax_finance.EQUITY_RATIO
        loan_type = params_tax_finance.LOAN_TYPE
        repayment_freq = params_tax_finance.REPAYMENT_FREQUENCY

        years = self.years

        loan_amount = total_investment * (1 - equity_ratio)
        equity_amount = total_investment * equity_ratio

        # ===== 根据还款频率计算期利率和总期数 =====
        if repayment_freq == "年":
            period_rate = loan_rate
            total_periods = loan_period
            periods_per_year = 1
        elif repayment_freq == "半年":
            period_rate = loan_rate / 2
            total_periods = loan_period * 2
            periods_per_year = 2
        elif repayment_freq == "月":
            period_rate = loan_rate / 12
            total_periods = loan_period * 12
            periods_per_year = 12
        else:
            raise ValueError(f"不支持的还款频率：{repayment_freq}，请选择'年'、'半年'或'月'")

        # ===== 每期还款额 =====
        if loan_type == "等额本息":
            if period_rate > 0:
                period_payment = loan_amount * period_rate * (1 + period_rate) ** total_periods / ((1 + period_rate) ** total_periods - 1)
            else:
                period_payment = loan_amount / total_periods
        elif loan_type == "等额本金":
            period_principal = loan_amount / total_periods
            period_payment = None
        else:
            raise ValueError(f"不支持的还款方式：{loan_type}，请选择'等额本息'或'等额本金'")

        # ===== 逐期计算 =====
        debt_service_period = [0] * (total_periods + 1)
        interest_period = [0] * (total_periods + 1)
        principal_period = [0] * (total_periods + 1)
        remaining_principal_period = [loan_amount] * (total_periods + 1)

        remaining = loan_amount

        for period in range(1, total_periods + 1):
            if loan_type == "等额本息":
                interest = remaining * period_rate
                principal = period_payment - interest
                debt_service_period[period] = period_payment

            elif loan_type == "等额本金":
                principal = period_principal
                interest = remaining * period_rate
                debt_service_period[period] = principal + interest

            if period == total_periods:
                principal = remaining
                debt_service_period[period] = principal + interest

            interest_period[period] = interest
            principal_period[period] = principal
            remaining = remaining - principal
            remaining_principal_period[period] = max(remaining, 0)

            if remaining <= 0:
                break

        # ===== 按年汇总 =====
        debt_service = [0] * (years + 1)
        interest_expense = [0] * (years + 1)
        principal_repayment = [0] * (years + 1)
        remaining_principal = [loan_amount] * (years + 1)

        for year in range(1, loan_period + 1):
            start_period = (year - 1) * periods_per_year + 1
            end_period = min(year * periods_per_year, total_periods)

            for period in range(start_period, end_period + 1):
                debt_service[year] += debt_service_period[period]
                interest_expense[year] += interest_period[period]
                principal_repayment[year] += principal_period[period]

            remaining_principal[year] = remaining_principal_period[end_period]

        # 贷款还清后，剩余年份债务为0
        for year in range(loan_period + 1, years + 1):
            debt_service[year] = 0
            interest_expense[year] = 0
            principal_repayment[year] = 0
            remaining_principal[year] = 0

        return {
            "loan_amount": loan_amount,
            "equity_amount": equity_amount,
            "period_payment": period_payment if loan_type == "等额本息" else None,
            "debt_service": debt_service,
            "interest_expense": interest_expense,
            "principal_repayment": principal_repayment,
            "remaining_principal": remaining_principal,
            "periods_per_year": periods_per_year,
            "total_periods": total_periods,
            "repayment_frequency": repayment_freq,
            "loan_type": loan_type
        }

    # ======================== 第七步：计算现金流和IRR ========================

    def calculate_cashflow(self, revenue, opex, dep_amort, loan, capex_schedule=None):
        """
        计算现金流

        :param revenue: 收入数据
        :param opex: 运营成本数据
        :param dep_amort: 折旧摊销数据
        :param loan: 贷款数据
        :param capex_schedule: 逐年资本性支出（含更换）
        :return: dict，现金流和财务指标
        """
        years = self.years

        total_revenue = revenue["total_revenue"]
        total_opex = opex["total_opex"]

        total_dep = dep_amort["total_dep"]
        total_amort = dep_amort["total_amort"]
        total_dep_amort = [0] * (years + 1)
        for year in range(1, years + 1):
            total_dep_amort[year] = total_dep[year] + total_amort[year]

        interest_expense = loan["interest_expense"]

        # ---- 计算税前利润 ----
        ebit = [0] * (years + 1)
        ebt = [0] * (years + 1)

        for year in range(1, years + 1):
            ebit[year] = total_revenue[year] - total_opex[year] - total_dep_amort[year]
            ebt[year] = ebit[year] - interest_expense[year]

        # ---- 计算所得税 ----
        tax = [0] * (years + 1)

        for year in range(1, years + 1):
            if ebt[year] <= 0:
                tax[year] = 0
            elif params_tax_finance.TAX_HOLIDAY and year <= 3:
                tax[year] = 0
            elif params_tax_finance.TAX_HOLIDAY and year <= 6:
                tax[year] = ebt[year] * params_tax_finance.INCOME_TAX_RATE * 0.5
            else:
                tax[year] = ebt[year] * params_tax_finance.INCOME_TAX_RATE

        # ---- 计算净利润 ----
        net_income = [0] * (years + 1)
        for year in range(1, years + 1):
            net_income[year] = ebt[year] - tax[year]

        # ---- 计算净现金流 ----
        if capex_schedule is None:
            capex_schedule = [0] * (years + 1)

        total_residual = (
            self.pv_residual +
            self.battery_residual +
            self.charger_residual +
            self.other_residual
        )

        debt_service = loan["debt_service"]
        equity_initial = loan["equity_amount"]

        fcf = [0] * (years + 1)
        fcfe = [0] * (years + 1)

        for year in range(0, years + 1):
            if year == 0:
                # ===== 关键修正 =====
                # 全投资现金流（FCF）：扣除总投资
                fcf[year] = -capex_schedule[year]
                # 自有资金现金流（FCFE）：只扣除自有资金（资本金）
                fcfe[year] = -equity_initial
                # =====================
            elif year == years:
                # 最后一年：加上残值回收
                fcf[year] = net_income[year] + total_dep_amort[year] - capex_schedule[year] + total_residual
                fcfe[year] = net_income[year] + total_dep_amort[year] - capex_schedule[year] - debt_service[year] + total_residual
            else:
                fcf[year] = net_income[year] + total_dep_amort[year] - capex_schedule[year]
                fcfe[year] = net_income[year] + total_dep_amort[year] - capex_schedule[year] - debt_service[year]

        return {
            "ebit": ebit,
            "ebt": ebt,
            "tax": tax,
            "net_income": net_income,
            "fcf": fcf,
            "fcfe": fcfe,
            "total_dep_amort": total_dep_amort,
            "total_residual": total_residual
        }

    # ======================== 第八步：计算财务指标 ========================

    def calculate_financial_metrics(self, cashflow):
        """
        计算IRR、投资回收期、NPV等财务指标

        :param cashflow: 现金流数据
        :return: dict，财务指标
        """

        fcf = cashflow["fcf"]
        fcfe = cashflow["fcfe"]

        fcf_array = np.array(fcf)
        fcfe_array = np.array(fcfe)

        def calculate_irr(cf):
            """计算IRR，如果无法计算则返回None"""
            if len(cf) < 2:
                return None
            try:
                return npf.irr(cf)
            except:
                return None

        def calculate_payback(cf):
            """计算投资回收期（年）"""
            cumsum = 0
            for i in range(len(cf)):
                cumsum += cf[i]
                if cumsum >= 0 and i > 0:
                    prev_cum = cumsum - cf[i]
                    if cf[i] != 0:
                        fraction = -prev_cum / cf[i]
                    else:
                        fraction = 0
                    return i - 1 + fraction
            return None

        def calculate_npv(cf, rate):
            """计算净现值"""
            npv = 0
            for i in range(len(cf)):
                npv += cf[i] / ((1 + rate) ** i)
            return npv

        metrics = {
            "full_investment_irr": calculate_irr(fcf_array),
            "full_investment_payback": calculate_payback(fcf),
            "full_investment_npv": calculate_npv(fcf, params_jichucanshu.DISCOUNT_RATE),

            "equity_irr": calculate_irr(fcfe_array),
            "equity_payback": calculate_payback(fcfe),
            "equity_npv": calculate_npv(fcfe, params_jichucanshu.DISCOUNT_RATE),
        }

        total_revenue = sum([r for r in cashflow.get("net_income", [0]) if r > 0]) + sum([r for r in cashflow.get("ebt", [0]) if r > 0])
        total_net_income = sum([r for r in cashflow.get("net_income", [0]) if r > 0])
        metrics["net_profit_margin"] = total_net_income / total_revenue if total_revenue > 0 else 0

        return metrics

    # ======================== 反向求解功能 ========================

    def solve_land_rent_for_target(self, target_type, target_value, precision=0.0001):
        """
        反向求解土地租金单价

        :param target_type: 目标指标类型，"irr_full", "irr_equity", "payback_full", "payback_equity"
        :param target_value: 目标值（IRR为小数，如0.08；回收期为年数）
        :param precision: 精度（IRR为0.0001即0.01%；回收期为0.01年）
        :return: (求解出的租金单价, 实际指标值, 迭代次数)
        """
        # 检查目标值是否可达
        low_rent = 0.0
        high_rent = 10.0

        # 计算租金为0时的指标
        result_low = self._run_core(rent_per_mu=low_rent, print_output=False)
        metric_low = self._get_metric(result_low, target_type)

        # 计算租金为10时的指标
        result_high = self._run_core(rent_per_mu=high_rent, print_output=False)
        metric_high = self._get_metric(result_high, target_type)

        # 检查目标值是否在可达到范围内
        if target_type in ["irr_full", "irr_equity"]:
            # IRR：租金越高，IRR越低（因为成本增加）
            min_val = min(metric_low, metric_high)
            max_val = max(metric_low, metric_high)
            if target_value < min_val or target_value > max_val:
                return None, None, 0

        elif target_type in ["payback_full", "payback_equity"]:
            # 回收期：租金越高，回收期越长
            min_val = min(metric_low, metric_high)
            max_val = max(metric_low, metric_high)
            if target_value < min_val or target_value > max_val:
                return None, None, 0

        # 二分搜索
        iterations = 0
        mid_rent = (low_rent + high_rent) / 2
        while (high_rent - low_rent) > precision and iterations < 100:
            mid_rent = (low_rent + high_rent) / 2
            result_mid = self._run_core(rent_per_mu=mid_rent, print_output=False)
            metric_mid = self._get_metric(result_mid, target_type)

            if target_type in ["irr_full", "irr_equity"]:
                # IRR随租金增加而减少（单调递减）
                if metric_mid > target_value:
                    low_rent = mid_rent
                else:
                    high_rent = mid_rent
            else:  # payback
                # 回收期随租金增加而增加（单调递增）
                if metric_mid < target_value:
                    low_rent = mid_rent
                else:
                    high_rent = mid_rent

            iterations += 1

        final_rent = (low_rent + high_rent) / 2
        final_result = self._run_core(rent_per_mu=final_rent, print_output=False)
        final_metric = self._get_metric(final_result, target_type)

        return final_rent, final_metric, iterations

    @staticmethod
    def _get_metric(result_dict, target_type):
        """从结果字典中提取目标指标值"""
        metrics = result_dict["metrics"]
        if target_type == "irr_full":
            return metrics["full_investment_irr"] if metrics["full_investment_irr"] is not None else 0.0
        elif target_type == "irr_equity":
            return metrics["equity_irr"] if metrics["equity_irr"] is not None else 0.0
        elif target_type == "payback_full":
            return metrics["full_investment_payback"] if metrics["full_investment_payback"] is not None else 999.0
        elif target_type == "payback_equity":
            return metrics["equity_payback"] if metrics["equity_payback"] is not None else 999.0
        else:
            raise ValueError(f"不支持的目标类型：{target_type}")

    # ======================== 主运行方法（适配正常测算） ========================

    def run(self):
        """
        运行完整测算流程（正常模式）
        """
        print("\n" + "=" * 60)
        print(f"🚀 开始测算：{self.technology}技术路线 | {self.loan_type}还款方式")
        print("=" * 60)

        return self._run_core(rent_per_mu=params_operating_cost.LAND_RENT_PER_MU, print_output=True)

    # ======================== 输出结果 ========================

    def print_results(self):
        """打印测算结果摘要"""
        metrics = self.results["metrics"]

        print("\n" + "=" * 60)
        print("📈 财务测算结果摘要")
        print("=" * 60)
        print(f"技术路线：              {self.technology}")
        print(f"还款方式：              {self.loan_type}")
        print(f"还款频率：              {params_tax_finance.REPAYMENT_FREQUENCY}")
        print(f"充电综合单价：          {params_price_revenue.WEIGHTED_AVG_PRICE + params_price_revenue.SERVICE_FEE:.4f} 元/kWh")
        print(f"  （加权平均电价：      {params_price_revenue.WEIGHTED_AVG_PRICE:.4f} 元/kWh）")
        print(f"  （服务费：            {params_price_revenue.SERVICE_FEE:.2f} 元/kWh）")
        print(f"增值服务收入（年）：    {params_operating_cost.LAND_AREA_VALUE_ADDED * params_operating_cost.LAND_REVENUE_PER_MU:>12,.0f} 元/年")
        equipment_cost = self.calculate_equipment_cost()
        print(f"设备销售收入（年）：    {equipment_cost * params_price_revenue.EQUIPMENT_SALES_REVENUE_RATIO:>12,.0f} 元/年")
        print(f"设备销售收入比例：      {params_price_revenue.EQUIPMENT_SALES_REVENUE_RATIO * 100:.0f}%")
        print(f"其它收入（年）：        {params_price_revenue.OTHER_INCOME:>12,.0f} 元/年")
        print(f"总投资（CapEx）：        {self.results['total_capex']:>12,.0f} 元")
        print(f"贷款金额：              {self.results['loan_amount']:>12,.0f} 元")
        print(f"自有资金：              {self.results['equity_amount']:>12,.0f} 元")
        print("-" * 40)

        if metrics["full_investment_irr"] is not None:
            print(f"全投资IRR：            {metrics['full_investment_irr'] * 100:>11.2f} %")
        else:
            print("全投资IRR：              无法计算")

        if metrics["full_investment_payback"] is not None:
            print(f"全投资回收期：          {metrics['full_investment_payback']:>11.2f} 年")
        else:
            print("全投资回收期：           无法计算")

        print(f"全投资NPV（折现率5%）： {metrics['full_investment_npv']:>12,.0f} 元")
        print("-" * 40)

        if metrics["equity_irr"] is not None:
            print(f"自有资金IRR：          {metrics['equity_irr'] * 100:>11.2f} %")
        else:
            print("自有资金IRR：            无法计算")

        if metrics["equity_payback"] is not None:
            print(f"自有资金回收期：        {metrics['equity_payback']:>11.2f} 年")
        else:
            print("自有资金回收期：         无法计算")

        print(f"自有资金NPV（折现率5%）：{metrics['equity_npv']:>12,.0f} 元")
        print("-" * 40)
        print(f"净利润率：              {metrics['net_profit_margin'] * 100:>11.2f} %")
        print("=" * 60)

    def print_detailed_tables(self):
        """打印逐年详细数据表（全投资口径 + 自有资金口径）"""
        revenue = self.results["revenue"]
        opex = self.results["opex"]
        cashflow = self.results["cashflow"]
        loan = self.results["loan"]

        # ===== 贷款明细表 =====
        print("\n【贷款本金和利息逐年明细（{}，按{}还款）】".format(loan["loan_type"], loan["repayment_frequency"]))
        print("年份\t本金偿还（元）\t利息支出（元）\t年供（元）\t剩余本金（元）")
        for year in range(1, params_tax_finance.LOAN_PERIOD + 1):
            principal = loan["principal_repayment"][year]
            interest = loan["interest_expense"][year]
            debt_service = loan["debt_service"][year]
            remaining = loan["remaining_principal"][year]
            print(f"  {year:>2}年\t{principal:>14,.0f}\t{interest:>14,.0f}\t{debt_service:>14,.0f}\t{remaining:>14,.0f}")
        print("-" * 70)

        # ---- 表1：全投资口径（不考虑贷款） ----
        print("\n【逐年利润表 — 全投资口径（不考虑贷款）】")
        print("年份\t收入（元）\t成本（元）\t净利润（元）\t净现金流（元）")
        for year in range(1, self.years + 1):
            rev = revenue["total_revenue"][year]
            cost = opex["total_opex"][year] + cashflow["total_dep_amort"][year]
            ebit = rev - cost
            if ebit <= 0:
                tax_full = 0
            elif params_tax_finance.TAX_HOLIDAY and year <= 3:
                tax_full = 0
            elif params_tax_finance.TAX_HOLIDAY and year <= 6:
                tax_full = ebit * params_tax_finance.INCOME_TAX_RATE * 0.5
            else:
                tax_full = ebit * params_tax_finance.INCOME_TAX_RATE
            net_income_full = ebit - tax_full
            fcf = cashflow["fcf"][year]
            print(f"  {year:>2}年\t{rev:>12,.0f}\t{cost:>12,.0f}\t{net_income_full:>12,.0f}\t{fcf:>14,.0f}")

        # ---- 表2：自有资金口径（考虑贷款） ----
        print("\n【逐年利润表 — 自有资金口径（考虑贷款）】")
        print("年份\t收入（元）\t成本（元）\t净利润（元）\t净现金流（元）")
        for year in range(1, self.years + 1):
            rev = revenue["total_revenue"][year]
            cost = opex["total_opex"][year] + cashflow["total_dep_amort"][year] + loan["interest_expense"][year]
            ni = cashflow["net_income"][year]
            fcfe = cashflow["fcfe"][year]
            print(f"  {year:>2}年\t{rev:>12,.0f}\t{cost:>12,.0f}\t{ni:>12,.0f}\t{fcfe:>14,.0f}")


# ======================== 标准化仿真接口（供 Streamlit 调用） ========================

def run_simulation(technology="交流", loan_type="等额本息", params_dict=None):
    """
    标准化仿真入口，供 Streamlit 调用

    :param technology: 技术路线，"交流" 或 "直流"
    :param loan_type: 还款方式，"等额本息" 或 "等额本金"
    :param params_dict: 参数字典，用于覆盖参数文件中的值
    :return: dict，包含所有结果
    """
    # 创建引擎实例，传入参数字典
    engine = OperationEngine(technology=technology, loan_type=loan_type, params_dict=params_dict)
    return engine.run()


# ======================== 主程序入口（交互部分） ========================

def main():
    """主程序入口 - 控制台交互"""
    print("=" * 60)
    print("    光储充重卡充电站测算模型 v1.0")
    print("=" * 60)

    # ---------- 第零步：选择模式 ----------
    print("\n【模式选择】")
    print("  1. 正常测算模式（完整输出财务指标）")
    print("  2. 反向求解模式（给定目标财务指标，求解土地租金）")
    print("-" * 40)
    mode_choice = input("请输入序号（1 或 2）：").strip()

    if mode_choice == "2":
        # ===== 反向求解模式 =====
        print("\n【反向求解模式】")
        print("请选择要计算的目标指标类型：")
        print("  1. 全投资IRR")
        print("  2. 自有资金IRR")
        print("  3. 全投资回收期（年）")
        print("  4. 自有资金回收期（年）")
        print("-" * 40)
        target_choice = input("请输入序号（1-4）：").strip()

        target_map = {
            "1": "irr_full",
            "2": "irr_equity",
            "3": "payback_full",
            "4": "payback_equity"
        }
        target_type = target_map.get(target_choice)
        if target_type is None:
            print("❌ 输入无效，退出程序")
            return

        # 输入目标值
        target_value_input = input("请输入目标值（IRR输入小数如0.08，回收期输入年数如8.5）：").strip()
        try:
            target_value = float(target_value_input)
        except ValueError:
            print("❌ 输入无效，请确保输入数字")
            return

        # 创建引擎（使用默认参数：交流、等额本息）
        print("\n🔍 使用默认参数进行反向求解...")
        print("  技术路线：交流")
        print("  还款方式：等额本息")
        print("  土地租金搜索范围：0 ~ 10 万元/亩/年")
        print("  求解精度：0.01% (IRR) 或 0.01年 (回收期)")
        print("-" * 40)

        engine = OperationEngine(technology="交流", loan_type="等额本息")
        result_rent, result_metric, iterations = engine.solve_land_rent_for_target(
            target_type=target_type,
            target_value=target_value,
            precision=0.0001
        )

        if result_rent is None:
            print("❌ 目标值无法达到，请检查目标值是否在合理范围内。")
            print(f"   提示：在当前参数下，最小土地租金为0时指标值约为 {engine._get_metric(engine.results, target_type):.4f}，最大为10时约为 ...")
            return

        print("\n" + "=" * 60)
        print("✅ 反向求解完成！")
        print("=" * 60)
        print(f"  目标指标类型：{target_type}")
        print(f"  目标值：{target_value}")
        print(f"  求解出的土地租金单价：{result_rent:.4f} 万元/亩/年")
        print(f"  对应实际指标值：{result_metric:.4f}")
        print(f"  迭代次数：{iterations}")
        print(f"  精度误差：{abs(result_metric - target_value):.6f}")
        print("=" * 60)

        # 输出详细结果（可选）
        show_detail = input("\n是否查看该租金下的详细财务结果？(y/n)：").strip().lower()
        if show_detail == 'y':
            engine._run_core(rent_per_mu=result_rent, print_output=True)

    else:
        # ===== 正常测算模式 =====
        print("\n【当前配置】")
        print(f"  项目周期：            {params_jichucanshu.PROJECT_YEARS} 年")
        print(f"  资本金比例：          {params_tax_finance.EQUITY_RATIO * 100:.0f}%")
        print(f"  贷款利率：            {params_tax_finance.LOAN_RATE * 100:.2f}%")
        print(f"  贷款年限：            {params_tax_finance.LOAN_PERIOD} 年")
        print(f"  还款频率：            {params_tax_finance.REPAYMENT_FREQUENCY}")
        print(f"  默认还款方式：        {params_tax_finance.LOAN_TYPE}")
        print(f"  充电需求：            100辆/天 × 400度/辆 = 40,000 kWh/天")
        print(f"  充电综合单价：        {params_price_revenue.WEIGHTED_AVG_PRICE + params_price_revenue.SERVICE_FEE:.4f} 元/kWh")
        print(f"  增值服务收入：        {params_operating_cost.LAND_AREA_VALUE_ADDED * params_operating_cost.LAND_REVENUE_PER_MU:,.0f} 元/年")
        print(f"  设备销售收入比例：    {params_price_revenue.EQUIPMENT_SALES_REVENUE_RATIO * 100:.0f}%")
        print(f"  其它收入：            {params_price_revenue.OTHER_INCOME:,.0f} 元/年")
        print("=" * 60)

        # ---------- 第一步交互：选择技术路线 ----------
        print("\n【技术路线选择】")
        print("  1. 交流技术路线（交流储能 + 交流充电）")
        print("     - 储能系统单价：0.6185 元/Wh")
        print("     - 充电桩单价：60 万元/台，充电堆 24 万元/个")
        print("  2. 直流技术路线（直流储能 + 直流充电）")
        print("     - 储能系统单价：0.535 元/Wh")
        print("     - 充电桩单价：75 万元/台，充电堆 30 万元/个")
        print("-" * 40)

        tech_choice = input("请输入序号（1 或 2）：").strip()

        if tech_choice == "1":
            technology = "交流"
        elif tech_choice == "2":
            technology = "直流"
        else:
            print("\n⚠️ 输入无效，默认使用交流技术路线")
            technology = "交流"

        print(f"✅ 已选择：{technology}技术路线")

        # ---------- 第二步交互：选择还款方式 ----------
        print("\n【还款方式选择】")
        print(f"  1. 等额本息（默认，来自参数文件）")
        print(f"  2. 等额本金")
        print("-" * 40)
        print(f"  提示：直接回车使用默认值「{params_tax_finance.LOAN_TYPE}」")

        loan_choice = input("请输入序号（1 或 2，直接回车使用默认）：").strip()

        if loan_choice == "1":
            loan_type = "等额本息"
        elif loan_choice == "2":
            loan_type = "等额本金"
        else:
            loan_type = params_tax_finance.LOAN_TYPE
            print(f"  使用默认值：{loan_type}")

        print(f"✅ 已选择：{loan_type}还款方式")

        # ---------- 第三步交互：是否启用固定总投资模式 ----------
        print("\n【固定总投资模式】")
        print("  说明：启用后，总投资将使用您指定的固定值，")
        print("        各子模块投资按比例缩放，占比保持不变。")
        print("  1. 启用固定总投资模式（手动输入总投资额）")
        print("  2. 关闭固定总投资模式（使用各子模块自动计算的总投资）")
        print("-" * 40)

        fixed_choice = input("请输入序号（1 或 2）：").strip()

        if fixed_choice == "1":
            # 启用固定总投资模式
            fixed_total_input = input("请输入固定总投资额（元，如 50000000）：").strip()
            try:
                fixed_total = float(fixed_total_input)
                if fixed_total <= 0:
                    print("\n⚠️ 输入金额必须大于0，已自动关闭固定总投资模式")
                    setattr(params_jichucanshu, "USE_FIXED_CAPEX", False)
                    setattr(params_jichucanshu, "FIXED_TOTAL_CAPEX", 0.0)
                else:
                    setattr(params_jichucanshu, "USE_FIXED_CAPEX", True)
                    setattr(params_jichucanshu, "FIXED_TOTAL_CAPEX", fixed_total)
                    print(f"\n✅ 固定总投资模式已启用，总投资额：{fixed_total:,.0f} 元")
            except ValueError:
                print("\n⚠️ 输入无效，已自动关闭固定总投资模式")
                setattr(params_jichucanshu, "USE_FIXED_CAPEX", False)
                setattr(params_jichucanshu, "FIXED_TOTAL_CAPEX", 0.0)
        else:
            # 关闭固定总投资模式
            setattr(params_jichucanshu, "USE_FIXED_CAPEX", False)
            setattr(params_jichucanshu, "FIXED_TOTAL_CAPEX", 0.0)
            print("\n✅ 固定总投资模式已关闭，使用各子模块自动计算的总投资")

        print("=" * 60)

        # ---------- 创建引擎并运行 ----------
        engine = OperationEngine(technology=technology, loan_type=loan_type)
        results = engine.run()

        print("\n🎉 测算完成！")

    return


if __name__ == "__main__":
    main()