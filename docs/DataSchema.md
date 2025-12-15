## **Simple Data Table - Sprint Weekend Example**

Here's what **2 rows** for **1 driver** in a **sprint weekend** should look like:

| race_id | session_code | target_session | is_sprint | season | race_num | track_id | total_laps | driver_tla | team_name | fp_best_time | fp_position | quali_pos | quali_best_time | quali_gap_pole | starting_grid | sprint_result | sprint_points | air_temp | track_temp | humidity | rainfall | champ_pos | champ_points | last_3_avg | **finishing_position** |
|---------|--------------|----------------|-----------|--------|----------|----------|------------|------------|-----------|--------------|-------------|-----------|-----------------|----------------|---------------|---------------|---------------|----------|------------|----------|----------|-----------|--------------|------------|------------------------|
| 1654000 | MEX0103_SPRINT | Sprint | True | 2024 | 20 | mexico | 24 | VER | Red Bull | 78.341 | 2 | 3 | 77.856 | 0.215 | 3 | NULL | NULL | 28.3 | 42.5 | 45.2 | 0.0 | 1 | 393 | 1.67 | **2** ← TARGET |
| 1654001 | MEX0103_RACE | Race | True | 2024 | 20 | mexico | 71 | VER | Red Bull | 78.341 | 2 | 1 | 77.523 | 0.000 | 2 | 2 | 7 | 29.1 | 45.2 | 43.8 | 0.0 | 1 | 400 | 1.67 | **1** ← TARGET |

---

## **Breaking Down Each Row**

### **Row 1: Predicting Sprint Race**
```
You're trying to predict: What position will Verstappen finish in the SPRINT race?

Features you have BEFORE the sprint:
- Practice session (FP1)
- Sprint Qualifying result
- Weather
- Championship standings
- Recent form

Target: Sprint finishing position = 2
```

### **Row 2: Predicting Main Race**
```
You're trying to predict: What position will Verstappen finish in the MAIN race?

Features you have BEFORE the main race:
- Practice session (FP1)
- Sprint Qualifying result
- Main Qualifying result
- Sprint Race result (position 2) ← This is now a FEATURE
- Weather
- Championship standings (updated after sprint)
- Recent form

Target: Main race finishing position = 1
```

---

## **Normal Weekend Example (Simpler - Only 1 Row per Driver)**

| race_id | session_code | target_session | is_sprint | season | race_num | track_id | total_laps | driver_tla | team_name | fp_best_time | fp_position | quali_pos | quali_best_time | quali_gap_pole | starting_grid | sprint_result | sprint_points | air_temp | track_temp | champ_pos | last_3_avg | **finishing_position** |
|---------|--------------|----------------|-----------|--------|----------|----------|------------|------------|-----------|--------------|-------------|-----------|-----------------|----------------|---------------|---------------|---------------|----------|------------|-----------|------------|------------------------|
| 1238001 | USA0101_RACE | Race | False | 2024 | 19 | austin | 56 | HAM | Mercedes | 95.234 | 5 | 4 | 94.812 | 0.412 | 4 | NULL | NULL | 26.5 | 38.7 | 3 | 3.33 | **3** ← TARGET |

```
Simpler! Only predicting the main race.

Features you have:
- Practice session (FP3)
- Qualifying result
- Weather
- Championship standings
- Recent form

Target: Race finishing position = 3
```

---

## **Minimal Column List (Priority 1 & 2)**

Here's the **bare minimum** you need to collect:

### **Identifiers (8 columns)**
1. `race_id` - Modified ID (1654000, 1654001)
2. `session_code` - Human readable (MEX0103_SPRINT)
3. `target_session` - "Sprint" or "Race"
4. `is_sprint_weekend` - True/False
5. `season` - 2024, 2025
6. `race_num` - Round number (1-24)
7. `track_id` - monaco, spa, austin
8. `total_laps` - 24 for sprint, 56-71 for race

### **Driver/Team (2 columns)**
9. `driver_tla` - VER, HAM, NOR
10. `team_name` - Red Bull, Mercedes

### **Practice (2 columns)**
11. `fp_best_time` - Best practice lap (seconds)
12. `fp_position` - Practice position (1-20)

### **Qualifying (3 columns)**
13. `quali_pos` - Qualifying position
14. `quali_best_time` - Best quali lap
15. `quali_gap_pole` - Gap to pole (seconds)

### **Starting Grid (1 column)**
16. `starting_grid` - Actual starting position

### **Sprint Data (2 columns - NULL if target is Sprint)**
17. `sprint_result` - Sprint finishing position
18. `sprint_points` - Sprint points (8-7-6-5-4-3-2-1)

### **Weather (4 columns)**
19. `air_temp` - Air temperature
20. `track_temp` - Track temperature
21. `humidity` - Humidity %
22. `rainfall` - Rainfall amount

