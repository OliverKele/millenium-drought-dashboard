import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -------------------- Manipulate Precipitation Data and Create Line Plot for Top of Dashboard -------------------

# Variables
DATA_PATH = "data/NASA/precip_sum_12mo.nc" 
LON_SLICE   = slice(110, 155)
LAT_SLICE   = slice(-10, -45)            

ds = xr.open_dataset(DATA_PATH)

# Use December-ending frames
end_ym = ds["integration_period_end_month"].astype("int64")
ds_dec = ds.sel(time=(end_ym % 100) == 12)

# Australia subset
sub = ds_dec.sel(lon=LON_SLICE, lat=LAT_SLICE).sortby("lat")
pr  = sub["Pr_sum"]

# Years array for titles
years_all = pd.to_datetime(sub.time.values).year

# Calculate spatial average over Australia for each time step
pr_australia_mean = pr.mean(dim=["lat", "lon"])

# Create styled time series line plot
fig_line, ax_line = plt.subplots(figsize=(12, 8))

ax_line.plot(years_all, pr_australia_mean.values, linewidth=2, color='#1f77b4', alpha=1.0)

# Add shaded region for Millennium Drought (1997-2010)
millennium_drought_start = 1997
millennium_drought_end = 2010
drought_patch = ax_line.axvspan(millennium_drought_start, millennium_drought_end, 
                               alpha=0.2, color='red', label='Millennium Drought (1997-2010)')

# Add text annotation for the drought period
legend = ax_line.legend([drought_patch], ['Millennium Drought (1997-2010)'], 
                       loc='upper left', frameon=False, fontsize=10)


ax_line.set_xlabel('Year', fontsize=12)
ax_line.set_ylabel('Precipitation (mm/12 months)', fontsize=12)
ax_line.set_title('Australia 12-month Precipitation Sum', 
                 fontsize=14, pad=20)

# Set y-axis limits and ticks with some padding
ax_line.set_ylim(130, 370)
ax_line.set_yticks(range(150, 375, 25))

# Set x-axis limits and ticks
ax_line.set_xlim(years_all.min(), years_all.max())
ax_line.set_xticks(range(1950, 2020, 10))

# Style the plot border
ax_line.spines['bottom'].set_linewidth(1)
ax_line.spines['left'].set_linewidth(1)

plt.tight_layout()
plt.savefig("outputs/aus_precip12mo_line_plot.png", dpi=300, bbox_inches='tight')

print("Saved: outputs/aus_precip12mo_line_plot.png")