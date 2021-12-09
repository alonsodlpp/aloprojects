import krakenex
from pykrakenapi import KrakenAPI
from pykrakenapi.pykrakenapi import KrakenAPIError, CallRateLimitError
from requests import HTTPError
import time
import datetime
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title='Cripto hoy', page_icon=":moneybag:", layout='wide', initial_sidebar_state='auto')

# Configuración de la API
kraken = krakenex.API()

# Conexión con la API
api = KrakenAPI(kraken)

st.markdown(
        f""" <style>.reportview-container .main .block-container{{
        max-width: {1450}px;
        padding-top: {0}rem;
        padding-right: {10}rem;
        padding-left: {10}rem;
        padding-bottom: {0}rem;
    }}
</style> 
""", unsafe_allow_html=True
    )

# Header y subtítulo con st.markdown para tener la posibilidad de alinear el texto en el centro
st.markdown("<h1 style='text-align: center; '>Aplicación para analizar la cotización de diferentes criptomonedas</h1>",
            unsafe_allow_html=True)

st.markdown("<h4 style='text-align: center;'>Seleccione la configuración que desee para ver en tiempo real "
            "la cotización de las criptomonedas más relevantes</h4>", unsafe_allow_html=True)

# Se crean 3 columnas para introducir en cada una un desplegable que permita seleccionar
# la moneda, la divisa y la fecha de inicio

c1, c2, c3 = st.columns((1, 1, 1))

with c1:
    cripto_elegida = st.selectbox('Elija qué moneda desea visualizar:',
                                  ('Bitcoin', 'Ethereum', 'Dogecoin'))
with c2:
    divisa_elegida = st.selectbox("Elija la divisa que desee:",
                                  ("USD", "EUR"))
with c3:
    fecha_elegida = st.date_input("Elija la fecha de inicio", value=datetime.date.today(),
                                  min_value=None, max_value=datetime.date.today(), key=None)

st.sidebar.markdown("<h4 style='text-align: center;'>Seleccione la casilla para visualizar el VWAP que tenga en cuenta "
                    "el número de intervalos que desee:</h4>", unsafe_allow_html=True)

vwap_por_intervalos = st.sidebar.checkbox('VWAP por intervalos',
                                          help="Si selecciona esta casilla, además del VWAP completo, "
                                               "puede visualizar un VWAP que tenga en cuenta los intervalos que desee")

if vwap_por_intervalos:
    numero_intervalos = st.sidebar.number_input('Elija el nº de intervalos del VWAP',
                                                min_value=1, max_value=720, value=50, step=25)

# El intervalo se corresponde con el tiempo que abarca cada una de las velas y se presenta en forma de slider

intervalo_elegido = st.select_slider("Seleccione el intervalo de tiempo que tendrá cada vela del gráfico:",
                                     ("1 minuto", "5 minutos", "15 minutos", "30 minutos",
                                      "1 hora", "4 horas", "1 día", "7 días", "15 días"),
                                     value="15 minutos")

# Con esta función se convierte el texto introducido por el usuario en el código de la moneda, que posteriormente
# se pasará a la función con la que se descargarán los datos.


def convertir_formato_moneda(cripto_str, divisa_str):
    divisa_codigo = ""
    for seleccion, moneda in (("Bitcoin", "BTC"), ("Ethereum", "ETH"), ("Dogecoin", "XDG")):
        if seleccion == cripto_str:
            divisa_codigo = moneda
    divisa_codigo = divisa_codigo + divisa_str

    return divisa_codigo

# Con esta función se convierte el texto introducido por el usuario en un entero que representa el tiempo
# del intervalo, que posteriormente se pasará a la función con la que se descargarán los datos.


def convertir_formato_intervalo(intervalo_str):
    intervalo_numero = 0
    for seleccion, numero in (("1 minuto", 1), ("5 minutos", 5), ("15 minutos", 15), ("30 minutos", 30),
                              ("1 hora", 60), ("4 horas", 240), ("1 día", 1440), ("7 días", 10080), ("15 días", 21600)):
        if seleccion == intervalo_str:
            intervalo_numero = numero

    return intervalo_numero

