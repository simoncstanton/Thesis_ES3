import os
from abc import ABC, abstractmethod
from run.util.exp_util import Exp_utility
import model.rgs.rgs_complete as rgs_complete

class Environment(ABC):

    def __init__(self, name, _options, create_rgs_complete_gamelock_record = False):
        
        super().__init__()
        self.options = {
            "env":  "environment_superclass"
        }
        self.set_options(name, _options)
        
        print(os.path.basename(__file__) + " env options", self.options)
        
        self.exp_utility = Exp_utility()

        self.rgs = rgs_complete.Rgs_complete(create_rgs_complete_gamelock_record)

    
    def set_options(self, name, _options):
        self.options['name'] = name
        self.options.update(_options)


    def name(self):
        return self.name            