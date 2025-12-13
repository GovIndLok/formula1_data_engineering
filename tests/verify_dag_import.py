
import sys
from pathlib import Path

# Add project root to sys.path so that imports within the DAG work
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from airflow.models import DagBag
    from dags.f1_data_pipeline import dag
    
    print(f"Successfully imported DAG: {dag.dag_id}")
    
    # Check for cycles
    dag.validate()
    print("DAG validation passed (no cycles)")
    
    # Print task structure to verify parallel tasks
    print("\nTask Structure:")
    for task in dag.tasks:
        print(f" - {task.task_id} ({task.task_type})")
        
except Exception as e:
    print(f"Failed to load DAG: {e}")
    sys.exit(1)
