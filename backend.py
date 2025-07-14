import requests
import json
from datetime import datetime, date
import os
import streamlit as st

# --- CONFIGURACIÓN (con diagnóstico) ---
if "API_KEY" in st.secrets:
    API_KEY = st.secrets["API_KEY"]
else:
    # Esto hará que la app falle, pero con un mensaje nuestro muy claro.
    st.error("ERROR CRÍTICO: La clave 'API_KEY' no se encontró en los secretos de Streamlit Cloud. Por favor, configúrala en el panel de 'Settings > Secrets'.")
    # Mostramos qué secretos SÍ encuentra, para depurar.
    st.warning(f"Secretos encontrados: {st.secrets.to_dict()}")
    st.stop() # Detiene la ejecución de la app aquí.

# TODAS LAS COMPETICIONES DE FÚTBOL DISPONIBLES EN THE ODDS API
DEPORTES = [
    # --- LIGAS EUROPEAS PRINCIPALES ---
    'soccer_epl',                    # Premier League (Inglaterra)
    'soccer_efl_champ',              # EFL Championship (Inglaterra)
    'soccer_england_league1',        # League One (Inglaterra)
    'soccer_england_league2',        # League Two (Inglaterra)
    'soccer_spain_la_liga',          # La Liga (España)
    'soccer_spain_segunda_division', # Segunda División (España)
    'soccer_italy_serie_a',          # Serie A (Italia)
    'soccer_italy_serie_b',          # Serie B (Italia)
    'soccer_germany_bundesliga',     # Bundesliga (Alemania)
    'soccer_germany_bundesliga2',    # 2. Bundesliga (Alemania)
    'soccer_germany_liga3',          # 3. Liga (Alemania)
    'soccer_france_ligue_one',       # Ligue 1 (Francia)
    'soccer_france_ligue_two',       # Ligue 2 (Francia)
    'soccer_netherlands_eredivisie', # Eredivisie (Países Bajos)
    'soccer_portugal_primeira_liga', # Primeira Liga (Portugal)
    'soccer_belgium_first_div',      # First Division A (Bélgica)
    'soccer_switzerland_superleague', # Super League (Suiza)
    'soccer_austria_bundesliga',     # Bundesliga (Austria)
    'soccer_turkey_super_league',    # Süper Lig (Turquía)
    'soccer_greece_super_league',    # Super League (Grecia)
    'soccer_denmark_superliga',      # Superliga (Dinamarca)
    'soccer_sweden_allsvenskan',     # Allsvenskan (Suecia)
    'soccer_norway_eliteserien',     # Eliteserien (Noruega)
    'soccer_finland_veikkausliiga',  # Veikkausliiga (Finlandia)
    'soccer_poland_ekstraklasa',     # Ekstraklasa (Polonia)
    'soccer_czech_republic_fnl',     # Fortuna Liga (República Checa)
    'soccer_slovakia_super_liga',    # Super Liga (Eslovaquia)
    'soccer_hungary_nb_i',           # NB I (Hungría)
    'soccer_romania_liga_1',         # Liga 1 (Rumania)
    'soccer_bulgaria_first_league',  # First League (Bulgaria)
    'soccer_croatia_hnl',            # HNL (Croacia)
    'soccer_serbia_super_liga',      # Super Liga (Serbia)
    'soccer_slovenia_prvaliga',      # PrvaLiga (Eslovenia)
    'soccer_russia_premier_league',  # Premier League (Rusia)
    'soccer_ukraine_premier_league', # Premier League (Ucrania)
    
    # --- COMPETICIONES EUROPEAS ---
    'soccer_uefa_champs_league',     # Champions League
    'soccer_uefa_europa_league',     # Europa League
    'soccer_uefa_europa_conference_league', # Europa Conference League
    'soccer_uefa_nations_league',    # Nations League
    'soccer_uefa_euros',             # Eurocopa (cuando esté disponible)
    'soccer_uefa_euros_qualification', # Clasificación Eurocopa
    
    # --- LIGAS SUDAMERICANAS ---
    'soccer_brazil_campeonato',      # Campeonato Brasileiro Série A
    'soccer_brazil_serie_b',         # Campeonato Brasileiro Série B
    'soccer_argentina_primera_division', # Primera División (Argentina)
    'soccer_chile_primera_division', # Primera División (Chile)
    'soccer_colombia_primera_a',     # Primera A (Colombia)
    'soccer_peru_primera_division',  # Primera División (Perú)
    'soccer_uruguay_primera_division', # Primera División (Uruguay)
    'soccer_ecuador_primera_a',      # Primera A (Ecuador)
    'soccer_bolivia_primera_division', # Primera División (Bolivia)
    'soccer_paraguay_primera_division', # Primera División (Paraguay)
    'soccer_venezuela_primera_profesional', # Primera Profesional (Venezuela)
    'soccer_conmebol_copa_libertadores', # Copa Libertadores
    'soccer_conmebol_copa_sudamericana', # Copa Sudamericana
    'soccer_copa_america',           # Copa América (cuando esté disponible)
    'soccer_conmebol_wc_qualification', # Clasificación Mundial CONMEBOL
    
    # --- LIGAS NORTEAMERICANAS ---
    'soccer_usa_mls',                # Major League Soccer (MLS)
    'soccer_mexico_ligamx',          # Liga MX (México)
    'soccer_canada_cpl',             # Canadian Premier League
    'soccer_concacaf_champions_league', # Champions League CONCACAF
    'soccer_concacaf_gold_cup',      # Copa Oro CONCACAF
    'soccer_concacaf_nations_league', # Nations League CONCACAF
    'soccer_concacaf_wc_qualification', # Clasificación Mundial CONCACAF
    
    # --- LIGAS ASIÁTICAS ---
    'soccer_japan_j_league',         # J1 League (Japón)
    'soccer_japan_j_league_2',       # J2 League (Japón)
    'soccer_south_korea_k_league_1', # K League 1 (Corea del Sur)
    'soccer_china_super_league',     # Chinese Super League
    'soccer_australia_aleague',      # A-League (Australia)
    'soccer_saudi_arabia_pro_league', # Pro League (Arabia Saudí)
    'soccer_uae_arabian_gulf_league', # Arabian Gulf League (EAU)
    'soccer_qatar_stars_league',     # Stars League (Qatar)
    'soccer_iran_pro_league',        # Pro League (Irán)
    'soccer_iraq_premier_league',    # Premier League (Irak)
    'soccer_thailand_premier_league', # Premier League (Tailandia)
    'soccer_vietnam_v_league',       # V.League 1 (Vietnam)
    'soccer_malaysia_super_league',  # Super League (Malasia)
    'soccer_singapore_premier_league', # Premier League (Singapur)
    'soccer_indonesia_liga_1',       # Liga 1 (Indonesia)
    'soccer_philippines_pfl',        # Philippines Football League
    'soccer_india_super_league',     # Indian Super League
    'soccer_afc_asian_cup',          # Copa Asiática AFC
    'soccer_afc_wc_qualification',   # Clasificación Mundial AFC
    
    # --- LIGAS AFRICANAS ---
    'soccer_south_africa_premier_division', # Premier Division (Sudáfrica)
    'soccer_egypt_premier_league',   # Premier League (Egipto)
    'soccer_morocco_gnf_1',          # Botola Pro (Marruecos)
    'soccer_tunisia_ligue_1',        # Ligue 1 (Túnez)
    'soccer_algeria_ligue_1',        # Ligue 1 (Argelia)
    'soccer_nigeria_npfl',           # Nigeria Professional Football League
    'soccer_ghana_premier_league',   # Premier League (Ghana)
    'soccer_kenya_premier_league',   # Premier League (Kenia)
    'soccer_uganda_premier_league',  # Premier League (Uganda)
    'soccer_tanzania_premier_league', # Premier League (Tanzania)
    'soccer_zambia_super_league',    # Super League (Zambia)
    'soccer_zimbabwe_premier_league', # Premier League (Zimbabwe)
    'soccer_caf_champions_league',   # Champions League CAF
    'soccer_caf_confederation_cup',  # Copa Confederación CAF
    'soccer_caf_african_cup_of_nations', # Copa Africana de Naciones
    'soccer_caf_wc_qualification',   # Clasificación Mundial CAF
    
    # --- OTRAS COMPETICIONES INTERNACIONALES ---
    'soccer_fifa_world_cup',         # Copa del Mundo FIFA
    'soccer_fifa_world_cup_qualification', # Clasificación Copa del Mundo
    'soccer_fifa_confederations_cup', # Copa Confederaciones FIFA
    'soccer_fifa_club_world_cup',    # Copa del Mundo de Clubes FIFA
    'soccer_fifa_womens_world_cup',  # Copa del Mundo Femenina FIFA
    'soccer_olympics_mens',          # Juegos Olímpicos (masculino)
    'soccer_olympics_womens',        # Juegos Olímpicos (femenino)
    
    # --- LIGAS FEMENINAS ---
    'soccer_fa_wsl',                 # Women's Super League (Inglaterra)
    'soccer_nwsl',                   # National Women's Soccer League (EE.UU.)
    'soccer_france_feminine_1',      # Première Ligue (Francia - femenino)
    'soccer_germany_frauen_bundesliga', # Frauen-Bundesliga (Alemania)
    'soccer_spain_primera_federacion_femenina', # Primera Federación Femenina (España)
    'soccer_italy_serie_a_femminile', # Serie A Femminile (Italia)
    'soccer_netherlands_eredivisie_vrouwen', # Eredivisie Vrouwen (Países Bajos)
    'soccer_sweden_damallsvenskan',  # Damallsvenskan (Suecia)
    'soccer_norway_toppserien',      # Toppserien (Noruega)
    'soccer_denmark_kvindeligaen',   # Kvindeligaen (Dinamarca)
    'soccer_australia_aleague_women', # A-League Women (Australia)
    'soccer_brazil_serie_a1_feminino', # Série A1 Feminino (Brasil)
    'soccer_uefa_womens_euro',       # Eurocopa Femenina UEFA
    'soccer_uefa_womens_champions_league', # Champions League Femenina UEFA
    
    # --- LIGAS MENORES Y REGIONALES ---
    'soccer_scotland_premiership',   # Premiership (Escocia)
    'soccer_scotland_championship',  # Championship (Escocia)
    'soccer_wales_premier_league',   # Premier League (Gales)
    'soccer_northern_ireland_premiership', # Premiership (Irlanda del Norte)
    'soccer_ireland_premier_division', # Premier Division (Irlanda)
    'soccer_iceland_urvalsdeild',    # Úrvalsdeild (Islandia)
    'soccer_faroe_islands_premier_league', # Premier League (Islas Feroe)
    'soccer_luxembourg_bgl_ligue',   # BGL Ligue (Luxemburgo)
    'soccer_malta_premier_league',   # Premier League (Malta)
    'soccer_cyprus_first_division',  # First Division (Chipre)
    'soccer_latvia_virsliga',        # Virsliga (Letonia)
    'soccer_lithuania_a_lyga',       # A Lyga (Lituania)
    'soccer_estonia_meistriliiga',   # Meistriliiga (Estonia)
    'soccer_albania_kategoria_superiore', # Kategoria Superiore (Albania)
    'soccer_north_macedonia_first_league', # First League (Macedonia del Norte)
    'soccer_montenegro_first_league', # First League (Montenegro)
    'soccer_bosnia_premier_league',  # Premier League (Bosnia y Herzegovina)
    'soccer_kosovo_superliga',       # Superliga (Kosovo)
    'soccer_moldova_super_liga',     # Super Liga (Moldavia)
    'soccer_georgia_erovnuli_liga',  # Erovnuli Liga (Georgia)
    'soccer_armenia_premier_league', # Premier League (Armenia)
    'soccer_azerbaijan_premier_league', # Premier League (Azerbaiyán)
    'soccer_kazakhstan_premier_league', # Premier League (Kazajistán)
    'soccer_uzbekistan_super_league', # Super League (Uzbekistán)
    'soccer_kyrgyzstan_top_league',  # Top League (Kirguistán)
    'soccer_tajikistan_higher_league', # Higher League (Tayikistán)
    'soccer_turkmenistan_yokary_liga', # Yokary Liga (Turkmenistán)
    'soccer_afghanistan_premier_league', # Premier League (Afganistán)
    'soccer_bangladesh_premier_league', # Premier League (Bangladesh)
    'soccer_bhutan_premier_league',  # Premier League (Bután)
    'soccer_cambodia_premier_league', # Premier League (Camboya)
    'soccer_laos_premier_league',    # Premier League (Laos)
    'soccer_myanmar_national_league', # National League (Myanmar)
    'soccer_nepal_super_league',     # Super League (Nepal)
    'soccer_sri_lanka_premier_league', # Premier League (Sri Lanka)
    'soccer_maldives_premier_league', # Premier League (Maldivas)
    'soccer_pakistan_premier_league', # Premier League (Pakistán)
    
    # --- COMPETICIONES DE CLUBES ESPECIALES ---
    'soccer_friendlies',             # Partidos amistosos
    'soccer_friendlies_clubs',       # Amistosos de clubes
    'soccer_friendlies_womens',      # Amistosos femeninos
    'soccer_youth_league',           # UEFA Youth League
    'soccer_europa_league_qualifying', # Clasificación Europa League
    'soccer_champions_league_qualifying', # Clasificación Champions League
    'soccer_conference_league_qualifying', # Clasificación Conference League
]

