from task.fleet_tracking import TrackCharacterFleet
from api.calls.character import CharacterFromID
from data_structures.fleet.fleet import Fleet

if __name__ == '__main__':
    character = CharacterFromID.get(1416973491)
    fleet_task = TrackCharacterFleet(character)

    t = Fleet()
    fleet_task.start()