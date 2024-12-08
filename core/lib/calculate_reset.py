class CalculateReset:
    STAGES = {
        'day': 1, 
        'week': 7, 
        'month': 30, 
        'three_month': 90, 
        'half_year': 180,
    }

    def __init__(self, stage='day', times_in_row=0):
        self._stage = stage
        self._times_in_row = times_in_row
        self._reset_in_days = 0


    def perform(self):
        if self._stage == 'half_year':
            self._times_in_row += 1
            return self

        if self._times_in_row >= 3:
            
            self._times_in_row = 0
            
            if self._stage == 'day':
                self._stage = 'week'
            elif self._stage == 'week':
                self._stage = 'month'
            elif self._stage == 'month':
                self._stage = 'three_month'
            elif self._stage == 'three_month':
                self._stage = 'half_year'
        else:
            self._times_in_row += 1
        return self

    @property
    def stage(self):
        return self._stage

    @property
    def reset_in_days(self):
        return self.STAGES[self.stage]

    @property
    def times_in_row(self):
        return self._times_in_row

