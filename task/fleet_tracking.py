from datetime import datetime
from .task import Task, TaskCreationException, TaskAbortException

from api import FleetFromCharacterID, FleetFromID, ParticipationsFromFleetID
from api.data_structures import User, Character, Fleet


class TrackCharacterFleet(Task):
    MAX_CONSECUTIVE_FAILURES = 5

    def __init__(self, user: User, character: Character, **kwargs):
        super().__init__(**kwargs)
        self.execution_failures = 0

        self.character = character

        # Try and get the auth_token
        self.auth_token = character.get_auth_token()
        if not self.auth_token:
            raise TaskCreationException('Failed to create task, could not locate auth_token', task=self)

        # Fetch Fleet ID from character
        character_fleet = FleetFromCharacterID.get(self.character.id, self.auth_token)
        if not character_fleet:
            raise Exception('Failed to create task, character is not in fleet')

        # Fetch Fleet from API
        api_fleet = FleetFromID.get(character_fleet.id, self.auth_token)
        if not api_fleet:
            raise Exception('Failed to create task, failed to fetch fleet info')
        self.fleet = api_fleet

        db_fleet = next(Fleet.from_db(id=character_fleet.id), None)
        if db_fleet and api_fleet == db_fleet:
            print('Found existing fleet in db, extending fleet')
            self.fleet = db_fleet

        self.fleet.user_id = user.id
        self.fleet.update()
        self.fleet.write_to_db()

    def execute(self):
        if self.execution_failures >= self.MAX_CONSECUTIVE_FAILURES:
            print(f'[{datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}] Task aborting, failed to many times!')
            self.stop()
            return

        print(f'[{datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}] Executing task')
        try:
            # Update fleet
            fetched_fleet = FleetFromID.get(self.fleet.id, self.auth_token)
            if fetched_fleet is None:
                raise Exception('Could not locate fleet')
            if self.fleet != fetched_fleet:
                raise TaskAbortException('Fleet changed!')
            self.fleet.update()
            self.fleet.write_to_db()

            # Update participations
            participations = ParticipationsFromFleetID.get(self.fleet.id, self.auth_token)
            if not participations:
                raise Exception('Failed to retrieve participations')
            self.fleet.update_participations(participations)

            self.execution_failures = 0
        except TaskAbortException as ex:
            print(f'[{datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}] Task aborting: {ex}!')
            raise ex
        except Exception as ex:
            print(f'[{datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}] Task execution failed: {ex}')
            self.execution_failures += 1