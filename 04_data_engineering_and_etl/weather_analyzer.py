# ==============================================================================
# WEATHER DATA CLI ANALYZER
# A Command Line Interface utility for loading, querying, and filtering 
# historical weather data stored in JSON format.
# ==============================================================================

import datetime
import json

# Mapping internal JSON keys to human-readable labels
weather_fields = {
    'weather_main': 'Main Weather',
    'weather_description': 'Weather Description',
    'temp': 'Temperature',
    'feels_like': 'Feels Like',
    'pressure': 'Pressure',
    'humidity': 'Humidity',
    'wind_speed': 'Wind Speed',
    'name': 'City',
    'date': 'Date',
}

fields_list = list(weather_fields.values())

def get_command():
    """Prompts the user for a command and splits it into arguments."""
    return input(" - - - Input command : ").split()

def log_to_file(output_file, message):
    """Prints a message to the console and appends it to the specified log file."""
    print(message)
    with open(output_file, 'a') as file:
        file.write(message + '\n')

def format_record(record):
    """Formats a single weather record dictionary into a readable string."""
    return (f"{record['name']} ({record['date'].strftime('%Y-%m-%d')}):\n"
            f"\t Main Weather: {record['weather_main']}\n"
            f"\t Weather Description: {record['weather_description']}\n"
            f"\t Temperature: {record['temp']}°C\n"
            f"\t Feels Like: {record['feels_like']}°C\n"
            f"\t Wind Speed: {record['wind_speed']} m/s\n"
            f"\t Humidity: {record['humidity']}%\n"
            f"\t Pressure: {record['pressure']} hPa\n")

def filter_by_city_and_date(data, city=None, date=None):
    """Filters weather records by an exact city name and specific date."""
    filtered_data = []
    if city and date:
        filtered_data = [record for record in data if record['name'] == city and record['date'] == date]
    elif city:
        filtered_data = [record for record in data if record['name'] == city]
    elif date:
        filtered_data = [record for record in data if record['date'] == date]
    else:
        return data
    return filtered_data

def filter_by_city_and_date_range(data, city=None, date_range=None):
    """Filters weather records by city name and a specific chronological date range."""
    filtered_data = []
    if city and date_range:
        filtered_data = [record for record in data if record['name'] == city and date_range[0] <= record['date'] <= date_range[1]]
    elif city:
        filtered_data = [record for record in data if record['name'] == city]
    elif date_range:
        filtered_data = [record for record in data if date_range[0] <= record['date'] <= date_range[1]]
    else:
        return data
    return filtered_data

def calculate_average_property(data, property_name, city=None, date_range=None):
    """Calculates the average value of a specific numerical property within filtered data."""
    filtered_data = filter_by_city_and_date_range(data, city, date_range)
    if not filtered_data:
        return 0
    total = sum(record[property_name] for record in filtered_data)
    return total / len(filtered_data)

def load_data(file_name):
    """
    Loads and parses weather data from a JSON file.
    Converts string dates to datetime objects and strictly types numerical fields.
    """
    records = []
    with open(file_name, 'r') as file:
        weather_data = json.load(file)

        for entry in weather_data:
            new_entry = entry
            new_entry['date'] = datetime.datetime.strptime(entry['date'], '%Y-%m-%d')
            new_entry['temp'] = float(entry['temp'])
            new_entry['weather_main'] = str(entry['weather_main'])
            new_entry['weather_description'] = str(entry['weather_description'])
            new_entry['feels_like'] = float(entry['feels_like'])
            new_entry['wind_speed'] = float(entry['wind_speed'])
            new_entry['humidity'] = float(entry['humidity'])
            new_entry['pressure'] = float(entry['pressure'])
            records.append(new_entry)
    return records

def find_min_property(data, property_name, city=None, date_range=None):
    """Finds the record containing the minimum value for a specific property."""
    filtered_data = filter_by_city_and_date_range(data, city, date_range)
    return min(filtered_data, key=lambda record: record[property_name], default=None)

def find_max_property(data, property_name, city=None, date_range=None):
    """Finds the record containing the maximum value for a specific property."""
    filtered_data = filter_by_city_and_date_range(data, city, date_range)
    return max(filtered_data, key=lambda record: record[property_name], default=None)

def find_records_with_property_equal(data, property_name, value, date_range=None):
    """Extracts records where a specific string property exactly matches a target value."""
    filtered_data = filter_by_city_and_date_range(data, None, date_range)
    return [record for record in filtered_data if str(record[property_name]) == value]

def find_records_with_property_less_than(data, property_name, value, date_range=None):
    """Extracts records where a specific numerical property is less than a target value."""
    filtered_data = filter_by_city_and_date_range(data, None, date_range)
    return [record for record in filtered_data if record[property_name] < value]

def find_records_with_property_greater_than(data, property_name, value, date_range=None):
    """Extracts records where a specific numerical property is strictly greater than a target value."""
    filtered_data = filter_by_city_and_date_range(data, None, date_range)
    return [record for record in filtered_data if record[property_name] > value]

