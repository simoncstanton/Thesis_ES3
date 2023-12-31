#!/usr/bin/env python3
# file: obs_compile_exp_recog_summary.py
'''
    obs_compile_exp_summary
        - create obs_id
       
        - assemble job parameters: jobid, e, t, s, g, r
        - create exp_id 
        - create exp_description from job_parameters
             - open each exp result EU and OU file
                - assemble
                    - resources_used.cpupercent
                    - resources_used.cput
                    - resources_used.mem
                    - resources_used.ncpus
                    - resources_used.vmem
                    - resources_used.walltime
                    - results data size
        - create eo_id
        
        usage: 
            for localhost execution:
                python -m obs_compile_exp_summary -j __STR__ -l true
'''

import os
import sys, getopt

import time
from datetime import datetime

import re

from run.obs.obs_util import Obs_utility as obs_utility
from run.obs.view_util import View_utility as view_utility

def main(argv):

    obs_data = initialise_obs_data()
    hpc_config = view_utility().load_hpc_config()

    parse_input(argv, obs_data)
    obs_utility().set_basepath(obs_data)
    print(obs_data)
    obs_utility().recog_set_obs_data_start(obs_data)    
    obs_data_summary = obs_utility().retrieve_obs_data_summary(obs_data)
    
    obs_utility().make_recog_job_paths(obs_data, obs_data_summary)
        
    result_set_data_gamelock_reward = {}
    result_set_data_gamelock_pref = {}
    result_set_data_interlock_reward = {}
    leaf_dir = hpc_config["exp_data_leaf_dirs"]["recog"]
    
    #print("Gamelock Reward") # writes 1 file: view_001_recog_complete_gamelock_reward.csv
    #result_set_data_gamelock_reward = obs_utility().fetch_all_subjobs_result_set_data_recog(obs_data, obs_data_summary, leaf_dir, "gamelock_reward")
    #obs_utility().recog_assemble_gamelock_df(result_set_data_gamelock_reward, obs_data, obs_data_summary, "gamelock_reward")

    print("Gamelock Pref") # writes 1 file: view_001_recog_complete_gamelock_pref.csv
    result_set_data_gamelock_pref = obs_utility().fetch_all_subjobs_result_set_data_recog(obs_data, obs_data_summary, leaf_dir, "gamelock_pref")
    obs_utility().recog_assemble_gamelock_df(result_set_data_gamelock_pref, obs_data, obs_data_summary, "gamelock_pref")


    # agents reward interlocks  # writes two files: view_001_recog_interlock_reward_agent_0 , ..._1
    #print("Agent Interlock Reward")
    #result_set_data_interlock_reward = obs_utility().fetch_all_subjobs_result_set_data_recog(obs_data, obs_data_summary, leaf_dir, "interlock_reward")
    #obs_utility().recog_assemble_interlock_df(result_set_data_interlock_reward, obs_data, obs_data_summary, "interlock_reward", "0")
    #obs_utility().recog_assemble_interlock_df(result_set_data_interlock_reward, obs_data, obs_data_summary, "interlock_reward", "1")

    # agents pref interlocks  # writes two files: view_001_recog_interlock_pref_agent_0 , ..._1
    print("Agent Interlock Preference")
    result_set_data_interlock_pref = obs_utility().fetch_all_subjobs_result_set_data_recog(obs_data, obs_data_summary, leaf_dir, "interlock_pref")
    obs_utility().recog_assemble_interlock_df(result_set_data_interlock_pref, obs_data, obs_data_summary, "interlock_pref", "0")
    obs_utility().recog_assemble_interlock_df(result_set_data_interlock_pref, obs_data, obs_data_summary, "interlock_pref", "1")





    #result_set_data_interlock = obs_utility().fetch_all_subjobs_result_set_data_recog(obs_data, obs_data_summary, leaf_dir, "interlock")
    #obs_utility().recog_assemble_interlock_df(result_set_data_interlock, obs_data, obs_data_summary, "interlock", "0")
    #obs_utility().recog_assemble_interlock_df(result_set_data_interlock, obs_data, obs_data_summary, "interlock", "1")


    #obs_utility().recog_set_obs_data_end(obs_data, obs_data_summary)
    #obs_utility().recog_write_obs_data_summary(obs_data, obs_data_summary)
    #obs_utility().recog_write_obs_journal(obs_data, obs_data_summary)
    
    
   