REGIONS = 'eu'
MARKETS = 'h2h'

# Archivo para guardar el historial de pronósticos
HISTORIAL_FILE = 'historial_pronosticos.json'

# --- FIN DE LA CONFIGURACIÓN ---

def cargar_historial():
    """Carga el historial de pronósticos desde el archivo"""
    if os.path.exists(HISTORIAL_FILE):
        try:
            with open(HISTORIAL_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def guardar_historial(historial):
    """Guarda el historial de pronósticos en el archivo"""
    with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)

def crear_id_partido(home_team, away_team, fecha):
    """Crea un ID único para cada partido"""
    fecha_str = fecha.strftime('%Y-%m-%d')
    return f"{home_team}_vs_{away_team}_{fecha_str}"

def cuota_a_probabilidad(cuota):
    """Convierte cuotas a probabilidad implícita (%)"""
    if cuota == 0:
        return 0
    return round((1 / cuota) * 100, 2)

def obtener_partidos_deporte(deporte):
    """Obtiene los partidos de un deporte específico"""
    url = f'https://api.the-odds-api.com/v4/sports/{deporte}/odds/?apiKey={API_KEY}&regions={REGIONS}&markets={MARKETS}'
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error al obtener datos de {deporte}: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error de conexión para {deporte}: {e}")
        return []

