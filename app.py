import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# =========================
# CARGAR DATOS
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("customer_shopping_data.csv")
    
    df["invoice_date"] = pd.to_datetime(
        df["invoice_date"],
        dayfirst=True,
        errors="coerce"
    )
    
    return df

df = load_data()

st.title("Análisis de desempeño comercial y hábitos de compra - Centros comerciales")

# =========================
# SIDEBAR - FILTROS
# =========================
st.sidebar.header("Filtros")

genero = st.sidebar.multiselect(
    "Género",
    options=df["gender"].unique(),
    default=df["gender"].unique()
)

edad = st.sidebar.slider(
    "Rango de edad",
    int(df["age"].min()),
    int(df["age"].max()),
    (int(df["age"].min()), int(df["age"].max()))
)

metodo_pago = st.sidebar.multiselect(
    "Método de pago",
    options=df["payment_method"].unique(),
    default=df["payment_method"].unique()
)

categoria = st.sidebar.multiselect(
    "Categorías",
    options=df["category"].unique(),
    default=df["category"].unique()
)

# Aplicar filtros
df_filtrado = df[
    (df["gender"].isin(genero)) &
    (df["age"].between(edad[0], edad[1])) &
    (df["payment_method"].isin(metodo_pago)) &
    (df["category"].isin(categoria))
]

if df_filtrado.empty:
    st.warning("No hay datos con los filtros seleccionados.")
    st.stop()

# =========================
# KPIs
# =========================
col1, col2, col3, col4 = st.columns(4)

ticket_promedio = df_filtrado["price"].mean()

meses_unicos = df_filtrado["invoice_date"].dt.to_period("M").nunique()
frecuencia_compra = df_filtrado.shape[0] / meses_unicos if meses_unicos > 0 else 0

categoria_mayor = df_filtrado["category"].value_counts().idxmax()
metodo_pref = df_filtrado["payment_method"].value_counts().idxmax()

col1.metric("Ticket Promedio", f"${ticket_promedio:,.2f}")
col2.metric("Frecuencia compra (Prom/Mes)", round(frecuencia_compra, 2))
col3.metric("Categoría más demandada", categoria_mayor)
col4.metric("Método de pago preferido", metodo_pref)

st.markdown("---")

# =========================
# GRÁFICOS
# =========================

col_g1, col_g2 = st.columns(2)

# -------------------------
# Gráfico 1: Tendencias por mall 
# -------------------------
with col_g1:
    st.subheader("Tendencia de compras por Centro Comercial")

    df_filtrado["mes"] = df_filtrado["invoice_date"].dt.to_period("M").astype(str)

    mall_tendencia = st.selectbox(
        "Selecciona un centro comercial (Tendencia)",
        df_filtrado["shopping_mall"].unique()
    )

    datos_mall = df_filtrado[df_filtrado["shopping_mall"] == mall_tendencia]

    trend_data = (
        datos_mall
        .groupby("mes")
        .size()
        .reset_index(name="Cantidad")
    )

    fig = px.line(
        trend_data,
        x="mes",
        y="Cantidad",
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Gráfico 2: Top categorías
# -------------------------
with col_g2:
    st.subheader("Top categorías por centro comercial")

    mall_categoria = st.selectbox(
        "Selecciona un centro comercial (Categorías)",
        df_filtrado["shopping_mall"].unique()
    )

    datos_mall = df_filtrado[df_filtrado["shopping_mall"] == mall_categoria]

    top_categorias = (
        datos_mall
        .groupby("category")["price"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )

    st.bar_chart(top_categorias)

# =========================
# SEGUNDA FILA DE GRÁFICOS
# =========================

col_g3, col_g4 = st.columns(2)

# -------------------------
# Gráfico 3: Perfil del comprador
# -------------------------
with col_g3:
    st.subheader("Distribución de compras por género")

    genero_counts = df_filtrado["gender"].value_counts().reset_index()
    genero_counts.columns = ["Genero", "Cantidad"]

    fig2 = px.pie(
        genero_counts,
        names="Genero",
        values="Cantidad",
        title="Distribución por género"
    )

    st.plotly_chart(fig2, use_container_width=True)

# -------------------------
# Gráfico 4: Ticket por edad
# -------------------------
with col_g4:
    st.subheader("Ticket promedio por rango de edad")

    bins = [0, 18, 25, 35, 45, 55, 65, 100]
    labels = ["<18","18-25","26-35","36-45","46-55","56-65","65+"]

    df_filtrado["edad_rango"] = pd.cut(df_filtrado["age"], bins=bins, labels=labels)

    ticket_edad = (
        df_filtrado.groupby("edad_rango")["price"]
        .mean()
        .reset_index()
    )

    fig3 = px.bar(
        ticket_edad,
        x="edad_rango",
        y="price",
        title="Ticket promedio por edad"
    )

    st.plotly_chart(fig3, use_container_width=True)