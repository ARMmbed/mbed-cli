# Introduction

*neo* is the name of the Morpheus command line tool.
It allows cloning of a Morpheus repository and its dependencies (.lib files), compiling the code in the repository, pushing/pulling the code and other operations.
The rest of this document details the installation and usage of *neo*.

# Installation

Currently, *neo* lives in https://github.com/ARMmbed/neo.

**NOTE**: if you don't have permissions to access the above repository, e-mail mihail.stoyanov@arm.com or bogdan.marinescu@arm.com with your github account name.

*neo* is a Python script, so you'll need Python installed in order to use it. *neo* was tested with version 2.7 of Python.

To get the latest version of *neo*, clone the above repository.

```
$ git clone https://github.com/ARMmbed/neo
```

To complete the installation of the `neo.py` script, make sure that the folder with `neo.py` (`neo` in this case) is in your PATH.

*neo* supports both git and mercurial repositories, so you'll also need to install mercurial and git. Use whatever installers you like, but remember that the directories containing the executables of `hg` and `git` need to be in your PATH.

# Using neo

Use `neo.py import` to clone a project and all its dependencies to your machine:

```
$ neo.py import https://developer.mbed.org/teams/Morpheus/code/mbed-Client-Morpheus-from-source/
$ cd mbed-Client-Morpheus-from-source
```

**NOTE**: some of the repositories that *neo* will clone might require special access (mercurial will ask you for your credentials if that's the case). If you don't have access, e-mail mihail.stoyanov@arm.com or bogdan.marinrescu@arm.com with your developer.mbed.org account name.

After importing, you need to tell *neo* where to find the toolchains that you want to use for compiling your source tree. *neo* gets this information from a file named `mbed_settings.py`, which is automatically created at the top of your cloned repository (if it doesn't already exist). As a rule, since `mbed_settings.py` contains local settings (possible relevant only to a single OS on a single machine), it should not be versioned. In this file:

-   if you want to use the [armcc toolchain](https://developer.arm.com/products/software-development-tools/compilers/arm-compiler-5/downloads), set **ARM_PATH** to the *base* directory of your armcc installation (example: c:\software\armcc5.06). The recommended version of the armcc toolchain is 5.06 (5.05 will very likely work too).
-   if you want to use the [GCC ARM Embedded toolchain](https://launchpad.net/gcc-arm-embedded), set **GCC_ARM_PATH** to the *binary* directory of your GCC ARM installation (example: c:\software\GNUToolsARMEmbedded\4.82013q4\bin). Use version 4.8 or 4.9 of GCC ARM Embedded, but **not** version 5.0 or any version above it.

Use `neo.py compile` to compile the code:

```
$ neo.py compile -t ARM -m K64F -j 0
```

The arguments to *compile* are:

-   `-m <mcu>` to select a target for the compilation. At the moment, the only supported value for `mcu` is `K64F` for the FRDM_K64F board.
-   `-t <toolchain>` to select a toolchain, where `toolchain` can be: ARM (armcc compiler), GCC_ARM (GNU ARM Embedded)
-   `-j <jobs>` (optional): will use multiple threads on your machine to compile the source (use 0 to infer the number of threads from the number of cores on your machine, or an actual number to specify the maximum number of thread).

The compiled binary (and ELF image) can be found in the `.build` subdirectory of your project.

If you need to debug your code, a good way to do that is to export your source tree to an IDE project file, so that you can use the IDE's debugging facilities. Currently *neo* supports exporting to Keil uVision. To export, run this command:

```
$ neo.py export -i uvision -m K64F
```

After running this command, a .uvproj file will be created at the top of your source tree, you can open that with uVision.

While working on your code, you might need to add another library (dependency) to your application. Use `neo.py add` to do that:

```
$ neo.py add https://developer.mbed.org/components/HD44780-Text-LCD/
```

**IMPORTANT**: adding a new library to your Morpheus project is not the same thing as just cloning the library locally. Use `neo.py add` to add the library, don't clone it direcly using hg or git.

If at some point you decide that you don't need a library anymore, you can use `neo.py remove` with the path of the library to get rid of it:

```
$ neo.py remove HD44780-Text-LCD
```

**IMPORTANT**: removing a library from your Morpheus project is not the same thing as just deleting its local clone. Use `neo.py remove` to remove the library, don't simply remove its directory with 'rm'.

# Other commands

The previous section showed the most usual commands in *neo*. This section lists the other available commands.

## deploy

Use *deploy* to clone the dependencies of an application (or library) that already exists on your machine, but its `.lib` dependencies are not yet cloned. For example, if you have a repository that looks like this:

```
main.cpp
mbed-os.lib
```

use `neo.py deploy` to clone `mbed-os` and all its dependencies locally.

## ls

Lists the revisions of the top level project and all its repositories.

```
$ neo.py ls
```

## status

Gets the status of all the repositories in the project, recursively. If a repository has uncomitted changes, this command will display these changes.

```
$ neo.py status
```