def procesar_partidos(partidos_raw, historial, fecha_hoy):
    """Procesa los partidos y filtra los ya pronosticados"""
    partidos_procesados = []
    
    for partido in partidos_raw:
        try:
            equipos = f"{partido['home_team']} vs {partido['away_team']}"
            fecha_partido = datetime.fromisoformat(partido['commence_time'].replace('Z', '+00:00'))
            
            # Crear ID único del partido
            partido_id = crear_id_partido(partido['home_team'], partido['away_team'], fecha_partido)
            
            # Verificar si ya fue pronosticado
            if partido_id in historial:
                continue
                
            # Verificar que el partido sea en los próximos 7 días
            dias_diferencia = (fecha_partido.date() - fecha_hoy).days
            if dias_diferencia < 0 or dias_diferencia > 7:
                continue

            # Procesar cuotas
            if partido.get('bookmakers') and partido['bookmakers'][0].get('markets'):
                outcomes = partido['bookmakers'][0]['markets'][0]['outcomes']
                
                if len(outcomes) >= 2:  # Al menos local y visitante
                    cuotas_dict = {}
                    
                    for outcome in outcomes:
                        if outcome['name'] == partido['home_team']:
                            cuotas_dict[f"Gana {outcome['name']}"] = outcome['price']
                        elif outcome['name'] == partido['away_team']:
                            cuotas_dict[f"Gana {outcome['name']}"] = outcome['price']
                        elif outcome['name'].lower() in ['draw', 'tie', 'empate']:
                            cuotas_dict["Empate"] = outcome['price']
                    
                    if cuotas_dict:
                        resultado_mas_probable = min(cuotas_dict, key=cuotas_dict.get)
                        cuota_minima = cuotas_dict[resultado_mas_probable]
                        
                        partidos_procesados.append({
                            'id': partido_id,
                            'equipos': equipos,
                            'fecha': fecha_partido.strftime('%d-%m-%Y %H:%M'),
                            'fecha_objeto': fecha_partido,
                            'resultado_probable': resultado_mas_probable,
                            'cuota': cuota_minima,
                            'probabilidad_implicita': cuota_a_probabilidad(cuota_minima),
                            'liga': partido.get('sport_title', 'Liga desconocida')
                        })
                        
        except Exception as e:
            print(f"Error procesando partido: {e}")
            continue
    
    return partidos_procesados

