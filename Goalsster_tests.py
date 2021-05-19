# I [aviv] do not understand this import business, which is bad and sad.
# import Goalsster
import os
import sys

# execfile("Goalsster.py")
exec(open("./Goalsster.py").read())


def test2():
    Goalsster.DAY_FACTORY = StubDayFactory()
    Goalsster.DAY_FACTORY.set_today(STUB_TODAY)

    goalsster = Goalsster()

    run = Goal("run", "Run.", Spec(2, 10))
    goalsster.add(run)

    pushups = Goal("push-ups", "Do 100 push ups, 2 minute breaks", Spec(2, 6))
    goalsster.add(pushups)
    pushups.make()
    # do pushups yesterday
    Goalsster.DAY_FACTORY.set_today(STUB_TODAY - 1)
    pushups.make()
    # do pushups day before yesterday
    Goalsster.DAY_FACTORY.set_today(STUB_TODAY - 2)
    pushups.make()
    Goalsster.DAY_FACTORY.set_today(STUB_TODAY)

    goalsster.add(Goal("word of the week", "Groovy", Spec(5, 10)))

    swim = Goal("swim", "Swim.", Spec(3, 365))
    goalsster.add(swim)
    swim.make()
    swim.make()

    goalsster.dump()


test2()


def test_json():
    Goalsster.DAY_FACTORY = StubDayFactory()
    Goalsster.DAY_FACTORY.set_today(STUB_TODAY)

    # Spec
    spec1 = Spec(3, 365)
    spec1_json_obj = spec1.to_json_obj()
    spec1_json = json.dumps(spec1_json_obj)
    # print("spec1_json = {}".format(spec1_json))

    spec2_json_obj = json.loads(spec1_json)
    spec2 = Spec.from_json_obj(spec2_json_obj)
    spec2_json_obj = spec2.to_json_obj()
    spec2_json = json.dumps(spec2_json_obj)
    # print("spec2_json = {}".format(spec2_json))
    assert spec1_json == spec2_json

    # Goal
    goal1 = Goal("run", "Run.", spec1)
    goal1.make()
    goal1_json_obj = goal1.to_json_obj()
    goal1_json = json.dumps(goal1_json_obj)
    print("goal1_json = {}".format(goal1_json))

    goal2_json_obj = json.loads(goal1_json)
    goal2 = Goal.from_json_obj(goal2_json_obj)
    goal2_json_obj = goal2.to_json_obj()
    goal2_json = json.dumps(goal2_json_obj)
    # print("goal2 = {}".format(goal2))
    print("goal2_json = {}".format(goal2_json))
    assert goal1_json == goal2_json


test_json()
