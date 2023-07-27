#!/usr/bin/env python3
# File: rgs_canonical.py


from .rgs import Rgs


class Rgs_canonical(Rgs):

    def __init__(self):
        super().__init__(False)


    def map_gameform_modules(self):
        gameform_modules = {
            "pd": "prisoners_dilemma",
            "chicken": "chicken",
            "staghunt": "stag_hunt",
            "coord": "coordination_game",
        }
        return gameform_modules