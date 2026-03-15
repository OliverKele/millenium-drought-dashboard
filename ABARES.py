import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import BoundaryNorm
from matplotlib.cm import ScalarMappable

# ------------------ Code to Manipulate & Visualise ABARES Data ------------------

# -------- Build ABARES Regions --------

# Read the ABARES AAGIS shapefile for regions
regions = gpd.read_file('data/aagis_asgs16v1_g5a.shp_')

# Map to Australia (in case of bad extents/projections)
regions = regions.to_crs(3577)

# Create Blank Map of ABARES Regions and Save to GeoJSON
fig, ax = plt.subplots(figsize=(9, 9))
regions.plot(ax=ax, edgecolor='black', linewidth=0.4, facecolor='white')
ax.set_title('ABARES AAGIS Regions (ASGS 2016)')
ax.set_axis_off()
plt.tight_layout()

regions.to_file('data/abares_aagis_2016_epsg3577.geojson', driver='GeoJSON')


# -------- Manipulate ABARES Data --------

# Read ABARES Data from Downloaded CSV
ABARES_df = pd.read_csv('data/fdp-regional-historical.csv')

# Farm Profit
farm_profit_df = ABARES_df[
    (ABARES_df['Variable'] == 'Farm business profit ($)') &
    (ABARES_df['Year'] >= 1992) &
    (ABARES_df['Year'] <= 2014)
][['Year', 'ABARES region', 'Value']]


# Wheat Production
wheat_df = ABARES_df[
    (ABARES_df['Variable'] == 'Wheat produced (t)') &
    (ABARES_df['Year'] >= 1992) &
    (ABARES_df['Year'] <= 2014)
][['Year', 'ABARES region', 'Value']]


# Get Livestock Counts (Beef, Sheep, and Dairy Herds)
herd_vars = [
    'Beef herd at 30 June (no.)',
    'Sheep flock at 30 June (no.)',
    'Dairy cattle at June 30 (no.)'
]
herd_df = ABARES_df[
    (ABARES_df['Variable'].isin(herd_vars)) &
    (ABARES_df['Year'] >= 1992) &
    (ABARES_df['Year'] <= 2014)
][['Year', 'ABARES region', 'Variable', 'Value']]

# Pivot to Get Herd Counts in Columns
herd_pivot = herd_df.pivot_table(
    index=['Year', 'ABARES region'],
    columns='Variable',
    values='Value',
    aggfunc='sum'
).reset_index()

# Calculate Total Herd Count
herd_pivot['Total herd count'] = (
    herd_pivot['Beef herd at 30 June (no.)'].fillna(0) +
    herd_pivot['Sheep flock at 30 June (no.)'].fillna(0) +
    herd_pivot['Dairy cattle at June 30 (no.)'].fillna(0)
)


# -------- Visualise Farm Profit --------

# Calculate 3-Year Rolling Average, Then Percentage Change
def calculate_three_year_avg_pct_change(group):
    group = group.sort_values('Year')
    group['Three_year_avg'] = group['Value'].rolling(window=3, min_periods=1).mean()
    group['Farm profit 3yr avg pct change'] = group['Three_year_avg'].pct_change() * 100
    return group

farm_profit_3yr_df = farm_profit_df.groupby('ABARES region').apply(calculate_three_year_avg_pct_change, include_groups=True).reset_index(drop=True)

# Remove First Year (won't have percentage change)
farm_profit_3yr_pct_df = farm_profit_3yr_df[farm_profit_3yr_df['Year'] > 1992][['Year', 'ABARES region', 'Value', 'Farm profit 3yr avg pct change']]

# Merge With ABARES Regions for Mapping
profit_3yr_map_df = regions.merge(farm_profit_3yr_pct_df, left_on='name', right_on='ABARES region')

fig1, ax1 = plt.subplots(figsize=(10, 8))
regions.plot(ax=ax1, edgecolor='black', facecolor='white')
profit_3yr_years = sorted(farm_profit_3yr_pct_df['Year'].unique())

# Create Boundaries & Colormap
profit_3yr_boundaries = [-50, -25, -15, -5, -2, 2, 5, 15, 25, 50]
profit_3yr_cmap = plt.cm.RdYlGn 
profit_3yr_norm = BoundaryNorm(profit_3yr_boundaries, profit_3yr_cmap.N)

