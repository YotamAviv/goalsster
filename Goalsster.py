import numpy
import datetime
import os

from numpy import ndarray


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


# TODO: BUG: This DayFactory business is not working correctly. UI Should run in real time.
class RealDayFactory:
    def get_day(self):
        days = (datetime.datetime.utcnow() - datetime.datetime(2021, 1, 1)).days
        return days


class StubDayFactory:
    def set_day(self, day):
        self.day = day

    def get_day(self):
        return self.day


class Spec:
    def __init__(self, goal, period):
        self.goal = goal
        self.period = period

    def __str__(self):
        return "{}/{}".format(self.goal, self.period)


# TODO:...
MAX_HISTORY = 1000  # should work until 1000 days after 1/1/2021


class Goalsster:
    def __init__(self, day_factory):
        self.day_factory = day_factory
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


class Goal:
    def __init__(self, day_factory, name, details, spec):
        history = numpy.zeros(MAX_HISTORY, dtype=int)

        self.day_factory = day_factory
        self.spec = spec
        self.name = name
        self.details = details
        self.history = history

    # Getting rid of "rest", not sure what to do with it.
    # # TODO: Maybe move this code to Spec
    # def min_time_for_goal(self):
    #     spec = self.spec
    #     return 1 + (spec.goal - 1) * (spec.rest + 1)
    #

    # return the number of days since 1/1/2021
    def get_today(self):
        return self.day_factory.get_day()

    def get_history(self, day):
        return self.history[day]

    def make(self):
        made = self.history[self.get_today()]
        self.history[self.get_today()] = made + 1

    def __str__(self):
        failing = ""
        if self.is_failing():
            failing = "FAILING "
        return "{}{:.2f} {} \"{}\" ({})".format(failing, self.score(), self.name, self.details, self.spec)

    # TODO: Cache score
    def score(self):
        spec = self.spec;
        history = self.history

        score = 0
        today = self.get_today()
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
                if (hits >= spec.goal):
                    return score

        return score

    # TODO: Make it so that new Goals aren't in failure, use a Goal created date or something.
    def is_failing(self):
        total = 0
        for i in range(0, self.spec.period):
            day = self.get_today() - i
            done = self.get_history(day)
            total += done
        return total < self.spec.goal


def test2():
    day_factory = StubDayFactory()
    day_factory.set_day(100)

    goalsster = Goalsster(day_factory)

    run = Goal(day_factory, "run", "Run.", Spec(2, 10))
    goalsster.add(run)

    pushups = Goal(day_factory, "push-ups", "Do 100 push ups, 2 minute breaks", Spec(2, 6))
    goalsster.add(pushups)
    pushups.make()
    # do pushups yesterday
    day_factory.set_day(99)
    pushups.make()
    # do pushups day before yesterday
    day_factory.set_day(98)
    pushups.make()
    day_factory.set_day(100)

    goalsster.add(Goal(day_factory, "word of the week", "Groovy", Spec(5, 10)))

    swim = Goal(day_factory, "swim", "Swim.", Spec(3, 365))
    goalsster.add(swim)
    swim.make()
    swim.make()

    goalsster.dump()


test2()


def runUI():
    day_factory = RealDayFactory()

    goalsster = Goalsster(day_factory)
    run = Goal(day_factory, "run", "Run.", Spec(2, 10))
    goalsster.add(run)

    pushups = Goal(day_factory, "push-ups", "Do 100 push ups, 2 minute breaks", Spec(2, 6))
    goalsster.add(pushups)

    goalsster.add(Goal(day_factory, "word of the week", "Groovy", Spec(5, 10)))

    swim = Goal(day_factory, "swim", "Swim.", Spec(3, 365))
    goalsster.add(swim)

    goalsster.ui()


runUI()
