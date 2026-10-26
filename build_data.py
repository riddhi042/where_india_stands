"""Build data/panel.csv from REAL World Bank WDI indicator files.

Source: github.com/datasets/world-development-indicators (a mirror of World Bank WDI)
        github.com/datasets/country-codes (ISO country list + regions; used to drop aggregates like 'World')
Usage:  python build_data.py <path-to-wdi-repo/indicators> <path-to-country-codes.csv>
"""
import sys
import pandas as pd

IND_DIR, CC = sys.argv[1], sys.argv[2]
CODES = {
    "ny.gdp.pcap.pp.cd": "GDP per capita (PPP, current intl $)",
    "sp.dyn.le00.in": "Life expectancy (years)",
    "se.sec.enrr": "Secondary school enrolment (% gross)",
    "sl.uem.totl.zs": "Unemployment (% of labour force)",
    "fp.cpi.totl.zg": "Inflation, consumer prices (% annual)",
    "it.cel.sets.p2": "Mobile subscriptions (per 100 people)",
    "eg.elc.accs.zs": "Access to electricity (% of population)",
    "sp.dyn.imrt.in": "Infant mortality (per 1,000 live births)",
}
cc = pd.read_csv(CC, keep_default_na=False)
cc = cc[cc["ISO3166-1-Alpha-3"] != ""]
meta = pd.DataFrame({
    "iso3": cc["ISO3166-1-Alpha-3"],
    "region": cc["Sub-region Name"].replace("", "Other"),
})
panel = None
for code, label in CODES.items():
    d = pd.read_csv(f"{IND_DIR}/{code}/data.csv")
    d = d.rename(columns={"Country Code": "iso3", "Year": "year", "Value": label})[["iso3", "year", label]]
    d = d[d["year"] >= 2000]
    panel = d if panel is None else panel.merge(d, on=["iso3", "year"], how="outer")
names = pd.read_csv(f"{IND_DIR}/sp.dyn.le00.in/data.csv")[["Country Code", "Country Name"]].drop_duplicates()
names.columns = ["iso3", "country"]
panel = panel.merge(meta, on="iso3", how="inner").merge(names, on="iso3", how="left")
panel["country"] = panel["country"].fillna(panel["iso3"])
panel = panel.sort_values(["iso3", "year"])
panel.to_csv("data/panel.csv", index=False)
print(panel.shape, panel["iso3"].nunique(), "countries", panel["year"].min(), "-", panel["year"].max())
ind = panel[panel.iso3 == "IND"].set_index("year")
print(ind.loc[[2000, 2010, 2020, 2022, 2023, 2024], [c for c in panel.columns if c not in ("iso3","year","region","country")]].round(1).T.to_string())
