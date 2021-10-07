from task.fleet_tracking import TrackCharacterFleet
from api import Fleet, Character

if __name__ == '__main__':
    user = 5
    character = Character.get(1416973491)
    fleet_task = TrackCharacterFleet(character)

    t = Fleet()
    fleet_task.start()