def weather_console(data_file, output_file):
    """Main CLI Read-Eval-Print Loop (REPL) for querying the weather database."""
    data = load_data(data_file)
    print(" - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n"
          " - - - - - - - - - - - - - - - - - - Menu: - - - - - - - - - - - - - - - - - \n"
          " - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n"
          " - - - get_by_city_and_date <city> <date>                              - - - \n"
          " - - - get_by_city_and_date_range <city> <start_date> <end_date>       - - - \n"
          " - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n"
          " - - - get_avg_property <property> <city> <start_date> <end_date>      - - - \n"
          " - - - get_min_property <property> <city> <start_date> <end_date>      - - - \n"
          " - - - get_max_property <property> <city> <start_date> <end_date>      - - - \n"
          " - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n"
          " - - - get_equal <property> <value> <start_date> <end_date>            - - - \n"
          " - - - get_less_than <property> <value> <start_date> <end_date>        - - - \n"
          " - - - get_more_than <property> <value> <start_date> <end_date>        - - - \n"
          " - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n"
          " - - - exit                                                            - - - \n"
          " - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n"
          " - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n")

    while True:
        cmd = get_command()
        try:
            if not cmd:
                continue

            log_to_file(output_file, f" - - - Command: {' '.join(cmd)}\n")

            if cmd[0] == "get_by_city_and_date":
                city = cmd[1]
                date = datetime.datetime.strptime(cmd[2], '%Y-%m-%d')
                result = filter_by_city_and_date(data, city, date)
                if not result:
                    log_to_file(output_file, "Empty data for this request\n")
                else:
                    for record in result:
                        log_to_file(output_file, format_record(record))

            elif cmd[0] == "get_by_city_and_date_range":
                city = cmd[1]
                dateRange = (datetime.datetime.strptime(cmd[2], '%Y-%m-%d'),
                             datetime.datetime.strptime(cmd[3], '%Y-%m-%d'))
                result = filter_by_city_and_date_range(data, city, dateRange)
                if not result:
                    log_to_file(output_file, "Empty data for this request\n")
                else:
                    for record in result:
                        log_to_file(output_file, format_record(record))

            elif cmd[0] == "get_min_property":
                propertyName = cmd[1]
                city = None
                dateRange = None
                if len(cmd) > 2:
                    city = cmd[2]
                if len(cmd) > 3:
                    dateRange = (datetime.datetime.strptime(cmd[3], '%Y-%m-%d'),
                                 datetime.datetime.strptime(cmd[4], '%Y-%m-%d'))
                result = find_min_property(data, propertyName, city, dateRange)
                if result is None:
                    log_to_file(output_file, "Empty data for this request\n")
                else:
                    log_to_file(output_file, format_record(result))

            elif cmd[0] == "get_max_property":
                propertyName = cmd[1]
                city = None
                dateRange = None
                if len(cmd) > 2:
                    city = cmd[2]
                if len(cmd) > 3:
                    dateRange = (datetime.datetime.strptime(cmd[3], '%Y-%m-%d'),
                                 datetime.datetime.strptime(cmd[4], '%Y-%m-%d'))
                result = find_max_property(data, propertyName, city, dateRange)
                if result is None:
                    log_to_file(output_file, "Empty data for this request\n")
                else:
                    log_to_file(output_file, format_record(result))

            elif cmd[0] == "get_avg_property":
                propertyName = cmd[1]
                city = None
                dateRange = None
                if len(cmd) > 2:
                    city = cmd[2]
                if len(cmd) > 3:
                    dateRange = (datetime.datetime.strptime(cmd[3], '%Y-%m-%d'),
                                 datetime.datetime.strptime(cmd[4], '%Y-%m-%d'))
                result = calculate_average_property(data, propertyName, city, dateRange)
                if result is None:
                    log_to_file(output_file, "Empty data for this request\n")
                else:
                    log_to_file(output_file, f"Average {propertyName}: {result:.2f}\n")

            elif cmd[0] == "get_less_than":
                propertyName = cmd[1]
                value = float(cmd[2])
                dateRange = None
                if len(cmd) > 3:
                    dateRange = (datetime.datetime.strptime(cmd[3], '%Y-%m-%d'),
                                 datetime.datetime.strptime(cmd[4], '%Y-%m-%d'))
                result = find_records_with_property_less_than(data, propertyName, value, dateRange)
                if not result:
                    log_to_file(output_file, "Empty data for this request\n")
                else:
                    for record in result:
                        log_to_file(output_file, format_record(record))

            elif cmd[0] == "get_more_than":
                propertyName = cmd[1]
                value = float(cmd[2])
                dateRange = None
                if len(cmd) > 3:
                    dateRange = (datetime.datetime.strptime(cmd[3], '%Y-%m-%d'),
                                 datetime.datetime.strptime(cmd[4], '%Y-%m-%d'))
                result = find_records_with_property_greater_than(data, propertyName, value, dateRange)
                if not result:
                    log_to_file(output_file, "Empty data for this request\n")
                else:
                    for record in result:
                        log_to_file(output_file, format_record(record))

            elif cmd[0] == "get_equal":
                propertyName = cmd[1]
                value = str(cmd[2])
                dateRange = None
                if len(cmd) > 3:
                    dateRange = (datetime.datetime.strptime(cmd[3], '%Y-%m-%d'),
                                 datetime.datetime.strptime(cmd[4], '%Y-%m-%d'))
                result = find_records_with_property_equal(data, propertyName, value, dateRange)
                if not result:
                    log_to_file(output_file, "Empty data for this request\n")
                else:
                    for record in result:
                        log_to_file(output_file, format_record(record))

            elif cmd[0] == "exit":
                print("Terminating CLI application...")
                break

            else:
                log_to_file(output_file, "Invalid command\n")

        except Exception as e:
            log_to_file(output_file, f"Error: {e}\n")


# === Script Execution Entry Point ===
if __name__ == "__main__":
    weather_console('weather_data.json', 'weather_results.log')