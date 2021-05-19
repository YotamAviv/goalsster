import datetime
import json
import os
import numpy


# NEXT STEPS:
# Persistence:
# Allow for my editing JSON files to fudge history, create new goals, edit goals. This is so that the UI for any of
# those can be deferred.
#
# Cloud (AppEngine mostly likely, maybe in Java)
# Possibly before Persistence

def screen_clear():
    if os.name == 'posix':
        # for mac and linux(here, os.name is 'posix')
        _ = os.system('clear')
    else:
        # for windows platfrom
        _ = os.system('cls')


class RealDayFactory:
    def get_today(self):
        days = (datetime.datetime.utcnow() - datetime.datetime(2021, 1, 1)).days
        return days


class StubDayFactory:
    def set_today(self, day):
        self.day = day

    def get_today(self):
        return self.day


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


# TODO:...
MAX_HISTORY = 1000  # should work until 1000 days after 1/1/2021
STUB_TODAY = 100


class Goal:
    def __init__(self, name, details, spec, history=None):
        if (history is None):
            history = numpy.zeros(MAX_HISTORY, dtype=int)

        self.spec = spec
        self.name = name
        self.details = details
        self.history = history

    def to_json_obj(self):
        dict = {}
        dict['spec'] = self.spec.to_json_obj()
        dict['name'] = self.name
        dict['details'] = self.details
        dict['history'] = self.history.tolist()
        return dict

    @staticmethod
    def from_json_obj(dict):
        spec = Spec.from_json_obj(dict['spec'])
        name = dict['name']
        details = dict['details']
        history = numpy.asarray(dict['history'])
        return Goal(name, details, spec, history)

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
        made = self.history[today]
        self.history[today] = made + 1

    def __str__(self):
        failing = ""
        if self.is_failing():
            failing = "FAILING "
        return "{}{:.2f} {} \"{}\" ({})".format(failing, self.score(), self.name, self.details, self.spec)

    def score(self):
        spec = self.spec
        history = self.history

        score = 0
        today = Goalsster.DAY_FACTORY.get_today()
        hits = 0
        for i in range(0, spec.period):
            day = today - i
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

    # TODO: Make it so that new Goals aren't in failure, use a Goal created date or something.
    def is_failing(self):
        total = 0
        for i in range(0, self.spec.period):
            day = Goalsster.DAY_FACTORY.get_today() - i
            done = self.get_history(day)
            total += done
        return total < self.spec.goal


class Goalsster:
    DAY_FACTORY = None

    def __init__(self):
        self.goals = []

    def add(self, goal):
        self.goals.append(goal)

    def dump(self):
        sortfunc = lambda goal: goal.score()
        sorted_goals = sorted(self.goals, key=sortfunc)
        for goal in sorted_goals:
            print(goal)

        return

    def ui(self):
        sortfunc = lambda goal: goal.score()
        while True:
            screen_clear()

            print("Today is: {}".format(Goalsster.DAY_FACTORY.get_today()))

            sorted_goals = sorted(self.goals, key=sortfunc)
            index = 0
            for goal in sorted_goals:
                print("{}) {}".format(index, goal))
                index = index + 1

            s = input("Which one did you just do?\n")
            try:
                index = int(s)
                sorted_goals[index].make()
            except:
                # do nothing
                print()
