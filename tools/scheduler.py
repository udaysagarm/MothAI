from datetime import datetime
from langchain.tools import tool
from scheduler_engine import get_scheduler, execute_scheduled_task

@tool
def schedule_task(task_description: str, trigger_type: str, time_value: str) -> str:
    """
    Schedules a task to run in the background.
    
    Args:
        task_description: The detailed prompt of what the agent should do (e.g. "Send email to John saying Hello").
        trigger_type: 'date' (one-off at specific time) or 'interval' (recurring) or 'cron' (specific daily time).
        time_value: 
            - For 'date': "YYYY-MM-DD HH:MM:SS"
            - For 'interval': "hours=X" or "minutes=X" (e.g. "hours=2")
            - For 'cron': "hour=X, minute=X" (e.g. "hour=8, minute=30")
    """
    scheduler = get_scheduler()
    
    try:
        if trigger_type == 'date':
            run_date = datetime.strptime(time_value, "%Y-%m-%d %H:%M:%S")
            job = scheduler.add_job(
                execute_scheduled_task, 
                'date', 
                run_date=run_date, 
                args=[task_description]
            )
            return f"Scheduled task '{task_description}' for {run_date}."

        elif trigger_type == 'interval':
            # rudimentary parsing for "hours=X" or "minutes=X"
            kwargs = {}
            parts = time_value.split(',')
            for part in parts:
                unit, val = part.strip().split('=')
                kwargs[unit] = int(val)
            
            job = scheduler.add_job(
                execute_scheduled_task, 
                'interval', 
                args=[task_description], 
                **kwargs
            )
            return f"Scheduled recurring task '{task_description}' every {time_value}."

        elif trigger_type == 'cron':
            # rudimentary parsing for "hour=X, minute=X"
            kwargs = {}
            parts = time_value.split(',')
            for part in parts:
                unit, val = part.strip().split('=')
                kwargs[unit] = int(val)
                
            job = scheduler.add_job(
                execute_scheduled_task, 
                'cron', 
                args=[task_description], 
                **kwargs
            )
            return f"Scheduled daily task '{task_description}' at {time_value}."
            
        else:
            return f"Unknown trigger_type: {trigger_type}. Use 'date', 'interval', or 'cron'."

    except Exception as e:
        return f"Error scheduling task: {e}"
