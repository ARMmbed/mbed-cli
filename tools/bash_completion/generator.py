#!/usr/bin/env python
# Michael Bartling (michael.bartling@arm.com)

from collections import defaultdict
import pystache
import re
import subprocess

# Top level --version is a pain to deal with so ignoring for now
# This one extracts single commands and the help txt
commandRegex = r"^\s+(?P<command>\w+)\s+(?P<helptxt>[a-zA-Z ]*)$"

# Why the hell do spaces get regexed in command1 ?
subcommandRegex = r"^\s+(?P<command1>-+[a-zA-Z_\-]+(?P<modifier1>\s+[A-Z_\-]+)?)"\
    r"(?P<command2>,\s+-+[a-zA-Z_-]+(?P<modifier2>\s+[A-Z_-]+)?)?"\
    r"\s+(?P<helptxt>.*)$"


def getHelpTxt(command=None):
    if command:
        p = subprocess.Popen(["mbed", command, "-h"], stdout=subprocess.PIPE)
    else:
        p = subprocess.Popen(["mbed", "-h"], stdout=subprocess.PIPE)
    out, err = p.communicate()
    return out

def getTargetCode():
    with open("templates/target.tmplt") as fp:
        txt = fp.read()
    return txt

def getToolchainCode():
    with open("templates/toolchain.tmplt") as fp:
        txt = fp.read()
    return txt

def getSCMCode():
    with open("templates/scm.tmplt") as fp:
        txt = fp.read()
    return txt

def getIDECode():
    with open("templates/ide.tmplt") as fp:
        txt = fp.read()
    return txt

def getProtocolCode():
    with open("templates/protocol.tmplt") as fp:
        txt = fp.read()
    return txt

def parseCommands():
    commands = defaultdict(defaultdict)
    commands["COMMAND"] = []
    helpTxt = getHelpTxt()
    # print helpTxt
    for line in helpTxt.split('\n'):
        match = re.search(commandRegex, line)
        if match:
            g = match.groupdict()
            commands[g["command"]]["helptxt"] = g["helptxt"]
            commands[g["command"]]["subcommands"] = []

            # Subcommand mustache generation
            commands[g["command"]]["DDASH_COMMANDS"] = []
            commands[g["command"]]["DASH_COMMANDS"] = []
            commands[g["command"]]["COMMAND"] = g["command"]

            commands[g["command"]]["HAVE_PREV"] = {"PREV_CASE": []}

            # Main function generation
            commands["COMMAND"].append({"name": g["command"]})

    for commandKey in commands:
        # Skip
        if commandKey == "COMMAND":
            continue

        helpTxt = getHelpTxt(commandKey)
        for line in helpTxt.split('\n'):
            match = re.search(subcommandRegex, line)
            if match:
                commandMatch = match.groupdict()

                # Clean up the subcommands
                command1 = commandMatch["command1"]
                command2 = commandMatch["command2"]

                if command1:
                    command1 = re.sub(",", "", command1)
                    command1.strip()
                    command1 = command1.split()[0]
                if command2:
                    command2 = re.sub(",", "", command2)
                    command2.strip()
                    command2 = command2.split()[0]

                # Not sure why the cleaning is even necessary,
                # the regex looks correct
                commandMatch["command1"] = command1
                commandMatch["command2"] = command2

                commands[commandKey]["subcommands"].append(commandMatch)

                # Push format for mustache
                if command1 and '--' in command1:
                    commands[commandKey]["DDASH_COMMANDS"].append(
                        {"name": command1})
                if command2 and '--' in command2:
                    commands[commandKey]["DDASH_COMMANDS"].append(
                        {"name": command2})

                if command1:
                    m = re.match("^-[a-zA-Z]{1,2}", command1)
                    if m:
                        commands[commandKey]["DASH_COMMANDS"].append(
                            {"name": command1})
                else:
                    command1 = ""

                if command2:
                    m = re.match("^-[a-zA-Z]{1,2}", command2)
                    if m:
                        commands[commandKey]["DASH_COMMANDS"].append(
                            {"name": command2})
                else:
                    command2 = ""

                # Adding the dependent command handlers
                if "target" in command1 or "target" in command2:
                    commands[commandKey]["HAVE_PREV"]["PREV_CASE"].append({"case": "|".join(filter(None, [command1, command2])), "code": getTargetCode()})

                if "toolchain" in command1 or "toolchain" in command2:
                    commands[commandKey]["HAVE_PREV"]["PREV_CASE"].append({"case": "|".join(filter(None, [command1, command2])), "code": getToolchainCode()})
                

                if "--ide" in command1 or "--ide" in command2:
                    commands[commandKey]["HAVE_PREV"]["PREV_CASE"].append({"case": "|".join(filter(None, [command1, command2])), "code": getIDECode()})

                if "scm" in command1 or "scm" in command2:
                    commands[commandKey]["HAVE_PREV"]["PREV_CASE"].append({"case": "|".join(filter(None, [command1, command2])), "code": getSCMCode()})
                
                if "protocol" in command1 or "protocol" in command2:
                    commands[commandKey]["HAVE_PREV"]["PREV_CASE"].append({"case": "|".join(filter(None, [command1, command2])), "code": getProtocolCode()})
                
        # Adding the dependent command handlers for target and toolchain
        if "target" in commandKey:
            commands[commandKey]["HAVE_PREV"]["PREV_CASE"].append({"case": commandKey, "code": getTargetCode()})
                
        if "toolchain" in commandKey:
            commands[commandKey]["HAVE_PREV"]["PREV_CASE"].append({"case": commandKey, "code": getToolchainCode()})

    return commands


def generateMain(commands):
    txt = []

    with open("templates/mbed.tmplt") as fp:
        tmplt = fp.read()

    txt.append(pystache.render(tmplt, commands))

    return txt


def generateCompleters(commands):
    txt = []

    renderer = pystache.Renderer(escape=lambda u: u)

    with open("templates/command.tmplt") as fp:
        tmplt = fp.read()

    for commandKey in commands:
        txt.append(renderer.render(tmplt, commands[commandKey]))

        # if need to add hacks add them here

    return txt


def generateBoilerPlate(_):
    txt = []

    with open("templates/boilerplate.tmplt") as fp:
        txt.append(fp.read())

    return txt


def generateScript(commands):
    txt = []

    txt.extend(generateBoilerPlate(commands))
    txt.extend(generateCompleters(commands))
    txt.extend(generateMain(commands))

    with open("mbed-completion", "w") as fp:
        for x in txt:
            fp.write("%s\n" % x)


if __name__ == '__main__':
    commands = parseCommands()

    # At this point we have a list of all the commands and sub commands
    # for each command create a Bash function
    # register each subcommand
    generateScript(commands)
