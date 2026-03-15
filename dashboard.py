from pathlib import Path

import streamlit as st
from PIL import Image


BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"


def outputs_path(name: str) -> Path:
    return OUTPUTS_DIR / name

# --------- Dashboard Layout ---------

st.set_page_config(layout="wide", page_title="Australian Water Availability & Agriculture", page_icon="🌦️")

st.markdown("<h1 style='text-align: center;'>Australian Water Availability & Agriculture</h1>", unsafe_allow_html=True)

# Top Section: Two Animations Side by Side
top_col1, top_col2 = st.columns([2,1])
with top_col1:
    col1, col2 = st.columns(2)
    with col1:
        st.image(str(outputs_path("aus_precip12mo_line_plot.png")), use_container_width=True)
        st.markdown("<p style='text-align: center; margin-top: 20px;'>Australian Precipitation Overtime</p>", unsafe_allow_html=True)
    with col2:
        st.image(str(outputs_path("soil_moisture_AUS_2003_Dec.png")), use_container_width=True)
        st.markdown("<p style='text-align: center; margin-top: 0px;'>2003 Soil Moisture Anomalies</p>", unsafe_allow_html=True)
with top_col2:
    st.markdown("#### About this Dashboard")
    st.write("""Farmer’s livelihoods are tied to water. Variability in rainfall and water availability directly affects crop yields, livestock health, and farm income (Kelly et al., 2019 ). Farmer’s mental health is also acutely affected by water availability – in times of drought, farmer suicide rates increase (Life In Mind, 2023).
\n This dashboard explores the relationship between water availability and farmer’s livelihoods, highlighting the difficulties they face in an industry dependent on water.
\n Agricultural drought occurs when there is insufficient water to support crops and livestock (National Centers for Environmental Information, 2025). Therefore, soil moisture is used throughout this dashboard to model water availability.
\n A focus of this dashboard is the devastating effects of the Millenium Drought which affected most of Australia from 1997-2010 (Bureau of Meteorology, 2025). Low precipitation and extreme temperatures caused record low water availability which devastated farmers livelihoods. Across Australia, agricultural productivity reduced by ~18% during the drought (Sheng & Xu, 2019). 
\n As climate change begins to affect Australia, understanding the impact of water availability on farmer’s livelihoods is more important than ever.
""")

lower_col1, lower_col2 = st.columns([2,2])
st.markdown("---")

# Lower Section: Dropdown Centered Above Both Graphs
options = {
    "Farm Profit": {"type": "video", "path": outputs_path("side_by_side_farm_profit.mp4")},
    "Livestock Count": {"type": "video", "path": outputs_path("side_by_side_livestock_count.mp4")},
    "Wheat Production": {"type": "video", "path": outputs_path("side_by_side_wheat_production.mp4")},
    "Suicide Rates": {
        "type": "image",
        "left": outputs_path("suicide_rates_by_remoteness_static.png"),
        "right": outputs_path("suicide_rates_pictogram_2004.png"),
    }
}
st.markdown("<h1 style='text-align: center;'>Select a Visualisation</h1>", unsafe_allow_html=True)
choice = st.selectbox("Choose a metric to display:", list(options.keys()))

# Dynamic text for bottom left
bottom_texts = {
    "Farm Profit": """Water availability is closely related to farm profits.
\n Severe droughts increase production costs & decrease farm output, harming farm profits (Sheng & Xu, 2019); likewise heavy rainfall can reduce crop quality, resulting in decreased profits (Reserve Bank of Australia, 2012). 
\n This visualisation compares soil moisture anomalies (water availability) and the percentage change in farm profits compared to a 3-year average.
\n A 3-year average was used to smooth volatility and better represent the long-term effects of water availability on farm profits.
\n Severe drought years such as 2002 and 2003 saw sharp decreases in farm profits across Australia. Similarly, 2011’s high soil moisture, caused by above-average precipitation and flooding, saw a decrease in farm profits across much of the country.
\n The effect of water availability on farm profits is complex, varying significantly region to region and by production type (e.g. livestock, broadacre, etc.) (Hughes et al., 2023).
\n **Readers are encouraged to pause the visualisation to examine specific years.**
""",
    "Livestock Count": """Water availability is closely related to livestock count.
\n In dry years, farmers typically increase the number of livestock sold. Additionally, more livestock die, and birth rates decrease. Reduced output from broadacre farms also increases the cost of stock feed, meaning farmers are able to support less livestock. Increased livestock sales can offset the effects of drought on farm profits in the short-term, but long-term farm profits decrease (Hughes et al., 2023). 
\n This visualisation compares soil moisture anomalies (water availability) and the percentage change in livestock count compared to a 3-year average.
\n A 3-year average was used to smooth volatility and better represent the long-term effects of water availability on livestock count.
\n Severe drought years such as 2002 and 2003 saw decreases in livestock count across most of Australia – particularly in the South. Years with high water availability such as 2011 saw widespread growth in livestock count.
\n The factors affecting livestock count are complex, however a strong relationship between water availability and livestock count can be observed in this visualisation.
\n **Readers are encouraged to pause the visualisation to examine specific years.**
""",
    "Wheat Production": """Wheat production is closely related to water availability.
\n In dry years, Australia’s wheat production can halve, due to less area planted and lower crop yields (Heberger, 2012) (Hughes et al., 2023). Above-average water availability increases wheat production but can decrease crop quality, leading to lower farm profits (Reserve Bank of Australia, 2012).
\n This visualisation compares soil moisture anomalies (water availability) and the percentage change in wheat production (tonnes) compared to a 3-year average.
\n A 3-year average was used to smooth volatility and better represent the long-term effects of water availability on wheat production.
\n Severe drought years such as 2002 and 2003 saw widespread reductions in wheat production; wet years such as 2010 and 2011 saw widespread increases in wheat production.
\n While the factors affecting wheat production are complex and influenced by global markets, the relationship between water availability and wheat production is strong.
\n **Readers are encouraged to pause the visualisation to examine specific years.**
""",
    "Suicide Rates": """Suicide rates amongst farmers are 59% higher than the general population (Norco, 2023).
\n In times of drought, farmer suicide rates increase dramatically. During the Millenium Drought, a month of ‘extreme’ drought in the previous 12 months was correlated with a 32% increase in the suicide rate (in the Murray-Darling basin) (Life in Mind, 2023).
\n Unfortunately, suicide data is only provided at very high spatial resolution for the general public, limiting researchers ability to study the effect of water availability on suicide rates.
\n A promising solution to this problem is Bayesian modelling which would allow wider access to low spatial resolution health data while protecting confidentiality (Hogg, 2025).
\n These visualisations highlight the stark contrast between suicide rates in remote and urban/regional areas. 
\n Farmers have challenging and volatile lives – more research should be done into the effects of water availability on their health.
"""
}

