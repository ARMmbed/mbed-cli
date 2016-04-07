# Introduction

*neo* is the name of the Morpheus command line tool.
It enables workflows with Morpheus repositories and maintaining dependencies, code publishing and updating from remotely hosted repositories (GitHub, GitLab, mbed.org), also invoking Morpheus own build system and exports, and other operations.
The rest of this document details the installation and usage of *neo*.

# Known limitations

**NOTE**: at this point, *neo* is alpha quality and very much in development. Breakages are fully expected. Please open issues on this repository for any problems that you find with *neo*.

1. *neo* assumes that you always work with remotely hosted repositories. If you depend on a library in a repository that exists only on your local machine (as opposed to a host like github of developer.mbed.org), various *neo* commands might not work as expected. If you want to depend on a new library, create it locally, push it to a remote host, then depend on the remote URL of the library, not the local one. *Note that this limitation will be resolved soon*
2. *neo* does not check whether you have Mercurial or Git installed and assumes that they are available.


# Installation

Currently, *neo* lives in https://github.com/ARMmbed/neo.

**NOTE**: if you don't have permissions to access the above repository, e-mail mihail.stoyanov@arm.com or bogdan.marinescu@arm.com with your github account name.

*neo* is a Python script, so you'll need Python installed in order to use it. *neo* was tested with version 2.7 and 3.3 of Python.

To get the latest version of *neo*, clone the above repository.

```
$ git clone https://github.com/ARMmbed/neo
```

To complete the installation of the `neo.py` script, make sure that the folder with `neo.py` (`neo` in this case) is in your PATH.

*neo* supports both Git and Mercurial repositories, so you'll also need to install mercurial and git. Use whatever installers you like, but remember that the directories containing the executables of `hg` and `git` need to be in your PATH.

# Using neo

## Importing and creating programs

Use `neo.py import` to clone an existing program and all its dependencies to your machine:

```
$ neo.py import https://developer.mbed.org/teams/Morpheus/code/mbed-Client-Morpheus-from-source/
$ cd mbed-Client-Morpheus-from-source
```

