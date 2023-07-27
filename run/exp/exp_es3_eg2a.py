#!/usr/bin/env python3
'''
Experiment Series Three: Experiment Group Two subgroup A

usage: 
        "hj:w:g:s:k:z:v:", ["pbs_jobstr", "pbs_scratch_dir",  "write_state", "compress_writes", "verbose"]
        
        python -m exp_es3_eg1a -j __STR__ -s __STR__ -w __STR__ -a __STR__ -k true -z false -v true
        
        
        OPTIONS
            -h: help
            -j: pbs_jobstr
            -s: scratch_dir
            -w: world_properties
            -a: agent_properties
            -k: write_state
            -z: compress_writes
            -v: verbose
            
            
            
    
'''

import os, sys, getopt
import re

from time import process_time_ns, time_ns
from datetime import datetime

'''
    instantiate an experiment group
        - ES3_EG2
            - two agents 
            - number of actions available defined by environment
            - env responsible for treatment of time
            - env responsible for collection of required data

'''


import model.world.exp_es3_eg2a as environment

from run.util.exp_util import Exp_utility as exp_utility




def main(argv):
    '''
        Initialise Experiment 
    '''
    exp_data = initialise_exp_data()
    parse_input(exp_data, argv)
    
    exp_utility().set_basepath(exp_data)
    exp_utility().set_exp_data_start(exp_data)
    exp_utility().make_exp_job_paths(exp_data)
    
    
    '''
        load property files for world and agents
            - in form 
                    "exp_world_properties_es3_eg2a.json"
                    "exp_agent_properties_es3_eg2a_allc.json"
                    
        instance ID obtainable from __JOBSTR__
    '''
    
    instance_id = int(exp_data["job_parameters"]["pbs_sub_jobid"])
    
    world_config = exp_utility().load_world_config(exp_data["exp_invocation"]["world_properties"])
    agent_config = exp_utility().load_agent_config(exp_data["exp_invocation"]["agent_properties"])

    exp_utility().set_properties(exp_data, world_config, agent_config)
    
    
    '''
        instantiate agents and environment with given properties
            - agents as defined in agent_properties plus env-defined num_actions
            - environment may require an instance_id (will do so for exp grp one - instance id maps to rgs)
            
        Note: we cannot add num_actions to the agent_config until instantiation as there are several methods for instantiation,
        some of whihc require the agent_id. so pass the env-supplied num_actions through. would be nice to enapsulate it somewhere,
        i.e., disappear it from this level but for now this works fine.
    
    '''
    agents = exp_utility().create_agents(agent_config, world_config["num_actions"], exp_data["exp_invocation"]["exp_type"], world_config["defection"]) 
    
    env = environment.Exp_es3_eg2a("exp_es3_eg2a", world_config, agents, instance_id, exp_data)
    
    
    
    
    ''' 
       run the model 
    '''
    
    env.run(exp_data)
    
    ''' 
        
    ''' 
    
    exp_utility().set_exp_data_end(exp_data)
    exp_utility().copy_configs(exp_data)
    exp_utility().write_exp_data_summary(exp_data)


   
   
   

