import streamlit as st
import pandas as pd
import pydeck as pdk
import time

st.set_page_config(page_title="Tráfico Zona Metropolitana", layout="wide")

st.title("Mapa de calor del tráfico – Zona Metropolitana")
st.write("Proyecto de programación – Regina López Corona")

@st.cache_data
def load_data():
    df = pd.read_csv("https://drive.google.com/uc?id=1BSbpXl5ksFzUbyBTKqyTIFXwnUonRyaY", encoding="ISO-8859-1")
    df["Coordx"] = (
        df["Coordx"].astype(str).str.replace(",", "", regex=False)
    )
    df["Coordy"] = (
        df["Coordy"].astype(str).str.replace(",", "", regex=False)
    )

    df["Coordx"] = pd.to_numeric(df["Coordx"], errors="coerce")
    df["Coordy"] = pd.to_numeric(df["Coordy"], errors="coerce")
    df = df.dropna(subset=["Coordx", "Coordy"])

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["weight"] = pd.to_numeric(
        df["exponential_color_weighting"], errors="coerce"
    ).fillna(0)

    return df


df = load_data()

center_lat = df["Coordy"].mean()
center_lon = df["Coordx"].mean()

st.sidebar.header("Controles de animación")

min_date = df["timestamp"].dt.date.min()
max_date = df["timestamp"].dt.date.max()

fecha = st.sidebar.date_input(
    "Elige un día para ver el tráfico",
    value=min_date,
    min_value=min_date,
    max_value=max_date,
)

df_dia = df[df["timestamp"].dt.date == fecha].copy()

if df_dia.empty:
    st.error("No hay datos para ese día.")
    st.stop()

df_dia["hora"] = df_dia["timestamp"].dt.floor("H")
horas_unicas = sorted(df_dia["hora"].unique())

st.sidebar.write(f"Hay **{len(horas_unicas)}** momentos de tiempo este día.")

velocidad = st.sidebar.slider(
    "Velocidad de animación (segundos entre cuadros)",
    min_value=0.1, max_value=2.0, value=0.5, step=0.1,
)

iniciar = st.sidebar.button("Iniciar animación")


map_placeholder = st.empty()
texto_hora = st.empty()

def mostrar_mapa(data_frame):
    layer = pdk.Layer(
        "HeatmapLayer",
        data=data_frame,
        get_position=["Coordx", "Coordy"],
        get_weight="weight",
        radiusPixels=60,
    )

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=11,
        pitch=45,
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "Tráfico: {diffuse_logic_traffic}"},
    )

    map_placeholder.pydeck_chart(deck)
if not iniciar:
    ultima_hora = horas_unicas[-1]
    df_ultima = df_dia[df_dia["hora"] == ultima_hora]
    texto_hora.markdown(f"Mostrando: **{ultima_hora}**")
    mostrar_mapa(df_ultima)
    st.info("Da clic en 'Iniciar animación' en la barra lateral para ver el tráfico moverse.")
else:
   
    for h in horas_unicas:
        frame = df_dia[df_dia["hora"] == h]

        if frame.empty:
            continue

        texto_hora.markdown(f"### Hora mostrada: **{h}**")
        mostrar_mapa(frame)

        time.sleep(velocidad)
