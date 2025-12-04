import fastf1


for session in range(2024, 2026):
    events = fastf1.get_event_schedule(session)
    for _, event in events[1:].iterrows():
        print(f"Downloading data for {event['EventName']} {session}...")
        try:
            fastf1.get_session(session, event['EventName'], 'R').load()
        except Exception as e:
            print(f"Failed to download data for {event['EventName']} {session}: {e}")
        