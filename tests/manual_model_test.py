from src.models.race_prediction import RacePredictionRow
import pytest

def test_model_validation():
    # Valid row data based on DataSchema.md example
    valid_data = {
        'race_id': 1654000,
        'session_code': 'MEX0103_SPRINT',
        'target_session': 'Sprint',
        'is_sprint_weekend': True,
        'season': 2024,
        'race_num': 20,
        'track_id': 'mexico',
        'total_laps': 24,
        'driver_tla': 'VER',
        'team_name': 'Red Bull',
        'fp_best_time': 78.341,
        'fp_position': 2,
        'quali_pos': 3,
        'quali_best_time': 77.856,
        'quali_gap_pole': 0.215,
        'starting_grid': 3,
        'sprint_result': None,
        'sprint_points': None,
        'air_temp': 28.3,
        'track_temp': 42.5,
        'humidity': 45.2,
        'rainfall': 0.0,
        'champ_pos': 1,
        'champ_points': 393,
        'last_3_avg': 1.67,
        'finishing_position': 2
    }
    
    # Should validate without error
    row = RacePredictionRow(**valid_data)
    assert row.driver_tla == 'VER'
    assert row.is_sprint_weekend is True
    
    # Validate alias usage
    assert row.championship_pos == 1
    assert row.last_3_avg_position == 1.67

if __name__ == "__main__":
    test_model_validation()
    print("Model validation test passed!")
