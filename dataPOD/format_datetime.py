import datetime
from dateutil import parser

def format_datetime(date_str, time_str):
    # Parse date
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y/%m/%d").date()
        except ValueError:
            try:
                date_obj = datetime.datetime.strptime(date_str, "%d/%m/%Y").date()
            except ValueError:
                try:
                    date_obj = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
                except ValueError:
                    try:
                        date_obj = parser.parse(date_str).date() if date_str else datetime.datetime.now().date()
                    except parser.ParserError:
                        return None  # Return None if the date cannot be parsed

    # Parse time
    if time_str.strip():  # Check if time_str is not an empty string
        try:
            time_obj = datetime.datetime.strptime(time_str, "%H:%M:%S").time()
        except ValueError:
            try:
                time_obj = datetime.datetime.strptime(time_str, "%I:%M %p").time()
            except ValueError:
                try:
                    time_obj = datetime.datetime.strptime(time_str, "%I:%M:%S %p").time()
                except ValueError:
                    try:
                        time_obj = parser.parse(time_str).time()
                    except parser.ParserError:
                        return None  # Return None if the time cannot be parsed
    else:
        time_obj = datetime.time(0, 0, 0)

    datetime_obj = datetime.datetime.combine(date_obj, time_obj)
    formatted_datetime_str = datetime_obj.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return formatted_datetime_str