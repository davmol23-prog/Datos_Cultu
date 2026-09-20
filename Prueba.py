import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch

# ─────────────────────────────────────────────
# 1. CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(page_title="Campogramas", layout="wide", page_icon="🦁")

# ─────────────────────────────────────────────
# 2. CONSTANTES
# ─────────────────────────────────────────────
LOGO_URL = "https://cdn.resfu.com/img_data/equipos/877.png?size=120x&lossy=1"

st.title("⚽ Análisis de tiros")

# Colores por tipo de disparo (del notebook del curso)
SHOT_COLORS = {
    'Gol':         '#2ecc71',
    'Parada':      '#3498db',
    'Fuera':       '#e74c3c',
    'Bloqueado':   '#f39c12',
    'otros':       '#7f8c8d',
}

# _________
# 2.1 Diccionarios
# _____
traducciones_resultado = {
    "Goal": "Gol",
    "Miss": "Fuera",
    "Saved": "Parada",
    "Blocked": "Bloqueado"
}

traducciones_situacion = {
    "OpenPlay": "Juego abierto",
    "SetPiece": "ABP",
    "CounterAttack": "Contraataque",
    "Penalty": "Penalti"
}

traducciones_parte_cuerpo = {
    "RightFoot": "Pie derecho",
    "LeftFoot": "Pie izquierdo",
    "Head": "Cabeza",
    "Other": "Otra"
}


# ============================================================
# 3. SIDEBAR - FILTROS
# ============================================================

with st.sidebar:

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.image(LOGO_URL, width=90)

    st.markdown(
        "<h3 style='text-align:center;'>Cultural y Deportiva Leonesa</h3>",
        unsafe_allow_html=True
    )

    st.divider()

    st.title("📂 Datos")

    df = pd.read_csv("Tiros.csv")

    equipo_seleccionado = st.selectbox(
        "Equipo",
        ["Todos"] + sorted(df["equipo"].dropna().unique().tolist())
    )

    jugador_seleccionado = st.selectbox(
        "Jugador",
        ["Todos"] + sorted(df["jugador"].dropna().unique().tolist())
    )

    st.markdown("""
    <style>

    [data-testid="stSidebar"] {
        background-color: #C71901;
    }

    /* Todo el texto del sidebar */
    [data-testid="stSidebar"] * {
        color: #CBD5E1;
    }

    </style>
    """, unsafe_allow_html=True)

    st.divider()
    st.caption("David Molina - Analista de Datos")
    st.caption("Powered by Sofascore")

# ============================================================
# 4. FILTROS
# ============================================================

# ============================================================
# APLICAR FILTROS
# ============================================================

df_filtrado = df.copy()


if equipo_seleccionado != "Todos":

    df_filtrado = df_filtrado[
        df_filtrado["equipo"].astype(str)
        == equipo_seleccionado
    ]


if jugador_seleccionado != "Todos":

    df_filtrado = df_filtrado[
        df_filtrado["jugador"].astype(str)
        == jugador_seleccionado
    ]


# _____
# Columnas
# ____
col_metricas, col_campo = st.columns([1, 2])


# ============================================================
# 5. MÉTRICAS
# ============================================================

numero_tiros = len(df_filtrado)

xg_total = df_filtrado["xG"].sum()

xgot_total = df_filtrado["xGOT"].sum()

# Intentamos identificar los goles
goles = (
    df_filtrado["resultado"]
    .astype(str)
    .str.lower()
    .str.contains("goal")
    .sum()
)

diferencia_goles_xg = goles - xg_total

with col_metricas:

    st.subheader("🎯 Métricas")

    col1, col2, col3 = st.columns(3)


    col1.metric(
        "Tiros",
        numero_tiros
    )

    col2.metric(
        "Goles",
        goles,
        delta=round(diferencia_goles_xg, 2)
    )

    col3.metric(
        "xG",
        f"{xg_total:.2f}"
    )


# ____________
# 6. Dibujar campo
# _________

with col_campo:
    st.subheader("Campograma de tiros")

    df_filtrado["x_plot"] = 100 - df_filtrado["x"]
    df_filtrado["y_plot"] = 100 - df_filtrado["y"]

    # Crear figura
    fig, ax = plt.subplots(
        figsize=(12, 8)
    )

    pitch = VerticalPitch(
        pitch_type='opta', half=True,
        pitch_color='#2d6a4f', line_color='white', linewidth=1,
        stripe=True, stripe_color='#2d6a4f',
        goal_type='box', pad_bottom=-5
    )

    pitch.draw(ax=ax)

    # Leyenda
    legend_handles = [ax.plot([], marker='o', ls='', color=c)[0] for c in SHOT_COLORS.values()]
    ax.legend(legend_handles, list(SHOT_COLORS.keys()),
                loc='lower right', fontsize=8, facecolor='#1b4332', labelcolor='white', framealpha=0.6)



# ============================================================
# DATOS PARA REPRESENTAR
# ============================================================

df_plot = df_filtrado.dropna(
    subset=["x_plot", "y_plot"]
).copy()


# ============================================================
# COLORES SEGÚN RESULTADO
# ============================================================

def color_resultado(resultado):

    resultado = str(resultado).lower()

    if "goal" in resultado:
        return "#2ecc71"

    elif (
        "save" in resultado
        or "on target" in resultado
    ):
        return "#3498db"

    elif (
        "miss" in resultado
        or "off target" in resultado
    ):
        return "#e74c3c"

    elif "block" in resultado:
        return "#f39c12"

    else:
        return "#7f8c8d"


df_plot["color"] = df_plot[
    "resultado"
].apply(color_resultado)


# ============================================================
# TAMAÑO SEGÚN xG
# ============================================================

# Tamaño mínimo para que los tiros con xG bajo
# sigan siendo visibles

df_plot["size"] = (
    df_plot["xG"] * 300
)
#.clip(lower=40)


# ============================================================
# DIBUJAR TIROS
# ============================================================

for _, tiro in df_plot.iterrows():

    pitch.scatter(
        tiro["x_plot"],
        tiro["y_plot"],
        ax=ax,
        s=tiro["size"],
        color=tiro["color"],
        marker='o',
        edgecolors="white",
        linewidth=0.5,
        alpha=0.85,
        zorder=3,
    )


# ============================================================
# MOSTRAR CAMPO
# ============================================================

with col_campo:
    st.pyplot(
    fig,
    use_container_width=True
    )