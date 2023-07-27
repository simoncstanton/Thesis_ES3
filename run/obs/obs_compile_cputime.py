#!/usr/bin/env python3
'''

counts cpu time recorded inhournal files for every subjob in provided exp_id

'''

import os
import sys, getopt
import re
import time
from datetime import datetime

#from run_obs.orderset_components import obs_compile_exp_summary as exp_summary

#from run_obs.obs_util import Obs_utility as obs_utility
from run.obs.obs_util import Obs_utility as obs_utility


def main(argv):
    
    
    obs_data = initialise_obs_data()
    
    parse_input(argv, obs_data)
    obs_utility().set_basepath(obs_data)

    obs_utility().meta_access_exp_result_set(obs_data, 0) 


    
    obs_utility().set_obs_data_start_compile_cputime(obs_data)

    #print(obs_data)



    sj_count = len(obs_data["obs_exp"]["exp_subjobs_list"])

    #print(sj_count)
    total_cpu_nanoseconds = 0
    total_cpu_seconds = 0

    #print(obs_data["obs_exp"]["exp_subjobs"]["0"]["exp_summary"]["exp_invocation"]["process_start_ns"])

    for sj in range(sj_count):
        start = obs_data["obs_exp"]["exp_subjobs"][str(sj)]["exp_summary"]["exp_invocation"]["process_start_ns"]
        end = obs_data["obs_exp"]["exp_subjobs"][str(sj)]["exp_summary"]["exp_invocation"]["process_end_ns"]
        print(end - start)
        total_cpu_nanoseconds = total_cpu_nanoseconds + (end - start)



    total_cpu_seconds = total_cpu_nanoseconds/1000000000

    print(total_cpu_seconds/60)


    # look in exp_type/exp_id



    #   count sj


    #   iterate sj


    #   collect cputime

    #start = obs_data["obs_invocation"]["process_start_ns"]
    #end = obs_data["obs_invocation"]["process_end_ns"]
    #print(start - end)

    #   sum, print,write.








    #exp_summary.main(argv[1:])
    



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