# Create Static Colorbar
sm_profit_3yr = ScalarMappable(norm=profit_3yr_norm, cmap=profit_3yr_cmap)
sm_profit_3yr.set_array([])
cbar1 = fig1.colorbar(sm_profit_3yr, ax=ax1, fraction=0.03, pad=0.02, boundaries=profit_3yr_boundaries, ticks=profit_3yr_boundaries)
cbar1.set_label('Farm Profit % Change (3-Year Average Base)')
cbar1.ax.set_yticklabels(['-50 +', '-25', '-15', '-5', '-2', '2', '5', '15', '25', '50 +'])
cbar1.ax.tick_params(size=0, pad=5)

ax1.set_axis_off()

# Animate Map (1 Year = 1 Frame)
def animate_profit_3yr(i):
    for coll in ax1.collections[1:]:
        coll.remove()
    year = profit_3yr_years[i]
    data = profit_3yr_map_df[profit_3yr_map_df['Year'] == year]
    data.plot(
        column='Farm profit 3yr avg pct change',
        ax=ax1,
        cmap=profit_3yr_cmap,
        norm=profit_3yr_norm,
        edgecolor='black',
        linewidth=0.4,
        legend=False,
        missing_kwds={'color': 'lightgrey', 'edgecolor': 'black', 'hatch': '///', 'label': 'No data'}
    )
    ax1.set_title(f'Farm Profit % Change (3-Year Average) — {year}')

ani_profit_3yr = animation.FuncAnimation(fig1, animate_profit_3yr, frames=len(profit_3yr_years), repeat=False)
profit_3yr_writer = animation.FFMpegWriter(fps=1, metadata=dict(artist='MXB362'), bitrate=1800, codec='libx264')
ani_profit_3yr.save('outputs/animated_farm_profit.mp4', writer=profit_3yr_writer)


# -------- Livestock Count --------
# Same General Method as Farm Profit, Slightly Different Ranges/Ticks

def calculate_livestock_three_year_avg_pct_change(group):
    group = group.sort_values('Year')
    group['Three_year_avg'] = group['Total herd count'].rolling(window=3, min_periods=1).mean()
    group['Livestock 3yr avg pct change'] = group['Three_year_avg'].pct_change() * 100
    return group

herd_3yr_df = herd_pivot.groupby('ABARES region').apply(calculate_livestock_three_year_avg_pct_change, include_groups=True).reset_index(drop=True)

herd_3yr_pct_df = herd_3yr_df[herd_3yr_df['Year'] > 1992][['Year', 'ABARES region', 'Total herd count', 'Livestock 3yr avg pct change']]

herd_3yr_map_df = regions.merge(herd_3yr_pct_df, left_on='name', right_on='ABARES region')

fig2, ax2 = plt.subplots(figsize=(10, 8))
regions.plot(ax=ax2, edgecolor='black', facecolor='white')
herd_3yr_years = sorted(herd_3yr_pct_df['Year'].unique())

herd_3yr_boundaries = [-30, -20, -10, -5, -2, 2, 5, 10, 20, 30]
herd_3yr_cmap = plt.cm.RdYlGn
herd_3yr_norm = BoundaryNorm(herd_3yr_boundaries, herd_3yr_cmap.N)

sm_herd_3yr = ScalarMappable(norm=herd_3yr_norm, cmap=herd_3yr_cmap)
sm_herd_3yr.set_array([])
cbar2 = fig2.colorbar(sm_herd_3yr, ax=ax2, fraction=0.03, pad=0.02, boundaries=herd_3yr_boundaries, ticks=herd_3yr_boundaries)
cbar2.set_label('Livestock Headcount % Change (3-Year Average Base)')
cbar2.ax.set_yticklabels(['-30 +', '-20', '-10', '-5', '-2', '2', '5', '10', '20', '30 +'])
cbar2.ax.tick_params(size=0, pad=5)

ax2.set_axis_off()

