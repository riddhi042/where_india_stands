# Where India Stands

**Live app:** https://whereindiastands.streamlit.app

An interactive research dashboard on **real World Bank World Development Indicators (WDI)** data
(215 countries, 2000-2025). It benchmarks India against peer countries and asks what actually goes along with prosperity.

## What it does
| Tab | Question it answers |
|---|---|
| India vs peers | How has India moved over time compared with China, Bangladesh, Viet Nam, Brazil, Pakistan, Indonesia? Where does it rank today? |
| Explorer | How do any two indicators relate across countries? (scatter + trendline, India highlighted) |
| What predicts income? | Cross-country OLS (robust SEs): which of health, schooling, connectivity and electricity track GDP per capita? Is India above or below the model? |
| Country clusters | Which countries have a development profile similar to India's? (k-means) |
| India trend | Where does a simple linear trend put India's indicators by 2035? |

**Indicators:** GDP per capita (PPP), life expectancy, secondary school enrolment, unemployment, inflation,
mobile subscriptions, access to electricity, infant mortality.

## Key findings
Snapshot = latest value per country since 2015.

1. **India has grown fast but is still in the lower half on income.** GDP per capita (PPP) rose about 5.3x between
   2000 and 2024, from roughly $2,090 to $11,160. That is still above only about a third of the 199 countries with data.
   China is at about $27,100 and Viet Nam at about $16,400, from similar starting points in 2000.
2. **The biggest success is child survival and basic access.** Infant mortality fell from 66 to 23 per 1,000 live births
   (2000-2024) and electricity access rose from 60% to 99.5%. India now has lower infant mortality than about 69% of countries
   with data, though it is still far above China (4.1) and Viet Nam (12.0).
3. **Infant mortality and schooling are the strongest correlates of income.** In a cross-country regression of
   log GDP per capita (174 countries, R² = 0.74), each extra infant death per 1,000 births goes with roughly 3.6% lower income
   and each extra point of secondary enrolment with roughly 1% higher income (both p < 0.01). Mobile subscriptions and electricity
   access are not statistically significant once the others are included, since they are highly correlated with them.
4. **India sits below what its profile predicts.** The model predicts about $13,100 for India versus an actual $11,160,
   about 15% lower. This is a descriptive gap, not proof of underperformance. The model leaves out many factors such as
   institutions, industry structure and natural resources.

## Limitations
- Associations, not causal effects. Richer countries differ from poorer ones in many ways at once.
- Cross-country snapshots use the latest available year since 2015, so reference years differ slightly across countries.
- GDP is PPP in *current* international dollars, so compare countries within a year, not across decades.
- Some countries have no data for some indicators (e.g. American Samoa) and are excluded automatically.
- The India trend tab is a naive linear extrapolation, a baseline and not a forecast.

## Run locally
````
pip install -r requirements.txt
streamlit run app.py
````
Keep `data/panel.csv` next to `app.py`.

## Data
Built from World Bank WDI indicator files (mirror: github.com/datasets/world-development-indicators), with regional
aggregates removed using ISO country codes (github.com/datasets/country-codes). Rebuild with:
````
python build_data.py <wdi-repo>/indicators <country-codes.csv>
````
Original source: World Bank Open Data, https://data.worldbank.org
````
````

