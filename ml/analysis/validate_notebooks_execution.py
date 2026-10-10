import os
import sys
import nbformat
import matplotlib
matplotlib.use("Agg")
import plotly.io as pio
pio.renderers.default = "json"

notebook_paths = [
    "notebooks/01_eda.ipynb",
    "notebooks/02_financial_analysis.ipynb",
    "notebooks/03_anomaly_analysis.ipynb",
    "notebooks/04_visualizations.ipynb",
]

orig_cwd = os.getcwd()
os.chdir("notebooks")
sys.path.insert(0, os.path.abspath(".."))

all_passed = True
for nb_rel in [os.path.basename(p) for p in notebook_paths]:
    print(f"--- Testing {nb_rel} ---")
    try:
        nb = nbformat.read(nb_rel, as_version=4)
        global_scope = {
            "display": lambda *args: None,
        }
        for idx, cell in enumerate(nb.cells):
            if cell.cell_type == "code":
                code = cell.source
                exec(code, global_scope)
        print(f"[OK] {nb_rel} executed all cells successfully.")
    except Exception as e:
        print(f"[FAILED] {nb_rel} error: {e}")
        all_passed = False

os.chdir(orig_cwd)

if all_passed:
    print("\n[SUCCESS] All 4 notebooks executed cleanly without errors!")
else:
    sys.exit(1)
