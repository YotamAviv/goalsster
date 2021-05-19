# I [aviv] do not understand this import business, which is bad and sad.
# import Goalsster
import os
import sys

# execfile("Goalsster.py")
exec(open("./Goalsster.py").read())


def runUI():
    Goalsster.DAY_FACTORY = RealDayFactory()

    goalsster = Goalsster()
    run = Goal("run", "Run.", Spec(2, 10))
    goalsster.add(run)

    pushups = Goal("push-ups", "Do 100 push ups, 2 minute breaks", Spec(2, 6))
    goalsster.add(pushups)

    goalsster.add(Goal("word of the week", "Groovy", Spec(5, 10)))

    swim = Goal("swim", "Swim.", Spec(3, 365))
    goalsster.add(swim)

    goalsster.ui()


runUI()