**NOTE**: some of the repositories that *neo* will clone might require special access (Mercurial will ask you for your credentials if that's the case). If you don't have access, e-mail mihail.stoyanov@arm.com or bogdan.marinescu@arm.com with your developer.mbed.org account name.

If you want to create a new program rather than importing an existing one, we recommend that you depend on the [mbed-os library] (https://developer.mbed.org/teams/Morpheus/code/mbed-os/). This library represents a **release** of mbed OS and will pull in all the components of the OS, including its build system and desktop IDE project generators. In the future, when we'll introduce mbed OS **releases**, you'll get the guarantee that all the components in *mbed-os* passed integration tests, so you know that they work together properly. With this in mind, these are the steps for creating a new program (we'll call it `myprog`):

```
$ mkdir myprog
$ cd myprog
$ "git init" or "hg init"
<add your source files>
$ neo.py import https://developer.mbed.org/teams/Morpheus/code/mbed-os/ # this adds the latest revision of mbed-os dependency to your project tree
```

`add` above works a lot like `clone`, except adds explicit dependency to the program that already exists on your local machine.

**NOTE**: at the moment, you have to initialize a new git or mercurial repository in your newly created program (third command in the code block above) for *neo* to work properly. This limitation will likely go away in a future version.

You can get a list of all the dependencies of your program by running `neo.py ls`.

## Compiling and exporting

After importing a program or creating a new one, you need to tell *neo* where to find the toolchains that you want to use for compiling your source tree. *neo* gets this information from a file named `mbed_settings.py`, which is automatically created at the top of your cloned repository (if it doesn't already exist). As a rule, since `mbed_settings.py` contains local settings (possible relevant only to a single OS on a single machine), it should not be versioned. In this file:

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
-   `-c` (optional): will build from scratch, e.g. a clean build or rebuild.

The compiled binary (and ELF image) can be found in the `.build` subdirectory of your project.

If you need to debug your code, a good way to do that is to export your source tree to an IDE project file, so that you can use the IDE's debugging facilities. Currently *neo* supports exporting to Keil uVision. To export, run this command:

```
$ neo.py export -i uvision -m K64F
```

After running this command, a .uvproj file will be created at the top of your source tree, you can open that with uVision.

Using `neo.py target <target>` and `neo.py toolchain <toolchain>` you can set default target and toolchain for your program, meaning that you don't have to specify these every time you compile or generate IDE project files.

### Customizing the build

*neo* uses the mbed Classic build system, which contains a few mechanisms that you can use to customize the way you build your code:

- To add new macro definitions, create a file named `MACROS.txt` in the top level directory of your project and list your macros there, line by line. An example of `MACROS.txt` (taken from the `mbed-Client-Morpheus-from-source` above):

```
YOTTA_CFG
YOTTA_CONFIG
TARGET_LIKE_MBED
TARGET_LIKE_CORTEX_M4
```

- Alternatively you can specify macros on command-line using the -D switch. For example:

```
$ neo.py compile -t GCC_ARM -m K64F -c -DUVISOR_PRESENT
```

- To compile in debug mode (as opposed to the default release mode) use `-o debug-info` in the compiler command line, for example:

```
$ neo.py compile -t GCC_ARM -m K64F -j 0 -o debug-info
```

- If you have files that you want to compile only in release mode, put them in a directory called `TARGET_RELEASE` at any level of your tree. If you have files that you want to compile only in debug mode, put them in a directory called `TARGET_DEBUG` at any level of your tree (then use `-o debug-info` as explained above).

## Adding and removing libraries

While working on your code, you might need to add another library (dependency) to your application. Use `neo.py add` to do that:

```
$ neo.py add https://developer.mbed.org/components/HD44780-Text-LCD/
```

You can give an additional argument to "add" to specify the directory in which you want to add your library. If you'd rather clone the previous library in a directory called "text-lcd", do this:

```
$ neo.py add https://developer.mbed.org/components/HD44780-Text-LCD text-lcd
```

Note that this behaviour (cloning a repository in a directory with a different name than the name of the repository) is not encouraged, since it can easily lead to confusion.

**IMPORTANT**: adding a new library to your Morpheus project is not the same thing as just cloning the library locally. Use `neo.py add` to add the library, don't clone it direcly using hg or git. *neo* will ensure that all library dependencies (or sub-libraries) will be populated as well.

If at some point you decide that you don't need a library anymore, you can use `neo.py remove` with the path of the library to get rid of it:

```
$ neo.py remove HD44780-Text-LCD
```

**IMPORTANT**: removing a library from your Morpheus project is not the same thing as just deleting its local clone. Use `neo.py remove` to remove the library, don't simply remove its directory with 'rm'.

## Synchronizing your tree (WIP)

As you work on your code, you'll edit parts of it: either your program code or code in some of the libraries that your depend on. You can get the status of all the repositories in your project (recursively) by running `neo.py status`. If a repository has uncommitted changes, this command will display these changes.

To synchronize changes that you made to the folders structure you can run `neo.py sync`, which will update the necessary library references and get rid of the invalid ones.

To update your program to another upstream version, go to the root of the program and run `neo.py update [rev]`. It will update the program to the specified revision (or to the latest one if `rev` is not specified), then it will update recursively all the other dependencies to match the top-level dependencies in `rev`. **NOTE**: this command will fail if there are changes in your local repository that will be overwritten as a result of running `update`. This is by design: *neo* will not run operations that would result in overwriting local changes that are not yet committed. If you get an error, take care of your local changes (commit or abandon them manually), then re-run `update`.

To push the changes in your local tree upstream version, run `neo.py publish`. `publish` works recursively, pushing the leaf dependencies first, then updating the dependants and pushing them too. This is best explained by an example. Let's assume that the list of dependencies of your program (obtained by running `neo.py ls`) looks like this:

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
