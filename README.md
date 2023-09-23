# axpert-monitor-sender

## Motivation

This repository is designed to retrieve inverter data from Voltronic and send that data to an MQTT server in Home Assistant.

I tried to use this repository [docker-voltronic-homeassistant](https://github.com/ned-kelly/docker-voltronic-homeassistant), but unfortunately, I received an error when communicating with the inverter. After days of research to fix the error, I created this basic Python script that uses the following library to get the data: [axpert-monitor](https://github.com/b48736/axpert-monitor).

## Usage

1. **Download and Install axpert-monitor**

   - Download the [axpert-monitor repository](https://github.com/b48736/axpert-monitor).
   - Follow the installation guide provided in that repository.

2. **Copy the Python Script**

   Copy the Python script `axpert_monitor_sender.py` to the directory where the `axpert-query` command is installed.

3. **Add Execution Permissions**

   Add execution permissions to `axpert-query.js` using the following command:

   ```bash
   chmod +x axpert-query.js
   ```

4. **To run the script, use the following command:**

```bash
python3 axpert_monitor_sender.py --client_id voltronic_bridge --mqtt_username <user> --mqtt_password <pass> --broker_address <address> --broker_port 8883 --topic homeassistant --device_name voltronic --command "<your_command>" --expiration_client_minutes 5 --data_batch_sleep_seconds 5 --data_batch_sleep_seconds_on_error 60
```

Replace the following placeholders with the appropriate values:

- `--client_id`: Set this to your desired MQTT client ID.
- `--mqtt_username`: Provide your MQTT username for authentication.
- `--mqtt_password`: Provide your MQTT password for authentication.
- `--broker_address`: Specify the address of your MQTT broker.
- `--topic`: Set the MQTT topic to which you want to publish the data.
- `--device_name`: Define the name of the device (e.g., "voltronic").
- `--command`: Specify the command to retrieve data from the inverter. For example, use "./axpert-query -c QPIGS" to fetch data. Note that only the "QPIGS" command is supported at the moment.

Optional Arguments with Default Values:

- `--expiration_client_minutes` (default: 5 minutes): This argument reloads the connection within the specified range to avoid connection issues.
- `--data_batch_sleep_seconds` (default: 30 seconds): Set the time between data batches in seconds.
- `--data_batch_sleep_seconds_on_error` (default: 30 seconds): Set the time between data batches on error in seconds.

Please ensure that you adjust these arguments according to your specific configuration and requirements.


## Test

You can use script `get_data_sample.sh` as command  to simulate what data is recieved from the inverter.

```bash
--command "./get_data_sample.sh"
```
