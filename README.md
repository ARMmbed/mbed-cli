# Introduction

*mbed CLI* is the name of the ARM mbed command line tool, packaged as mbed-cli, which enables the full mbed workflow: repositories version control, maintaining dependencies, publishing code, updating from remotely hosted repositories (GitHub, GitLab and mbed.org), and invoking ARM mbed's own build system and export functions, among other operations.

This document covers the installation and usage of *mbed CLI*.

## Table of Contents
1. [Requirements](#requirements)
1. [Installing and uninstalling](#installing-mbed-cli)
1. [Working context and command help](#working-context-and-command-help)
1. [Creating and importing programs](#creating-and-importing-programs)
	1. [Importing an existing program](#importing-and-creating-programs)
	2. [Creating a new program](#creating-a-new-program)
1. [Adding and removing libraries](#adding-and-removing-libraries)
	1. [Adding a library](#adding-a-library)
	2. [Removing a library](#removing-a-library)
1. [Updating programs and libraries](#updating-programs-and-libraries)
	1. [Synchronizing library references](#synchronizing-library-references)
	2. [Removing a library](#removing-a-library)
	3. [Updating to an upstream version](#updating-to-an-upstream-version)
1. [Publishing your changes](#publishing-your-changes)
	1. [Checking status](#checking-status)
	2. [Pushing upstream](#pushing-upstream)
1. [Compiling code](#compiling-code)
	1. [Toolchain selection](#toolchain-selection)
	2. [Compiling your program](#compiling-your-program)
	3. [Compiling static libraries](#compiling-static-libraries)
	4. [Compiling tests](#compiling-tests)
1. [Exporting to desktop IDEs](#exporting-to-desktop-ides)
1. [Known limitations](#known-limitations)

## Installation

<span class="notes">**Note**: *mbed-cli* lives in [https://github.com/ARMmbed/mbed-cli](https://github.com/ARMmbed/mbed-cli). If you don't have permission to access the above repository, e-mail [mihail.stoyanov@arm.com](mailto:mihail.stoyanov@arm.com) or [bogdan.marinescu@arm.com](mailto:bogdan.marinescu@arm.com) with your GitHub account name.</span>

### Requirements

* *mbed-cli* is a Python script, so you'll need Python installed in order to use it. *mbed-cli* was tested with [version 2.7 of Python](https://www.python.org/download/releases/2.7/).

* *mbed-cli* supports both Git and Mercurial repositories, you'll need to install both:
    * [Mercurial](https://www.mercurial-scm.org/).
    * [Git](https://git-scm.com/).
	
<span class="tips">**Tip:** Remember that the directories containing the executables of `hg` and `git` need to be in your system's PATH.</span>


### Installing mbed-cli

1. To get the latest version of *mbed-cli*, clone the repository [https://github.com/ARMmbed/mbed-cli](https://github.com/ARMmbed/mbed-cli):

    ``$ git clone https://github.com/ARMmbed/mbed-cli``

1. Once cloned you can install *mbed-cli* as a python package:

    ``$ python setup.py install`` (on Linux/Mac, you may need to run with ``sudo`` as well)

### Uninstalling mbed-cli

To uninstall *mbed-cli* you can use:

``pip uninstall mbed-cli``


## Using mbed-cli

### Working context and command help

All *mbed CLI* commands use the current directory as a working context, meaning that before calling any *mbed* command, you should first change your working directory to the one you want to operate in. For example:
```
$ cd my-program
$ cd mbed-os
$ mbed update master # updates "mbed-os", not "my-program"
```

Also note that *mbed CLI* requires that a program, the root of the code tree, is under version control - either Git or Mercurial. This makes it possible to seamlessly switch between revisions of the whole program and its libraries, control the program history, synchronize the program with remote repositories, share it with others, etc. Version control is also the primary and preferred delivery mechanism for mbed OS source code, which allows everyone to contribute to mbed OS at any time!

*mbed CLI* provides list of all available commnads and global help via `mbed --help`, and also command-specific help via `--help` param to the command, e.g. `mbed update --help`. 

### Creating and importing programs

mbed CLI allows creating new programs and importing existing ones, always with the full mbed-os release as the program's basis.

#### Creating a new program

When you create a new program, *mbed-cli* automatically imports the [mbed-os library](https://github.com/ARMmbed/mbed-os/) for you. This library represents a **release** of mbed OS and will pull in all the components of the OS, including its build system and desktop IDE project generators. 

With this in mind, these are the steps for creating a new program (we'll call it `myprog`):

```
$ mbed new myprog  # this creates a new folder "myprog", initializes a new repository and imports the latest revision of the mbed-os dependency to your program tree.
$ cd myprog
$ mbed ls -a       # this lists all libraries in your program
myprog (no revision)
`- mbed-os (https://github.com/ARMmbed/mbed-os/#e472a51e45f30d793cbb430b6ebf3e1c53d82f57)
   |- core\mbedtls (https://mbed.org/teams/sandbox/code/mbedtls/#bef26f687287)
   |- core\uvisor-mbed-lib (https://github.com/ARMmbed/uvisor-mbed-lib/#32b6df4a39df49dd14624d1503c4f2a27ab62516)
   |- frameworks\greentea-client (https://github.com/bridadan/greentea-client/#398d96e25630ed62dfa7436bda8556d8d7e16969)
   |- net\atmel-rf-driver (https://github.com/ARMmbed/atmel-rf-driver-mirror/#f4c48e5e98f66f145882b404e67998ad5cf2fe28)
   |- net\coap-service (https://github.com/ARMmbed/coap-service-mirror/#0c78050989706c54c3e25c2854c379bdd734d539)
   |- net\mbed-client (https://github.com/ARMmbed/mbed-client-mirror/#2a839d6c5beff8c19b16f3edc7b3e7ae10d5a471)
   |- net\mbed-client-c (https://github.com/ARMmbed/mbed-client-c-mirror/#753541105a6fa7e1c66d905e0f2ee28815b3ffba)
   |- net\mbed-client-classic (https://github.com/ARMmbed/mbed-client-classic/#0cf03c143a2a612e8225c18a88ecb7918be69cf5)
   |- net\mbed-client-mbedtls (https://github.com/ARMmbed/mbed-client-mbedtls-mirror/#582821c96be81cbd92b3a33019051ad10a0d0693)
   |- net\mbed-client-randlib (https://github.com/ARMmbed/mbed-client-randlib-mirror/#237b3fa0255f00194113814e8cc47cc38ee7ac5b)
   |- net\mbed-mesh-api (https://github.com/ARMmbed/mbed-mesh-api-mirror/#f7a198bb1e668e6640bf8c46b99adcbdb49d9020)
   |- net\mbed-trace (https://github.com/ARMmbed/mbed-trace-mirror/#f9a11fcaa2b5be4dc85bb5721c0cabaf0a96ea6d)
   |- net\nanostack-hal-mbed-cmsis-rtos (https://github.com/ARMmbed/nanostack-hal-mbed-cmsis-rtos/#ab64e255deb92f6a363886cd621d60475738508a)
   |- net\nanostack-libservice (https://github.com/ARMmbed/nanostack-libservice-mirror/#e3f7da74a143fc5c822be6213e4b6eca3d7e007a)
   |- net\sal-iface-6lowpan-morpheus-private (https://github.com/ARMmbed/sal-iface-6lowpan-morpheus-private-mirror/#2b4852e22679353c7f96e1a90120933d4eadd6f6)
   |- net\sal-stack-nanostack-eventloop (https://github.com/ARMmbed/sal-stack-nanostack-eventloop-mirror/#627b9769e3521800161f3abab2be26b32b5fa91e)
   `- net\sal-stack-nanostack-private (https://github.com/ARMmbed/sal-stack-nanostack-private-mirror/#1374c77b03fb900425c09a1dd9a0cb8b4e4904ea)
```


<span class="notes">**Note**: At the moment, if you want to start from an existing folder in your workspace, you can simply use `mbed new .`, which will initialize a new Git or Mercurial repository in that folder. While this might seem like a limitation, it helps with correct versioning for all program files, and helps mbed-cli find mbed-os and tooling. You can always drop the version control by removing the ``.git`` or ``.hg`` source management folders.</span>


#### Importing an existing program

Use `mbed import` to clone an existing program and all its dependencies to your machine:

```
$ mbed import https://developer.mbed.org/teams/Morpheus/code/mbed-Client-Morpheus-from-source/
$ cd mbed-Client-Morpheus-from-source
```

<span class="notes">**Note**: Some of the repositories that *mbed-cli* will clone might require special access (Mercurial will ask you for your credentials if that's the case). If you don't have access, e-mail [mihail.stoyanov@arm.com](mailto:mihail.stoyanov@arm.com) or [bogdan.marinescu@arm.com](mailto:bogdan.marinescu@arm.com) with your developer.mbed.org account name.</span>

### Adding and removing libraries

While working on your code, you might need to add another library (dependency) to your application, or remove existing libraries.

#### Adding a library

___The add command___

Use `mbed add` to do that:

```
$ mbed add https://developer.mbed.org/users/wim/code/TextLCD/
```

To add a library at a specific revision you can use the full URL#hash:

``
$ mbed add https://developer.mbed.org/users/wim/code/TextLCD/#e5a0dcb43ecc
``

___Specifying a destination directory___

You can give an additional argument to `add` to specify the directory in which you want to add your library. For example, If you'd rather clone the previous library in a directory called "text-lcd" (instead of TextLCD):

```
$ mbed add https://developer.mbed.org/users/wim/code/TextLCD/ text-lcd
```

Note that cloning a repository in a directory with a different name than the name of the repository is not encouraged, since it can easily lead to confusion.

<span class="notes">**Note**: Adding a new library to your Morpheus program is not the same thing as just cloning the library locally. Don't clone a library using hg or git; use `mbed add` to add the library, and it will ensure that all library (or sub-library) dependencies are populated as well</span>


#### Removing a library

If at any point you decide that you don't need a library anymore, you can use `mbed remove` with the path of the library:

```
$ mbed remove TextLCD
```

<span class="notes">**Note**: Removing a library from your Morpheus program is not the same thing as just deleting its local clone. Use `mbed remove` to remove the library, don't simply remove its directory with 'rm'.</span>

<span class="warnings">**Warning**: *mbed-cli* stores information about libraries and dependencies in `lib_name.lib` reference files. While these files are human-readable, we *strongly* advise that you don't edit these manually and let *mbed-cli* manage them instead.</span>


### Updating programs and libraries

There are two main scenarios when you'll want to update your code:
* Update to a *moving* revision, for example the tip of a particular or current branch.
* Update to a *specific* revision, identified by revision hash or tag name.

Each scenario has two variants - update with local uncommitted changes (or *dirty* update), and update without local uncommitted changes (or *clean* update).


#### Updating to an upstream version

__Synchronizing library references__

Before updating you might want to synchronize any changes that you made to the directory structure by running ``mbed sync``, which will update the necessary library references and get rid of the invalid ones.

__Updating__

To update your program to another upstream version, go to the root folder of the program and run:

`mbed update [branch|tag|#rev]`. 

This fetches the latest revisions from the remote repository, updates the program to the specified branch, tag or revision (or to the latest one in the current branch if `#rev` is not specified), then fetches and updates recursively all the other dependencies to match the top-level dependencies in `#rev`. 

You can apply the same mechanism for libraries and their dependencies by executing the update command in the library folder instead of the root of your program.

<span style="background-color:#E6E6E6;border:1px solid #000;display:block; height:100%; padding:10px">**Note**: This command will fail if there are changes in your program or library that will be overwritten as a result of running `update`. This is by design: *mbed-cli* does not run operations that would result in overwriting local changes that are not yet committed. If you get an error, take care of your local changes (commit or use one of the switches below), then re-run `update`.</span>

#### Update options

<span style="background-color:#E6E6E6;border:1px solid #000;display:block; height:100%; padding:10px">**Note**: As with any *mbed CLI* command, `mbed update` uses the current directory as a working context, meaning that before calling `mbed update` you should first change your working directory to the one you want to update, e.g. `cd mbed-os`.</span>

To help understand what options you can use with *mbed-cli*, please see the examples below.

**Case 1: I want to update a program or a library to the latest version in a specific or current branch**

__I want to preserve my uncommitted changes__ 

Run `mbed update [branch]`. You might have to commit or stash your changes if the source control tool (Git or Mercurial) throws an error that the update will overwrite local changes.

__I want a clean update (and discard uncommitted changes)__

Run `mbed update [branch] --clean`

It's important to remember that specifying a branch to `mbed update` would only checkout that branch and won't automatically merge/fast-forward to the remote/upstream branch. You can run `mbed update` to merge (fast-forward) your local branch with the latest remote branch. On git you can do `git pull`.

**Case 2: I want to update a program or a library to a specific revision or a tag**
 
__I want to preserve my uncommitted changes__ 

Run `mbed update <#rev|tag_name>`. You might have to commit or stash your changes if they conflict with the latest revision.

__I want a clean update (discard changes)__

Run `mbed update <#rev|tag_name> --clean`

The `--clean` option tells *mbed-cli* to update that program or library and its dependencies, and discard all local changes.

__When you have unpublished local libraries__

There are two additional options that define how unpublished local libraries are handled:

`mbed update --ignore` - update the current program or library and its dependencies, and ignore any local unpublished libraries (they won't be deleted or modified, just ignored).

`mbed update --force` - update the current program or library and its dependencies, and discard all local unpublished repositories. Use this with caution as your local unpublished repositories cannot be restored unless you have a backup copy.

__Combining switches__

You can combine the switches above for the following scenarios:

`mbed update --clean --ignore` - update the current program or library and its dependencies, but ignore any local repositories. mbed-cli will update whatever it can from public repositories.

`mbed update --clean --force` - update the current program or library and all its dependencies, and restore my source tree to stock layout. This wipes every change that you made in the source tree that didn't belong to the original commit, including uncommitted changes and unpublished local libraries.

Use these with caution as your uncommitted changes and unpublished libraries cannot be restored.


### Publishing your changes

#### Checking status

As you work on your code, you'll edit parts of it - either your own program code or code in some of the libraries that you depend on. You can get the status of all the repositories in your program (recursively) by running `mbed status`. If a repository has uncommitted changes, this command will display these changes.

#### Pushing upstream

To push the changes in your local tree upstream, run `mbed publish`. `publish` works recursively, pushing the leaf dependencies first, then updating the dependents and pushing them too. 

This is best explained by an example. Let's assume that the list of dependencies of your program (obtained by running `mbed ls`) looks like this:

```
mbed-Client-Morpheus-from-source (189949915b9c)
`- mbed-os (71a471196d89)
   |- net (96479b47e63d)
   |  |- mbed-trace (506ad37c6bd7)
   |  |- LWIPInterface (82796df87b0a)
   |  |  |- lwip-sys (12e78a2462d0)
   |  |  |- lwip (08f08bfc3f3d)
   |  |  `- lwip-eth (4380f0749039)
   |  |- nanostack-libservice (a87c5afee2a6)
   |  |- mbed-client-classic (17cb48fbeb85)
   |  |- mbed-client (ae5178938864)
   |  |- mbed-client-mbedtls (b2db21f25041)
   |  |- NetworkSocketAPI (aa343098aa61)
   |  |  `- DnsQuery (248f32a9c48d)
   |  `- mbed-client-c (5d91b0f5038c)
   |- core (2f7f0a7fc6b3)
   |  |- mbedtls (dee5972f341f)
   |  |- mbed-uvisor (af27c87db9c2)
   |  `- mbed-rtos (bdd541595fc5)
   |- hal (e4b241e107f9)
   |  `- TARGET_Freescale (a35ebe05b3bd)
   |     |- TARGET_KPSDK_MCUS (e4d670b91a9a)
   |     `- TARGET_MCU_K64F (c5e2f793b59a)
   `- tools (042963870f7a)
```

Furthermore, let's assume that you make changes to `lwip-eth`. `publish` detects the change on the leaf `lwip-eth` dependency and asks you to commit it. Then it detects that `LWIPInterface` depends on `lwip-eth`, updates LWIPInterface's dependency on `lwip-eth` to its latest version (by updating the `lwip-eth.lib` file inside `LWIPINterface`) and asks you to commit it. This propagates up to `net`, `mbed-os` and finally `mbed-Client-Morpheus-from-source`.


### Compiling code

#### Toolchain selection

After importing a program or creating a new one, you need to tell *mbed-cli* where to find the toolchains that you want to use for compiling your source tree. *mbed-cli* gets this information from a file named `mbed_settings.py`, which is automatically created at the top of your cloned repository (if it doesn't already exist). As a rule, since `mbed_settings.py` contains local settings (possibly relevant only to a single OS on a single machine), it should not be versioned. In this file:

* If you want to use the [armcc toolchain](https://developer.arm.com/products/software-development-tools/compilers/arm-compiler-5/downloads), set ``ARM_PATH`` to the *base* directory of your armcc installation (example: c:\software\armcc5.06). The recommended version of the armcc toolchain is 5.06 (5.05 will very likely work too).
* If you want to use the [GCC ARM Embedded toolchain](https://launchpad.net/gcc-arm-embedded), set ``GCC_ARM_PATH`` to the *binary* directory of your GCC ARM installation (example: c:\software\GNUToolsARMEmbedded\4.82013q4\bin). Use versions 4.8 or 4.9 of GCC ARM Embedded, but **not** version 5.0 or any version above it.

#### Compiling your program

Use `mbed compile` to compile the code:

```
$ mbed compile -t ARM -m K64F -j 0
```

The arguments to *compile* are:

* `-m <mcu>` to select a target for the compilation. At the moment, the only supported value for `mcu` is `K64F` (for the FRDM_K64F board).
* `-t <toolchain>` to select a toolchain, where `toolchain` can be either ARM (armcc compiler) or GCC_ARM (GNU ARM Embedded).
* `-j <jobs>` (optional): to use multiple threads on your machine to compile the source. Use 0 to infer the number of threads from the number of cores on your machine, or an actual number to specify the maximum number of thread.
* `-c ` (optional): will build from scratch; a clean build or rebuild.

The compiled binary (and ELF image) can be found in the `.build` subdirectory of your program.


#### Compiling static libraries

You can build a static library of your code by adding `--library` argument to `mbed compile`, for example:

```
$ cd mbed-os
$ mbed compile -t ARM -m K64F --library
```

A typical application for static libraries is when you want to build multiple applications from the same mbed-os codebase without having to recompile for every application. To achieve this:
1. Build a static library for mbed-os
2. Compile multiple applications or tests against the static library

```
$ cd mbed-os # unles you are in mbed-os already
$ mbed compile -t ARM -m K64F --library --no-archive --build=..\..\mbed-os-build
Building library mbed-os (K64F, ARM)
[...]
Completed in: (47.4)s

$ mbed compile -t ARM -m K64F --source=TESTS\integration\basic --source=..\..\mbed-os-build --build=..\..\basic-out
Building project basic (K64F, ARM)
Compile: main.cpp
Link: basic
Elf2Bin: basic
Image: ..\..\basic-out\basic.bin

$ mbed compile -t ARM -m K64F --source=TESTS\integration\threaded_blinky --source=..\..\mbed-os-build --build=..\..\threaded_blinky-out
Building project threaded_blinky (K64F, ARM)
Compile: main.cpp
Link: threaded_blinky
Elf2Bin: threaded_blinky
Image: ..\..\threaded_blinky-out\threaded_blinky.bin
```


#### Compiling tests

Use `mbed test --list` to list the tests available:

```
$ mbed test --list
Test Case:
    Name: mbed-os-core-mbed-rtos-TESTS-mbed-rtos-signals
    Path: ./mbed-os/core/mbed-rtos/TESTS/mbed-rtos/signals
Test Case:
    Name: mbed-os-core-mbed-rtos-TESTS-mbed-rtos-basic
    Path: ./mbed-os/core/mbed-rtos/TESTS/mbed-rtos/basic
Test Case:
    Name: mbed-os-TESTS-integration-basic
    Path: ./mbed-os/TESTS/integration/basic
  
...
```

Tests are compiled by adding the argument ```--tests``` in the above compile command:

```
$ mbed compile --tests -t ARM -m K64F -j 0
```

Test code exists in the following directory structure:

```
<module>
|_main.cpp          # Optional main.cpp with ```main()``` if it is an application module.
|_pqr.lib           # Required libs
|_xyz.lib
\_mbed-os
  |_frameworks        # Test dependencies
  |  \_greentea-client # Greentea client required by tests.
  |...
\_TESTS             # Tests directory. Special name upper case TESTS is excluded during application build process
  |_TestGroup1      # Test Group directory
  | \_TestCase1     # Test case source directory
  |   \_main.cpp    # Test source
  |_TestGroup2
  | \_TestCase2
  |   \_main.cpp
  \_host_tests      # Python host tests script directory
    |_host_test1.py
    \_host_test2.py
\_.build             # Build directory
  |_<TARGET>        # Target directory
  | \_<TOOLCHAIN>   # Toolchain directory
  |   |_TestCase1.bin    # Test binary
  |   \_TestCase2.bin

```

As shown above, tests exist inside ```TESTS\testgroup\testcase\``` directories. Please note that `TESTS` is a special upper case directory that is excluded from module sources while compiling. Any testing libraries can be put inside the ```frameworks``` directory. This is currently just a good convention, but in the future tests might be able to limit which libraries should and should not be included when compiling them.

Compiled test binaries are created in ```.build/<TARGET>/<TOOLCHAIN>/TestCase1.bin```

<span class="notes">**Note:** This feature does not work in application modules that contain ```main()```. This issue is being worked on in parallel. However, currently we don't have any module with ```main()``` and ```TESTS``` together. Hence it does not break any existing module.</span>

#### Automating toolchain and target selection

Using ``mbed target <target>`` and ``mbed toolchain <toolchain>`` you can set the default target and toolchain for your program, meaning you won't have to specify these every time you compile or generate IDE project files.

#### Customizing the build

*mbed-cli* uses the mbed Classic build system, which contains a few mechanisms that you can use to customize the way you build your code:

___Macros___

To add new macro definitions, create a file named `MACROS.txt` in the top level directory of your program and list your macros there, line by line. 

An example of `MACROS.txt` (taken from the `mbed-Client-Morpheus-from-source` above):

```
YOTTA_CFG
YOTTA_CONFIG
TARGET_LIKE_MBED
TARGET_LIKE_CORTEX_M4
```

Alternatively, you can specify macros in your command line using the -D switch. For example:

``$ mbed compile -t GCC_ARM -m K64F -c -DUVISOR_PRESENT``

___Compiling in debug mode___

To compile in debug mode (as opposed to the default *release* mode) use `-o debug-info` in the compiler command line:

```
$ mbed compile -t GCC_ARM -m K64F -j 0 -o debug-info
```

<span class="tips">**Tip:** If you have files that you want to compile only in release mode, put them in a directory called `TARGET_RELEASE` at any level of your tree. If you have files that you want to compile only in debug mode, put them in a directory called `TARGET_DEBUG` at any level of your tree (then use `-o debug-info` as explained above).
</span>

### Exporting to desktop IDEs

If you need to debug your code, a good way to do that is to export your source tree to an IDE project file, so that you can use the IDE's debugging facilities. Currently *mbed-cli* supports exporting to Keil uVision, DS-5, IAR Workbench, Simplicity Studio and other IDEs.

For example, to export to uVision run:

```
$ mbed export -i uvision -m K64F
```

A ``.uvproj`` file is created in the projectfiles/uvision folder. You can open the project file with uVision.

## Known limitations

<span class="warnings">**Warning**: At this point, *mbed-cli* is alpha quality and very much in development. Breakages are fully expected. Please open issues on this repository for any problems that you find with *mbed-cli*.</span>

* *mbed-cli* does not check whether you have Mercurial or Git installed and assumes that they are available.