# Display videos (if suicide rates, display the static visualisations side-by-side)
lower_col1, lower_col2 = st.columns([3,1], vertical_alignment="center")
with lower_col1:
    if choice == "Suicide Rates":
        col1, col2 = st.columns(2)
        with col1:
            img_left = Image.open(options[choice]["left"])
            img_left = img_left.resize((700, 400))
            st.image(img_left, caption="Suicide Rates by Remoteness", use_container_width=True)
        with col2:
            img_right = Image.open(options[choice]["right"])
            img_right = img_right.resize((800, 450))
            st.image(img_right, caption="Suicide Rates Pictogram", use_container_width=True)
    else:
        st.video(str(options[choice]["path"]))
with lower_col2:
    st.write(bottom_texts[choice])

st.markdown("---")

st.markdown("###### _References_")
st.markdown(""" Bureau of Meteorology. (2025). Previous Droughts. Bom.gov.au. https://www.bom.gov.au/climate/drought/knowledge-centre/previous-droughts.shtml

Heberger, M. (2012). Australia’s Millennium Drought: Impacts and Responses. The World’s Water. https://doi.org/10.5822/978-1-59726-228-6_5

Hogg, J. (2025, September 9). Bayesian modelling with the Department of Health Western Australia. From Campus to Collaboration; Queensland University of Technology. https://qut.pressbooks.pub/from-campus-to-collaboration/chapter/bayesian-modelling-with-the-department-of-health-western-australia/

Hughes, N., Galeano, D., & Hatfield-Dodds, S. (2023). The effects of drought and climate variability on Australian farms - Department of Agriculture. Www.agriculture.gov.au. https://www.agriculture.gov.au/abares/products/insights/effects-of-drought-and-climate-variability-on-Australian-farms#abares-research-on-climate-variability

Kelly, S., Cunningham, R., Plant, R., & Maras, K. (2019). Water scarcity risk for Australian farms and the implications for the financial sector. Institute for Sustainable Futures, University of Technology Sydney. https://www.uts.edu.au/globalassets/sites/default/files/2019-06/water-risk-report---jan-2019-web.pdf

Life In Mind. (2023). Life in Mind. https://lifeinmind.org.au/research/research-updates/extreme-drought-and-increasing-temperature-contribute-to-suicide-rates-in-rural-areas

National Centers for Environmental Information. (2025). Did You Know? | National Centers for Environmental Information (NCEI). Www.ncei.noaa.gov. https://www.ncei.noaa.gov/access/monitoring/dyk/drought-definition

Norco. (2023). National Farmer Wellbeing Report. https://norcofoods.com.au/wp-content/uploads/2023/03/1212_Farmer-wellbeing-report_Navigation_FINAL.pdf

Reserve Bank of Australia. (2012). Box D: Conditions in the Farm Sector | Statement on Monetary Policy – May 2012. Statement on Monetary Policy, May. https://www.rba.gov.au/publications/smp/2012/may/box-d.html

Sheng, Y., & Xu, X. (2019). The productivity impact of climate change: Evidence from Australia’s Millennium drought. Economic Modelling, 76, 182–191. https://doi.org/10.1016/j.econmod.2018.07.031

""")
