# pip install pandas plotly country_converter requests
import re
import pandas as pd
import plotly.express as px
import requests
import country_converter as coco

# 1) Cargar datos
df = pd.read_csv("universal_top_spotify_songs.csv")
df.columns = [c.strip().lower() for c in df.columns]

country_col = "country"
valence_col = "valence"
position_col = "daily_rank"
date_col = "snapshot_date"

# 2) Filtrar última fecha por país + top 50
df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
df = df[df[date_col] == df.groupby(country_col)[date_col].transform("max")]
df[position_col] = pd.to_numeric(df[position_col], errors="coerce")
df_top50 = df[df[position_col] <= 50]

# 3) Promedio de valence por país
valence_avg = (df_top50.groupby(country_col)[valence_col]
               .mean().reset_index().rename(columns={valence_col: "positividad promedio"}))

# 4) Obtener top 1 por país
df_top1 = df[df[position_col] == 1][[country_col, "name", "artists"]].copy()


# --- Selección por país: track más cercano al valence promedio, con preview iTunes ---

# A) Prep: valence promedio + Top 50 del último día
# (ya lo tienes como valence_avg y df_top50)

# Normalizar país y códigos
def clean_name(s):
    if not isinstance(s, str): return s
    return re.sub(r"[^\w\s\-\&\.,'’]", "", s).strip()

df_top50[country_col] = df_top50[country_col].map(clean_name)
cc = coco.CountryConverter()
valence_avg["iso3"] = cc.convert(valence_avg[country_col].tolist(), to="ISO3", not_found=None)
df_top50["iso3"] = cc.convert(df_top50[country_col].tolist(), to="ISO3", not_found=None)
df_top50["iso2"] = cc.convert(df_top50["iso3"].tolist(), to="ISO2", not_found=None)

# Map del promedio por iso3
avg_map = dict(zip(valence_avg["iso3"], valence_avg["positividad promedio"]))

# B) Función para pedir preview en iTunes
import requests
def itunes_preview(track, artists, iso2="US"):
    q = f"{track} {artists}".strip()
    params = {"term": q, "entity": "song", "limit": 1, "country": (iso2 or "US")}
    try:
        r = requests.get("https://itunes.apple.com/search", params=params, timeout=8)
        r.raise_for_status()
        res = r.json().get("results", [])
        if res:
            x = res[0]
            return x.get("previewUrl"), x.get("trackViewUrl")
    except Exception:
        pass
    return None, None

# C) Para cada país, ordena por |valence - promedio| y toma el primero que tenga preview
rows = []
for iso3, g in df_top50.dropna(subset=["iso3"]).groupby("iso3"):
    avg = avg_map.get(iso3)
    if avg is None: 
        continue
    g = g.assign(dist=(g[valence_col] - avg).abs()).sort_values("dist")
    # intenta en orden hasta encontrar preview
    found = None
    for _, r in g.iterrows():
        purl, link = itunes_preview(r["name"], r["artists"], r.get("iso2"))
        if purl:
            found = {
                "iso3": iso3,
                "preview_url": purl,
                "link": link,
                "track": r["name"],
                "artists": r["artists"]
            }
            break
    if found:
        rows.append(found)

itunes_df = pd.DataFrame(rows)

# D) Merge para el mapa (solo países con preview)
plot_df = valence_avg.merge(itunes_df, on="iso3", how="inner")

# 8) Crear mapa
fig = px.choropleth(
    plot_df,
    locations="iso3",
    color="positividad promedio",
    color_continuous_scale=px.colors.sequential.Viridis,
    title="Positividad promedio de las 50 canciones más escuchadas por país."
)

fig.update_traces(
    hovertemplate="<b>%{location}</b><br>Valence: %{z:.2f}<br>%{customdata[2]} — %{customdata[3]}<extra></extra>",
    customdata=plot_df[["preview_url", "link", "track", "artists"]].values
)

html = fig.to_html(include_plotlyjs="cdn")
inject = """
<div id="player" style="position:fixed;left:20px;bottom:20px;background:#fff;padding:10px;border:1px solid #ddd;border-radius:8px">
  <audio id="aud" controls></audio>
  <div id="meta" style="font:14px/1.2 sans-serif;margin-top:6px;color:#333"></div>
</div>
<script>
  const aud = document.getElementById('aud');
  const meta = document.getElementById('meta');
  const gd = document.querySelector('div.js-plotly-plot');
  gd.on('plotly_hover', (ev) => {
    const [url, link, track, artists] = ev.points[0].customdata || [];
    meta.innerHTML = track ? (track + ' — ' + artists + (link ? ' · <a href="'+link+'" target="_blank">Apple Music</a>' : '')) : '';
    aud.src = url || "";
  });
  gd.on('plotly_click', (ev) => {
    const [url, link] = ev.points[0].customdata || [];
    if (url) { aud.play().catch(()=>{}); }
    else if (link) { window.open(link, "_blank"); }
  });
</script>
"""
with open("mapa_valence_preview.html","w",encoding="utf-8") as f:
    f.write(html.replace("</body>", inject + "</body>"))

print("Listo: se generó mapa_valence_preview.html con previews de Apple Music.")