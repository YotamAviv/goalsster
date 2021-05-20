import datetime
import json
import os
import numpy

# Immediate next steps
# - tests silent (they pass, they don't print)
# - stub date business clear, crisp
# - history and created considered carefully (I think that they're correct as is, but they might be off by one and and
#   might benefit from a few helper functions)
#
# NEXT STEPS:

# Persistence:
# Allow for my editing JSON files to fudge history (edit the saved files by hand), create new goals, edit goals.
# This is so that the UI for any of those can be deferred.
#
# Cloud:
# (AppEngine mostly likely, maybe in Java)
# Possibly before Persistence

# TODO:...
MAX_HISTORY = 1000  # should work until 1000 days after 1/1/2021


def screen_clear():
    if os.name == 'posix':
        # for mac and linux(here, os.name is 'posix')
        _ = os.system('clear')
    else:
        # for windows platfrom
        _ = os.system('cls')


class Spec:
    def __init__(self, goal, period):
        self.goal = goal
        self.period = period

    def __str__(self):
        return "{}/{}".format(self.goal, self.period)

    def to_json_obj(self):
        return json.dumps({'goal': self.goal, 'period': self.period})

    @staticmethod
    def from_json_obj(obj):
        d = json.loads(obj)
        goal = d['goal']
        period = d['period']
        return Spec(goal, period)


class RealDayFactory:
    def get_today(self):
        days = (datetime.datetime.utcnow() - datetime.datetime(2021, 1, 1)).days
        return days


class Goal:
    def __init__(self, name, details, spec, created, history=None):
        if (history is None):
            history = numpy.zeros(MAX_HISTORY, dtype=int)

        self.spec = spec
        self.name = name
        self.details = details
        self.created = created
        self.history = history

    def to_json_obj(self):
        dict = {}
        # NOTE: If this were any bigger, I'd [aviv ] come up with a mechanism to nest objects that have a "to_json_obj"
        # inside each other.
        dict['spec'] = self.spec.to_json_obj()
        dict['name'] = self.name
        dict['details'] = self.details
        dict['created'] = self.created
        dict['history'] = self.history.tolist()
        return dict

    @staticmethod
    def from_json_obj(dict):
        spec = Spec.from_json_obj(dict['spec'])
        name = dict['name']
        details = dict['details']
        created = dict['created']  # day number (since 1/1/2021) this goal was created.
        history = numpy.asarray(dict['history'])  # history of this goal starting when it was created.
        return Goal(name, details, spec, created, history)

    # Getting rid of "rest", not sure what to do with it.
    # # TODO: Maybe move this code to Spec
    # def min_time_for_goal(self):
    #     spec = self.spec
    #     return 1 + (spec.goal - 1) * (spec.rest + 1)
    #

    def get_history(self, day):
        return self.history[day]

    def make(self):
        today = Goalsster.DAY_FACTORY.get_today()
        made = self.history[today - self.created]
        self.history[today - self.created] = made + 1

    # TODO: Move to a UI class
    def __str__(self):
        failing = ""
        if self.compute_is_failing():
            failing = "FAILING "
        return "{}{:.2f} {} \"{}\" ({})".format(failing, self.compute_score(), self.name, self.details, self.spec)

    def compute_score(self):
        spec = self.spec
        history = self.history

        score = 0
        today = Goalsster.DAY_FACTORY.get_today()
        today_offset = today - self.created
        hits = 0
        for i in range(0, spec.period):
            day = today_offset - i
            done = self.get_history(day)
            for j in range(0, done):
                hits += 1

                # reward for work on this day should be
                # 1.0 if it's today,
                # (1.0 / period) if it was so long ago it barely counts, and
                # 0 if it's just too long  ago (we should have stopped looping and not even considered it)
                day_work_reward = (spec.period - i) / spec.period

                day_score = day_work_reward / spec.goal
                score += day_score
                if hits >= spec.goal:
                    return score

        return score

    def compute_is_failing(self):
        # New Goals aren't in failure until (spec.period days have elapsed from when created).
        if self.spec.period > (Goalsster.DAY_FACTORY.get_today() - self.created):
            return False

        total = 0
        for i in range(0, self.spec.period):
            day = Goalsster.DAY_FACTORY.get_today() - i
            day_offset = day - self.created
            done = self.get_history(day)
            total += done
        return total < self.spec.goal


class Goalsster:
    DAY_FACTORY = None

    def __init__(self):
        self.goals = []

    def to_json_obj(self):
        dict = {}
        dict['goals'] = list(map(lambda spec: spec.to_json_obj(), self.goals))
        return dict

    def add(self, goal):
        self.goals.append(goal)

    # (sorted)
    def compute_sorted_goals(self):
        # (goals in failure first.)
        def sort(goal):
            if goal.compute_is_failing():
                failing_penalty = 0
            else:
                failing_penalty = 1
            return goal.compute_score() + failing_penalty

        return sorted(self.goals, key=sort)

    def dump(self):
        sorted_goals = self.compute_sorted_goals()
        for goal in sorted_goals:
            print(goal)

    def ui(self):
        while True:
            screen_clear()

            print("Today is: {}".format(Goalsster.DAY_FACTORY.get_today()))

            goals = self.compute_sorted_goals()
            index = 0
            for goal in goals:
                print("{}) {}".format(index, goal))
                index = index + 1

            s = input("Which one did you just do?\n")
            try:
                index = int(s)
                goals[index].make()
            except:
                # do nothing. (Nothing didn't work, and so I added "print()")
                print()
