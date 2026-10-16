import subprocess
import sys

# -------------------------------1. Execute the Plan simulation------------------------------------------
print("\n------------------------ Running Plan Simulation with disturbance --------------------------\n")

result = subprocess.run(
    [sys.executable, "plan_simulation/main_distr.py"],
    check=False
)

if result.returncode != 0:
    print("Plan simulation failed. STL monitoring will not execute.")
    sys.exit(result.returncode)

# -------------------------------2. Execute STL monitoring------------------------------------------
print("\n---------------- Running STL Monitoring -----------------------------\n")

result = subprocess.run(
    [sys.executable, "stl_monitor/main.py"],
    check=False
)

if result.returncode != 0:
    print("STL monitoring failed.")
    sys.exit(result.returncode)

print("\n-------------------- Execution Completed Successfully ------------------------------\n")
