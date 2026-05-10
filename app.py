import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings("ignore")

# ---------------- CONFIGURACIÓN ----------------
st.set_page_config(
    page_title="Negative Equity Dashboard",
    page_icon="🏠",
    layout="wide"
)

# ---------------- CARGA DE DATOS ----------------
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_csv("NegativeEquity_2017Q1_Public.csv")
        return df
    except Exception as e:
        st.error(f"Error cargando archivo: {e}")
        return None

df = cargar_datos()

if df is None:
    st.stop()

# Detectar columnas trimestrales
quarters = [c for c in df.columns if len(c) == 6 and c[4] == "Q"]

# Filtrar datasets
nacional = df[df["RegionType"] == "Country"].copy()
estados = df[df["RegionType"] == "State"].copy()

# Métricas por estado
estados["pico"] = estados[quarters].max(axis=1)
estados["valor_2017"] = estados["2017Q1"]
estados["recuperacion"] = (
    (estados["pico"] - estados["valor_2017"]) / estados["pico"] * 100
).round(1)

# ---------------- SIDEBAR ----------------
st.sidebar.title("📌 Filtros")

estado_seleccionado = st.sidebar.selectbox(
    "Selecciona un estado",
    sorted(estados["RegionName"].tolist())
)

st.sidebar.markdown("---")
st.sidebar.info("""
**Dataset:** Zillow Research  
**Periodo:** 2011Q1 - 2017Q1  
**Herramienta:** Streamlit
""")

# ---------------- TITULO ----------------
st.title("🏠 Negative Equity en EE.UU.")
st.markdown("""
### Análisis del mercado inmobiliario estadounidense (2011 - 2017)

Este dashboard analiza la evolución de viviendas con **negative equity**
(propiedades cuyo valor es menor que la deuda hipotecaria).
""")

st.markdown("---")

# ---------------- KPIs DINÁMICOS ----------------
valores_nacional = [nacional[q].iloc[0] for q in quarters]

pico_valor = max(valores_nacional)
pico_idx = valores_nacional.index(pico_valor)

estado_max = estados.loc[estados["pico"].idxmax()]
estado_nombre = estado_max["RegionName"]
estado_valor = estado_max["pico"]

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Pico Nacional",
    f"{pico_valor:.1%}",
    quarters[pico_idx]
)

col2.metric(
    "Valor Final 2017Q1",
    f"{valores_nacional[-1]:.1%}"
)

col3.metric(
    "Estado Más Afectado",
    estado_nombre
)

col4.metric(
    "Peak Estatal",
    f"{estado_valor:.1%}"
)

st.markdown("---")

# ---------------- TENDENCIA NACIONAL ----------------
st.header("📈 Tendencia Nacional")

fig, ax = plt.subplots(figsize=(12,5))

ax.plot(
    range(len(quarters)),
    valores_nacional,
    color="steelblue",
    linewidth=3
)

ax.fill_between(
    range(len(quarters)),
    valores_nacional,
    alpha=0.2
)

ax.scatter(
    pico_idx,
    pico_valor,
    color="red",
    s=100
)

ax.annotate(
    f"Pico: {pico_valor:.1%}",
    xy=(pico_idx, pico_valor),
    xytext=(pico_idx+1, pico_valor+0.02),
    arrowprops=dict(arrowstyle="->")
)

posiciones = list(range(0, len(quarters), 4))
etiquetas_x = [quarters[i][:4] for i in posiciones]

ax.set_xticks(posiciones)
ax.set_xticklabels(etiquetas_x)

ax.yaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, _: f"{x:.0%}")
)

ax.set_title("Evolución Nacional de Negative Equity")

st.pyplot(fig)
plt.close()

st.markdown("---")

# ---------------- ANALISIS POR ESTADO ----------------
st.header("🗺️ Análisis por Estado")

fila = estados[
    estados["RegionName"] == estado_seleccionado
].iloc[0]

colA, colB = st.columns([1,2])

with colA:
    st.subheader("Indicadores")
    st.metric("Pico histórico", f"{fila['pico']:.1%}")
    st.metric("Valor 2017Q1", f"{fila['valor_2017']:.1%}")
    st.metric("Recuperación", f"{fila['recuperacion']:.1f}%")

with colB:
    valores_estado = [fila[q] for q in quarters]

    fig2, ax2 = plt.subplots(figsize=(10,4))

    ax2.plot(
        range(len(quarters)),
        valores_nacional,
        linestyle="--",
        color="gray",
        label="Promedio nacional"
    )

    ax2.plot(
        range(len(quarters)),
        valores_estado,
        color="darkblue",
        linewidth=3,
        label=estado_seleccionado
    )

    ax2.legend()

    ax2.set_xticks(posiciones)
    ax2.set_xticklabels(etiquetas_x)

    ax2.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"{x:.0%}")
    )

    ax2.set_title(f"Comparación: {estado_seleccionado} vs EE.UU.")

    st.pyplot(fig2)
    plt.close()

st.markdown("---")

# ---------------- HEATMAP ----------------
st.header("🔥 Heatmap por Estados")

heatmap_data = estados.set_index("RegionName")[quarters]

fig3, ax3 = plt.subplots(figsize=(14,8))

sns.heatmap(
    heatmap_data,
    cmap="Reds",
    ax=ax3
)

ax3.set_title("Intensidad de Negative Equity por Estado")

st.pyplot(fig3)
plt.close()

st.markdown("---")

# ---------------- TOP Y BOTTOM ----------------
st.header("🏆 Ranking de Estados")

col_top, col_bottom = st.columns(2)

with col_top:
    st.subheader("Top 5 estados más afectados")

    top5 = estados.nlargest(
        5,
        "pico"
    )[["RegionName", "pico"]]

    top5["pico"] = top5["pico"].apply(
        lambda x: f"{x:.1%}"
    )

    st.dataframe(
        top5,
        use_container_width=True
    )

with col_bottom:
    st.subheader("Top 5 estados menos afectados")

    bottom5 = estados.nsmallest(
        5,
        "pico"
    )[["RegionName", "pico"]]

    bottom5["pico"] = bottom5["pico"].apply(
        lambda x: f"{x:.1%}"
    )

    st.dataframe(
        bottom5,
        use_container_width=True
    )

st.markdown("---")

# ---------------- INSIGHTS AUTOMÁTICOS ----------------
st.header("💡 Hallazgos Clave")

st.success(f"""
✅ El pico nacional ocurrió en **{quarters[pico_idx]}**
con un valor de **{pico_valor:.1%}**.

✅ El estado más afectado fue **{estado_nombre}**
con un pico de **{estado_valor:.1%}**.

✅ Para 2017 el mercado mostró señales importantes
de recuperación.
""")

# ---------------- CONCLUSIÓN ----------------
st.header("📌 Conclusión Ejecutiva")

st.write("""
La crisis hipotecaria afectó de forma desigual a los estados
de EE.UU., concentrando mayores niveles de riesgo en regiones
como Nevada, Florida y Arizona.

Aunque para 2017 hubo una recuperación importante,
algunos mercados permanecieron vulnerables.

Este análisis puede ser útil para:

- Bancos
- Inversionistas inmobiliarios
- Analistas de riesgo
- Empresas hipotecarias
""")

st.markdown("---")
st.caption("Datos: Zillow Research | Dashboard desarrollado con Streamlit")