def animate_herd_3yr(i):
    for coll in ax2.collections[1:]:
        coll.remove()
    year = herd_3yr_years[i]
    data = herd_3yr_map_df[herd_3yr_map_df['Year'] == year]
    data.plot(
        column='Livestock 3yr avg pct change',
        ax=ax2,
        cmap=herd_3yr_cmap,
        norm=herd_3yr_norm,
        edgecolor='black',
        linewidth=0.4,
        legend=False,
        missing_kwds={'color': 'lightgrey', 'edgecolor': 'black', 'hatch': '///', 'label': 'No data'}
    )
    ax2.set_title(f'Livestock Headcount % Change (3-Year Average) — {year}')

ani_herd_3yr = animation.FuncAnimation(fig2, animate_herd_3yr, frames=len(herd_3yr_years), repeat=False)
herd_3yr_writer = animation.FFMpegWriter(fps=1, metadata=dict(artist='MXB362'), bitrate=1800, codec='libx264')
ani_herd_3yr.save('outputs/animated_livestock.mp4', writer=herd_3yr_writer)


# -------- Wheat Production --------
# Same General Method as Previous Variables, Slightly Different Ranges/Ticks

def calculate_wheat_three_year_avg_pct_change(group):
    group = group.sort_values('Year')
    group['Three_year_avg'] = group['Value'].rolling(window=3, min_periods=1).mean()
    group['Wheat 3yr avg pct change'] = group['Three_year_avg'].pct_change() * 100
    return group

wheat_3yr_df = wheat_df.groupby('ABARES region').apply(calculate_wheat_three_year_avg_pct_change, include_groups=True).reset_index(drop=True)

wheat_3yr_pct_df = wheat_3yr_df[wheat_3yr_df['Year'] > 1992][['Year', 'ABARES region', 'Value', 'Wheat 3yr avg pct change']]

wheat_3yr_map_df = regions.merge(wheat_3yr_pct_df, left_on='name', right_on='ABARES region')

fig3, ax3 = plt.subplots(figsize=(10, 8))
regions.plot(ax=ax3, edgecolor='black', facecolor='white')
wheat_3yr_years = sorted(wheat_3yr_pct_df['Year'].unique())

wheat_3yr_boundaries = [-40, -25, -15, -5, -2, 2, 5, 15, 25, 40]
wheat_3yr_cmap = plt.cm.RdYlGn
wheat_3yr_norm = BoundaryNorm(wheat_3yr_boundaries, wheat_3yr_cmap.N)

sm_wheat_3yr = ScalarMappable(norm=wheat_3yr_norm, cmap=wheat_3yr_cmap)
sm_wheat_3yr.set_array([])
cbar3 = fig3.colorbar(sm_wheat_3yr, ax=ax3, fraction=0.03, pad=0.02, boundaries=wheat_3yr_boundaries, ticks=wheat_3yr_boundaries)
cbar3.set_label('Wheat Production % Change (3-Year Average Base)')
cbar3.ax.set_yticklabels(['-40 +', '-25', '-15', '-5', '-2', '2', '5', '15', '25', '40 +'])
cbar3.ax.tick_params(size=0, pad=5)

ax3.set_axis_off()

def animate_wheat_3yr(i):
    for coll in ax3.collections[1:]:
        coll.remove()
    year = wheat_3yr_years[i]
    data = wheat_3yr_map_df[wheat_3yr_map_df['Year'] == year]
    data.plot(
        column='Wheat 3yr avg pct change',
        ax=ax3,
        cmap=wheat_3yr_cmap,
        norm=wheat_3yr_norm,
        edgecolor='black',
        linewidth=0.4,
        legend=False,
        missing_kwds={'color': 'lightgrey', 'edgecolor': 'black', 'hatch': '///', 'label': 'No data'}
    )
    ax3.set_title(f'Wheat Production % Change (3-Year Average) — {year}')

ani_wheat_3yr = animation.FuncAnimation(fig3, animate_wheat_3yr, frames=len(wheat_3yr_years), repeat=False)
wheat_3yr_writer = animation.FFMpegWriter(fps=1, metadata=dict(artist='MXB362'), bitrate=1800, codec='libx264')
ani_wheat_3yr.save('outputs/animated_wheat.mp4', writer=wheat_3yr_writer)