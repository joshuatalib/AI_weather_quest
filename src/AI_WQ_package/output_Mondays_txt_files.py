from datetime import datetime, timedelta

dir='/perm/ecm0847/S2S_comp/AI_WEATHER_QUEST_code/AI_weather_quest/src/AI_WQ_package/'

# Define the start and end dates
start_date = datetime(2020, 1, 1)
end_date = datetime(2030, 12, 31)

# Find the first Monday on or after the start_date
current_date = start_date + timedelta(days=(7 - start_date.weekday()) % 7)

# Generate all Mondays in the range
mondays = []
while current_date <= end_date:
    mondays.append(current_date.strftime("%Y%m%d"))
    current_date += timedelta(weeks=1)

# Save the list of Mondays to a text file
with open(dir+"mondays_start_dates.txt", "w") as file:
    file.write("\n".join(mondays))

print("Mondays list has been written to "+dir+"mondays_start_dates.txt")

