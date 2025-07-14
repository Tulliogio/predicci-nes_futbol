import streamlit as st
import os
from datetime import date
import pandas as pd

# Importamos todo tu código backend como un módulo
# Es crucial que tu archivo original se llame 'backend.py'
import backend 

# --- CONFIGURACIÓN DE LA PÁGINA DE STREAMLIT ---
st.set_page_config(
    page_title="Predictor de Fútbol",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS PERSONALIZADOS (Opcional, para mejorar la estética) ---
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background: #ffffff;
    }
    .stButton>button {
        color: #ffffff;
        background-color: #007bff;
        border-radius: 5px;
        border: 1px solid #007bff;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        border: 1px solid #0056b3;
    }
    .css-1d391kg { /* Estilo para el expander */
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)


# --- FUNCIONES DE LA INTERFAZ ---

def mostrar_pronosticos():
    st.header("🎯 Generar Pronóstico Diario")
    st.markdown("Busca en todas las ligas activas los 5 partidos con el resultado más probable en los próximos 7 días.")

    if st.button("🚀 Iniciar Análisis"):
        with st.spinner('🔍 Analizando ligas y partidos... Esto puede tardar unos minutos.'):
            # 1. Cargar historial para no repetir
            historial = backend.cargar_historial()
            fecha_hoy = date.today()

            # 2. Obtener ligas activas (más eficiente)
            ligas_activas = backend.obtener_ligas_activas()
            if not ligas_activas:
                st.warning("No se encontraron ligas con partidos disponibles en este momento.")
                return

            # 3. Obtener y procesar partidos de todas las ligas activas
            todos_los_partidos = []
            progreso = st.progress(0)
            for i, deporte in enumerate(ligas_activas):
                partidos_raw = backend.obtener_partidos_deporte(deporte)
                partidos_procesados = backend.procesar_partidos(partidos_raw, historial, fecha_hoy)
                todos_los_partidos.extend(partidos_procesados)
                progreso.progress((i + 1) / len(ligas_activas), text=f"Consultando: {deporte}")
            
            progreso.empty()

            if not todos_los_partidos:
                st.error("❌ No se encontraron partidos nuevos para pronosticar.")
                st.info("Posibles razones: Todos los partidos próximos ya fueron pronosticados, no hay partidos en los próximos 7 días, o hubo un error en la API.")
                return
            
            # 4. Ordenar y seleccionar los mejores
            partidos_ordenados = sorted(todos_los_partidos, key=lambda x: x['cuota'])
            top_partidos = partidos_ordenados[:5]

        st.success(f"✅ Análisis completado. Se encontraron {len(todos_los_partidos)} partidos nuevos.")
        st.subheader(f"🏆 Top 5 Pronósticos - {fecha_hoy.strftime('%d/%m/%Y')}")

        # 5. Mostrar resultados de forma atractiva
        for p in top_partidos:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.markdown(f"**🏟️ {p['equipos']}**")
                    st.caption(f"📅 {p['fecha']} | 🏆 {p['liga']}")
                with col2:
                    st.metric(label="⭐ Pronóstico", value=p['resultado_probable'])
                with col3:
                    st.metric(label="📊 Probabilidad (Cuota)", value=f"{p['probabilidad_implicita']}% ({p['cuota']})")
                st.divider()

        # 6. Guardar en el historial
        fecha_str = fecha_hoy.strftime('%Y-%m-%d')
        if fecha_str not in historial:
            historial[fecha_str] = []
        
        for partido in top_partidos:
            historial[partido['id']] = {
                'fecha_pronostico': fecha_str,
                'equipos': partido['equipos'],
                'resultado_probable': partido['resultado_probable'],
                'cuota': partido['cuota'],
                'liga': partido['liga']
            }
        
        backend.guardar_historial(historial)
        st.success(f"💾 Pronósticos guardados en `{backend.HISTORIAL_FILE}`")


