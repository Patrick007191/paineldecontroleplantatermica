import streamlit as st
import requests
import time
import pandas as pd

# Function to get data from ESP32
def get_data():
    esp32_ip = "192.168.15.155"  # Replace with your ESP32 IP address
    try:
        response = requests.get(f"http://{esp32_ip}/data")
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            st.error("Failed to get data from ESP32")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")

# Function to send command to ESP32
def send_command(command, value=None):
    esp32_ip = "192.168.15.155"  # Replace with your ESP32 IP address
    try:
        url = f"http://{esp32_ip}/command"
        payload = {"command": command}
        if value is not None:
            payload["value"] = value
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            st.success(f"Command '{command}' executed successfully.")
        else:
            st.error(f"Failed to execute command '{command}'")
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")

# Page configuration
image_path = "Projeto/images.jpg"
st.set_page_config(page_title="roboblackcat", page_icon=image_path, layout="wide")

st.markdown(
    """
    <style>
    body {
        background-color: #f4f4f4;
        color: #333;
    }
    .title {
        text-align: center;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 20px;
        color: #000;
    }
    .header-img {
        text-align: center;
    }
    .header-img img {
        width: 100px;
        height: 100px;
        margin-bottom: 10px;
    }
    .metrics {
        display: flex;
        justify-content: space-around;
        margin: 30px 0;
        flex-wrap: wrap;
    }
    .metric {
        border: 2px solid #000;
        padding: 10px;
        border-radius: 15px;
        width: 15%;
        text-align: center;
        font-size: 1.2em;
        background-color: #fff;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
        margin: 10px;
    }
    .control-buttons {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    .control-buttons button {
        margin: 10px;
        padding: 15px 30px;
        font-size: 1.2em;
        color: #FFF;
        background-color: #000;
        border: none;
        border-radius: 15px;
        cursor: pointer;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
    }
    .control-buttons button:hover {
        background-color: #444;
    }
    .chart-container {
        margin-top: 70px;
        padding: 20px;
        background-color: #fff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("### ESP32 Data Control and Monitoring Panel")

# Control buttons
st.markdown(
    """
    <div class="control-buttons">
    """,
    unsafe_allow_html=True
)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("Start Plant"):
        send_command("A")

with col2:
    if st.button("Stop Plant"):
        send_command("B")

with col3:
    if st.button("Closed Loop"):
        send_command("MF")

with col4:
    if st.button("Open Loop"):
        send_command("ME")

with col5:
    ref_temp = st.number_input("Reference Temperature (°C)", min_value=0.0, max_value=100.0, step=0.1)
    if st.button("Set Ref. Temp."):
        send_command("R", ref_temp)

st.markdown(
    """
    </div>
    """,
    unsafe_allow_html=True
)

# Initiating line charts for continuous monitoring
placeholder = st.empty()

# Lists to store historical data
timestamps = []
temperatures = []
ref_temperatures = []
powers = []
voltages = []
currents = []

# Continuous update loop
while True:
    data = get_data()
    if data:
        # Updating data
        current_time = time.strftime('%H:%M:%S')
        timestamps.append(current_time)
        temperatures.append(data.get("temperature", 0))
        ref_temperatures.append(ref_temp)  # Use the set reference temperature
        powers.append(data.get("power", 0))
        voltages.append(data.get("voltage", 0))
        currents.append(data.get("current", 0))

        # Creating DataFrame
        df = pd.DataFrame({
            'Time': timestamps,
            'Temperature': temperatures,
            'Reference Temperature': ref_temperatures,
            'Power': powers,
            'Voltage': voltages,
            'Current': currents
        })

        # Displaying real-time data
        with placeholder.container():
            st.markdown("### ESP32 Data")

            # Display metrics
            st.markdown(
                """
                <div class="metrics">
                    <div class="metric">Voltage (V)<br>{}</div>
                    <div class="metric">Current (A)<br>{}</div>
                    <div class="metric">Measured Temperature (°C)<br>{}</div>
                    <div class="metric">Reference Temperature (°C)<br>{}</div>
                    <div class="metric">Power (W)<br>{}</div>
                </div>
                """.format(
                    f"{voltages[-1]:.2f}",
                    f"{currents[-1]:.2f}",
                    f"{temperatures[-1]:.2f}",
                    f"{ref_temperatures[-1]:.2f}",
                    f"{powers[-1]:.2f}"
                ),
                unsafe_allow_html=True
            )

            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.line_chart(df[['Time', 'Temperature', 'Reference Temperature', 'Power']].set_index('Time'), height=500)
            st.markdown("</div>", unsafe_allow_html=True)

        # Wait 1 second before updating again
        time.sleep(1)
    else:
        time.sleep(5)
