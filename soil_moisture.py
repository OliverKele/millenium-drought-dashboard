import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap, Normalize
import matplotlib as mpl

# --------- Manipulate and Visualise Soil Moisture (Produces Static (2003) and Animated Visualisation) ---------

DATA_PATH = "data/NASA/soil_moisture_avg_12mo.nc"

LON_SLICE   = slice(110, 155)
LAT_SLICE   = slice(-10, -45)             
YEAR      = 2003                         

# Load data
ds = xr.open_dataset(DATA_PATH)

# Use December-ending frames
end_ym = ds["integration_period_end_month"].astype("int64")
ds_dec = ds.sel(time=(end_ym % 100) == 12)

# Australia subset
sub = ds_dec.sel(lon=LON_SLICE, lat=LAT_SLICE).sortby("lat")

# Select standardized anomaly variable
sa = sub["Ws_ave_sa"]          

# Years array for titles
years = pd.to_datetime(sub.time.values).year

# Set Limits
abs_q = np.nanquantile(np.abs(sa.values), 0.99)
vlim = float(abs_q) if np.isfinite(abs_q) and abs_q > 0 else float(np.nanmax(np.abs(sa.values)))
vlim = max(vlim, 1.5)
vmin, vmax = -vlim, vlim

# Build a colour map with a neutral band around 0
NEUTRAL_LO, NEUTRAL_HI = -0.5, 0.5
NEUTRAL_COLOR = "#fff2c1"

# Red for dry, Blue for wet
neg_color = mpl.colormaps["RdBu"](0.05)
pos_color = mpl.colormaps["RdBu"](0.95)

def make_div_with_neutral(vmin, vmax,
                          neutral_lo=NEUTRAL_LO, neutral_hi=NEUTRAL_HI,
                          neg=neg_color, neu=NEUTRAL_COLOR, pos=pos_color):
    w = (vmax - vmin)
    x_lo = np.clip((neutral_lo - vmin) / w, 0, 1)
    x_hi = np.clip((neutral_hi - vmin) / w, 0, 1)
    # Build the piecewise colour map
    return LinearSegmentedColormap.from_list(
        "div_with_neutral",
        [(0.0, neg), (x_lo, neu), (x_hi, neu), (1.0, pos)]
    )

cmap = make_div_with_neutral(vmin, vmax)
norm = Normalize(vmin=vmin, vmax=vmax)


# ------ Create a Static Plot for a Specific Year (2003) ------

dsy = sa.sel(time=sub.time.values[years == YEAR]).squeeze("time")
lat_min, lat_max = float(sub.lat.min()), float(sub.lat.max())
lon_min, lon_max = float(sub.lon.min()), float(sub.lon.max())

fig, ax = plt.subplots(figsize=(10, 7))
ax.set_facecolor("#f3f6f9")
ax.set_title(f"Australia Soil Moisture (12-mo) Anomaly — {YEAR}")
ax.axis('off')

im = ax.imshow(
    dsy.transpose("lat","lon").values,
    origin="lower",
    extent=[lon_min, lon_max, lat_min, lat_max],
    cmap=cmap, norm=norm, interpolation="nearest"
)


cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
cbar.set_label("Soil moisture standardized anomaly (z)\nBlue = wetter, Red = drier")

plt.tight_layout()
plt.savefig(f"outputs/soil_moisture_AUS_{YEAR}_Dec.png", dpi=170)
print(f"Saved: outputs/soil_moisture_AUS_{YEAR}_Dec.png")


# ------ Create Animated Visualisation for All Years (from 1993) ------

mask_1993 = years >= 1993
sa_1993 = sa.sel(time=sub.time.values[mask_1993])
years_1993 = years[mask_1993]
fig_1993, ax_1993 = plt.subplots(figsize=(10, 7))
ax_1993.set_facecolor("#f3f6f9")
ax_1993.axis('off')
im_1993 = ax_1993.imshow(
    sa_1993.isel(time=0).transpose("lat","lon").values,
    origin="lower",
    extent=[lon_min, lon_max, lat_min, lat_max],
    cmap=cmap, norm=norm, interpolation="nearest"
)

cbar_1993 = fig_1993.colorbar(im_1993, ax=ax_1993, fraction=0.035, pad=0.02)
cbar_1993.set_label("Soil moisture standardized anomaly (z)\nBlue = wetter, Red = drier")
title_1993 = ax_1993.set_title(f"Australia Soil Moisture (12-mo) Anomaly — {int(years_1993[0])}")
def update_1993(i):
    im_1993.set_data(sa_1993.isel(time=i).transpose("lat","lon").values)
    title_1993.set_text(f"Australia Soil Moisture (12-mo) Anomaly — {int(years_1993[i])}")
    return (im_1993, title_1993)
ani_1993 = animation.FuncAnimation(fig_1993, update_1993, frames=sa_1993.sizes["time"], interval=1000, blit=False)
ani_1993.save("outputs/soil_moisture_AUS_anom_from1993.mp4", writer="ffmpeg", fps=1, codec='libx264')
plt.close(fig_1993)
print("Saved: outputs/soil_moisture_AUS_anom_from1993.mp4")