def obtener_ligas_activas():
    """Obtiene una lista de las ligas que tienen partidos disponibles"""
    ligas_activas = []
    contador = 0
    
    print("🔍 Verificando ligas activas...")
    
    for deporte in DEPORTES:
        try:
            partidos = obtener_partidos_deporte(deporte)
            if partidos:
                ligas_activas.append(deporte)
                contador += 1
                if contador % 10 == 0:
                    print(f"   Verificadas {contador} ligas...")
        except:
            continue
    
    print(f"✅ Se encontraron {len(ligas_activas)} ligas activas de {len(DEPORTES)} disponibles")
    return ligas_activas

def generar_pronostico_diario():
    """Genera el pronóstico diario de 5 partidos (aumentado por más ligas)"""
    print("🏆 GENERANDO PRONÓSTICO DIARIO DE FÚTBOL MUNDIAL 🏆")
    print("=" * 55)
    
    fecha_hoy = date.today()
    print(f"Fecha: {fecha_hoy.strftime('%d-%m-%Y')}")
    print(f"Total de competiciones configuradas: {len(DEPORTES)}")
    
    # Cargar historial
    historial = cargar_historial()
    
    # Obtener solo ligas activas para optimizar el proceso
    ligas_activas = obtener_ligas_activas()
    
    # Obtener partidos de todas las ligas activas
    todos_los_partidos = []
    
    for deporte in ligas_activas:
        print(f"Consultando {deporte}...")
        partidos_raw = obtener_partidos_deporte(deporte)
        partidos_procesados = procesar_partidos(partidos_raw, historial, fecha_hoy)
        todos_los_partidos.extend(partidos_procesados)
    
    if not todos_los_partidos:
        print("\n❌ No se encontraron partidos nuevos para pronosticar.")
        print("Posibles razones:")
        print("- Todos los partidos próximos ya fueron pronosticados")
        print("- No hay partidos en los próximos 7 días")
        print("- Error en la API")
        return
    
    # Ordenar por probabilidad (cuota más baja = más probable)
    partidos_ordenados = sorted(todos_los_partidos, key=lambda x: x['cuota'])
    
    # Seleccionar los 5 mejores (aumentado por más variedad)
    top_partidos = partidos_ordenados[:5]
    
    # Mostrar pronósticos
    print(f"\n🎯 PRONÓSTICOS DEL DÍA - {fecha_hoy.strftime('%d/%m/%Y')}")
    print("=" * 55)
    
    for i, p in enumerate(top_partidos, 1):
        print(f"\n{i}. 🏟️  {p['equipos']}")
        print(f"   📅 Fecha: {p['fecha']}")
        print(f"   🏆 Liga: {p['liga']}")
        print(f"   ⭐ Pronóstico: {p['resultado_probable']}")
        print(f"   💰 Cuota: {p['cuota']}")
        print(f"   📊 Probabilidad: {p['probabilidad_implicita']}%")
        print("-" * 50)
    
    # Mostrar estadísticas adicionales
    print(f"\n📊 ESTADÍSTICAS DEL ANÁLISIS:")
    print(f"   • Ligas analizadas: {len(ligas_activas)}")
    print(f"   • Partidos encontrados: {len(todos_los_partidos)}")
    print(f"   • Partidos ya pronosticados: {len([k for k in historial.keys() if '_vs_' in k])}")
    
    # Guardar en el historial
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
    
    guardar_historial(historial)
    
    print(f"\n✅ Pronósticos guardados en {HISTORIAL_FILE}")

