# Introduction

*mbed-cli* is the name of the ARM mbed command line tool, which enables workflows with version control repositories, maintaining dependencies, code publishing, updating from remotely hosted repositories (GitHub, GitLab, mbed.org), as well as invoking ARM mbed's own build system and export functions, and other operations.

This document covers the installation and usage of *mbed-cli*.

## Table of Contents
1. [Requierements](#requierements)
1. [Installing mbed-cli](#installing-mbed-cli)
1. [Importing and creating programs](#importing-and-creating-programs)
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
	4. [Compiling binary library](#compiling-binary-library)
	4. [Compiling tests](#compiling-tests)
1. [Exporting to desktop IDEs](#exporting-to-desktop-ides)
1. [Known limitations](#known-limitations)

# Installation

<span style="background-color:#E6E6E6;border:1px solid #000;display:block; height:100%; padding:10px">**Note**: *mbed-cli* lives in [https://github.com/ARMmbed/mbed-cli](https://github.com/ARMmbed/mbed-cli). If you don't have permissions to access the above repository, e-mail [mihail.stoyanov@arm.com](mailto:mihail.stoyanov@arm.com) or [bogdan.marinescu@arm.com](mailto:bogdan.marinescu@arm.com) with your GitHub account name.</span>

## Requierements

* *mbed-cli* is a Python script, so you'll need Python installed in order to use it. *mbed-cli* was tested with [version 2.7 of Python](https://www.python.org/download/releases/2.7/).

* *mbed-cli* supports both Git and Mercurial repositories, so you'll also need to install:
    * [Mercurial](https://www.mercurial-scm.org/).
    * [Git](https://git-scm.com/).
	
<span style="background-color:#E6E6E6;border:1px solid #000;display:block; height:100%; padding:10px">**Tip:** Remember that the directories containing the executables of `hg` and `git` need to be in your system's PATH.</span>


## Installing mbed-cli

1. To get the latest version of *mbed-cli*, clone the repository [https://github.com/ARMmbed/mbed-cli](https://github.com/ARMmbed/mbed-cli):

``$ git clone https://github.com/ARMmbed/mbed-cli``

Once cloned you can install *mbed-cli* as a python package:

``$ sudo ./setup.py install`` on Linux/Mac or ``> setup.py install`` on Windows

To uninstall *mbed-cli* you can use:

``pip uninstall mbed-cli``


# Using mbed-cli

## Importing and creating programs


### Importing an existing program

Use `mbed import` to clone an existing program and all its dependencies to your machine:

```
$ mbed import https://developer.mbed.org/teams/Morpheus/code/mbed-Client-Morpheus-from-source/
$ cd mbed-Client-Morpheus-from-source
```

<span style="background-color:#E6E6E6;border:1px solid #000;display:block; height:100%; padding:10px">**Note**: some of the repositories that *mbed-cli* will clone might require special access (Mercurial will ask you for your credentials if that's the case). If you don't have access, e-mail [mihail.stoyanov@arm.com](mailto:mihail.stoyanov@arm.com) or [bogdan.marinescu@arm.com](mailto:bogdan.marinescu@arm.com) with your developer.mbed.org account name.</span>


### Creating a new program

If you want to create a new program rather than importing an existing one, *mbed-cli* will automatically import the [mbed-os library] for you (https://github.com/ARMmbed/mbed-os/). This library represents a **release** of mbed OS and will pull in all the components of the OS, including its build system and desktop IDE project generators. In the future, when we introduce mbed OS **releases**, you'll get the guarantee that all the components in *mbed-os* passed integration tests, so that you know they work properly together. 

With this in mind, these are the steps for creating a new program (we'll call it `myprog`):

```
$ mbed new myprog  # this creates new folder "myprog", initializes new repository and also imports the latest revision of mbed-os dependency to your program tree.
$ cd myprog
<add your source files>
```

<span style="background-color:#E6E6E6;border:1px solid #000;display:block; height:100%; padding:10px">**Note**: At the moment, if you want to start from an existing folder in your workspace, you can simply use `mbed new .`, which will initialize a new Git or Mercurial repository in that folder. While this might seem like a limitation, it helps start versioning all files in a program and also help *mbed-cli* find mbed-os and tooling. You can always drop the version control by removing the .git or .hg source management folders.</span>

## Adding and removing libraries

### Adding a library

___The add command___

While working on your code, you might need to add another library (dependency) to your application. Use `mbed add` to do that:

```
$ mbed add https://developer.mbed.org/users/wim/code/TextLCD/
```

To add a library at a specific revision you can use the full URL#hash:

``
$ mbed add https://developer.mbed.org/users/wim/code/TextLCD/#e5a0dcb43ecc
``

___Specifying a directory___

You can give an additional argument to "add" to specify the directory in which you want to add your library. If you'd rather clone the previous library in a directory called "text-lcd", do this:

```
$ mbed add https://developer.mbed.org/users/wim/code/TextLCD/ text-lcd
```

Note that this behavior (cloning a repository in a directory with a different name than the name of the repository) is not encouraged, since it can easily lead to confusion.

<span style="background-color:#ffffe6;border:1px solid #000;display:block; height:100%; padding:10px">**Note**: Adding a new library to your Morpheus program is not the same thing as just cloning the library locally. Don't clone a library using hg or git; use `mbed add` to add the library, and it will ensure that all library (or sub-library) dependencies are populated as well</span>


### Removing a library

If at some point you decide that you don't need a library anymore, you can use `mbed remove` with the path of the library:

```
$ mbed remove TextLCD
```

<span style="background-color:#ffffe6;border:1px solid #000;display:block; height:100%; padding:10px">**Note**: Removing a library from your Morpheus program is not the same thing as just deleting its local clone. Use `mbed remove` to remove the library, don't simply remove its directory with 'rm'.</span>

<span style="background-color:#ffffe6;border:1px solid #000;display:block; height:100%; padding:10px">**Warning**: *mbed-cli* stores information about libraries and dependencies in lib_name.lib reference files. While these files are human-readable, we *strongly* advise that you don't edit these manually and let *mbed-cli* manage them instead.</span>


## Updating programs and libraries

### Synchronizing library references

Before updating you might want to synchronize any changes that you made to the directory structure by running ``mbed sync``, which will update the necessary library references and get rid of the invalid ones.


### Updating to an upstream version

To update your program to another upstream version, go to the root folder of the program and run `mbed update [branch|tag|rev]`. This will fetch the latest revisions from the remote repository, update the program to the specified branch, tag or revision (or to the latest one in the current branch if `rev` is not specified), then fetch and update recursively all the other dependencies to match the top-level dependencies in `rev`. You can apply the same mechanism for libraries and their depedencies by executing the update command in the library folder, not the root of your program.

<span style="background-color:#E6E6E6;border:1px solid #000;display:block; height:100%; padding:10px">**Note**: This command will fail if there are changes in your program or library that will be overwritten as a result of running `update`. This is by design: *mbed-cli* does not run operations that would result in overwriting local changes that are not yet committed. If you get an error, take care of your local changes (commit or use one of the switches below), then re-run `update`.</span>

### Updating to an upstream version

There are 2 major scanarios for when updating your code:
* Update to a "moving" revision, e.g. the tip of a particular or current branch; and
* Update to a "specific" revision, identified by revision hash or tag name

Each of the above have 2 variants - update with local uncommitted changes (or *dirty* update); and update without local uncommitted changes (or *clean* update).

To help understand what options to use with *mbed-cli*, please see examples below.

**Case 1: I want to update program or library to the latest version in a specific or current branch:**
* I want to preserve local changes - `mbed update [branch]`
* I want a clean update (and discard changes if any) - `mbed update [branch] --clean`

**Case 2: I want to update program or library to a specific revision or a tag:**
 * I want to preserve local changes - `mbed update <#rev|tag_name>`
 * I want clean update (discard changes) - `mbed update <#rev|tag_name> --clean`

The `--clean` option tells *mbed-cli* to update the current program or library and its dependencies, and discard all local changes. This is useful for when you modified something and you want to the original state of your source tree. 

There are 2 addition options that define how unpublished local libraries are handled:

`mbed update --ignore` - update the current program or library and its dependencies, and ignore any local unpublished libraries as if they are not present of your source tree (they won't be deleted or modified, just ignored)

`mbed update --force` - update the current program or library and its dependencies, and discard all local unpublished repositories. Use this with caution as your local unpublished repositories cannot be restored unless you have a backup copy.

You can combine the switches above for the following scenarios:

`mbed update --clean --ignore` - update the current program or library and its depedencies, but ignore any local repositories, e.g. update whatever you can from public repositories.

`mbed update --clean --force` - update the current program or library and all its depedencies, and restore my source tree to stock layout. This wipes every single change you made in the source tree that didn't belong to the original commit.

Use these with caution as your uncommitted changes cannot be restored.

## Publishing your changes

### Checking status

As you work on your code, you'll edit parts of it: either your own program code or code in some of the libraries that you depend on. You can get the status of all the repositories in your program (recursively) by running `mbed status`. If a repository has uncommitted changes, this command will display these changes.

### Pushing upstream
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


## Compiling code

### Toolchain selection

After importing a program or creating a new one, you need to tell *mbed-cli* where to find the toolchains that you want to use for compiling your source tree. *mbed-cli* gets this information from a file named `mbed_settings.py`, which is automatically created at the top of your cloned repository (if it doesn't already exist). As a rule, since `mbed_settings.py` contains local settings (possibly relevant only to a single OS on a single machine), it should not be versioned. In this file:

* If you want to use the [armcc toolchain](https://developer.arm.com/products/software-development-tools/compilers/arm-compiler-5/downloads), set ``ARM_PATH`` to the *base* directory of your armcc installation (example: c:\software\armcc5.06). The recommended version of the armcc toolchain is 5.06 (5.05 will very likely work too).
* If you want to use the [GCC ARM Embedded toolchain](https://launchpad.net/gcc-arm-embedded), set ``GCC_ARM_PATH`` to the *binary* directory of your GCC ARM installation (example: c:\software\GNUToolsARMEmbedded\4.82013q4\bin). Use versions 4.8 or 4.9 of GCC ARM Embedded, but **not** version 5.0 or any version above it.

### Compiling your program

Use `mbed compile` to compile the code:

```
$ mbed compile -t ARM -m K64F -j 0
```

The arguments to *compile* are:

* `-m <mcu>` to select a target for the compilation. At the moment, the only supported value for `mcu` is `K64F` for the FRDM_K64F board.
* `-t <toolchain>` to select a toolchain, where `toolchain` can be either ARM (armcc compiler) or GCC_ARM (GNU ARM Embedded).
* `-j <jobs>` (optional): to use multiple threads on your machine to compile the source. Use 0 to infer the number of threads from the number of cores on your machine, or an actual number to specify the maximum number of thread.
* `-c ` (optional): will build from scratch; a clean build or rebuild.

The compiled binary (and ELF image) can be found in the `.build` subdirectory of your program.

### Compiling binary library

**Work in progress**
```
$ mbed compile --library=<output_dir> -t ARM -m K64F -j 0
```
**Work in progress**


### Compiling tests

Tests are compiled by adding argument ```--tests``` in the above compile command:

```
$ mbed compile --tests -t ARM -m K64F -j 0
```

Test code exists in following directory structure

```
<module>
|_main.cpp          # Optional main.cpp with ```main()``` if it is an application module.
|_pqr.lib           # Required libs
|_xyz.lib
|_frameworks        # Test dependencies. Excluded from module sources while compilation.
  \_greentea-client # Greentea client required by tests.
\_TESTS             # Tests directory. Special name upper case TESTS is excluded just like frameworks.
  |_TestGroup1      # Test Group directory
  | \_TestCase1     # Test case source directory
  |   \_main.cpp    # Test source
  |_TestGroup2
  | \_TestCase2
  |   \_main.cpp
  \_host_tests      # Python host tests script directory
    |_host_test1.py
    \_host_test2.py
\.build             # Build directory
  |_<TARGET>        # Target directory
  | \_<TOOLCHAIN>   # Toolchain directory
  |   |_TestCase1.bin    # Test binary
  |   \_TestCase2.bin

```

As shown above tests exist inside ```TESTS\testgroup\testcase\``` directory. Please observe TESTS is a special upper case directory that is excluded from module sources while compiling. Any Test case dependency libs can be put inside the ```frameworks``` directory. ```frameworks``` is also excluded when compiling module sources and only compiled and linked to the tests. 
Compiled test binaries are created in ```.build/<TARGET>/<TOOLCHAIN>/TestCase1.bin```


Note: This feature does not work in application modules that contain ```main()```. This issue is being worked on in parallel. However, currently we don't have any module with ```main()``` and ```TESTS``` together. Hence it does not break any existing module.

### Automating toolchain and target selection

Using ``mbed target <target>`` and ``mbed toolchain <toolchain>`` you can set the default target and toolchain for your program, meaning you won't have to specify these every time you compile or generate IDE project files.

### Customizing the build

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

___Compile in debug mode___

To compile in debug mode (as opposed to the default *release* mode) use `-o debug-info` in the compiler command line, for example:

```
$ mbed compile -t GCC_ARM -m K64F -j 0 -o debug-info
```

<span style="background-color:#E6E6E6;border:1px solid #000;display:block; height:100%; padding:10px">**Tip:** If you have files that you want to compile only in release mode, put them in a directory called `TARGET_RELEASE` at any level of your tree. If you have files that you want to compile only in debug mode, put them in a directory called `TARGET_DEBUG` at any level of your tree (then use `-o debug-info` as explained above).
</span>

## Exporting to desktop IDEs

If you need to debug your code, a good way to do that is to export your source tree to an IDE project file, so that you can use the IDE's debugging facilities. Currently *mbed-cli* supports exporting to Keil uVision, DS-5, IAR Workbench, Simplicity Studio and other IDEs.

To export, run this command:

```
$ mbed export -i uvision -m K64F
```

After running this command, a ``.uvproj`` file is created at the top of your source tree. You can open that with uVision.

# Known limitations

<span style="background-color:#ffffe6;border:1px solid #000;display:block; height:100%; padding:10px">**Warning**: At this point, *mbed-cli* is alpha quality and very much in development. Breakages are fully expected. Please open issues on this repository for any problems that you find with *mbed-cli*.</span>

1. *mbed-cli* does not check whether you have Mercurial or Git installed and assumes that they are available.