def parse_input(argv, obs_data):

    try:
        options, args = getopt.getopt(argv, "hj:l:", ["exp_id", "localhost"])
        print(os.path.basename(__file__) + ":: args", options)
    except getopt.GetoptError:
        print(os.path.basename(__file__) + ":: error in input, try -h for help")
        sys.exit(2)
        
    for opt, arg in options:
        if opt == '-h':
            print("usage: " + os.path.basename(__file__) + " \r\n \
            -j <pbs_jobstr [__JOBSTR__]> | \r\n \
            -l <localhost> boolean (default is false) \r\n \
        ")
        
        elif opt in ('-j', '--pbs_jobstr'):
            obs_data["obs_exp"]["exp_parent_id"] = arg
            

             
    if obs_data["obs_exp"]["exp_parent_id"] == "":
        print(os.path.basename(__file__) + ":: error in input: exp_parent_id is required, use -j __STR__ or try -h for help")
        sys.exit(2)
    
    elif opt in ('-l', '--localhost'):
        if arg == 'true':
            obs_data["obs_invocation"]["localhost"] = True
                
    if not options:
        print(os.path.basename(__file__) + ":: error in input: no options supplied, try -h for help")
        
    else:
        obs_data["obs_invocation"]["obs_args"] = options
        
         
        
  
def initialise_obs_data():    
    '''
        exp_data is added to obs_data in main()::meta_access_exp_result_set()

    '''
    obs_time_start_ns = time.time_ns()
    
    return {
        "obs_id"                    : str(time.time_ns()),
        "eo_id"                     :   "",
        "journal_output_filename"   : "",
        "obs_exp"   : {
            "exp_parent_id"             : "",
            "exp_type"                  : "",
            "exp_episodes"              : "",
            "exp_timesteps"             : "",
            "exp_strategy_set"          : "",
            "exp_gameform_list"         : "",
            "exp_localhost"             : False,
            "exp_server"                : "",
            "exp_data_path"             : "",
            "exp_heartbeat_path"        : "",
            "exp_journal_path"          : "",
            "exp_archive_total_size"    : "",
            "exp_compressed_writes"     : True,
            "result_set_extension"      : ".tar.gz",
            "exp_subjobs_list"          : [0],
            "exp_result_set"            : [],
            "exp_subjobs"  : {
                "0"                     : {
                    "exp_subjob_parent_id"          : 0,
                    "exp_subjob_id"                 : 0,
                    "exp_subjob_data_path"          : "",
                    "exp_subjob_data_file"          : "",
                    "exp_subjob_process_time_ns"    : 0,
                    "exp_subjob_result_set_size"    : 0,
                    "exp_subjob_pbs_resources_used" : {
                        "cpupercent"                : "",
                        "cput"                      : "",
                        "mem"                       : "",
                        "ncpus"                     : "",
                        "vmem"                      : "",
                        "walltime"                  : "",
                    },
                    "exp_summary" : {},
                }
            },
        },
        "obs_invocation"        : {
            "filename"              : __file__,
            "obs_args"              : "",
            "obs_type"              : re.search(r"obs_([A-Za-z_\s]*)", os.path.basename(__file__))[1],
            "obs_time_start_hr"     : datetime.fromtimestamp(obs_time_start_ns / 1E9).strftime("%d%m%Y-%H%M%S"),
            "obs_time_end_hr"       : "",
            "obs_time_start_ns"     : obs_time_start_ns,
            "obs_time_end_ns"       : 0,
            "process_start_ns"      : time.process_time_ns(),
            "process_end_ns"        : 0,
            "localhost"             : False,
            "home"				    : "",
            "basepath"				: "",
        },
        
    }

    
if __name__ == '__main__':
    main(sys.argv[1:]) 