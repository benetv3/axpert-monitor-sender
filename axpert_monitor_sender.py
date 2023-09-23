import paho.mqtt.client as mqtt
import ssl
import time
import json
import datetime
import subprocess
import argparse


# Create an MQTT client instance
def create_mqtt_client(args):
    client = mqtt.Client(client_id=args.client_id)
    client.username_pw_set(args.mqtt_username, args.mqtt_password)
    client.tls_set_context(ssl.SSLContext(ssl.PROTOCOL_TLSv1_2))
    client.on_connect = on_connect
    client.connect(args.broker_address, args.broker_port)
    client.loop_start()
    return client


def on_connect(client, userdata, flags, rc):
    if rc != 0:
        print("Connection failed with error code " + str(rc))


def publish_message(client, topic_input, message):
    result = client.publish(topic_input, message)
    if result.rc != mqtt.MQTT_ERR_SUCCESS:
        print("Failed to publish message with error code " + str(result.rc))


def get_data(args):
    command = args.command

    # Execute the command and capture the output
    output = subprocess.check_output(command, shell=True)

    response = output.decode('utf-8')

    # Find the position of the first curly brace indicating the start of the JSON object
    json_start = response.find('{')

    # Extract the JSON part of the response
    json_data = response[json_start:]

    # Parse the JSON data
    data = json.loads(json_data)

    return data


def init_topic(client, args, data):
    sensor_name = data[0]
    unit_of_measurement = data[1]
    icon = data[2]

    topic_sensor = f"{args.topic}/sensor/{args.device_name}_{sensor_name}"

    data = {
        "name": f"{args.device_name}_{sensor_name}",
        "unit_of_measurement": unit_of_measurement,
        "state_topic": f"{topic_sensor}",
        "icon": f"mdi:{icon}"
    }

    publish_message(client, f"{topic_sensor}/config", json.dumps(data, indent=4))


def publish_data(client, args, sensor_name, value):
    topic_sensor = f"{args.topic}/sensor/{args.device_name}_{sensor_name}"

    publish_message(client, topic_sensor, value)


param_names = {
    "gridVoltage": ["AC_grid_voltage", "V", "power-plug"],
    "gridFrequency": ["AC_grid_frequency", "Hz", "current-ac"],
    "outputVoltage": ["AC_out_voltage", "V", "power-plug"],
    "outputFrequency": ["AC_out_frequency", "Hz", "current-ac"],
    "pvInputVoltage": ["PV_in_voltage", "V", "solar-panel-large"],
    "pvPower": ["PV_in_watts", "W", "solar-panel-large"],
    "outputPowerActive": ["Load_watt", "W", "chart-bell-curve"],
    "outputPowerApparent": ["Load_va", "VA", "chart-bell-curve"],
    "busVoltage": ["Bus_voltage", "V", "details"],
    "temperature": ["Heatsink_temperature", "", "details"],
    "batteryCapacity": ["Battery_capacity", "%", "battery-outline"],
    "batteryVoltage": ["Battery_voltage", "V", "battery-outline"],
    "batteryChargingCurrent": ["Battery_charge_current", "A", "current-dc"],
    "batteryDischargeCurrent": ["Battery_discharge_current", "A", "current-dc"],
    "batteryVoltageSCC": ["SCC_voltage", "V", "current-dc"],
    "timeSentMessage": ["message_sent", "", "clock"],
}


def get_next_expiration_client(args):
    next_expiration = datetime.datetime.now()

    next_expiration = next_expiration + datetime.timedelta(minutes=args.expiration_client_minutes)

    return next_expiration


def get_and_process_data(client, args):
    data = get_data(args)

    for entityKey, entityValue in data.items():

        param_name = param_names.get(entityKey, None)

        if param_name is not None:
            publish_data(client, args, param_name[0], entityValue)

    publish_data(client, args, param_names['timeSentMessage'][0], int(time.time()))

    time.sleep(args.data_batch_sleep_seconds)


def init_topic_data(client, args):
    for _, entity in param_names.items():
        init_topic(client, args, entity)


def main(args):
    client = create_mqtt_client(args)

    init_topic_data(client, args)

    next_expiration = get_next_expiration_client(args)

    while True:

        try:
            if datetime.datetime.now() > next_expiration:
                client.disconnect()
                client = create_mqtt_client(args)
                init_topic_data(client, args)
                next_expiration = get_next_expiration_client(args)

            get_and_process_data(client, args)
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(args.data_batch_sleep_seconds_on_error)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MQTT Client with Constants as Arguments')
    parser.add_argument('--client_id', required=True, help='MQTT client ID')
    parser.add_argument('--mqtt_username', required=True, help='MQTT username')
    parser.add_argument('--mqtt_password', required=True, help='MQTT password')
    parser.add_argument('--broker_address', required=True, help='MQTT broker address')
    parser.add_argument('--broker_port', required=True, type=int, help='MQTT broker port')
    parser.add_argument('--topic', required=True, help='MQTT topic')
    parser.add_argument('--device_name', required=True, help='Device name')
    parser.add_argument('--command', default='./get_data.sh', help='Command to execute for data retrieval')
    parser.add_argument('--expiration_client_minutes', type=int, default=5, help='Expiration client (in minutes)')
    parser.add_argument('--data_batch_sleep_seconds', type=int, default=30, help='Sleep time between data batches ('
                                                                                 'seconds)')
    parser.add_argument('--data_batch_sleep_seconds_on_error', type=int, default=30, help='Sleep time between data '
                                                                                          'batches on error (seconds)')
    main(parser.parse_args())
