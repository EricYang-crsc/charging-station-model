# ==================== project_params.py ====================
# 项目宏观参数（Project Level）

# ---------- 项目周期 ----------
PROJECT_YEARS = 20              # 项目周期（年）
CONSTRUCTION_MONTHS = 6         # 建设期（月）

# ---------- 残值与折现 ----------
RESIDUAL_RATE = 0.05            # 残值率（5%）
DISCOUNT_RATE = 0.05            # 基准折现率（5%）

# ---------- 总投资控制 ----------
# 说明：
#   1. USE_FIXED_CAPEX = False 时，总投资 = 各子模块投资自动相加
#   2. USE_FIXED_CAPEX = True 时，总投资 = FIXED_TOTAL_CAPEX（用户指定）
#   3. 当使用固定总投资时，各子模块投资按比例缩放，占比保持不变
USE_FIXED_CAPEX = False         # 是否使用固定总投资（False=自动计算，True=手动指定）
FIXED_TOTAL_CAPEX = 0.0         # 固定总投资额（元），当 USE_FIXED_CAPEX = True 时生效