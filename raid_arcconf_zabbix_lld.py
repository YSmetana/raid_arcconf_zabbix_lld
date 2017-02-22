#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 03.01.17, SYM

""" 
Zabbix LLD and monitoring script for Adaptec controllers.

See README.md for details
"""

import argparse
from subprocess import check_output, CalledProcessError
import logging
import os
import json
import re

parser = argparse.ArgumentParser(
    description='Adaptec RAID controller (arcconf compatible) LLD and monitoring for Zabbix.',
    epilog="""Example of use:
    
        > ./raid_arcconf_zabbix_lld.py ld -1 lld
        > {"data": [{"{#OBJ_ALIAS}": "zeta-r1-3t", "{#OBJ_TYPE}": "ld", "{#OBJ_ID}": 0}]}

        > ./raid_arcconf_zabbix_lld.py ld 0 'Status of Logical Device'
        > Optimal        

        > ./raid_arcconf_zabbix_lld/raid_arcconf_zabbix_lld.py --verbose pd -1 lld
        > ERROR - Command '['arcconf', 'GETCONFIG', '1', 'PD', '0']' returned non-zero exit status 6
        > Traceback (most recent call last)
        > ...

        See README.md for installation details.
    """,
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument('obj_type',
                        choices=['ad', 'ld', 'pd'],
                        help='Type of information needed (ad - adapter (controller), ld - logical disk/RAID, pd - physical disk).'
                        )
parser.add_argument('obj_id', type=int, help='Logical disk ID, or physical disk ID. -1 for Zabbix LLD.')
parser.add_argument('param', help='Object parameter (status, size etc - as in arcconf output). "lld" for Zabbix LLD.')            
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
args = parser.parse_args()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter2 = logging.Formatter('%(levelname)s - %(message)s')
ch.setFormatter(formatter2)
logger.addHandler(ch)

if args.verbose:
    ch.setLevel(logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
else:
    ch.setLevel(logging.INFO)

# Result for LLD
data=[]

def run(command):
    """ Run shell command.

    Args:
        command (str): command with attributes.

    Returns: command output, or False on error.
    """

    commands = command.split()

    try:
        res = check_output(commands, stderr=open(os.devnull, 'wb'))
        return res
    except CalledProcessError as e:
        if args.verbose:
            logger.error(e)
        return False

def col_value(data, key, index=0):
    """ Parse data as columns and returns 'value' for given 'key'.

    Args: 
        data    (str): raw output of 'arconf'.
        key     (str): key to search for.
        index   (int): if data consist of repeatable parts (multiple keys) - return N's key value. 

    Returns: 
        value of a key or False if key was not found.
    """

    col_index = 0

    for line in data.splitlines():
        columns = line.split(' : ')
        col_key = columns[0].strip()
        if col_key == key:
            if col_index == index:
                return columns[1].strip()
            col_index += 1
                
    # Nothing found?
    return False

def last_value(data, key, index=0):
    """" Parse data to find the 'key' and returns the last digit/word in the line.

    Args:
        data    (str): raw output of 'arconf'.
        key     (str): key to search for.
        index   (int): if data consist of repeatable parts (multiple keys) - return N's key value.

    Returns:
        last digit/word in the line.
    """

    col_index = 0

    for line in data.splitlines():
        if key in line:
            if col_index == index:
                return line.split()[-1]

    # Nothing found?
    return False


if args.obj_type == 'ad':

    if args.obj_id == -1:

        for ad_num in [1]: # TODO 0-9 ?

            command = 'sudo /usr/sbin/arcconf GETCONFIG %d AD' %ad_num
            res = run(command)
    
            if res: # AD command returns exception (False) if AD number is wrong
                obj_data = {}            
                obj_data['{#OBJ_ID}'] = str(ad_num)
                obj_data['{#OBJ_TYPE}'] = 'ad'

                value = col_value(res, 'Controller Model')
                if value:
                    obj_data['{#OBJ_ALIAS}'] = value
    
                data.append(obj_data)
    # get value
    else:
        command = 'sudo /usr/sbin/arcconf GETCONFIG %d AD' %int(args.obj_id)
        res = run(command)

        if res:
            value = col_value(res, args.param)
            if value:
                print value

# Logical disk
if args.obj_type == 'ld':

    if args.obj_id == -1:

        command = 'sudo /usr/sbin/arcconf GETCONFIG 1 LD'
        res = run(command)
        
        for ld_num in range(10): # 0-9

            if last_value(res, 'Logical Device number %s' %ld_num):
                obj_data = {}
                obj_data['{#OBJ_ID}'] = ld_num
                obj_data['{#OBJ_TYPE}'] = 'ld'

                value = col_value(res, 'Logical Device name', ld_num)
                if value:
                    obj_data['{#OBJ_ALIAS}'] = value

                data.append(obj_data)

    # get value
    else:
        command = 'sudo /usr/sbin/arcconf GETCONFIG 1 LD %d' %int(args.obj_id)
        res = run(command)

        if res:
            value = col_value(res, args.param)
            if value:
                print value

# Physical disk
# For PD always add index number to the 'command'!
if args.obj_type == 'pd':

    if args.obj_id == -1:

        # Single command output consist of all physical discs
        command = 'sudo /usr/sbin/arcconf GETCONFIG 1 PD'
        res = run(command)

        if res:
        
            for pd_num in range(10): # 0-9
    
                if col_value(res, 'State', pd_num):
                    obj_data = {}
                    obj_data['{#OBJ_ID}'] = pd_num
                    obj_data['{#OBJ_TYPE}'] = 'pd'
    
                    pd_vendor = col_value(res, 'Vendor', pd_num)
                    pd_slot =  col_value(res, 'Reported Location', pd_num)
                    obj_data['{#OBJ_ALIAS}'] = '%s %s' %(pd_vendor, pd_slot)
    
                    data.append(obj_data)
    # get value
    else:
        command = "sudo /usr/sbin/arcconf GETCONFIG 1 PD"
        res = run(command)

        if res:
            value = col_value(res, args.param, args.obj_id)
            if value:
                print value

# Only for LLD
if args.obj_id == -1 and args.param == 'lld':
    print json.dumps({'data': data})