def mostrar_historial():
    """Muestra el historial de pronósticos"""
    historial = cargar_historial()
    
    if not historial:
        print("No hay historial de pronósticos.")
        return
    
    print("\n📚 HISTORIAL DE PRONÓSTICOS")
    print("=" * 40)
    
    fechas = [k for k in historial.keys() if len(k) == 10]  # Solo fechas (formato YYYY-MM-DD)
    fechas.sort(reverse=True)
    
    for fecha in fechas[:10]:  # Mostrar últimos 10 días
        print(f"\n📅 {fecha}:")
        partidos_del_dia = [v for k, v in historial.items() if k.startswith(fecha.replace('-', ''))]
        
        for partido in partidos_del_dia:
            liga = partido.get('liga', 'Liga desconocida')
            print(f"  • {partido['equipos']} ({liga})")
            print(f"    {partido['resultado_probable']} (Cuota: {partido['cuota']})")

def mostrar_estadisticas_ligas():
    """Muestra estadísticas sobre las ligas disponibles"""
    print("\n📊 ESTADÍSTICAS DE COMPETICIONES")
    print("=" * 50)
    
    # Categorizar ligas por región
    regiones = {
        'Europa': [d for d in DEPORTES if any(x in d for x in ['epl', 'spain', 'italy', 'germany', 'france', 'netherlands', 'portugal', 'belgium', 'switzerland', 'austria', 'turkey', 'greece', 'denmark', 'sweden', 'norway', 'finland', 'poland', 'czech', 'slovakia', 'hungary', 'romania', 'bulgaria', 'croatia', 'serbia', 'slovenia', 'russia', 'ukraine', 'uefa', 'scotland', 'wales', 'ireland', 'iceland', 'faroe', 'luxembourg', 'malta', 'cyprus', 'latvia', 'lithuania', 'estonia', 'albania', 'macedonia', 'montenegro', 'bosnia', 'kosovo', 'moldova', 'georgia', 'armenia', 'azerbaijan'])],
        'Sudamérica': [d for d in DEPORTES if any(x in d for x in ['brazil', 'argentina', 'chile', 'colombia', 'peru', 'uruguay', 'ecuador', 'bolivia', 'paraguay', 'venezuela', 'conmebol', 'copa_america'])],
        'Norteamérica': [d for d in DEPORTES if any(x in d for x in ['usa', 'mexico', 'canada', 'concacaf'])],
        'Asia': [d for d in DEPORTES if any(x in d for x in ['japan', 'south_korea', 'china', 'australia', 'saudi', 'uae', 'qatar', 'iran', 'iraq', 'thailand', 'vietnam', 'malaysia', 'singapore', 'indonesia', 'philippines', 'india', 'afc', 'kazakhstan', 'uzbekistan', 'kyrgyzstan', 'tajikistan', 'turkmenistan', 'afghanistan', 'bangladesh', 'bhutan', 'cambodia', 'laos', 'myanmar', 'nepal', 'sri_lanka', 'maldives', 'pakistan'])],
        'África': [d for d in DEPORTES if any(x in d for x in ['south_africa', 'egypt', 'morocco', 'tunisia', 'algeria', 'nigeria', 'ghana', 'kenya', 'uganda', 'tanzania', 'zambia', 'zimbabwe', 'caf'])],
        'Internacionales': [d for d in DEPORTES if any(x in d for x in ['fifa', 'olympics', 'friendlies'])],
        'Femeninas': [d for d in DEPORTES if any(x in d for x in ['women', 'feminine', 'frauen', 'femminile', 'vrouwen', 'damall', 'kvinde', 'feminino'])]
    }
    
    for region, ligas in regiones.items():
        print(f"\n🌍 {region}: {len(ligas)} competiciones")
        if len(ligas) <= 5:
            for liga in ligas:
                print(f"   • {liga}")
        else:
            print(f"   • {ligas[0]}")
            print(f"   • {ligas[1]}")
            print(f"   • ... y {len(ligas)-2} más")
    
    print(f"\n🏆 TOTAL: {len(DEPORTES)} competiciones de fútbol configuradas")

