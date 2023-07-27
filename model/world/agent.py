import importlib

import numpy as np
import copy
import model.rgs.rgs_partial as rgs_partial

class Agent:

    def __init__(self, agent_id, agent_options, strategy, strategy_options, exp_type, defection_action, create_rgs_partial_interlock_record = False):
        
        self.agent_id = agent_id
        self.has_state = agent_options["has_state"]
        
        self.action_history = []
        self.reward_history = []
        self.state_history = []
        
        self.total_reward = 0
        self.previous_reward = 0
        
        #strategy_options.update({"num_actions": num_actions})
        
        # self._m is dynamically loaded strategy module 
        self._m = importlib.import_module('model.algorithms.{}'.format(strategy), 'model')
        self.strategy = getattr(self._m, str.capitalize(strategy))(strategy, strategy_options)
        
        self.rgs = rgs_partial.Rgs_partial(exp_type, self.agent_id, create_rgs_partial_interlock_record)
        
        #self.action_prefs = {"00": [], "01": [], "10": [], "11": []} 
        
        
    def step(self, t, e, previous_step = []):
        action = self.strategy.action(self, previous_step)
        self.action_history.append(action)
        
        if self.strategy.strategy_has_state():
            self.state_history.append(self.strategy.get_strategy_internal_state())
            
        if t > 0:
            self.total_reward += self.previous_reward
            self.reward_history.append(self.previous_reward)
        
        # rgs_partial
        # acts on previous timestep (requires last step reward for self)
        
        # removed single agent restriction 21022022
        #r_interlock = self.rgs.identify_gameform_reward(self.agent_id, self.previous_reward, t, previous_step, e)
        self.rgs.identify_gameform_reward(self.agent_id, self.previous_reward, t, previous_step, e)
        
        if t > 0:
            #relative_response = self.rgs.relative_response(copy.deepcopy(self.reward_history))
            # the term relative response was chosen for a more complicated attempt prior to finding this current method 
            relative_response = self.rgs.normalise_bin_reward_2(copy.deepcopy(self.reward_history))

            #p_interlock = self.rgs.identify_gameform_pref(self.agent_id, relative_response, t, previous_step, e)
            self.rgs.identify_gameform_pref(self.agent_id, relative_response, t, previous_step, e)    

        return action
        
        
        
    def final_step(self, t, previous_step):
        self.total_reward += self.previous_reward
        self.reward_history.append(self.previous_reward)
        
        # write strategy state
        if self.strategy.strategy_has_state():
            self.state_history.append(self.strategy.get_strategy_internal_state())
            
        r_interlock = self.rgs.identify_gameform_reward(self.agent_id, self.previous_reward, t, previous_step)
  
        # this probably had no observable effect becuase lock is usually achieved before end of epsiode, but this should call nbr_2
        # also the term relative response was chosen for a more complicated attempt prior to finding the current method 
        # relative_response = self.rgs.relative_response(copy.deepcopy(self.reward_history))
        relative_response = self.rgs.normalise_bin_reward_2(copy.deepcopy(self.reward_history))
        p_interlock = self.rgs.identify_gameform_pref(self.agent_id, relative_response, t, previous_step)
            
            


    def reset_agent_histories(self):
        self.action_history = []
        self.reward_history = []
        self.state_history = []
        self.total_reward = 0
    
    def agent_has_state(self):
        return self.has_state