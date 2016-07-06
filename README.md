# Introduction

*mbed CLI* is the name of the ARM mbed command line tool, packaged as mbed-cli, which enables the full mbed workflow: repositories version control, maintaining dependencies, publishing code, updating from remotely hosted repositories (GitHub, GitLab and mbed.org), and invoking ARM mbed's own build system and export functions, among other operations.

This document covers the installation and usage of *mbed CLI*.

## Table of Contents
1. [Requirements](#requirements)
1. [Installing and uninstalling](#installing-mbed-cli)
1. [Working context and command help](#working-context)
1. [Creating and importing programs](#creating-and-importing-programs)
  1. [Creating a new program](#creating-a-new-program)
	2. [Importing an existing program](#importing-an-existing-program)
1. [Adding and removing libraries](#adding-and-removing-libraries)
	1. [Adding a library](#adding-a-library)
	2. [Removing a library](#removing-a-library)
1. [Updating programs and libraries](#updating-programs-and-libraries)
	1. [Synchronizing library references](#synchronizing-library-references)
	2. [Update scenarios](#update-scenarios)
	3. [Updating to an upstream version](#updating-to-an-upstream-version)
1. [Publishing your changes](#publishing-your-changes)
	1. [Checking status](#checking-status)
	2. [Pushing upstream](#pushing-upstream)
1. [Compiling code](#compiling-code)
	1. [Toolchain selection](#toolchain-selection)
	2. [Compiling your program](#compiling-your-program)
	3. [Compiling static libraries](#compiling-static-libraries)
  4. [Compile configuration system](#compile-configuration-system)
  5. [Compile-time customizations](#compile-time-customizations)
  6. [Automating toolchain and target selection](#automating-toolchain-and-target-selection)
1. [Exporting to desktop IDEs](#exporting-to-desktop-ides)
1. [Testing](#testing)
  1. [Finding available tests](#finding-available-tests)
  2. [Change the test action](#change-the-test-action)
  3. [Limiting the test scope](#limiting-the-test-scope)
  4. [Test directory structure](#test-directory-structure)
1. [mbed CLI configuration](#mbed-cli-configuration)
1. [Known limitations](#known-limitations)

## Installation

*mbed CLI* is supported on Windows, Linux and Mac OSX. We're keen to learn about your experience with *mbed CLI* on other operating systems at the [mbed CLI development page](https://github.com/ARMmbed/mbed-cli).

### Requirements

* **Python** - mbed CLI* is a Python script, so you'll need Python installed in order to use it. *mbed CLI* was tested with [version 2.7 of Python](https://www.python.org/download/releases/2.7/).

* **Git and Mercurial** - mbed CLI* supports both Git and Mercurial repositories, so you'll need to install both:
    * [Git](https://git-scm.com/).
    * [Mercurial](https://www.mercurial-scm.org/).

    <span class="tips">**Note:** The directories of Git and Mercurial executables (`git` and `hg`) need to be in your system's PATH.</span>

* **Command-line compiler or IDE Toolchain** - *mbed CLI* invokes the [mbed OS 5.0](https://github.com/ARMmbed/mbed-os) tools for various features - compiling, testing, exporting to industry standard toolchains. To compile your code, you would need either of these:
    * Compilers: GCC ARM, ARMCC 5, IAR
    * Toolchains: Keil uVision, DS-5, IAR Workbench

### Installing mbed CLI

You can get the latest stable version of *mbed CLI* via PyPI by running:

```
$ pip install mbed-cli
```

On Linux/Mac, you may need to run with `sudo`.

Alternatively you get the development version of *mbed CLI* by cloning the development repository [https://github.com/ARMmbed/mbed-cli](https://github.com/ARMmbed/mbed-cli):

  `$ git clone https://github.com/ARMmbed/mbed-cli`

  Once cloned you can install *mbed CLI* as a python package:

  `$ python setup.py install` (on Linux/Mac, you may need to run with `sudo` as well)

<span class="tips">**Note:** *mbed CLI* is compatible with [Virtual Python Environment (virtualenv)](https://pypi.python.org/pypi/virtualenv). You can read more about isolated Python virtual environments [here](http://docs.python-guide.org/en/latest/).</span>

### Uninstalling mbed CLI

To uninstall *mbed CLI*, simply run:

```
pip uninstall mbed-cli
```

## Using mbed CLI

### Working context 

*mbed CLI* uses the current directory as a working context, in a similar way to Git, Mercurial and many other command-line tools. This means that before calling any *mbed CLI* command, you should first change to a working directory of choice. For example:
```
$ cd mbed-example-program
$ cd mbed-os
$ mbed update master   # This will update "mbed-os", not "my-program"
```

Various *mbed CLI* features require a program root, which whenever possible should be under version control - either [Git](https://git-scm.com/) or [Mercurial](https://www.mercurial-scm.org/). This makes it possible to seamlessly switch between revisions of the whole program and its libraries, control the program history, synchronize the program with remote repositories, share it with others, etc. Version control is also the primary and preferred delivery mechanism for mbed OS source code, which allows everyone to contribute to mbed OS!

<span class="warnings">**Warning**: *mbed CLI* stores information about libraries and dependencies in reference files that use the `.lib` extension (e.g. `lib_name.lib`). While these files are human-readable, we *strongly* advise that you don't edit these manually and let *mbed CLI* manage them instead.</span>

### mbed CLI help

To list all *mbed CLI* commands use `mbed --help`. A detailed command-specific help is available via `mbed <command> --help`. 

### Creating and importing programs

*mbed CLI* can create and import both mbed 2.0 and mbed OS 5.0 based programs.

#### Creating a new program

When you create a new program, *mbed CLI* automatically imports the latest [mbed OS release](https://github.com/ARMmbed/mbed-os/). This represents a **release** of mbed OS and will pull in all the components, including its build tools and desktop IDE project generators. 

With this in mind, these are the steps for creating a new program (we'll call it `mbed-os-program`):

```
$ mbed new mbed-os-program
```

This creates a new folder "mbed-os-program", initializes a new repository and imports the latest revision of the mbed-os dependency to your program tree.

Use `mbed ls` to list all imported libraries to your program.

```
$ cd mbed-os-program
$ mbed ls -a
mbed-os-program (mbed-os-program#189949915b9c)
`- mbed-os (0d5eb2b8cee8)
   |- core (737a7809f9e7)
   |- features\FEATURE_CLIENT\coap-service (7a11be1ccb07)
   |- features\FEATURE_CLIENT\mbed-client (a6a46726f027)
   |- features\FEATURE_CLIENT\mbed-client-c (086b9c97f65b)
   |- features\FEATURE_CLIENT\mbed-client-classic (c8ccada6b9ff)
   |- features\FEATURE_CLIENT\mbed-client-mbed-tls (b14e7b3303c8)
   |- features\FEATURE_CLIENT\mbed-client-randlib (80f5c491dd4d)
   |- features\FEATURE_IPV6\mbed-mesh-api (0e92921f3dce)
   |- features\FEATURE_IPV6\mbed-trace (e419c488f4f8)
   |- features\FEATURE_IPV6\nanostack-hal-mbed-cmsis-rtos (36968fc133c7)
   |- features\FEATURE_IPV6\nanostack-libservice (f61c845e0c59)
   |- features\FEATURE_IPV6\sal-stack-nanostack-eventloop (c163be9183b0)
   |- features\FEATURE_IPV6\sal-stack-nanostack-private (5d3365ce7df3)
   |- frameworks\greentea-client (d0cbb41ae793)
   `- frameworks\unity (14fd303f30f9)
```

<span class="notes">**Note**: If you want to start from an existing folder in your workspace, you can simply use `mbed new .`, which will initialize an mbed program and also initialize a new Git or Mercurial repository in that folder. You can control which source control management is used or prevent source control management initialization via `--scm [name|none]` option.</span>

*mbed CLI* is also compatible with mbed 2.0 programs based on the [mbed library](https://mbed.org/users/mbed_official/code/mbed/) and will automatically import the latest [mbed library release](https://mbed.org/users/mbed_official/code/mbed/) if `--mbedlib` option is specified e.g.
```
$ mbed new mbed-classic-program --mbedlib
```

You can create plain (empty) programs, without either mbed OS 5.0 or mbed 2.0  by adding the `--create-only` option.


#### Importing an existing program

Use `mbed import` to clone an existing program and all its dependencies to your machine:

```
$ mbed import https://github.com/ARMmbed/mbed-blinky/
$ cd mbed-blinky
```

*mbed CLI* also supports programs based on the mbed 2.0, which are automatically detected and do not require additional options.

```
$ mbed import https://developer.mbed.org/teams/mbed/code/mbed_blinky/
$ cd mbed_blinky
```


#### Importing from git/hg clone

If you have manually cloned a git repository into your workspace and you want to add all missing libraries, then you can use the `deploy` command:

```
$ mbed deploy
[mbed] Creating new program "test-prog" (git)
[mbed] Adding library "mbed-os" from "https://github.com/ARMmbed/mbed-os/" at latest revision in the current branch
[mbed] Adding library "mbed-os/core" from "https://github.com/mbedmicro/mbed/" at rev #b4bb088876cb72bda7006e423423aba4895d380c
...
```

Don't forget to set the current directory as a root of your program:

```
$ mbed new .
```


### Adding and removing libraries

While working on your code, you might need to add another library (dependency) to your application, or remove existing libraries.

#### Adding a library

Use `mbed add` to add the latest revision of a library:

```
$ mbed add https://developer.mbed.org/users/wim/code/TextLCD/
```

Use the URL#hash format to add a library at a specific revision:

```
$ mbed add https://developer.mbed.org/users/wim/code/TextLCD/#e5a0dcb43ecc
```

___Specifying a destination directory___

You can give an additional argument to `add` to specify the directory in which you want to add your library. For example, If you'd rather add the previous library in a directory called "text-lcd" (instead of TextLCD):

```
$ mbed add https://developer.mbed.org/users/wim/code/TextLCD/ text-lcd
```

Note that add a library with a different name than the name of the repository is not encouraged, since it can easily lead to confusion.

<span class="notes">**Note**: Adding a new library to your program is not the same as just cloning the repository. Don't clone a library using `hg` or `git`; use `mbed add` to add the library as it will ensure that all dependencies - libraries or sub-libraries - are populated as well</span>


#### Removing a library

If at any point you decide that you don't need a library anymore, you can use `mbed remove` with the path of the library:

```
$ mbed remove text-lcd
```

<span class="notes">**Note**: Removing a library from your program is not the same as deleting the library directory - there are library reference files that would need updating or cleaning. Use `mbed remove` to remove the library, don't simply remove its directory with 'rm'.</span>


### Updating programs and libraries

#### Synchronizing library references

Before triggering an update you might want to synchronize any changes that you've made to the program structure by running ``mbed sync``, which will update the necessary library references and get rid of the invalid ones.

#### Update scenarios

There are two main scenarios when updating:
* Update to a *moving* revision, e.g. the tip of a branch
* Update to a *specific* revision that is identified by revision hash or tag name

Each scenario has two cases:
* Update with local uncommitted changes - *dirty* update
* Update without local uncommitted changes - *clean* update

#### Updating to an upstream version

To update your program to another upstream version, go to the root folder of the program and run:

```
$ mbed update [branch|tag|revison]
```

This fetches new revisions from the remote repository, updates the program to the specified branch, tag or revision. If none of these is specified then it updates the latest revision in the current branch. These series of actions are performed recursively against all dependencies and sub-dependencies in the program tree.

You can change the working directory to a library folder and use `mbed update` to update that library and its dependencies to a different revision than the one referenced in the parent program or library. This allows you to experiment with different versions of libraries/dependencies in the program tree without having to change the parent program or library.

<span style="background-color:#E6E6E6;border:1px solid #000;display:block; height:100%; padding:10px">**Note**: This command will fail if there are changes in your program or library that will be overwritten as a result of running `update`. This is by design: *mbed CLI* does not run operations that would result in overwriting local changes that are not yet committed. If you get an error, take care of your local changes (commit or use one of the options below), then re-run `update`.</span>

#### Update options

<span style="background-color:#E6E6E6;border:1px solid #000;display:block; height:100%; padding:10px">**Note**: As with any *mbed CLI* command, `mbed update` uses the current directory as a working context, meaning that before calling `mbed update` you should first change your working directory to the one you want to update, e.g. `cd mbed-os`.</span>

#### Update examples

To help understand what options you can use with *mbed CLI*, check the examples below.

**Case 1: I want to update a program or a library to the latest version in a specific or current branch**

__I want to preserve my uncommitted changes__ 

Run `mbed update [branch]`. You might have to commit or stash your changes if the source control tool (Git or Mercurial) throws an error that the update will overwrite local changes.

__I want a clean update (and discard uncommitted changes)__

Run `mbed update [branch] --clean`

Specifying a branch to `mbed update` would only checkout that branch and won't automatically merge/fast-forward to the remote/upstream branch. You can run `mbed update` to merge (fast-forward) your local branch with the latest remote branch. On git you can do `git pull`

<span style="background-color:#E6E6E6;border:1px solid #000;display:block; height:100%; padding:10px">**Note**: The `--clean` option tells *mbed CLI* to update that program or library and its dependencies, and discard all local changes. WARNING: This action cannot be undone. Use with caution.</span>

**Case 2: I want to update a program or a library to a specific revision or a tag**
 
__I want to preserve my uncommitted changes__ 

Run `mbed update <tag_name|revision>`. You might have to commit or stash your changes if they conflict with the latest revision.

__I want a clean update (discard changes)__

Run `mbed update <tag_name|revision> --clean`


__When you have unpublished local libraries__

There are 3 additional options that define how unpublished local libraries are handled:

`mbed update --clean-deps` - update the current program or library and its dependencies, and discard all local unpublished repositories. Use this with caution as your local unpublished repositories cannot be restored unless you have a backup copy.

`mbed update --clean-files` - update the current program or library and its dependencies, discard local uncommitted changes and remove any untracked or ignored files. Use this with caution as your local unpublished repositories cannot be restored unless you have a backup copy.

`mbed update --ignore` - update the current program or library and its dependencies, and ignore any local unpublished libraries (they won't be deleted or modified, just ignored).

__Combining update options__

You can combine the options above for the following scenarios:

`mbed update --clean --clean-deps --clean-files` - update the current program or library and its dependencies, remove all local unpublished libraries, discard local uncommitted changes, and remove all untracked or ignored files. This wipes every single change that you made in the source tree and restores the stock layout.

`mbed update --clean --ignore` - update the current program or library and its dependencies, but ignore any local repositories. mbed CLI will update whatever it can from the public repositories.

Use these with caution as your uncommitted changes and unpublished libraries cannot be restored.


### Publishing your changes

#### Checking status

As you develop your program, you'll edit parts of it - either your own code or code in some of the libraries that it depends on. You can get the status of all the repositories in your program (recursively) by running `mbed status`. If a repository has uncommitted changes, this command will display these changes. Example:

```
[mbed] Status for "mbed-os-program":
 M main.cpp
 M mbed-os.lib
?? gdb_log.txt
?? test_spec.json

[mbed] Status for "mbed-os":
 M tools/toolchains/arm.py
 M tools/toolchains/gcc.py

[mbed] Status for "mbed-client-classic":
 M source/m2mtimerpimpl.cpp

[mbed] Status for "mbed-mesh-api":
 M source/include/static_config.h
```

#### Pushing upstream

To push the changes in your local tree upstream, run `mbed publish`. `publish` works recursively, pushing the leaf dependencies first, then updating the dependents and pushing them too. 

This is best explained by an example. Let's assume that the list of dependencies of your program (obtained by running `mbed ls`) looks like this:

```
mbed-os-program (189949915b9c)
`- mbed-os (e39199afa2da)
   |- frameworks/greentea-client (571cfef17dd0)
   |- frameworks/unity (7483099b9df1)
   |- core (d1ec4beabef3)
   |- mbedtls (bef26f687287)
   |- net/coap-service (eae41d1df943)
   |- net/mbed-client (5dc62d168aa4)
   |- net/mbed-client-c (ce64d6a0bdef)
   |- net/mbed-client-classic (abda3cef87f0)
   |- net/mbed-client-mbed-tls (8c436e5d1109)
   |- net/mbed-client-randlib (80f5c491dd4d)
   |- net/mbed-mesh-api (8187d3d275cc)
   |- net/mbed-trace (07ce2714915d)
   |- net/nanostack-hal-mbed-cmsis-rtos (023fd8906ce7)
   |- net/nanostack-libservice (f61c845e0c59)
   |- net/sal-stack-nanostack-eventloop (c163be9183b0)
   `- net/sal-stack-nanostack (cd18b5a50df4)
```

Furthermore, let's assume that you make changes to `mbed-mesh-api`. `publish` detects the change on the leaf `mbed-mesh-api` dependency and asks you to commit it. Then it detects that `mbed-os` depends on `mbed-mesh-api`, updates mbed-os' dependency on `mbed-mesh-api` to its latest version (by updating the `mbed-mesh-api.lib` file inside `mbed-os/net/`) and asks you to commit it. This propagates up to `mbed-os` and finally to your program `mbed-os-program`.

#### Forking workflow

Git enables asymmetric workflow where the publish/push repository might be different than the original ("origin") one. This allows new revisions to land in a fork repository, while maintaining association with the original repository.

To achieve this, first import an mbed OS program or mbed OS itself and then associate the push remote with your fork, e.g:

```
$ git remote set-url --push origin https://github.com/screamerbg/repo-fork
```

Each time you `git` commit+push or use `mbed publish`, the new revisions will be pushed against you fork. You can fetch from the original repository using `mbed update` or `git pull`. If you explicitly want to fetch/pull from your fork, then you can use `git pull https://github.com/screamerbg/repo-fork [branch]`

Through the workflow explained above, mbed CLI will maintain association to the original ("origin") repository to which you might want to send pull request to), and will record references with the revision hashes that you push to your fork. Until your pull request is accepted, all recorded references will be invalid, but once the PR is accepted all revision hashes from your fork will become part the original repository, thus all references will become valid.


### Compiling code

#### Toolchain selection

After importing a program or creating a new one, you need to tell *mbed CLI* where to find the toolchains that you want to use for compiling your source tree. *mbed CLI* gets this information from a file named `mbed_settings.py`, which is automatically created at the top of your cloned repository (if it doesn't already exist). As a rule, since `mbed_settings.py` contains local settings (possibly relevant only to a single OS on a single machine), it should not be versioned. In this file:

* If you want to use the [ARM Compiler toolchain](https://developer.arm.com/products/software-development-tools/compilers/arm-compiler-5/downloads), set `ARM_PATH` to the *base* directory of your ARM Compiler installation (example: c:\software\armcc5.06). The recommended version of the ARM Compiler toolchain is 5.06.
* If you want to use the [GCC ARM Embedded toolchain](https://launchpad.net/gcc-arm-embedded), set `GCC_ARM_PATH` to the *binary* directory of your GCC ARM installation (example: c:\software\GNUToolsARMEmbedded\4.82013q4\bin). Use versions 4.8 or 4.9 of GCC ARM Embedded, but version 5.0 or any version above might be incompatible with the tools.

#### Compiling your program

Use the `mbed compile` command to compile your code:

```
$ mbed compile -t ARM -m K64F
Building project mbed-os-program (K64F, GCC_ARM)
Compile: aesni.c
Compile: blowfish.c
Compile: main.cpp
... [SNIP] ...
Compile: configuration_store.c
Link: mbed-os-program
Elf2Bin: mbed-os-program
+----------------------------+-------+-------+------+
| Module                     | .text | .data | .bss |
+----------------------------+-------+-------+------+
| Fill                       |   170 |     0 | 2294 |
| Misc                       | 36282 |  2220 | 2152 |
| core/hal                   | 15396 |    16 |  568 |
| core/rtos                  |  6751 |    24 | 2662 |
| features/FEATURE_IPV4      |    96 |     0 |   48 |
| frameworks/greentea-client |   912 |    28 |   44 |
| frameworks/utest           |  3079 |     0 |  732 |
| Subtotals                  | 62686 |  2288 | 8500 |
+----------------------------+-------+-------+------+
Allocated Heap: 65540 bytes
Allocated Stack: 32768 bytes
Total Static RAM memory (data + bss): 10788 bytes
Total RAM memory (data + bss + heap + stack): 109096 bytes
Total Flash memory (text + data + misc): 66014 bytes
Image: .build/K64F/GCC_ARM/mbed-os-program.bin
```

The arguments to *compile* are:

* `-m <MCU>` to select a target
* `-t <TOOLCHAIN>` to select a toolchain, where `toolchain` can be either `ARM` (armcc compiler), `GCC_ARM` (GNU ARM Embedded), or `IAR` (IAR Embedded Workbench for ARM)
* `--source <SOURCE>` to select the source directory. Default is `.` (the current dir). You can specify multiple source locations, even outside the program tree
* `--build <BUILD>` to select the build directory. Default: `.build/` inside your program
* `--library` to compile the code as a [static .a/.ar library](#compiling-static-libraries)
* `--config` to inspect the run-time compile configuration (see below)
* `-S` or `--supported` shows supported matrix of targets and toolchains
* `-c ` (optional): will build from scratch; a clean build or rebuild.
* `-j <jobs>` (optional): control the compile threads on your machine. Default value is 0, which infer the number of threads from the number of cores on your machine. You can use `-j 1` to trigger sequential compile of source code..
* `-v` or `--verbose` for verbose diagnostic output
* `-vv` or `--very_verbose` for very verbose diagnostic output

The compiled binary, ELF image, memory usage and link statistics can be found in the `.build` subdirectory of your program.


#### Compiling static libraries

You can build a static library of your code by adding `--library` argument to `mbed compile`, for example:

```
$ mbed compile -t ARM -m K64F --library --source=mbed-os
```

A typical application for static libraries is when you want to build multiple applications from the same mbed-os codebase without having to recompile for every application. To achieve this:
1. Build a static library for mbed-os
2. Compile multiple applications or tests against the static library

```
$ mbed compile -t ARM -m K64F --library --no-archive --source=mbed-os --build=../mbed-os-build
Building library mbed-os (K64F, ARM)
[...]
Completed in: (47.4)s

$ mbed compile -t ARM -m K64F --source=mbed-os/TESTS/integration/basic --source=../mbed-os-build --build=../basic-out
Building project basic (K64F, ARM)
Compile: main.cpp
Link: basic
Elf2Bin: basic
Image: ../basic-out/basic.bin

$ mbed compile -t ARM -m K64F --source=mbed-os/TESTS/integration/threaded_blinky --source=../mbed-os-build --build=..\/hreaded_blinky-out
Building project threaded_blinky (K64F, ARM)
Compile: main.cpp
Link: threaded_blinky
Elf2Bin: threaded_blinky
Image: ../threaded_blinky-out/threaded_blinky.bin
```

#### Compile configuration system

The [compile configuration system](https://github.com/ARMmbed/mbed-os/blob/master/docs/config_system.md) provides a flexible mechanism for configuring the mbed program, its libraries and the build target. Refer to the previous link for more details about the configuration system.

#### Inspecting configuration

If the [compile configuration system](https://github.com/ARMmbed/mbed-os/blob/master/docs/config_system.md) is used by the program, the configuration can be displayed using `mbed compile --config`:

```
$ mbed compile --config -t GCC_ARM -m K64F
```

To display more verbose information about the configuration parameters, use `-v`:

```
$ mbed compile --config -t GCC_ARM -m K64F -v
```

It's possible to filter the output of `mbed compile --config` by specifying one or more prefixes for the configuration parameters that will be displayed. For example, to display only the configuration defined by the targets:

```
$ mbed compile --config -t GCC_ARM -m K64F --prefix target
```

`--prefix` can be used more than once. To display only the configuration defined by the application and the targets, use two `--prefix` options:


```
$ mbed compile --config -t GCC_ARM -m K64F --prefix target --prefix app
```

#### Compile-time customizations

___Macros___

You can specify macros in your command line using the -D option. For example:

`$ mbed compile -t GCC_ARM -m K64F -c -DUVISOR_PRESENT`

___Compiling in debug mode___

To compile in debug mode (as opposed to the default *release* mode) use `-o debug-info` in the compile command line:

```
$ mbed compile -t GCC_ARM -m K64F -o debug-info
```

<span class="tips">**Tip:** If you have files that you want to compile only in release mode, put them in a directory called `TARGET_RELEASE` at any level of your tree. If you have files that you want to compile only in debug mode, put them in a directory called `TARGET_DEBUG` at any level of your tree (then use `-o debug-info` as explained above).
</span>

#### Automating toolchain and target selection

Using `mbed target <target>` and `mbed toolchain <toolchain>` you can set the default target and toolchain for your program, meaning you won't have to specify these every time you compile or generate IDE project files.

### Exporting to desktop IDEs

If you need to debug your code, a good way to do that is to export your source tree to an IDE project file, so that you can use the IDE's debugging facilities. Currently *mbed CLI* supports exporting to Keil uVision, DS-5, IAR Workbench, Simplicity Studio and other IDEs.

For example, to export to uVision run:

```
$ mbed export -i uvision -m K64F
```

A `.uvproj` file is created in the projectfiles/uvision folder. You can open the project file with uVision.

### Testing

Use the `mbed test` command to compile and run tests:

```
$ mbed test -m K64F -t GCC_ARM
Building library mbed-build (K64F, GCC_ARM)
Building project GCC_ARM to TESTS-unit-myclass (K64F, GCC_ARM)
Compile: main.cpp
Link: TESTS-unit-myclass
Elf2Bin: TESTS-unit-myclass
+-----------+-------+-------+------+
| Module    | .text | .data | .bss |
+-----------+-------+-------+------+
| Fill      |   74  |   0   | 2092 |
| Misc      | 47039 |  204  | 4272 |
| Subtotals | 47113 |  204  | 6364 |
+-----------+-------+-------+------+
Allocated Heap: 65540 bytes
Allocated Stack: 32768 bytes
Total Static RAM memory (data + bss): 6568 bytes
Total RAM memory (data + bss + heap + stack): 104876 bytes
Total Flash memory (text + data + misc): 48357 bytes
Image: .build\tests\K64F\GCC_ARM\TESTS\mbedmicro-rtos-mbed\mutex\TESTS-unit-myclass.bin
...[SNIP]...
mbedgt: test suite report:
+--------------+---------------+---------------------------------+--------+--------------------+-------------+
| target       | platform_name | test suite                      | result | elapsed_time (sec) | copy_method |
+--------------+---------------+---------------------------------+--------+--------------------+-------------+
| K64F-GCC_ARM | K64F          | TESTS-unit-myclass | OK     | 21.09              | shell       |
+--------------+---------------+---------------------------------+--------+--------------------+-------------+
mbedgt: test suite results: 1 OK
mbedgt: test case report:
+--------------+---------------+---------------------------------+---------------------------------+--------+--------+--------+--------------------+
| target       | platform_name | test suite         | test case           | passed | failed | result | elapsed_time (sec) |
+--------------+---------------+---------------------------------+---------------------------------+--------+--------+--------+--------------------+
| K64F-GCC_ARM | K64F          | TESTS-unit-myclass | TESTS-unit-myclass1 | 1      | 0      | OK     | 5.00               |
| K64F-GCC_ARM | K64F          | TESTS-unit-myclass | TESTS-unit-myclass2 | 1      | 0      | OK     | 5.00               |
| K64F-GCC_ARM | K64F          | TESTS-unit-myclass | TESTS-unit-myclass3 | 1      | 0      | OK     | 5.00               |
+--------------+---------------+---------------------------------+---------------------------------+--------+--------+--------+--------------------+
mbedgt: test case results: 3 OK
mbedgt: completed in 21.28 sec
```

The arguments to `test` are:

* `-m <MCU>` to select a target for the compilation.
* `-t <TOOLCHAIN>` to select a toolchain, where `toolchain` can be either `ARM` (armcc compiler), `GCC_ARM` (GNU ARM Embedded), or `IAR` (IAR Embedded Workbench for ARM)
* `--compile-list` to list all the tests that can be built
* `--run-list` to list all the tests that can be ran (they must be built first)
* `--compile` to only compile the tests
* `--run` to only run the tests
* `-n <TESTS_BY_NAME>` to limit the tests built or ran to a comma separated list (ex. test1,test2,test3)
* `--source <SOURCE>` to select the source directory. Default is `.` (the current dir). You can specify multiple source locations, even outside the program tree.
* `--build <BUILD>` to select the build directory. Default: `.build/ inside your program
* `-c or --clean` to clean the build directory before compiling
* `--test-spec <TEST_SPEC>` to set the path for the test spec file used when building and running tests (the default path is the build directory)
* `-v` or `--verbose` for verbose diagnostic output
* `-vv` or `--very_verbose` for very verbose diagnostic output

The compiled binaries and test artifacts can be found in the `.build/tests/<TARGET>/<TOOLCHAIN>` directory of your program.

#### Finding available tests

You can find the tests that are available for **building** by using the `--compile-list` option:

```
$ mbed test --compile-list
Test Case:
    Name: TESTS-functional-test1
    Path: .\TESTS\functional\test1
Test Case:
    Name: TESTS-functional-test2
    Path: .\TESTS\functional\test2
Test Case:
    Name: TESTS-functional-test3
    Path: .\TESTS\functional\test3
```

You can find the tests that are available for **running** by using the `--run-list` option:

```
$ mbed test --run-list
mbedgt: test specification file '.\.build/tests\K64F\ARM\test_spec.json' (specified with --test-spec option)
mbedgt: using '.\.build/tests\K64F\ARM\test_spec.json' from current directory!
mbedgt: available tests for built 'K64F-ARM', location '.\.build/tests\K64F\ARM'
        test 'TESTS-functional-test1'
        test 'TESTS-functional-test2'
        test 'TESTS-functional-test3'
```

#### Change the test action

You can specify to only **build** the tests by using the `--compile` option:

```
$ mbed test -m K64F -t GCC_ARM --compile
```

You can specify to only **run** the tests by using the `--run` option:

```
$ mbed test -m K64F -t GCC_ARM --run
```

#### Limiting the test scope

You can limit the scope of the tests built and ran by using the `-n` option. This takes a comma separated list of test names as an argument:

```
$ mbed test -m K64F -t GCC_ARM -n TESTS-functional-test1,TESTS-functional-test2
```

#### Test directory structure

Test code exists in the following directory structure:

```
mbed-os-program
 |- main.cpp            # Optional main.cpp with main() if it is an application module.
 |- pqr.lib             # Required libs
 |- xyz.lib
 |- mbed-os
 |  |- frameworks        # Test dependencies
 |  |  `_greentea-client # Greentea client required by tests.
 |  |...
 |  `- TESTS              # Tests directory. Special name upper case TESTS is excluded during application build process
 |     |- TestGroup1      # Test Group directory
 |     |  `- TestCase1    # Test case source directory
 |     |      `- main.cpp # Test source
 |     |- TestGroup2
 |     |   `- TestCase2
 |     |      `- main.cpp
 |     `- host_tests      # Python host tests script directory
 |        |- host_test1.py
 |        `- host_test2.py
 `- .build                # Build directory
     |- <TARGET>          # Target directory
     | `- <TOOLCHAIN>     # Toolchain directory
     |   |- TestCase1.bin # Test binary
     |   `- TestCase2.bin
     | ....
```

As shown above, tests exist inside ```TESTS\testgroup\testcase\``` directories. Please note that `TESTS` is a special upper case directory that is excluded from module sources while compiling.

<span class="notes">**Note:** This feature does not work in applications that contain a  ```main``` function that is outside of a `TESTS` directory.</span>

## mbed CLI configuration

Many options in *mbed CLI* can be streamlined with global and local configuration.

The *mbed CLI* configuration syntax is:
```
mbed config [--global] <var> [value] [--unset]
```

The **global** configuration (via `--global` option) defines the default behavior of *mbed CLI* across programs unless overridden by *local* settings.

The **local** configuration (without `--global`) is per mbed program and allows overriding of global or default *mbed CLI* settings within the scope of a program or library and its dependencies.

If **no value** is specified then *mbed CLI* will print the currently set value for this settings from either local or global scope.

The `--unset` option allows removing of a setting.

Here is a list of currently implemented configuration settings:
 * `target` - Define default target for `compile`, `test` and `export`, and is an alias to `mbed target`. Default: none.
 * `toolchain` - Defines default toolchain for `compile` and `test` can be set through `mbed toolchain`. Default: none.
 * `ARM_PATH`, `GCC_ARM_PATH`, `IAR_PATH` - defines default path to ARM Compiler, GCC ARM and IAR Workbench toolchains. Default: none.
 * `protocol` - Defines the default protocol used for importing/cloning of programs and libraries. Possible values are `https`, `http` and `ssh`. Use `ssh` if you have generated and registered SSH keys (Public Key Authentication) with a service like GitHub, GitLab, Bitbucket, etc. Read more about SSH keys [here](https://help.github.com/articles/generating-an-ssh-key/) Default: `https`.
 * `depth` - Defines *clone* depth for importing/cloning and applies only to *Git* repositories. Note that while this option may improve cloning speed, it may also prevent you from correctly checking out a dependency tree when the reference revision hash is older than the clone depth. Read more about shallow clones [here](https://git-scm.com/docs/git-clone). Default: none.
 * `cache` (EXPERIMENTAL) - Defines local path that will be used to store minimalistic copies of the imported/cloned repositories and attempt to use them to minimize traffic and speed up future importing. This feature is still under development, so this should not be used within a production environment. Default: none (disabled).

## Known limitations

<span class="warnings">**Warning**: At this point, *mbed CLI* is alpha quality and very much in development. Breakages are fully expected. Please open issues on this repository for any problems that you find with *mbed CLI*.</span>

* *mbed CLI* does not check whether you have Mercurial or Git installed and assumes that they are available.
