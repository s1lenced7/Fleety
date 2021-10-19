from datetime import datetime, timedelta
from collections import defaultdict

from api import Fleet, System, UniverseItem, Character, User, FleetParticipation, Session

from .task import Task, TaskCreationException, TaskAbortException




class TrackCharacterFleet(Task):
    MAX_CONSECUTIVE_FAILURES = 5

    def __init__(self, user_id, character_id, name=None, **kwargs):
        super().__init__(**kwargs)
        self.execution_failures = 0
        with Session(expire_on_commit=False) as session:
            user = session.query(User).filter(User.id == user_id).one()
            character = next(c for c in user.characters if c.id == character_id)
            fleet_id = character.get_fleet_id()
            if not fleet_id:
                raise Exception('Could not locate fleet!')

            # TODO, bring some consistency into these? hide the token access? pass the character?
            fleet = Fleet.get_and_add(session, fleet_id, character.client_token, fleet_name=name)
            fleet.user_id = user.id
            fleet.update()
            session.commit()

        # Store NON_SYNCED copies
        self.client_token = character.client_token
        self.fleet = fleet

    def execute(self):
        if self.execution_failures >= self.MAX_CONSECUTIVE_FAILURES:
            print(f'[{datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}] Task aborting, failed to many times!')
            self.stop()
            return

        print(f'[{datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}] Executing task')
        try:
            with Session() as session:
                fleet = session.query(Fleet).filter(Fleet.id == self.fleet.id).one()
                fleet_participations = FleetParticipation.get(self.fleet.id, self.client_token)

                # Store Characters and Systems
                for fleet_participation in fleet_participations:
                    Character.get_and_add(session, fleet_participation.character_id)
                    System.get_and_add(session, fleet_participation.system_id)

                # Store ships
                ship_ids = list(set([f.ship_id for f in fleet_participations]))
                UniverseItem.get_and_add(session, ship_ids)

                # Fetch participations for present characters
                updated_participations = []
                character_ids = [fp.character_id for fp in fleet_participations]

                # Update Participations
                stored_fleet_participations = session.query(FleetParticipation).filter(
                    FleetParticipation.character_id.in_(character_ids),
                    FleetParticipation.close > datetime.utcnow() - timedelta(seconds=5*60)
                ).all()
                stored_participations_by_character = defaultdict(list)
                for stored_fleet_participation in stored_fleet_participations:
                    stored_participations_by_character[stored_fleet_participation.character_id].append(stored_fleet_participation)

                for fleet_participation in fleet_participations:
                    stored_character_participations = stored_participations_by_character[fleet_participation.character_id]
                    if stored_character_participations:
                        most_recent_participation = max(stored_character_participations, key=lambda x: x.close)

                        if most_recent_participation.system_id == fleet_participation.system_id and most_recent_participation.ship_id == fleet_participation.ship_id:
                            most_recent_participation.update()
                        else:
                            session.add(fleet_participation)
                    else:
                        # No most recent one that matches, Store a new one!
                        session.add(fleet_participation)

                fleet.update()
                session.commit()

            self.execution_failures = 0
        except TaskAbortException as ex:
            print(f'[{datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}] Task aborting: {ex}!')
            raise ex
        except Exception as ex:
            print(f'[{datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}] Task execution failed: {ex}')
            self.execution_failures += 1