import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
import matplotlib.image as mpimg

# -------------------- Data Manipulation & Visualisation of Suicide Rates --------------------


file_path = "data/2023-aihw-suicide-and-self-harm-monitoring-nmd-suicide-icd-10-x60-x84-y87-0_1.xlsx"
SHEET     = "Table NMD S8"

df_all = pd.read_excel(file_path, sheet_name=SHEET, header=1)

# Select relevant rows (spreadsheet also has number of suicide deaths in each region & other statistics)
df = df_all.iloc[10:15].copy()

# Get remoteness column
rem_col = "Remoteness area"
# Get year column
year_cols = [c for c in df.columns if isinstance(c, int) and 1900 < c < 2100]

df = df[[rem_col] + year_cols]

# Convert to long format for animation
df_long = df.melt(
    id_vars=[rem_col],
    value_vars=year_cols,
    var_name="year",
    value_name="rate_per_100k"
).dropna(subset=["rate_per_100k"])

df_long["year"] = df_long["year"].astype(int)
df_long["rate_per_100k"] = pd.to_numeric(df_long["rate_per_100k"], errors="coerce")

# Define colors to match the grave icons (from svgrepo)
color_mapping = {
    "Major Cities": "#648FFF",      
    "Inner Regional": "#785EF0",    
    "Outer Regional": "#DC267F",    
    "Remote": "#FE6100",            
    "Very Remote": "#FFB000"        
}

# Create line chart
rem_levels = df_long[rem_col].unique()
years = sorted([y for y in df_long["year"].unique() if 2001 <= y <= 2014])

ymin = float(np.floor(df_long["rate_per_100k"].min()))
ymax = float(np.ceil(df_long["rate_per_100k"].max()))

fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(min(years), max(years))
ax.set_ylim(ymin, ymax)
ax.set_xlabel("Year")
ax.set_ylabel("Suicide Rate per 100k")
ax.set_title("Suicide Rates by Remoteness (2001-2014)")
ax.grid(True, alpha=0.3)

# Plot lines
for rem in rem_levels:
    rem_data = df_long[df_long[rem_col] == rem]
    color = color_mapping.get(rem, "gray")
    ax.plot(rem_data["year"], rem_data["rate_per_100k"], 
            label=rem, linewidth=2, color=color)

ax.legend(loc="upper left", fontsize=9)
plt.tight_layout()
plt.savefig("outputs/suicide_rates_by_remoteness_static.png", dpi=150, bbox_inches='tight')

# Filter data for 2004 and prepare for pictogram
df_2004 = df_long[df_long["year"] == 2004].copy()
df_2004 = df_2004.dropna(subset=["rate_per_100k"]).reset_index(drop=True)

# Create pictogram chart
UNIT = 1  # 1 icon = 1 death per 100k

fig_picto, ax_picto = plt.subplots(figsize=(12, 6))

y = np.arange(len(df_2004))
counts = (df_2004["rate_per_100k"] / UNIT).astype(int)

zoom = 0.06
bar_spacing = 0.4

# Paths to svg icons in icons folder
icon_mapping = {
    "Major Cities": "icons/grave-col1.png",
    "Inner Regional": "icons/grave-col2.png", 
    "Outer Regional": "icons/grave-col3.png",
    "Remote": "icons/grave-col4.png",
    "Very Remote": "icons/grave-col5.png"
}

# Load all icons
icons = {}
for area, icon_path in icon_mapping.items():
    icons[area] = mpimg.imread(icon_path)

# Plot icons for each remoteness area    
for yi, (n, region) in enumerate(zip(counts, df_2004[rem_col])):

    icon = icons.get(region)
    
    y_pos = yi * bar_spacing
    
    for i in range(n):
        ab = AnnotationBbox(
            OffsetImage(icon, zoom=zoom),
            (i + 0.5, y_pos),
            frameon=False, pad=0
        )
        ax_picto.add_artist(ab)

# Set axes limits
max_icons = max(counts) if len(counts) > 0 else 1
ax_picto.set_xlim(0, max_icons + 1)

# Reduce vertical spacing
ax_picto.set_ylim(-0.3, (len(df_2004) - 1) * bar_spacing + 0.3)

# Adjust y-tick positions to match the vertical spacing
y_positions = np.arange(len(df_2004)) * bar_spacing
ax_picto.set_yticks(y_positions)
ax_picto.set_yticklabels(df_2004[rem_col])
ax_picto.set_xlabel(f"Suicide Rate per 100k (1 icon = {UNIT} death)")
ax_picto.set_title("Suicide Rates by Remoteness - 2004")

ax_picto.xaxis.grid(True, linestyle="-", linewidth=0.7, alpha=1)
ax_picto.set_axisbelow(True)

plt.tight_layout()
plt.savefig("outputs/suicide_rates_pictogram_2004.png", dpi=150, bbox_inches='tight')