def parse_input(exp_data, argv):

    try:
        options, args = getopt.getopt(argv, "hj:s:w:a:k:z:c:v:", ["pbs_jobstr", "scratch_dir", "world_properties", "agent_properties", "write_state", "compress_writes", "verbose"])
        print(os.path.basename(__file__) + ":: args", options)
    except getopt.GetoptError:
        print(os.path.basename(__file__) + ":: error in input, try -h for help")
        sys.exit(2)
        
    for opt, arg in options:
    
        if opt == '-h':
            print("usage: " + os.path.basename(__file__) + " \r\n \
            -j <pbs_jobstr [__JOBSTR__]> | \r\n \
            -s <scratch_dir [__PATH__]> | \r\n \
            -w <world_properties ['{file}.world_properties'|'na']> \r\n \
            -a <agent_properties ['{file}.agent_properties'|'na']> \r\n \
            -k <write_state> boolean (default is false)\r\n \
            -z <compress_writes> boolean (default is true) \r\n \
            -v <verbose> \r\n \
        ")
        
        elif opt in ('-j', '--pbs_jobstr'):
            exp_data["job_parameters"]["pbs_jobstr"] = arg
            
        elif opt in ('-s', '--scratch_dir'):
            exp_data["job_parameters"]["scratch_dir"] = arg
            if arg == "localhost":
                exp_data["exp_invocation"]["localhost"] = True
            
        
            
        elif opt in ('-w', '--world_properties'):
            exp_data["exp_invocation"]["world_properties"] = arg
        elif opt in ('-a', '--agent_properties'):
            exp_data["exp_invocation"]["agent_properties"] = arg            
        
        elif opt in ('-k', '--write_state'):
            if arg == 'true':
                exp_data["exp_invocation"]["write_state"] = True
            
        elif opt in ('-z', '--compress_writes'):
            if arg == 'false':
                exp_data["exp_invocation"]["compress_writes"] = False
 
        elif opt in ('-v', '--verbose'):
            if arg == 'true':
                exp_data["exp_invocation"]["verbose"] = True 
    
    if not options:
        print(os.path.basename(__file__) + ":: error in input: no options supplied, try -h for help")
    else:
        exp_data["exp_invocation"]["exp_args"] = options
        
    if exp_data["job_parameters"]["pbs_jobstr"] == "":
        print(os.path.basename(__file__) + ":: error in input: pbs_jobstr is required, use -j __STR__ or try -h for help")
        sys.exit(2)
        
    if exp_data["job_parameters"]["scratch_dir"] == "":
        print(os.path.basename(__file__) + ":: error in input: scratch_dir is required, use -s __STR__ or try -h for help")
        sys.exit(2) 
          

      
    if exp_data["exp_invocation"]["world_properties"] == "" :
        print(os.path.basename(__file__) + ":: error in input: world_properties is required, use -w __STR__ or try -h for help")
        sys.exit(2)
        
    if exp_data["exp_invocation"]["agent_properties"] == "" :
        print(os.path.basename(__file__) + ":: error in input: agent_properties is required, use -a __STR__ or try -h for help")
        sys.exit(2)        
    
    
def initialise_exp_data():    
    
    exp_time_start_ns = time_ns()
    
    return {
        "exp_id"                    : "",
        "journal_output_filename"   : "",
        "job_parameters"            : {
            "pbs_jobstr"            : "",
            "pbs_jobid"             : "",
            "pbs_parent_jobid"      : "",
            "pbs_sub_jobid"         : 0,
            "scratch_dir"           : "",
            "hpc_name"              : "",
            "data_filename_prefix"  : "",
            "job_dir"               : "",
            "job_args"              : "",
            "heartbeat_path"        : "",
            "heartbeat_interval"    : 0
        },
        "exp_invocation"          : {
            "filename"              : __file__,
            "exp_args"              : "",
            "exp_time_start_hr"     : datetime.fromtimestamp(exp_time_start_ns / 1E9).strftime("%d%m%Y-%H%M%S"),
            "exp_time_end_hr"       : "",
            "exp_time_start_ns"     : str(exp_time_start_ns),
            "exp_time_end_ns"       : "",
            "process_start_ns"      : process_time_ns(),
            "process_end_ns"        : 0,
            "exp_type"              : re.search(r"exp_([A-Za-z_0-9\s]*)", os.path.basename(__file__))[1],
            
            "world_properties"      : {},
            "agent_properties"      : {},
            
            "write_state"           : False,
            "compress_writes"       : True,
            "localhost"             : False,
            "home"				    : "",
            "basepath"				: "",
            "verbose"               : False,            
        },
        "agent_properties"      : {},
        "world_properties"      : {},

    }

    
if __name__ == '__main__':
    main(sys.argv[1:]) 