# Con esta función se convierte la fecha elegida en el calendario en formato unix,
# que posteriormente se pasará a la función con la que se descargarán los datos.


def convertir_fecha_inicio(fecha_calendario):
    tiempo_unix = time.mktime(fecha_calendario.timetuple())

    return tiempo_unix

# Con esta función, se llamará a las anteriores, se descargarán los datos dependiendo de la selección
# del usuario y se graficará el precio de la moneda elegida, el vwap y el volumen.


def grafico_moneda():
    coin = convertir_formato_moneda(cripto_elegida, divisa_elegida)
    intervalo = convertir_formato_intervalo(intervalo_elegido)
    fecha = convertir_fecha_inicio(fecha_elegida)

    df = api.get_ohlc_data(pair=coin, interval=intervalo, since=fecha, ascending=True)  # Se descargan los datos
    datos = df[0]
    datos = datos.reset_index()  # Se resetea el index, ya que la fecha está en el índice de las filas.
                                 # De esta manera pasa a ser una columna.

    # Se despliega un aviso si el número de intervalos descargados es 720, ya que coincide
    # con el límite que permite la API
    if datos.shape[0] == 720:
        st.warning("No se pueden visualizar más de 720 intervalos de tiempo. "
                   "Seleccione intervalos de tiempo más grandes o un día de inicio más reciente")
    datos["typical_price"] = (datos["high"] + datos["low"] + datos["close"]) / 3
    datos["vwap_completo"] = np.cumsum(datos["typical_price"] * datos["volume"]) / np.cumsum(datos["volume"])

    graph_cripto = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                 vertical_spacing=0.06,
                                 subplot_titles=("Gráfico de la cotización de " + cripto_elegida,
                                                 "Gráfico del volumen de " + cripto_elegida),
                                 x_title="Fecha",
                                 row_width=[0.3, 0.7])

    graph_cripto.add_trace(go.Candlestick(x=datos['dtime'],
                                          open=datos['open'],
                                          high=datos['high'],
                                          low=datos['low'],
                                          close=datos['close'],
                                          name=cripto_elegida),
                           row=1, col=1)

    graph_cripto.add_trace(go.Scatter(x=datos["dtime"],
                                      y=datos["vwap_completo"],
                                      mode="lines",
                                      name="VWAP completo"),
                           row=1, col=1)

    graph_cripto.add_trace(go.Bar(x=datos["dtime"],
                                  y=datos["volume"],
                                  marker_color='crimson',
                                  name="Volumen",
                                  showlegend=False),
                           row=2, col=1)

    if vwap_por_intervalos:
        lista_vwap = []
        i = 1
        while i < numero_intervalos:
            vwap = np.sum(datos["typical_price"][0:i] * datos["volume"][0:i]) / np.sum(datos["volume"][0:i])
            lista_vwap.append(vwap)
            i += 1
        else:
            for i in range(numero_intervalos, datos.shape[0]):
                vwap = np.sum(datos["typical_price"][(i - numero_intervalos):i] * datos["volume"][(i - numero_intervalos):i]) / np.sum(datos["volume"][(i - numero_intervalos):i])
                lista_vwap.append(vwap)

        lista_wvap = pd.Series(lista_vwap)
        datos["vwap_diferentes_intervalos"] = lista_wvap

        graph_cripto.add_trace(go.Scatter(x=datos["dtime"],
                                          y=datos["vwap_diferentes_intervalos"],
                                          mode="lines",
                                          name="VWAP " + str(numero_intervalos),
                                          marker_color='rgba(5, 255, 5, 1)'),
                               row=1, col=1)

    graph_cripto.update_layout(
        yaxis_title="Precio " + ("(Dólares)" if divisa_elegida == "USD" else "(Euros)"),
        height=700)

    graph_cripto.update(layout_xaxis_rangeslider_visible=False)

    return graph_cripto


try:
    graf = grafico_moneda()
    st.plotly_chart(graf, use_container_width=True)
except (HTTPError, KrakenAPIError, CallRateLimitError) as err:
    st.warning("Actualmente el servicio no está disponible. Por favor, inténtelo de nuevo más tarde.")

