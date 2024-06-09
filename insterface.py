import streamlit as st
import paho.mqtt.client as mqtt
import json
import pandas as pd

# Configurações MQTT
MQTT_BROKER = "BROKER_IP_ADDRESS"  # Substitua pelo endereço IP do seu broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC_DATA = "esp32/data"
MQTT_TOPIC_COMMANDS = "esp32/commands"

# Variáveis de controle
temperatura_atual = None
temperatura_referencia = None
voltagem_atual = None
corrente_atual = None
potencia_atual = None

# DataFrame para armazenar os dados recebidos
dados = pd.DataFrame(columns=["Tempo", "Temperatura", "Temperatura_Referencia", "Voltagem", "Corrente", "Potência"])
tempo = 0


# Função de callback quando uma mensagem é recebida
def on_message(client, userdata, message):
    global temperatura_atual, temperatura_referencia, voltagem_atual, corrente_atual, potencia_atual, dados, tempo
    payload = message.payload.decode("utf-8")
    data = json.loads(payload)
    temperatura_atual = data.get("Temp", None)
    temperatura_referencia = data.get("Temp_Ref", None)
    voltagem_atual = data.get("Voltage", None)
    corrente_atual = data.get("Current", None)
    potencia_atual = data.get("Power", None)

    # Atualiza o DataFrame com os novos valores
    if temperatura_atual is not None and temperatura_referencia is not None and voltagem_atual is not None and corrente_atual is not None and potencia_atual is not None:
        tempo += 1
        novos_dados = pd.DataFrame({
            "Tempo": [tempo],
            "Temperatura": [temperatura_atual],
            "Temperatura_Referencia": [temperatura_referencia],
            "Voltagem": [voltagem_atual],
            "Corrente": [corrente_atual],
            "Potência": [potencia_atual]
        })
        dados = pd.concat([dados, novos_dados], ignore_index=True)


# Função de callback quando o cliente MQTT se conecta ao broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado ao broker MQTT!")
        client.subscribe(MQTT_TOPIC_DATA)
    else:
        print("Falha na conexão, código de erro: ", rc)


# Conectando ao broker MQTT
client = mqtt.Client()
client.on_message = on_message
client.on_connect = on_connect

try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
except Exception as e:
    st.error(f"Erro ao conectar ao broker MQTT: {e}")
    st.stop()

client.loop_start()

st.title("ESP32 Control Interface")

st.subheader("Sensor Data")

if temperatura_atual is not None:
    st.metric("Temperatura", f"{temperatura_atual} °C")

if temperatura_referencia is not None:
    st.metric("Temperatura de Referência", f"{temperatura_referencia} °C")

if voltagem_atual is not None:
    st.metric("Voltagem", f"{voltagem_atual} V")

if corrente_atual is not None:
    st.metric("Corrente", f"{corrente_atual} A")

if potencia_atual is not None:
    st.metric("Potência", f"{potencia_atual} W")

st.subheader("Control Panel")

# Controles
command = st.selectbox("Comando",
                       ["Ligar", "Desligar", "Fechar Malha", "Abrir Malha", "Definir Temperatura de Referência",
                        "Definir Potência"])
value = st.text_input("Valor")


def enviar_comando(command, value):
    if command == "Ligar":
        client.publish(MQTT_TOPIC_COMMANDS, "TURN_ON")
    elif command == "Desligar":
        client.publish(MQTT_TOPIC_COMMANDS, "TURN_OFF")
    elif command == "Fechar Malha":
        client.publish(MQTT_TOPIC_COMMANDS, "CLOSE_LOOP")
    elif command == "Abrir Malha":
        client.publish(MQTT_TOPIC_COMMANDS, "OPEN_LOOP")
    elif command == "Definir Temperatura de Referência":
        client.publish(MQTT_TOPIC_COMMANDS, f"SET_REF {value}")
    elif command == "Definir Potência":
        client.publish(MQTT_TOPIC_COMMANDS, f"SET_POWER {value}")


if st.button("Enviar Comando"):
    enviar_comando(command, value)

# Gráficos
st.subheader("Gráficos")
if not dados.empty:
    st.line_chart(
        dados.set_index("Tempo")[["Temperatura", "Temperatura_Referencia", "Voltagem", "Corrente", "Potência"]])
