#!/usr/bin/env python

from collections import defaultdict
import re
import subprocess

commandRegex = r"^\s+(?P<command>\w+)\s+(?P<helptxt>[a-zA-Z ]*)$"  # This one extracts single commands and the help txt
# Why the hell do spaces get regexed in command1 ?
subcommandRegex = r"^\s+(?P<command1>-+[a-zA-Z_\-]+(?P<modifier1>\s+[A-Z_\-]+){0,1})(?P<command2>,\s+-+[a-zA-Z_-]+(?P<modifier2>\s+[A-Z_-]+){0,1}){0,1}\s+(?P<helptxt>.*)$" # Gets just about everything

def getHelpTxt(command=None):
    if command:
        p = subprocess.Popen(["mbed", command, "-h"], stdout=subprocess.PIPE)
    else:
        p = subprocess.Popen(["mbed", "-h"], stdout=subprocess.PIPE)
    out, err = p.communicate()
    return out

if __name__ == '__main__':
    #commands = defaultdict(defaultdict(list))
    commands = defaultdict(defaultdict)
    helpTxt = getHelpTxt()
    #print helpTxt
    for line in helpTxt.split('\n'):
        match = re.search(commandRegex, line)
        if match:
            print "have match"
            g = match.groupdict()
            commands[g["command"]]["helptxt"] = g["helptxt"]
            commands[g["command"]]["subcommands"] = []

    for commandKey in commands:
        command = commands[commandKey]
        helpTxt = getHelpTxt(commandKey)
        for line in helpTxt.split('\n'):
            match = re.search(subcommandRegex, line)
            if match:
                print match.groupdict()
        
# At this point we have a list of all the commands and sub commands
# for each command create a Bash function
# register each subcommand
