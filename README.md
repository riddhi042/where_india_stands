# Where India Stands

Interactive research dashboard on **real World Bank World Development Indicators (WDI)** data (2000-2025, 215 countries):
India vs peer countries, a cross-country regression of income on health/education/connectivity, country clustering,
and a baseline trend projection.

## Run
```
pip install -r requirements.txt
streamlit run app.py
```
Keep the `data/` folder next to `app.py` - the dataset (`data/panel.csv`) is bundled.

## Indicators
GDP per capita (PPP), life expectancy, secondary school enrolment, unemployment, inflation,
mobile subscriptions, access to electricity, infant mortality.

## Rebuild the data
`build_data.py` assembles `data/panel.csv` from the World Bank WDI indicator files
(mirror: github.com/datasets/world-development-indicators) and drops regional aggregates using ISO country codes
(github.com/datasets/country-codes).
```
python build_data.py <wdi-repo>/indicators <country-codes.csv>
```

## Method notes
- Snapshot = latest non-missing value per country since 2015, so reference years differ slightly across countries.
- GDP is PPP in *current* international $: compare countries within a year, not across decades.
- Regressions and clusters describe association, not causation.

## Findings (fill in after exploring)
1. ...
2. ...
3. ...
