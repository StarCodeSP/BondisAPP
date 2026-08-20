import geopandas as gpd
import pandas as pd
import folium
from pyproj import Transformer
from folium.plugins import MarkerCluster

def generar_mapa_paradas():
    # Cargar el archivo DBF con las paradas de Montevideo - codificación 'latin1'
    df = gpd.read_file('v_uptu_paradas.dbf', encoding='latin1')

    # Eliminar la columna DESC_LINEA del DataFrame S
    if 'DESC_LINEA' in df.columns:
        df = df.drop(columns=['DESC_LINEA'])

    if 'COD_VARIAN' in df.columns:
        df = df.drop(columns=['COD_VARIAN'])

    if 'ORDINAL' in df.columns:
        df = df.drop(columns=['ORDINAL'])

    if 'COD_CALLE1' in df.columns:
        df = df.drop(columns=['COD_CALLE1'])

    if 'COD_CALLE2' in df.columns:
            df = df.drop(columns=['COD_CALLE2'])

    

    # Eliminar duplicados basados en la columna COD_UBIC_P, manteniendo el primer registro
    df_unicos = df.drop_duplicates(subset=['COD_UBIC_P'], keep='first')

    # Guardar a CSV el archivo procesado 
    df_unicos.to_csv('archivo_procesado.csv', index=False, encoding='utf-8')

    # Cargar el archivo CSV 
    df = pd.read_csv('archivo_procesado.csv')

    # Transformar las coordenadas de EPSG:32721 a EPSG:4326 (latitud/longitud)
    # always_xy=True mantiene la convención (X/longitud, Y/latitud)
    transformador = Transformer.from_crs("EPSG:32721", "EPSG:4326", always_xy=True)

    # Hacer la conversión de todas las coordenadas
    df['lon'], df['lat'] = transformador.transform(df['X'].values, df['Y'].values)

    # Crear el mapa centrado en Montevideo
    mapa = folium.Map(location=[-34.9011, -56.1645], zoom_start=20, tiles="CartoDB positron")

    # Cluster de marcadores para agrupar las paradas cercanas para evitar la saturación del mapa
    cluster = MarkerCluster(disableClusteringAtZoom=18).add_to(mapa)

    # Por cada registro en el DataFrame, agregar un marcador al mapa
    for _, fila in df.iterrows():
        lat = fila['lat']
        lon = fila['lon']

        cod_ubic = fila['COD_UBIC_P']
        calle = fila.get('CALLE', '')
        esquina = fila.get('ESQUINA', '')

        # Crear el contenido del popup con la información de la parada
        popup_text = f"""
        <div style="font-family: sans-serif; font-size: 13px;">
            <b>Código Parada:</b> {cod_ubic}<br>
            <b>Calle:</b> {calle}<br>
            <b>Esquina:</b> {esquina}
        </div>
        """

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_text, max_width=250),
            tooltip=f"Parada {cod_ubic}"
        ).add_to(cluster)

    # Guardar el mapa interactivo
    mapa.save('mapa_paradas_montevideo.html')

    return "Proceso completado. Mapa generado en 'mapa_paradas_montevideo.html'"

generar_mapa_paradas()