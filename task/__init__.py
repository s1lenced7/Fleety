from .fleet_tracking import TrackCharacterFleet

TASKS = {}


def start_fleet_task(user, character, **kwargs):
    key = f'{user.id}.{character.id}'
    existing_task = TASKS.get(key)
    if existing_task:
        return

    fleet_task = TrackCharacterFleet(user.id, character.id, **kwargs)
    TASKS[key] = fleet_task
    fleet_task.start()