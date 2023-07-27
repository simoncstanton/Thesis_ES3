import os, sys
from pathlib import Path

from datetime import datetime
from time import process_time_ns, time_ns

import re
import json, csv

from .utility import Utility
import model.world.agent as agent

class Exp_utility(Utility):

    def __init__(self):
        super().__init__()
        self.config = self.load_run_config()

        
    def set_basepath(self, exp_data):

        exp_data["exp_invocation"]["home"] = str(Path.home())
        print(os.path.basename(__file__) + ":: setting home to " + exp_data["exp_invocation"]["home"])

        if exp_data["exp_invocation"]["localhost"] == True:
            platform_base = os.sep.join(self.run_config["paths"]["basepath_localhost"]) 
        else:
            platform_base = os.sep.join(self.run_config["paths"]["basepath_hpc"])
        exp_data["exp_invocation"]["basepath"] = os.path.join(exp_data["exp_invocation"]["home"], platform_base)    
        print(os.path.basename(__file__) + ":: setting basepath to " + exp_data["exp_invocation"]["basepath"]) 
        
        
        
    def set_exp_data_start(self, exp_data):
    
        exp_data["job_parameters"]["job_args"] = str(list(map(''.join, sys.argv[1:])))
        exp_data["job_parameters"]["pbs_jobid"], exp_data["job_parameters"]['hpc_name'] = exp_data["job_parameters"]['pbs_jobstr'].split('.', 1)
        
        if '[' in exp_data["job_parameters"]['pbs_jobid']:
            exp_data["job_parameters"]["pbs_parent_jobid"] = exp_data["job_parameters"]['pbs_jobid'].split('[', 1)[0]
            exp_data["job_parameters"]["pbs_sub_jobid"] = re.search(r"\[([0-9\s]*)\]", exp_data["job_parameters"]['pbs_jobid'])[1]
        else:
            exp_data["job_parameters"]["pbs_parent_jobid"] = exp_data["job_parameters"]['pbs_jobid']
         
        exp_data["exp_id"] = exp_data["job_parameters"]['pbs_parent_jobid'] + "_" + str(exp_data["job_parameters"]["pbs_sub_jobid"])
        
        if exp_data["job_parameters"]["scratch_dir"] == "localhost":
            exp_path = os.sep.join([exp_data["exp_invocation"]["exp_type"], exp_data["job_parameters"]["pbs_parent_jobid"], exp_data["exp_id"]])
            print("exp path", exp_path)
            exp_data["job_parameters"]['job_dir'] = os.path.join(exp_data["exp_invocation"]["basepath"], os.sep.join(self.config["paths"]["data"]), exp_path)

        else:
        
            scratch_path = os.sep.join(exp_data["job_parameters"]['scratch_dir'].split('/'))
            exp_data["job_parameters"]['job_dir'] = os.path.join(scratch_path, exp_data["exp_id"])
        
        exp_data["job_parameters"]["data_filename_prefix"] = self.run_config["data_file_prefix"] + exp_data["exp_id"]
        exp_data["journal_output_filename"] = exp_data["job_parameters"]['data_filename_prefix'] + self.run_config["journal_entry_suffix"] + self.run_config["journal_entry_extension"]        
    
    
    def set_exp_data_end(self, exp_data):
        exp_time_end_ns = time_ns()
        
        exp_data["exp_invocation"]["exp_time_end_hr"] = datetime.fromtimestamp(exp_time_end_ns / 1E9).strftime("%d%m%Y-%H%M%S")
        exp_data["exp_invocation"]["exp_time_end_ns"] = str(exp_time_end_ns)
        exp_data["exp_invocation"]["process_end_ns"] = process_time_ns()

        
    def set_properties(self, exp_data, world_properties, agent_properties):
        exp_data["world_properties"] = world_properties
        exp_data["agent_properties"] = agent_properties
        
    def copy_configs(self, exp_data):      
        self.copy_world_config(exp_data)
        self.copy_agent_config(exp_data)
        

    def exp_data_update_gameform(self, exp_data, gameform):
        exp_data["world_properties"]["gameform"] = gameform
    
    def write_exp_data_summary(self, exp_data):        
        path = exp_data["job_parameters"]['job_dir']
        file = exp_data["journal_output_filename"]
        
        with open(os.path.join(path, file), 'w') as json_file:
            json.dump(exp_data, json_file)     


    def make_exp_job_paths(self, exp_data):
            
        '''
            on hpc, this directory *has* to be made by the pbs_script calling the agent_model experiment, 
                so that the shell can move compressed data files from __PBS_SCRATCH_DIR__/ to ~/kunanyi/results/experiments/__PBS_PARENT_JOBID__/{__PBS_PARENT_JOBID__}_{__PBS_SUBJOB__}/
                If this job_path does not exist, then exit.
            
            on localhost, we can create it here, from the assigned value in exp_data["job_parameters"]['job_dir']
                see set_exp_data_start():
                    creates directory such as:  
                        ~/kunanyi/results/experiments/__EXP_TYPE__/__PBS_PARENT_JOBID__/{__PBS_PARENT_JOBID__}_{__PBS_JOBID__}/
                    or, 
                        ~/kunanyi/results/experiments/symmetric_self_play/001/001_0/
                If this job_path does not exist, then we can make it..
        '''
        
        if exp_data["exp_invocation"]["localhost"]:
            self.make_job_path(exp_data["job_parameters"]['job_dir'], exp_data["exp_invocation"]['verbose'])

        else:            
            if not os.path.isdir(exp_data["job_parameters"]['job_dir']):
                print(os.path.basename(__file__) + ":: Error: Results (Job) Directory (" + exp_data["job_parameters"]['job_dir'] + ") does not exist.")
                sys.exit(2)

        self.make_job_episode_paths(exp_data)


    def make_job_episode_paths(self, exp_data):    
        '''
            for both hpc and localhost context, these directories store the data from the experiment
            
            NOTE: These should really iterate over self.config["paths"]["exp_data_leaf_dirs"] and make each in turn
                    ok for now (dev)
            
        '''
        action_history_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.config["paths"]["exp_data_leaf_dirs"]["action_history"])
        self.make_job_path(action_history_path, exp_data["exp_invocation"]['verbose'])
        
        reward_history_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.config["paths"]["exp_data_leaf_dirs"]["reward_history"])
        self.make_job_path(reward_history_path, exp_data["exp_invocation"]['verbose'])
        
        agent_internal_state_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.config["paths"]["exp_data_leaf_dirs"]["agent_internal_state"])
        self.make_job_path(agent_internal_state_path, exp_data["exp_invocation"]['verbose'])

        strategy_internal_state_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.config["paths"]["exp_data_leaf_dirs"]["strategy_internal_state"])
        self.make_job_path(strategy_internal_state_path, exp_data["exp_invocation"]['verbose'])
        
        map_outcome_history_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.config["paths"]["exp_data_leaf_dirs"]["map_outcome_history"])
        self.make_job_path(map_outcome_history_path, exp_data["exp_invocation"]['verbose'])
        
        rgs_history = os.path.join(exp_data["job_parameters"]['job_dir'], self.config["paths"]["exp_data_leaf_dirs"]["rgs"])
        self.make_job_path(rgs_history, exp_data["exp_invocation"]['verbose'])
        
    '''
        create_agents(self, agent_config)
        
        instantiate agents with given properties
            - agents as defined in agent_properties
                - manner of instantiation depends on exp_mode {symmetric, asymmetric, mixed}
                    - for symmetric, read number_of_agents, and strategy name and options; apply to all agents
                    - for asymmetric, read number of agents, strategy name, iterate over strategy_option blocks (equal to number_of_agents)
                    - for mixed, read number of agents, iterate over this number of strategy+strategy_option blocks

        Note, in the case of two agents only, the different formats for the agent property files seems superfluous
            - but for future experiment group (ES3_EG3 or ES4) the number of agents will increase
            - so the short form (symmetric) will then be useful
            - as won't have to define a block for every agent's strategy parameters.
    '''

    def create_agents(self, agent_config, num_actions, exp_type, create_rgs_partial_interlock_record = False):
        agents = []
        agent_options = {}
        
        if agent_config["exp_mode"] == "symmetric":
            for i in range(agent_config["number_of_agents"]):
                agent_config["strategy_parameters"].update({"num_actions":num_actions})
                agent_options = {"num_actions": num_actions, "has_state" : agent_config["has_state"]}
                agent_i = agent.Agent(i, agent_options, agent_config["strategy"], agent_config["strategy_parameters"], exp_type, create_rgs_partial_interlock_record)
                agents.append(agent_i)
        
        elif agent_config["exp_mode"] == "mixed" or agent_config["exp_mode"] == "asymmetric":
            for i in range(agent_config["number_of_agents"]):
                agent_config["agent_"+str(i)]["strategy_parameters"].update({"num_actions":num_actions})
                agent_options = {"num_actions": num_actions, "has_state" : agent_config["agent_"+str(i)]["has_state"]}
                agent_i = agent.Agent(i, agent_options, agent_config["agent_"+str(i)]["strategy"], agent_config["agent_"+str(i)]["strategy_parameters"], exp_type, create_rgs_partial_interlock_record)
                agents.append(agent_i)

                
        for i in range(agent_config["number_of_agents"]):
            print(os.path.basename(__file__) + ":: agent " + str(agents[i].agent_id) + " agent_options['num_actions']: " + str(agent_options["num_actions"]) + " strategy: ", agents[i].strategy.options)
            
        return agents
        
        
        
    '''
        write state / history
            - compressed, or not, dependent on exp parameter: exp_data["exp_invocation"]["compress_writes"]
            
            
        Standard Experiment Types 
            - use the same functions (only tournament writes use own functions)
            - agent action_history and reward_history are both written from write_agent_history_single_episode()
            
            - exp_symmetric_selfplay
            - exp_selfplay_parameter_study
        
    '''
    
    def write_agent_history_single_episode(self, exp_data, agents,  e):
        for a in agents:
            self.write_agent_episode_history(exp_data, e, "agent_" + str(a.agent_id), "action_history", a.action_history)
            self.write_agent_episode_history(exp_data, e, "agent_" + str(a.agent_id), "reward_history", a.reward_history)
            
            if a.agent_has_state() and exp_data["exp_invocation"]["write_state"]:
                self.write_agent_state(exp_data, a, e)
                
            if a.strategy.strategy_has_state() and exp_data["exp_invocation"]["write_state"]:
                self.write_strategy_state(exp_data, a, e)

    def write_agent_episode_history(self, exp_data, episode, agent_id, history_type, data):
        history_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.config["paths"]["exp_data_leaf_dirs"][history_type])
        file = exp_data["job_parameters"]['data_filename_prefix'] + "_" + history_type + "_" + agent_id + "_" + "episode_" + str(episode+1)
        
        if exp_data["exp_invocation"]["compress_writes"]:
            file = file + ".csv.gz"
            self.write_compressed_csv(data, os.path.join(history_path, file))
        else:
            file = file + ".csv"
            self.write_csv(data, os.path.join(history_path, file))
            

    def write_agent_state(self, exp_data, agent, episode):
        data = agent.total_reward
        agent_state_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.config["paths"]["exp_data_leaf_dirs"]["agent_internal_state"]) 
        file = exp_data["job_parameters"]['data_filename_prefix'] + "_" + self.config["paths"]["exp_data_leaf_dirs"]["agent_internal_state"] + "_agent_" + str(agent.agent_id) + "_episode_" + str(episode+1)
        
        if exp_data["exp_invocation"]["compress_writes"]:
            file = file + ".json.gz"
            self.write_compressed_json(data, os.path.join(agent_state_path, file))
        else:
            file = file + ".json"
            self.write_json(data, os.path.join(agent_state_path, file))            

    def write_strategy_state(self, exp_data, agent, episode):
        strategy_state_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.config["paths"]["exp_data_leaf_dirs"]["strategy_internal_state"])
        
        if exp_data["agent_properties"]["exp_mode"] == "symmetric":
            strategy = exp_data["agent_properties"]['strategy']
        else:
            strategy = exp_data["agent_properties"]['agent_' + str(agent.agent_id)]['strategy']
            
        file = exp_data["job_parameters"]['data_filename_prefix'] + "_" + self.config["paths"]["exp_data_leaf_dirs"]["strategy_internal_state"] + "_" + \
                strategy + "_agent_" + str(agent.agent_id) + "_episode_" + str(episode+1)
        
        if exp_data["exp_invocation"]["compress_writes"]:
            file = file + ".json.gz"
            self.write_compressed_json(agent.state_history, os.path.join(strategy_state_path, file))
        else:
            file = file + ".json"
            self.write_json(agent.state_history, os.path.join(strategy_state_path, file)) 


    def write_single_episode_outcomes_timestep_map(self, exp_data, episode, single_episode_outcomes_timestep_map):
        o_t_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.config["paths"]["exp_data_leaf_dirs"]["map_outcome_history"])
        
        for o, d in single_episode_outcomes_timestep_map.items():
            file = exp_data["job_parameters"]['data_filename_prefix'] + "_outcomes_" + "episode_" + str(episode+1) + "_" + o + "_map"
            
            if exp_data["exp_invocation"]["compress_writes"]:
                file = file + ".csv.gz"
                self.write_compressed_csv(single_episode_outcomes_timestep_map[o], os.path.join(o_t_path, file))
            else:
                file = file + ".csv"
                self.write_csv(single_episode_outcomes_timestep_map[o], os.path.join(o_t_path, file))


    def write_single_episode_outcomes_cumulative(self, exp_data, episode, single_episode_outcomes_cumulative):
        o_d_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.config["paths"]["exp_data_leaf_dirs"]["cumulative_outcome_history"])
        
        for o, d in single_episode_outcomes_cumulative.items():
            file = exp_data["job_parameters"]['data_filename_prefix'] + "_outcomes_" + "episode_" + str(episode+1) + "_" + o + "_cumulative"
            
            if exp_data["exp_invocation"]["compress_writes"]:
                file = file + ".csv.gz"
                self.write_compressed_csv(single_episode_outcomes_cumulative[o], os.path.join(o_d_path, file))
            else:
                file = file + ".csv"
                self.write_csv(single_episode_outcomes_cumulative[o], os.path.join(o_d_path, file)) 


    def write_single_episode_rgs_complete_candidate_match_history(self, exp_data, episode, data, tag):
        rgs_complete_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.config["paths"]["exp_data_leaf_dirs"]["rgs"])
        
        file = exp_data["job_parameters"]['data_filename_prefix'] + "_complete_candidate_match_" + tag + "_episode_" + str(episode+1)

        if exp_data["exp_invocation"]["compress_writes"]:
            file = file + ".json.gz"
            self.write_compressed_json(data, os.path.join(rgs_complete_path, file))
        else:
            file = file + ".json"
            self.write_json(data, os.path.join(rgs_complete_path, file)) 

    def write_single_episode_rgs_complete_gamelock_history(self, exp_data, episode, data, tag):
        rgs_complete_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.config["paths"]["exp_data_leaf_dirs"]["rgs"])
        
        file = exp_data["job_parameters"]['data_filename_prefix'] + tag + "episode_" + str(episode+1)
        
        if exp_data["exp_invocation"]["compress_writes"]:
            file = file + ".json.gz"
            self.write_compressed_json(data, os.path.join(rgs_complete_path, file))
        else:
            file = file + ".json"
            self.write_json(data, os.path.join(rgs_complete_path, file))             

    
    def write_single_episode_rgs_partial_interlock_history(self, exp_data, a, e, data, tag):               
        rgs_complete_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.config["paths"]["exp_data_leaf_dirs"]["rgs"])
        
        file = exp_data["job_parameters"]['data_filename_prefix'] + tag + "agent_" + str(a.agent_id) + "_episode_" + str(e+1)

        if exp_data["exp_invocation"]["compress_writes"]:
            file = file + ".json.gz"
            self.write_compressed_json(data, os.path.join(rgs_complete_path, file))
        else:
            file = file + ".json"
            self.write_json(data, os.path.join(rgs_complete_path, file))                 
        
    def write_json(self, data, path):
        with open(path, 'w') as json_file:
            json.dump(data, json_file)
            
    def write_csv(self, data, path):
        with open(path, 'wt', newline='') as csv_file:
            write = csv.writer(csv_file)
            write.writerow(data)            
            
    '''
        es3_eg1c functions
    
    '''
    def write_agent_reward_history_sum_episodes(self, exp_data, agent_id, agent_reward_episode_totals):
      
        history_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.config["paths"]["exp_data_leaf_dirs"]["reward_history"])
        file = exp_data["job_parameters"]['data_filename_prefix'] + "_" + "agent_" + str(agent_id) + "_reward_history" + "_" + "sum_episodes"
        
        if exp_data["exp_invocation"]["compress_writes"]:
            file = file + ".csv.gz"
            self.write_compressed_csv(agent_reward_episode_totals, os.path.join(history_path, file))
        else:
            file = file + ".csv"
            self.write_csv(agent_reward_episode_totals, os.path.join(history_path, file))

    def write_sum_episode_outcomes_cumulative(self, exp_data, outcome, sum_episode_outcome_cumulative):
        o_d_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.config["paths"]["exp_data_leaf_dirs"]["map_outcome_history"])
        file = exp_data["job_parameters"]['data_filename_prefix'] + "_" + outcome + "_outcomes_" + "sum_episodes_cumulative"
        
        if exp_data["exp_invocation"]["compress_writes"]:
            file = file + ".csv.gz"
            self.write_compressed_csv(sum_episode_outcome_cumulative, os.path.join(o_d_path, file))
        else:
            file = file + ".csv"
            self.write_csv(sum_episode_outcome_cumulative, os.path.join(o_d_path, file))
            
    def write_rgs_complete_gamelock_record(self, exp_data, data):
        rgs_complete_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.config["paths"]["exp_data_leaf_dirs"]["rgs"])
        file = exp_data["job_parameters"]['data_filename_prefix'] + "_rgs_complete_gamelock_record"
        
        if exp_data["exp_invocation"]["compress_writes"]:
            file = file + ".json.gz"
            self.write_compressed_json(data, os.path.join(rgs_complete_path, file))
        else:
            file = file + ".json"
            self.write_json(data, os.path.join(rgs_complete_path, file))   

    def write_rgs_complete_candidate_record(self, exp_data, data):
        rgs_complete_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.config["paths"]["exp_data_leaf_dirs"]["rgs"])
        file = exp_data["job_parameters"]['data_filename_prefix'] + "_rgs_complete_candidate_record"
        
        if exp_data["exp_invocation"]["compress_writes"]:
            file = file + ".json.gz"
            self.write_compressed_json(data, os.path.join(rgs_complete_path, file))
        else:
            file = file + ".json"
            self.write_json(data, os.path.join(rgs_complete_path, file))      

    def write_rgs_partial_interlock_record(self, exp_data, agent):
        data = agent.rgs.rgs_partial_interlock_record
        rgs_complete_path = os.path.join(exp_data["job_parameters"]['job_dir'], self.config["paths"]["exp_data_leaf_dirs"]["rgs"])
        file = exp_data["job_parameters"]['data_filename_prefix'] + "_rgs_partial_interlock_record" + "_agent_" + str(agent.agent_id)
        
        if exp_data["exp_invocation"]["compress_writes"]:
            file = file + ".json.gz"
            self.write_compressed_json(data, os.path.join(rgs_complete_path, file))
        else:
            file = file + ".json"
            self.write_json(data, os.path.join(rgs_complete_path, file))    