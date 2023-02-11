import json

class policy:
    def __init__(self, action, enact_year, enact_week, enactment_duration_years, enactment_duration_weeks):
        self.action = action
        self.enact_year = enact_year
        self.enact_week = enact_week
        self.enactment_duration_years = enactment_duration_years
        self.enactment_duration_weeks = enactment_duration_weeks

    def is_expired(self, year, week):
        if year > self.enact_year + self.enactment_duration_years:
            return True
        elif year == self.enact_year + self.enactment_duration_years:
            if week > self.enact_week + self.enactment_duration_weeks:
                return True
        return False

    def __str__(self):
        return self.action

    # serialize to JSON
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    # deserialize from JSON
    @staticmethod
    def fromJSON(json_string):
        return json.loads(json_string)