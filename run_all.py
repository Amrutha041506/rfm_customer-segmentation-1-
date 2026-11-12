"""One command to rebuild every output:  python run_all.py"""
import subprocess, sys
for script in ["src/rfm_pipeline.py", "src/visualizations.py"]:
    print(f"\n>>> {script}")
    subprocess.run([sys.executable, script], check=True)
print("\nAll done. See /outputs")
