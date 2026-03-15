import subprocess
import sys

# -------- Runs all Data Manipulation and Visualisation Scripts --------

print("Running ABARES analysis...")
subprocess.run([sys.executable, 'ABARES.py'])

print("\nRunning precipitation analysis...")
subprocess.run([sys.executable, 'precipitation.py'])

print("\nRunning soil moisture analysis...")
subprocess.run([sys.executable, 'soil_moisture.py'])

print("\nRunning national mortality analysis...")
subprocess.run([sys.executable, 'national_mortality.py'])

print("\nRunning side by side comparison...")
subprocess.run([sys.executable, 'make_side_by_side.py'])

print("\nAll done! Run 'streamlit run dashboard.py' to view final results.")