def mostrar_historial():
    st.header("📚 Historial de Pronósticos")
    historial = backend.cargar_historial()
    
    if not any('_vs_' in k for k in historial.keys()):
        st.info("Aún no hay pronósticos en el historial.")
        return

    # Extraer y ordenar pronósticos por fecha
    pronosticos = [v for k, v in historial.items() if '_vs_' in k]
    df = pd.DataFrame(pronosticos)
    df['fecha_pronostico'] = pd.to_datetime(df['fecha_pronostico'])
    df = df.sort_values(by='fecha_pronostico', ascending=False)
    
    for fecha, grupo in df.groupby('fecha_pronostico'):
        with st.expander(f"📅 Pronósticos del {fecha.strftime('%d-%m-%Y')}", expanded=True):
            for _, partido in grupo.iterrows():
                st.markdown(f"**{partido['equipos']}** ({partido['liga']})")
                st.markdown(f"→ **Pronóstico:** {partido['resultado_probable']} (Cuota: {partido['cuota']})")
                st.divider()

def mostrar_estadisticas_ligas():
    st.header("📊 Estadísticas de Competiciones")
    
    # La lógica de categorización es la misma que en tu backend, pero mostrada con Streamlit
    regiones = {
        'Europa': [d for d in backend.DEPORTES if any(x in d for x in ['epl', 'spain', 'italy', 'germany', 'france', 'netherlands', 'portugal', 'uefa', 'scotland'])],
        'Sudamérica': [d for d in backend.DEPORTES if any(x in d for x in ['brazil', 'argentina', 'colombia', 'conmebol'])],
        'Norteamérica': [d for d in backend.DEPORTES if any(x in d for x in ['usa', 'mexico', 'concacaf'])],
        'Asia': [d for d in backend.DEPORTES if any(x in d for x in ['japan', 'australia', 'saudi', 'afc'])],
        'África': [d for d in backend.DEPORTES if any(x in d for x in ['egypt', 'south_africa', 'caf'])],
        'Internacionales': [d for d in backend.DEPORTES if any(x in d for x in ['fifa', 'olympics', 'friendlies'])],
        'Femeninas': [d for d in backend.DEPORTES if any(x in d for x in ['women', 'feminine', 'frauen'])]
    }
    
    # Para no duplicar, calculamos las ligas ya categorizadas
    categorizadas = set(sum(regiones.values(), []))
    regiones['Otras Regiones'] = [d for d in backend.DEPORTES if d not in categorizadas]

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total de Competiciones", len(backend.DEPORTES))
    
    for region, ligas in regiones.items():
        if not ligas: continue
        with st.expander(f"🌍 {region} ({len(ligas)} competiciones)"):
            df = pd.DataFrame(ligas, columns=["Identificador de la Liga"])
            st.table(df)

def verificar_ligas_activas():
    st.header("📡 Verificar Ligas Activas")
    st.markdown("Comprueba qué ligas de la configuración tienen partidos disponibles en la API en este momento.")
    if st.button("Verificar Ahora"):
        with st.spinner("Buscando ligas activas..."):
            ligas_activas = backend.obtener_ligas_activas()
        
        if ligas_activas:
            st.success(f"Se encontraron {len(ligas_activas)} ligas activas de {len(backend.DEPORTES)} configuradas.")
            df = pd.DataFrame(ligas_activas, columns=["Ligas Activas"])
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No se encontraron ligas activas en este momento.")

def limpiar_historial():
    st.header("🗑️ Limpiar Historial")
    st.warning("⚠️ ¡Cuidado! Esta acción eliminará permanentemente el archivo `historial_pronosticos.json` y no se puede deshacer.")
    
    if os.path.exists(backend.HISTORIAL_FILE):
        if st.button("Eliminar Historial Permanentemente"):
            os.remove(backend.HISTORIAL_FILE)
            st.success("✅ Historial limpiado con éxito.")
            st.balloons()
    else:
        st.info("No existe un archivo de historial para limpiar.")

# --- SIDEBAR Y NAVEGACIÓN PRINCIPAL ---
st.sidebar.title("Menú de Opciones")
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/857/857454.png", width=100) # Un ícono para decorar

opciones = {
    "Generar Pronóstico": mostrar_pronosticos,
    "Ver Historial": mostrar_historial,
    "Estadísticas de Ligas": mostrar_estadisticas_ligas,
    "Verificar Ligas Activas": verificar_ligas_activas,
    "Limpiar Historial": limpiar_historial
}

seleccion = st.sidebar.radio("Elige una acción:", list(opciones.keys()))

# Ejecutar la función correspondiente a la selección
opciones[seleccion]()

st.sidebar.info(
    "Este proyecto utiliza la API de 'The Odds API'. "
    "Recuerda que las cuotas son solo probabilidades y no garantizan resultados."
)