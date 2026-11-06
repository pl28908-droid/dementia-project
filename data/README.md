# Data

The project generates a synthetic dataset locally using `python -m src.data.generate_dataset`.

Generated columns:
- `age_group`: broad, simulated age band (not used as a clinical signal)
- `game_type`, `difficulty`
- `accuracy`, `reaction_time_ms`, `mistakes`, `completion_time_sec`
- `previous_score`, `score`
- `performance_band`: rule-generated development target

The target is deliberately a software-demo label. It is not a diagnosis or validated cognitive assessment.
