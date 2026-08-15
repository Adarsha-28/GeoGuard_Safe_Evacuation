from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from geopy.distance import geodesic
from streamlit_folium import st_folium
import requests

import folium


CITY_NAME = "Chennai"
DATA_PATH = Path("data/chennai_places.csv")
MAP_CENTER = (13.0827, 80.2707)

RISK_COLORS = {
    "Safe": "#22C55E",
    "Moderate": "#EAB308",
    "High": "#F97316",
    "Severe": "#EF4444",
}
RISK_ORDER = {"Safe": 0, "Moderate": 1, "High": 2, "Severe": 3}

SHELTERS = pd.DataFrame(
    [
        {"name": "Chennai Trade Centre Relief Camp", "latitude": 13.0300, "longitude": 80.1700},
        {"name": "YMCA Nandanam Shelter", "latitude": 13.0308, "longitude": 80.2425},
        {"name": "Anna University Emergency Hall", "latitude": 13.0109, "longitude": 80.2337},
        {"name": "Rajiv Gandhi Govt. Hospital Shelter", "latitude": 13.0825, "longitude": 80.2769},
    ]
)

EMERGENCY_CONTACTS = [
    ("State Disaster Helpline", "1070"),
    ("District Emergency Ops", "1077"),
    ("Fire and Rescue", "101"),
    ("Ambulance", "108"),
]


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #0F172A; color: #E5E7EB; }
        [data-testid="stSidebar"] { background: #111827; border-right: 1px solid #1F2937; }
        .card {
            background: #111827;
            border: 1px solid #1F2937;
            border-radius: 16px;
            padding: 14px;
            margin-bottom: 10px;
        }
        .metric-title { color: #93C5FD; font-size: 0.8rem; margin: 0; }
        .metric-value { color: #F9FAFB; font-size: 1.2rem; font-weight: 700; margin: 0; }
        .risk-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 700;
            color: #0B0F19;
        }
        .header-wrap {
            background: linear-gradient(135deg, #111827 0%, #1F2937 100%);
            border: 1px solid #374151;
            border-radius: 18px;
            padding: 16px 18px;
            margin-bottom: 14px;
        }
        .panel-title { color: #93C5FD; font-size: 1rem; font-weight: 700; margin-bottom: 8px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_places(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"place", "latitude", "longitude", "risk_level"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in CSV: {sorted(missing)}")
    return df


@st.cache_data
def build_zone_metrics(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        seed = abs(hash(row["place"])) % 10000
        rng = np.random.default_rng(seed)
        rainfall = float(np.round(rng.uniform(35, 220), 1))
        water_level = float(np.round(rng.uniform(1.1, 5.3), 2))
        flood_prob = float(np.round(rng.uniform(10, 95), 1))
        alert = "Active" if row["risk_level"] in {"High", "Severe"} else "Normal"
        rows.append(
            {
                "place": row["place"],
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "risk_level": row["risk_level"],
                "rainfall_mm": rainfall,
                "water_level_m": water_level,
                "flood_probability": flood_prob,
                "alert_status": alert,
            }
        )
    return pd.DataFrame(rows)


def nearest_zone(df: pd.DataFrame, lat: float, lon: float) -> pd.Series:
    distances = df.apply(
        lambda r: geodesic((lat, lon), (r["latitude"], r["longitude"])).km,
        axis=1,
    )
    idx = distances.idxmin()
    zone = df.loc[idx].copy()
    zone["distance_km"] = float(distances.loc[idx])
    return zone


def nearest_shelters(lat: float, lon: float, count: int = 3) -> pd.DataFrame:
    tmp = SHELTERS.copy()
    tmp["distance_km"] = tmp.apply(
        lambda r: geodesic((lat, lon), (r["latitude"], r["longitude"])).km,
        axis=1,
    )
    return tmp.sort_values("distance_km").head(count)


@st.cache_data(ttl=900)
def detect_location_ip() -> tuple[float, float, str]:
    try:
        resp = requests.get("https://ipapi.co/json/", timeout=5)
        resp.raise_for_status()
        payload = resp.json()
        lat = float(payload.get("latitude"))
        lon = float(payload.get("longitude"))
        city = str(payload.get("city", "Unknown"))
        return lat, lon, city
    except Exception:
        return MAP_CENTER[0], MAP_CENTER[1], CITY_NAME


def build_map(df: pd.DataFrame, selected_place: str | None, route: tuple[tuple[float, float], tuple[float, float]] | None):
    fmap = folium.Map(location=MAP_CENTER, zoom_start=11, tiles="CartoDB dark_matter", control_scale=True)

    for _, zone in df.iterrows():
        color = RISK_COLORS.get(zone["risk_level"], "#9CA3AF")
        popup = (
            f"<b>{zone['place']}</b><br>"
            f"Risk: {zone['risk_level']}<br>"
            f"Predicted rainfall: {zone['rainfall_mm']} mm<br>"
            f"Water level: {zone['water_level_m']} m"
        )
        radius = 14 if zone["place"] == selected_place else 10
        folium.CircleMarker(
            location=[zone["latitude"], zone["longitude"]],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,
            tooltip=zone["place"],
            popup=popup,
        ).add_to(fmap)

    for _, s in SHELTERS.iterrows():
        folium.Marker(
            location=[s["latitude"], s["longitude"]],
            tooltip=s["name"],
            icon=folium.Icon(color="green", icon="home", prefix="fa"),
        ).add_to(fmap)

    if route:
        src, dst = route
        folium.PolyLine(
            locations=[list(src), list(dst)],
            weight=6,
            color="#22C55E",
            opacity=0.9,
            tooltip="Safest evacuation path",
        ).add_to(fmap)

    return fmap


def risk_badge(risk: str) -> str:
    color = RISK_COLORS.get(risk, "#9CA3AF")
    return f'<span class="risk-badge" style="background:{color};">{risk}</span>'


def sidebar_cards(df: pd.DataFrame, selected: pd.Series | None) -> None:
    zone = selected if selected is not None else df.sort_values("flood_probability", ascending=False).iloc[0]
    st.sidebar.markdown("### Left Panel")
    st.sidebar.markdown(
        f"""
        <div class="card">
            <p class="metric-title">Rainfall prediction</p>
            <p class="metric-value">{zone["rainfall_mm"]} mm</p>
        </div>
        <div class="card">
            <p class="metric-title">River water level</p>
            <p class="metric-value">{zone["water_level_m"]} m</p>
        </div>
        <div class="card">
            <p class="metric-title">Flood probability</p>
            <p class="metric-value">{zone["flood_probability"]}%</p>
        </div>
        <div class="card">
            <p class="metric-title">Emergency alert status</p>
            <p class="metric-value">{zone["alert_status"]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chart_section(df: pd.DataFrame) -> None:
    st.markdown("### Forecast Analytics")
    c1, c2, c3 = st.columns(3)

    fig_rain = go.Figure(go.Bar(x=df["place"], y=df["rainfall_mm"], marker_color="#38BDF8"))
    fig_rain.update_layout(
        title="Rainfall Prediction (mm)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111827",
        font_color="#E5E7EB",
        margin=dict(l=20, r=10, t=40, b=20),
    )
    c1.plotly_chart(fig_rain, use_container_width=True)

    fig_water = go.Figure(go.Scatter(x=df["place"], y=df["water_level_m"], mode="lines+markers", line=dict(color="#22D3EE", width=3)))
    fig_water.update_layout(
        title="Water Level Trend (m)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111827",
        font_color="#E5E7EB",
        margin=dict(l=20, r=10, t=40, b=20),
    )
    c2.plotly_chart(fig_water, use_container_width=True)

    color_scale = [RISK_COLORS[r] for r in df["risk_level"]]
    fig_prob = go.Figure(go.Bar(x=df["place"], y=df["flood_probability"], marker_color=color_scale))
    fig_prob.update_layout(
        title="Flood Probability (%)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111827",
        font_color="#E5E7EB",
        margin=dict(l=20, r=10, t=40, b=20),
    )
    c3.plotly_chart(fig_prob, use_container_width=True)


def resolve_selected_zone(df: pd.DataFrame, map_state: dict, fallback_name: str) -> pd.Series:
    selected = df[df["place"] == fallback_name].iloc[0]
    clicked = map_state.get("last_object_clicked")
    if clicked and "lat" in clicked and "lng" in clicked:
        selected = nearest_zone(df, clicked["lat"], clicked["lng"])
    return selected


def main() -> None:
    st.set_page_config(page_title="DisasterMind - Chennai", page_icon="D", layout="wide")
    apply_theme()

    raw_places = load_places(DATA_PATH)
    zones = build_zone_metrics(raw_places)

    city_risk = max(zones["risk_level"], key=lambda r: RISK_ORDER.get(r, -1))
    now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    st.markdown(
        f"""
        <div class="header-wrap">
            <div style="font-size:1.6rem;font-weight:800;">DisasterMind - Hyperlocal Disaster Intelligence</div>
            <div style="margin-top:8px;">
                <b>City:</b> {CITY_NAME} &nbsp; | &nbsp;
                <b>Current Risk:</b> {risk_badge(city_risk)} &nbsp; | &nbsp;
                <b>Last Updated:</b> {now_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    default_zone_name = zones.sort_values("flood_probability", ascending=False).iloc[0]["place"]
    zone_choice = st.selectbox("Select Chennai Zone", zones["place"].tolist(), index=zones["place"].tolist().index(default_zone_name))

    map_col, right_col = st.columns([2.6, 1.2], gap="large")
    map_state_holder = {}

    with map_col:
        st.markdown("### Chennai Risk Map")
        fmap = build_map(zones, selected_place=zone_choice, route=None)
        map_state_holder = st_folium(fmap, width=None, height=520, returned_objects=["last_object_clicked"])

    selected_zone = resolve_selected_zone(zones, map_state_holder or {}, zone_choice)
    sidebar_cards(zones, selected_zone)

    evacuation_route = None
    nearest_for_selected = nearest_shelters(selected_zone["latitude"], selected_zone["longitude"], count=3)
    if selected_zone["risk_level"] in {"High", "Severe"}:
        best = nearest_for_selected.iloc[0]
        evacuation_route = (
            (selected_zone["latitude"], selected_zone["longitude"]),
            (best["latitude"], best["longitude"]),
        )

    with map_col:
        if evacuation_route:
            st.warning(f"High-risk zone selected: {selected_zone['place']}. Displaying safest evacuation path.")
            fmap2 = build_map(zones, selected_place=selected_zone["place"], route=evacuation_route)
            st_folium(fmap2, width=None, height=520, returned_objects=[])

        st.markdown(
            f"""
            <div class="card">
                <div class="panel-title">Selected Zone</div>
                <b>Zone:</b> {selected_zone['place']}<br>
                <b>Flood Risk:</b> {risk_badge(selected_zone['risk_level'])}<br>
                <b>Predicted Rainfall:</b> {selected_zone['rainfall_mm']} mm<br>
                <b>Water Level:</b> {selected_zone['water_level_m']} m
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        st.markdown("### Emergency Panel")
        st.markdown('<div class="card"><div class="panel-title">Nearest Relief Shelters</div>', unsafe_allow_html=True)
        for _, s in nearest_for_selected.iterrows():
            st.markdown(f"- {s['name']} ({s['distance_km']:.2f} km)")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="panel-title">Emergency Contacts</div>', unsafe_allow_html=True)
        for label, number in EMERGENCY_CONTACTS:
            st.markdown(f"- {label}: `{number}`")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="panel-title">Disaster Alerts</div>', unsafe_allow_html=True)
        if city_risk in {"High", "Severe"}:
            st.error("Active flood watch: Avoid low-lying roads and follow official advisories.")
        elif city_risk == "Moderate":
            st.warning("Moderate risk pockets identified. Keep emergency kit ready.")
        else:
            st.success("No city-wide severe alerts at the moment.")
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Check My Location Risk", use_container_width=True):
            lat, lon, detected_city = detect_location_ip()
            user_point = nearest_zone(zones, lat, lon)
            st.info(
                f"Approximate location risk check complete.\n\n"
                f"Detected location: {detected_city} ({lat:.4f}, {lon:.4f})\n"
                f"Nearest zone: {user_point['place']}\n"
                f"Risk: {user_point['risk_level']}\n"
                f"Flood probability: {user_point['flood_probability']}%"
            )
            st.caption("IP-based location detection is approximate.")

    chart_section(zones)


if __name__ == "__main__":
    main()