### **Championship Context (2 columns)**
23. `championship_pos` - Driver's championship position
24. `championship_points` - Driver's total points

### **Recent Form (1 column)**
25. `last_3_avg_position` - Average position last 3 races

### **Target (1 column)**
26. `finishing_position` - **THIS IS WHAT YOU'RE PREDICTING**

---

## **Total: 26 Columns**

That's it! Just **26 columns** to start with.

---

## **CSV Example (3 Drivers, Sprint Weekend)**

```csv
race_id,session_code,target_session,is_sprint,season,race_num,track_id,total_laps,driver_tla,team_name,fp_best_time,fp_position,quali_pos,quali_best_time,quali_gap_pole,starting_grid,sprint_result,sprint_points,air_temp,track_temp,humidity,rainfall,champ_pos,champ_points,last_3_avg,finishing_position
1654000,MEX0103_SPRINT,Sprint,True,2024,20,mexico,24,VER,Red Bull,78.341,2,3,77.856,0.215,3,,,28.3,42.5,45.2,0.0,1,393,1.67,2
1654001,MEX0103_RACE,Race,True,2024,20,mexico,71,VER,Red Bull,78.341,2,1,77.523,0.000,2,2,7,29.1,45.2,43.8,0.0,1,400,1.67,1
1654000,MEX0103_SPRINT,Sprint,True,2024,20,mexico,24,NOR,McLaren,78.523,3,1,77.641,0.000,1,,,28.3,42.5,45.2,0.0,2,331,2.33,1
1654001,MEX0103_RACE,Race,True,2024,20,mexico,71,NOR,McLaren,78.523,3,2,77.689,0.166,1,1,8,29.1,45.2,43.8,0.0,2,339,2.00,2
1654000,MEX0103_SPRINT,Sprint,True,2024,20,mexico,24,LEC,Ferrari,78.812,5,5,78.123,0.482,5,,,28.3,42.5,45.2,0.0,3,307,3.67,4
1654001,MEX0103_RACE,Race,True,2024,20,mexico,71,LEC,Ferrari,78.812,5,3,77.734,0.211,4,4,5,29.1,45.2,43.8,0.0,3,312,3.50,3
```

---

## **Key Things to Notice**

### **1. Sprint Result Column**
- **Empty/NULL** when `target_session = "Sprint"` (you're predicting it!)
- **Filled in** when `target_session = "Race"` (it becomes a feature)

### **2. Starting Grid**
- For **Sprint rows**: `starting_grid` = `quali_pos` (from sprint qualifying)
- For **Race rows** (sprint weekend): `starting_grid` = `sprint_result` (sprint determines race grid)
- For **Race rows** (normal weekend): `starting_grid` = `quali_pos` (qualifying determines race grid)

### **3. Championship Points**
- **Sprint rows**: Points BEFORE sprint
- **Race rows**: Points AFTER sprint (if sprint weekend)

### **4. Practice Data**
- **Sprint weekends**: Use FP1 data
- **Normal weekends**: Use FP3 data

---

## **Code to Create One Row (Pseudo-code)**

```python
# Sprint weekend - Sprint row
sprint_row = {
    'race_id': 1654000,
    'session_code': 'MEX0103_SPRINT',
    'target_session': 'Sprint',
    'is_sprint': True,
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
    'starting_grid': 3,  # From sprint quali
    'sprint_result': None,  # We're predicting this!
    'sprint_points': None,
    'air_temp': 28.3,
    'track_temp': 42.5,
    'humidity': 45.2,
    'rainfall': 0.0,
    'champ_pos': 1,
    'champ_points': 393,
    'last_3_avg': 1.67,
    'finishing_position': 2  # TARGET
}

# Sprint weekend - Main race row
race_row = {
    'race_id': 1654001,
    'session_code': 'MEX0103_RACE',
    'target_session': 'Race',
    'is_sprint': True,
    'season': 2024,
    'race_num': 20,
    'track_id': 'mexico',
    'total_laps': 71,
    'driver_tla': 'VER',
    'team_name': 'Red Bull',
    'fp_best_time': 78.341,
    'fp_position': 2,
    'quali_pos': 1,  # Main qualifying position
    'quali_best_time': 77.523,
    'quali_gap_pole': 0.000,
    'starting_grid': 2,  # From SPRINT result, not quali!
    'sprint_result': 2,  # Now a feature!
    'sprint_points': 7,  # P2 in sprint = 7 points
    'air_temp': 29.1,
    'track_temp': 45.2,
    'humidity': 43.8,
    'rainfall': 0.0,
    'champ_pos': 1,
    'champ_points': 400,  # Updated after sprint
    'last_3_avg': 1.67,
    'finishing_position': 1  # TARGET
}
```

---