if __name__ == "__main__":
    print("🌍 PREDICTOR DE FÚTBOL MUNDIAL")
    print("=" * 35)
    print("1. Generar pronóstico diario")
    print("2. Ver historial")
    print("3. Limpiar historial")
    print("4. Ver estadísticas de ligas")
    print("5. Verificar ligas activas")
    
    opcion = input("\nElige una opción (1-5): ").strip()
    
    if opcion == "1":
        generar_pronostico_diario()
    elif opcion == "2":
        mostrar_historial()
    elif opcion == "3":
        if input("¿Seguro que quieres limpiar el historial? (s/N): ").lower() == 's':
            if os.path.exists(HISTORIAL_FILE):
                os.remove(HISTORIAL_FILE)
                print("✅ Historial limpiado.")
            else:
                print("No hay historial para limpiar.")
    elif opcion == "4":
        mostrar_estadisticas_ligas()
    elif opcion == "5":
        ligas_activas = obtener_ligas_activas()
        print(f"\n🏆 Ligas activas encontradas: {len(ligas_activas)}")
        for i, liga in enumerate(ligas_activas[:20], 1):  # Mostrar primeras 20
            print(f"{i:2d}. {liga}")
        if len(ligas_activas) > 20:
            print(f"    ... y {len(ligas_activas)-20} más")
    else:
        print("Opción no válida.")