'''
    Defines game world, available actions, payoffs

    (28/01/2022)  implementing es3_eg2 experiments as matrix games
        eg2 implements the 'social behaviour metric', or rather, a cooperation ratio
        this group (2a) adds the coop-ratio function to the environment.
        for matrix games this is the rate of the 'defect' action over time.

    Game World
        es3_eg2a
        gameform matrix
        independent episodes
        fixed episode length
        reward per timestep
        resets agent state over all episodes
        
        reset game world externalities every episode
'''

import os
from collections import Counter

from .environment import Environment



class Exp_es3_eg2a(Environment):

    def __init__(self, name, _options, agents, instance_id, exp_data):
        super().__init__(name, _options)
        self.agents = agents
        

        
        # if gameform id is set in world_properties then override the incoming instance_id.
        # this allows the default single job (i.e., localhost, or single job in PBS, to run rgs pd by default
        # but also allows to play any rgs gameform with the id in the form 'g121', for example.
        # NOTE: should place an assert in the run/exp harness to ensure that when an rgs form is specified that the appropriate 
        # reward type is specified, and vice versa for canonical forms. (08122021)
        if self.options["gameform"] == "":
            self.options["gameform"] = self.rgs.map_instance_id_to_gameform_name(instance_id)
            self.exp_utility.exp_data_update_gameform(exp_data, self.options["gameform"])

        self.matrix = self.exp_utility.retrieve_matrix(self.rgs, self.options["gameform"], self.options["reward_type"])

        self.ratio = 0

        
        
    def run(self, exp_data):
        
        episodes = self.options["episodes"]
        timesteps = self.options["timesteps"]
        
        for e in range(episodes):
            
            self.distribution = Counter({(0,0): 0, (0,1): 0, (1,0): 0, (1,1): 0})
            single_episode_outcomes_cumulative  = {"cc": [], "cd": [], "dc": [], "dd": []}
            single_episode_outcomes_timestep_map = {"cc": [0] * timesteps, "cd": [0] * timesteps, "dc": [0] * timesteps, "dd": [0] * timesteps}
            
            previous_step = []
            for t in range(timesteps):
                
            
                self.rgs.identify_gameform_reward(self.agents, t, previous_step, e)

                actions = self.step(t, e, previous_step)
                
                self.rgs.identify_gameform_prefs(self.agents, t, previous_step, e)                
                previous_step = actions
                
                single_episode_outcomes_timestep_map[self.rgs.map_actions_to_semantic_outcome(actions)][t] = 1
                self.append_timestep_outcome_to_single_episode_outcomes_cumulative(single_episode_outcomes_cumulative)
            
            self.final_step(t, e, previous_step)
            
            
            '''
                ^^ end single episode
                ---------------------------
                    
                - write single episode histories
                    - write agent action, reward history, and [strategy_state, agent_state] if specified on exp_invocation
                    - write single episode outcomes (cumulative and count)
                    - write agent and strategy state (if has_state && write_state)
                
                - write single episode timestep outcome map
                - Not writing single episode timestep outcome cumulative (as was done in ES1 and ES2) as this can be derived from the outcoem map in obs phase.

                - write rgs_complete single episode history of outcome rewards
                
                This set of operations is exp_grp dependent
                For es3_eg1a:
                
                    - then reset each agent's reward and action history 
                        - NOTE: do not reset agents' strategy state.
                    
                - reset rgs_complete.rgs_complete_candidate_match_history
            '''
            self.exp_utility.write_agent_history_single_episode(exp_data, self.agents, e)
            
            self.exp_utility.write_single_episode_outcomes_timestep_map(exp_data, e, single_episode_outcomes_timestep_map)

            
            # write rgs_complete candidate match history
            self.exp_utility.write_single_episode_rgs_complete_candidate_match_history(exp_data, e, self.rgs.rgs_complete_candidate_match_history_reward, "reward")
            self.exp_utility.write_single_episode_rgs_complete_candidate_match_history(exp_data, e, self.rgs.rgs_complete_candidate_match_history_prefs, "prefs")
            
            # write rgs_complete gamelock history
            self.exp_utility.write_single_episode_rgs_complete_gamelock_history(exp_data, e, self.rgs.gamelock_reward_history, "_complete_gamelock_reward_")

            self.exp_utility.write_single_episode_rgs_complete_gamelock_history(exp_data, e, self.rgs.gamelock_pref_history, "_complete_gamelock_pref_combined_")
           
            
            # write rgs_partial interlock history 
            # 
            
            for a in self.agents:
                self.exp_utility.write_single_episode_rgs_partial_interlock_history(exp_data, a, e, a.rgs.interlock_history_reward, "_partial_interlock_reward_")
                self.exp_utility.write_single_episode_rgs_partial_interlock_history(exp_data, a, e, a.rgs.interlock_history_pref, "_partial_interlock_pref_")
             


            for a in self.agents:
                a.reset_agent_histories()
                a.rgs.reset_rgs_partial()
                # es3_eg1a only; reset strategy state
                a.strategy.reset_state()
            
            self.rgs.reset_rgs_complete()
            


    def step(self, t, e, previous_step):
        actions = []
        
        for a in self.agents:
            actions.append(a.step(t, e, previous_step))
        
        (p0, p1) = self.matrix[actions[0]][actions[1]]

        self.agents[0].previous_reward = p0
        self.agents[1].previous_reward = p1
        
        self.distribution[tuple(actions)] += 1
        
        return actions
        
    def final_step(self, t, e, previous_step):
        for a in self.agents:
            a.final_step(t+1, previous_step)
        # this comes after calling step() on agents in run(), above. 
        self.rgs.identify_gameform_prefs(self.agents, t+1, previous_step, e)
            
    # Note these four functions:
    #   get_CC(), get_CD(), get_DC(), get_DD()
    # are env specific - only make sense for a matrix env.
    #   maybe, they should go in a util, but don't have plan to do another matrix env in es3.
    #       until now (28/01/2022) as implementing es3_eg2 experiments as matrix games
    
    # tuple here so can hash into Counter self.distribution   
    def get_CC(self):
        return self.distribution[(0, 0)]
        
    def get_CD(self):
        return self.distribution[(0, 1)]
    
    def get_DC(self):
        return self.distribution[(1, 0)] 
    
    def get_DD(self):
        return self.distribution[(1, 1)]    

    def append_timestep_outcome_to_single_episode_outcomes_cumulative(self, single_episode_outcomes_cumulative):
        single_episode_outcomes_cumulative["cc"].append(self.get_CC())
        single_episode_outcomes_cumulative["cd"].append(self.get_CD())
        single_episode_outcomes_cumulative["dc"].append(self.get_DC())
        single_episode_outcomes_cumulative["dd"].append(self.get_DD())