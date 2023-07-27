import os
import re
import json
import copy
import shutil
from abc import ABC, abstractmethod

class Utility(ABC):

    def __init__(self):
    
        self.run_config = self.load_run_config()

        
    # load_run_config has to have hardcodeed path somewhere 
    # as this config file has all the paths required for all 
    # other properties ...
    
    def load_run_config(self):
        with open('run/config/run_config.json') as f:
            return json.load(f)

            
    def load_agent_config(self, tag):
        path = os.sep.join(self.config["paths"]["agent_config"])
        file = self.config["config"]["agent_config"] + tag + self.config["config"]["config_ext"]
        
        with open(os.path.join(path, file)) as f:
            return json.load(f)


    def load_world_config(self, tag):
        path = os.sep.join(self.config["paths"]["world_config"])
        file = self.config["config"]["world_config"] + tag + self.config["config"]["config_ext"]
        
        with open(os.path.join(path, file)) as f:
            return json.load(f)

    def copy_world_config(self, exp_data):
        path_src = os.sep.join(self.config["paths"]["world_config"])
        file_src = self.config["config"]["world_config"] + exp_data["exp_invocation"]["world_properties"] + self.config["config"]["config_ext"]
        path_dest = os.path.join(exp_data["job_parameters"]['job_dir'])
        
        shutil.copyfile(os.path.join(path_src, file_src), os.path.join(path_dest, file_src))
        
    def copy_agent_config(self, exp_data):
        path_src = os.sep.join(self.config["paths"]["agent_config"])
        file_src = self.config["config"]["agent_config"] + exp_data["exp_invocation"]["agent_properties"] + self.config["config"]["config_ext"]
        path_dest = os.path.join(exp_data["job_parameters"]['job_dir'])
        
        shutil.copyfile(os.path.join(path_src, file_src), os.path.join(path_dest, file_src))        
            
    def make_job_path(self, path, verbose):
        if not os.path.isdir(path):
            try:
                os.makedirs(path, exist_ok=True)
                if verbose:
                    print(os.path.basename(__file__) + ":: created new job_path: " + path)
            except  OSError as e:
                print(os.path.basename(__file__) + ":: The job_path " + path + " already exists. OSError caught: " + e)


    def retrieve_matrix(self, rgs, gameform, reward_type):       

        
        if re.match(r"[g]\d{3}", gameform):
            topology_items = rgs.reference_rgs
            canonical_matrix = topology_items[gameform]
            print(os.path.basename(__file__) + ":: gameform match to topology")
            
        else:
            import importlib
            from model.rgs.rgs_canonical import Rgs_canonical as rgs_canonical
            
            game_properties = {"preferences": reward_type}
            gameform_lookup = rgs_canonical().map_gameform_modules()
            _m = importlib.import_module('model.rgs.canonical.{}'.format(gameform_lookup[gameform]), 'model')
            gameform_module = getattr(_m, str.capitalize(gameform_lookup[gameform]))(game_properties)
            canonical_matrix = gameform_module.matrix
        
        matrix = self.transform_reward_type(canonical_matrix, reward_type)
        
        return matrix


    def transform_reward_type(self, canonical_matrix, reward_type):

        matrix_transform = copy.deepcopy(canonical_matrix)
        print(os.path.basename(__file__) + " 1. transform_reward_type: ", canonical_matrix, matrix_transform)
        print(os.path.basename(__file__) + " 2. mapping transform_reward_type to:", reward_type)
        
        if reward_type == "ordinal" or reward_type == "scalar":
            print(os.path.basename(__file__) + " 2.1 noop, target_reward_type", reward_type)
            # Note, attempting to transform from rgs game(i.e., g111) to scalar reward type does not map to canonical or classical values.
            # in the case of ord->sca then noop
            
        else:
            
            (reward_type, precision) = reward_type.split(".")
            print(os.path.basename(__file__) + " 3. extracted reward_type, precision: ", reward_type, precision)
            
            if reward_type == "ordinal_norm":
                
                values = [1, 2, 3, 4]
                normalised_vector = self.normalise_reward_type(reward_type, int(precision), values)
                
                for i, r in enumerate(canonical_matrix):
                    for j, c in enumerate(r):
                        for k, v in enumerate(c):
                            matrix_transform[i][j][k] = normalised_vector[v-1]
                                
            elif reward_type == "scalar_norm":
                
                values = [0, 1, 3, 5]
                normalised_vector = self.normalise_reward_type(reward_type, int(precision), values)
                
                value_map = {
                    0 : normalised_vector[0],
                    1 : normalised_vector[1],
                    3 : normalised_vector[2],
                    5 : normalised_vector[3],
                }
                
                for i, r in enumerate(canonical_matrix):
                    for j, c in enumerate(r):
                        for k, v in enumerate(c):
                            matrix_transform[i][j][k] = value_map[v]
                
        print(os.path.basename(__file__) + " 4. transform_reward_type: ", canonical_matrix, matrix_transform)

        return matrix_transform      


    def normalise_reward_type(self, reward_type, precision, values):
                
        max_value = max(values)
        min_value = min(values)
        for i in range(len(values)):
            values[i] = round((values[i] - min_value) / (max_value - min_value), precision)
                
        return values        