import fastf1

def get_session_weather(session):
    weather = session.weather_data()
    air_temp = weather['AirTemperature'].mean()
    track_temp = weather['TrackTemperature'].mean()
    humidity = weather['Humidity'].mean()
    pressure = weather['Pressure'].mean()
    rainfall = weather['Rainfall'].sum() # mean rainfall doent work as most might be 0
    
    return {
        'air_temp': air_temp,
        'track_temp': track_temp,
        'humidity': humidity,
        'pressure': pressure,
        'rainfall': rainfall
        }


for season in range(2024, 2026):
    events = fastf1.get_event_schedule(season)
    for _, event in events[1:].iterrows():
        print(f"Downloading data for {event['Location']} {season}...")
        race_session = fastf1.get_session(season, event['Location'], 'Race')
        race_session.load(weather=True)
        pratice_session = fastf1.get_session(season, event['Location'], 'Practice')
        pratice_session.load()
        target_session = "Race"
        race_no = event['RoundNumber']
        track = event['Location']
        total_laps = race_session.total_laps

        # driver specific data
        # driver_tla = driver abbreviation
        # team_name = team name
        # fp_best_time = best practice time
        # fp_position = practice position
        # quali_pos = qualifying position
        # quali_best_time = best qualifying time
        # quali_gap_pole = gap to pole position
        # starting_grid = starting grid position
        # sprint_result = sprint result
        # sprint_points = sprint points
        # champ_pos = championship position
        # champ_points = championship points

        if "sprint" in event['EventFormat']:
            sprint_session = fastf1.get_session(season, event['Location'], 'Sprint')
            sprint_session.load(weather=True)
            target_session = "Sprint"
            is_sprint = True
        else:
            is_sprint = False