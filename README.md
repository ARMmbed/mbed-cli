## Introduction

*mbed CLI* is the name of the ARM mbed command line tool, packaged as mbed-cli, which enables the full mbed workflow: repositories version control, maintaining dependencies, publishing code, updating from remotely hosted repositories (GitHub, GitLab and mbed.org), and invoking ARM mbed's own build system and export functions, among other operations.

This document covers the installation and usage of mbed CLI.

## Table of Contents

1. [Using mbed CLI](#using-mbed-cli)
1. [Installing and uninstalling](#installing-mbed-cli)
1. [Understanding working context and program root](#before-you-begin-understanding-the-working-context-and-program-root)
1. [Creating and importing programs](#creating-and-importing-programs)
  1. [Creating a new program](#creating-a-new-program-for-mbed-os-5)
  2. [Importing an existing program](#importing-an-existing-program)
1. [Adding and removing libraries](#adding-and-removing-libraries)
1. [Compiling code](#compiling-code)
  1. [Toolchain selection](#toolchain-selection)
  2. [Compiling your program](#compiling-your-program)
  3. [Compiling static libraries](#compiling-static-libraries)
  4. [Compile configuration system](#compile-configuration-system)
  5. [Compile-time customizations](#compile-time-customizations)
1. [Exporting to desktop IDEs](#exporting-to-desktop-ides)
1. [Testing](#testing)
  1. [Finding available tests](#finding-available-tests)
  2. [Compiling and running tests](#compiling-and-running-tests)
  3. [Limiting the test scope](#limiting-the-test-scope)
  4. [Test directory structure](#test-directory-structure)
1. [Publishing your changes](#publishing-your-changes)
  1. [Checking status](#checking-status)
  2. [Pushing upstream](#pushing-upstream)
1. [Updating programs and libraries](#updating-programs-and-libraries)
  1. [Updating to an upstream version](#updating-to-an-upstream-version)
  2. [Update examples](#update-examples)
1. [mbed CLI configuration](#mbed-cli-configuration)
1. [Troubleshooting](#troubleshooting)


## Using mbed CLI

The basic workflow for mbed CLI is to:

1. Initialize a new repository, for either a new application (or library) or an imported one. In both cases, this action also brings in the mbed OS codebase.
1. Build the application code.
1. Test your build.
1. Publish your application.

But mbed CLI goes much further than the basic workflow. To support long-term development, mbed CLI offers nuanced source control, including selective updates of libraries and the code base, support for multiple toolchains, and manual configuration of the system.

<span class="tips">**Tip:** mbed CLI help: To list all mbed CLI commands, use `mbed --help`. A detailed command-specific help is available by using `mbed <command> --help`.</span>

## Installation

mbed CLI is supported on Windows, Linux and Mac OS X. We're keen to learn about your experience with mbed CLI on other operating systems at the [mbed CLI development page](https://github.com/ARMmbed/mbed-cli).

### Requirements

* **Python** - mbed CLI is a Python script, so you'll need Python in order to use it. mbed CLI was tested with [version 2.7.9 of Python](https://www.python.org/download/releases/2.7/).

* **Git and Mercurial** - mbed CLI supports both Git and Mercurial repositories, so you'll need to install both:
    * [Git](https://git-scm.com/).
    * [Mercurial](https://www.mercurial-scm.org/).

    <span class="tips">**Note:** The directories of Git and Mercurial executables (`git` and `hg`) need to be in your system's PATH.</span>

* **Command-line compiler or IDE Toolchain** - mbed CLI invokes the [mbed OS 5](https://github.com/ARMmbed/mbed-os) tools for various features, like compiling, testing and exporting to industry standard toolchains. To compile your code, you will need either of these:
    * Compilers: GCC ARM, ARM Compiler 5, IAR
    * Toolchains: Keil uVision, DS-5, IAR Workbench


### Video tutorial for manual installation 

<span class="images">[![Video tutorial](http://img.youtube.com/vi/cM0dFoTuU14/0.jpg)](https://www.youtube.com/watch?v=cM0dFoTuU14)</span>

### Installing mbed CLI

You can get the latest stable version of mbed CLI through PyPI, by running:

```
$ pip install mbed-cli
```

On Linux or Mac, you may need to run with `sudo`.

Alternatively, you can get the development version of mbed CLI by cloning the development repository [https://github.com/ARMmbed/mbed-cli](https://github.com/ARMmbed/mbed-cli):

```
$ git clone https://github.com/ARMmbed/mbed-cli
```

Once cloned, you can install mbed CLI as a python package:

```
$ python setup.py install
```

On Linux or Mac, you may need to run with `sudo`.

<span class="tips">**Note:** mbed CLI is compatible with [Virtual Python Environment (virtualenv)](https://pypi.python.org/pypi/virtualenv). You can read more about isolated Python virtual environments [here](http://docs.python-guide.org/en/latest/).</span>

### Uninstalling mbed CLI

To uninstall mbed CLI, simply run:

```
pip uninstall mbed-cli
```

## Quicks start video

<span class="images">[![Video tutorial](http://img.youtube.com/vi/PI1Kq9RSN_Y/0.jpg)](https://www.youtube.com/watch?v=PI1Kq9RSN_Y)</span>

## Before you begin: understanding the working context and program root

mbed CLI uses the current directory as a working context, in a similar way to Git, Mercurial and many other command-line tools. This means that before calling any mbed CLI command, you must first change to the directory containing the code you want to act on. For example, if you want to update the mbed OS sources in your ``mbed-example-program`` directory:

```
$ cd mbed-example-program
$ cd mbed-os
$ mbed update master   # This will update "mbed-os", not "my-program"
```

Various mbed CLI features require a program root, which whenever possible should be under version control - either [Git](https://git-scm.com/) or [Mercurial](https://www.mercurial-scm.org/). This makes it possible to seamlessly switch between revisions of the whole program and its libraries, control the program history, synchronize the program with remote repositories, share it with others, and so on. Version control is also the primary and preferred delivery mechanism for mbed OS source code, which allows everyone to contribute to mbed OS.

<span class="warnings">**Warning**: mbed CLI stores information about libraries and dependencies in reference files that use the `.lib` extension (like `lib_name.lib`). While these files are human-readable, we *strongly* advise that you don't edit these manually - let mbed CLI manage them instead.</span>


## Creating and importing programs

mbed CLI can create and import programs based on both mbed OS 2 and mbed OS 5.

### Creating a new program for mbed OS 5

When you create a new program, mbed CLI automatically imports the latest [mbed OS release](https://github.com/ARMmbed/mbed-os/). Each release includes all the components: code, build tools and desktop IDE project generators. 

With this in mind, let's create a new program (we'll call it `mbed-os-program`):

```
$ mbed new mbed-os-program
[mbed] Creating new program "mbed-os-program" (git)
[mbed] Adding library "mbed-os" from "https://github.com/ARMmbed/mbed-os" at latest revision in the current branch
[mbed] Updating reference "mbed-os" -> "https://github.com/ARMmbed/mbed-os/#89962277c20729504d1d6c95250fbd36ea5f4a2d"
```

This creates a new folder "mbed-os-program", initializes a new repository and imports the latest revision of the mbed-os dependency to your program tree.

<span class="tips">**Tip:** You can control which source control management is used, or prevent source control management initialization, by using `--scm [name|none]` option.</span>

Use `mbed ls` to list all the libraries imported to your program:

```
$ cd mbed-os-program
$ mbed ls -a
mbed-os-program (mbed-os-program)
`- mbed-os (https://github.com/ARMmbed/mbed-os#89962277c207)
```

<span class="notes">**Note**: If you want to start from an existing folder in your workspace, you can simply use `mbed new .`, which will initialize an mbed program, as well as a new Git or Mercurial repository in that folder. </span>

### Creating a new program for mbed OS 2

mbed CLI is also compatible with mbed OS 2 programs based on the [mbed library](https://mbed.org/users/mbed_official/code/mbed/), and will automatically import the latest [mbed library release](https://mbed.org/users/mbed_official/code/mbed/) if you use the `--mbedlib` option:

```
$ mbed new mbed-classic-program --mbedlib
[mbed] Creating new program "mbed-classic-program" (git)
[mbed] Adding library "mbed" from "https://mbed.org/users/mbed_official/code/mbed/builds" at latest revision in the current branch
[mbed] Downloading mbed library build "f9eeca106725" (might take a minute)
[mbed] Unpacking mbed library build "f9eeca106725" in "D:\Work\examples\mbed-classic-program\mbed"
[mbed] Updating reference "mbed" -> "https://mbed.org/users/mbed_official/code/mbed/builds/f9eeca106725"
[mbed] Couldn't find build tools in your program. Downloading the mbed 2.0 SDK tools...
```
### Creating a new program without OS version selection

You can create plain (empty) programs, without either mbed OS 5 or mbed OS 2, by using the `--create-only` option.

### Importing an existing program

Use `mbed import` to clone an existing program and all its dependencies to your machine:

```
$ mbed import https://github.com/ARMmbed/mbed-os-example-blinky
[mbed] Importing program "mbed-os-example-blinky" from "https://github.com/ARMmbed/mbed-os-example-blinky" at latest revision in the current branch
[mbed] Adding library "mbed-os" from "https://github.com/ARMmbed/mbed-os" at rev #dd36dc4228b5
$ cd mbed-os-example-blinky
```

mbed CLI also supports programs based on mbed OS 2, which are automatically detected and do not require additional options:

```
$ mbed import https://mbed.org/teams/mbed/code/mbed_blinky/
[mbed] Importing program "mbed_blinky" from "https://mbed.org/teams/mbed/code/mbed_blinky" at latest revision in the current branch
[mbed] Adding library "mbed" from "http://mbed.org/users/mbed_official/code/mbed/builds" at rev #f9eeca106725
[mbed] Couldn't find build tools in your program. Downloading the mbed 2.0 SDK tools...
$ cd mbed-os-example-blinky
```

You can use the "import" command without specicying a full URL; a default prefix (https://github.com/ARMmbed) is added to the URL. For example, this command:
 
```
$ mbed import mbed-os-example-blinky
```

is equivalent to this command:
 
```
$ mbed import https://github.com/ARMmbed/mbed-os-example-blinky
```

### Importing from a Git or GitHub clone

If you have manually cloned a git repository into your workspace and you want to add all missing libraries, then you can use the `deploy` command:

```
$ mbed deploy
[mbed] Adding library "mbed-os" from "https://github.com/ARMmbed/mbed-os" at rev #dd36dc4228b5
```

Don't forget to set the current directory as the root of your program:

```
$ mbed new .
```

## Adding and removing libraries

While working on your code, you might need to add another library (dependency) to your application, or remove existing libraries. 

The mbed CLI add and remove features aren't simply built-in versions of ``hg``, ``git`` and ``rm``; their functionality is tailored to the way mbed OS and mbed CLI work:

* Adding a new library to your program is not the same as just cloning the repository. Don't clone a library using `hg` or `git`; use `mbed add` to add the library. This ensures that all dependencies - libraries or sub-libraries - are populated as well.
* Removing a library from your program is not the same as deleting the library directory - there are library reference files that will need updating or cleaning. Use `mbed remove` to remove the library, don't simply remove its directory with 'rm'.

### Adding a library

Use `mbed add` to add the latest revision of a library:

```
$ mbed add https://developer.mbed.org/users/wim/code/TextLCD/
```

Use the URL#hash format to add a library at a specific revision:

```
$ mbed add https://developer.mbed.org/users/wim/code/TextLCD/#e5a0dcb43ecc
```

___Specifying a destination directory___

If you want to specify a directory to which to add your library, you can give an additional argument to ``add`` which names that directory. For example, If you'd rather add the previous library in a directory called "text-lcd" (instead of TextLCD):

```
$ mbed add https://developer.mbed.org/users/wim/code/TextLCD/ text-lcd
```

While mbed CLI supports this functionality, we don't encourage it - adding a library with a name that differs from its source repository can easily lead to confusion.

### Removing a library

If at any point you decide that you don't need a library any more, you can use `mbed remove` with the path of the library:

```
$ mbed remove text-lcd
```

## Compiling code

### Toolchain selection

After importing a program or creating a new one, you need to tell mbed CLI where to find the toolchains that you want to use for compiling your source tree.

There are two ways to do this:
* Through the mbed CLI configuration
* Via mbed_settings.py file in the root of your program, which is automatically created (if it doesn't already exist). 

#### Through mbed CLI configuration

You can set the ARM Compiler  5 location via the command:

```
$ mbed config --global ARM_PATH "C:\Program Files\ARM"
[mbed] C:\Program Files\ARM now set as global ARM_PATH
```

The `-G` switch tells mbed CLI to set this as a global setting, rather than local for the current program.

Supported settings for toolchain paths are `ARM_PATH`, `GCC_ARM_PATH` and `IAR_PATH`

You can see the active mbed CLI configuration via:

```
$ mbed config --list
[mbed] Global config:
ARM_PATH=C:\Program Files\ARM\armcc5.06
IAR_PATH=C:\Program Files\IAR Workbench 7.0\arm

[mbed] Local config (D:\temp\mbed-os-program):
No local configuration is set
```

More information about mbed CLI configuration is available in the [configuration section](#mbed-cli-configuration) of this document.

#### Through mbed_settings.py

Edit `mbed_settings.py` to set your toolchain:

* If you want to use the [ARM Compiler toolchain](https://developer.arm.com/products/software-development-tools/compilers/arm-compiler-5/downloads), set `ARM_PATH` to the *base* directory of your ARM Compiler installation (example: C:\Program Files\ARM\armcc5.06). The recommended version of the ARM Compiler toolchain is 5.06.
* If you want to use the [GCC ARM Embedded toolchain](https://launchpad.net/gcc-arm-embedded), set `GCC_ARM_PATH` to the *binary* directory of your GCC ARM installation (example: C:\Program Files\GNU Tools ARM Embedded\4.9 2015q2\bin). Use versions 4.9 of GCC ARM Embedded; version 5.0 or any version above might be incompatible with the tools.

As a rule, since `mbed_settings.py` contains local settings (possibly relevant only to a single OS on a single machine), it should not be versioned. 

### Compiling your program

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
Image: BUILD/K64F/GCC_ARM/mbed-os-program.bin
```

The arguments for *compile* are:

* `-m <MCU>` to select a target.
* `-t <TOOLCHAIN>` to select a toolchain (of those defined in `mbed_settings.py`, see above). The value can be either `ARM` (ARM Compiler 5), `GCC_ARM` (GNU ARM Embedded), or `IAR` (IAR Embedded Workbench for ARM).
* `--source <SOURCE>` to select the source directory. The default is `.` (the current directorty). You can specify multiple source locations, even outside the program tree.
* `--build <BUILD>` to select the build directory. Default: `BUILD/` inside your program.
* `--profile <PATH_TO_BUILD_PROFILE>` to select a path to a build profile configuration file. Example: mbed-os/tools/profiles/debug.json
* `--library` to compile the code as a [static .a/.ar library](#compiling-static-libraries).
* `--config` to inspect the run-time compile configuration (see below).
* `-S` or `--supported` shows a matrix of the supported targets and toolchains.
* `-c ` (optional) to build from scratch; a clean build or rebuild.
* `-j <jobs>` (optional) to control the compile threads on your machine. The default value is 0, which infers the number of threads from the number of cores on your machine. You can use `-j 1` to trigger a sequential compile of source code.
* `-v` or `--verbose` for verbose diagnostic output.
* `-vv` or `--very_verbose` for very verbose diagnostic output.

The compiled binary, ELF image, memory usage and link statistics can be found in the `build` subdirectory of your program.

### Compiling static libraries

You can build a static library of your code by adding the `--library` argument to `mbed compile`. A typical application for static libraries is when you want to build multiple applications from the same mbed-os codebase without having to recompile for every application. To achieve this:

1. Build a static library for mbed-os.
2. Compile multiple applications or tests against the static library:

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

### Compile configuration system

The [compile configuration system](https://docs.mbed.com/docs/mbed-os-handbook/en/5.1/advanced/config_system/) provides a flexible mechanism for configuring the mbed program, its libraries and the build target. Refer to the previous link for more details about the configuration system.

___Inspecting the configuration___

If the program uses the [compile configuration system](https://github.com/ARMmbed/mbed-os/blob/master/docs/config_system.md), you can use `mbed compile --config` to view the configuration:

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

### Compile-time customizations

___Macros___

You can specify macros in your command line using the -D option. For example:

```
$ mbed compile -t GCC_ARM -m K64F -c -DUVISOR_PRESENT
```

___Compiling in debug mode___

To compile in debug mode (as opposed to the default *release* mode) use `--profile mbed-os/tools/profiles/debug.json` in the compile command line:

```
$ mbed compile -t GCC_ARM -m K64F --profile mbed-os/tools/profiles/debug.json
```

<span class="tips">**Tip:** If you have files that you want to compile only in release mode, put them in a directory called `TARGET_RELEASE` at any level of your tree. If you have files that you want to compile only in debug mode, put them in a directory called `TARGET_DEBUG` at any level of your tree (then use `--profile` as explained above).
</span>

### Automating toolchain and target selection

Using `mbed target <target>` and `mbed toolchain <toolchain>` you can set the default target and toolchain for your program, meaning you won't have to specify these every time you compile or generate IDE project files.


## Exporting to desktop IDEs

If you need to debug your code, a good way to do that is to export your source tree to an IDE project file, so that you can use the IDE's debugging facilities. Currently mbed CLI supports exporting to Keil uVision, DS-5, IAR Workbench, Simplicity Studio and other IDEs.

For example, to export to uVision run:

```
$ mbed export -i uvision -m K64F
```

A `.uvproj` file is created in the projectfiles/uvision folder. You can open the project file with uVision.

## Testing

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
Image: build\tests\K64F\GCC_ARM\TESTS\mbedmicro-rtos-mbed\mutex\TESTS-unit-myclass.bin
...[SNIP]...
mbedgt: test suite report:
+--------------+---------------+---------------------------------+--------+--------------------+-------------+
| target       | platform_name | test suite                      | result | elapsed_time (sec) | copy_method |
+--------------+---------------+---------------------------------+--------+--------------------+-------------+
| K64F-GCC_ARM | K64F          | TESTS-unit-myclass              | OK     | 21.09              |    shell    |
+--------------+---------------+---------------------------------+--------+--------------------+-------------+
mbedgt: test suite results: 1 OK
mbedgt: test case report:
+--------------+---------------+------------------------------------------+--------+--------+--------+--------------------+
| target       | platform_name | test suite         | test case           | passed | failed | result | elapsed_time (sec) |
+--------------+---------------+--------------------+---------------------+--------+--------+--------+--------------------+
| K64F-GCC_ARM | K64F          | TESTS-unit-myclass | TESTS-unit-myclass1 | 1      | 0      | OK     | 5.00               |
| K64F-GCC_ARM | K64F          | TESTS-unit-myclass | TESTS-unit-myclass2 | 1      | 0      | OK     | 5.00               |
| K64F-GCC_ARM | K64F          | TESTS-unit-myclass | TESTS-unit-myclass3 | 1      | 0      | OK     | 5.00               |
+--------------+---------------+--------------------+---------------------+--------+--------+--------+--------------------+
mbedgt: test case results: 3 OK
mbedgt: completed in 21.28 sec
```

The arguments to `test` are:
* `-m <MCU>` to select a target for the compilation.
* `-t <TOOLCHAIN>` to select a toolchain (of those defined in `mbed_settings.py`, see above), where `toolchain` can be either `ARM` (ARM Compiler 5), `GCC_ARM` (GNU ARM Embedded), or `IAR` (IAR Embedded Workbench for ARM).
* `--compile-list` to list all the tests that can be built
* `--run-list` to list all the tests that can be ran (they must be built first)
* `--compile` to only compile the tests
* `--run` to only run the tests
* `-n <TESTS_BY_NAME>` to limit the tests built or ran to a comma separated list (ex. test1,test2,test3)
* `--source <SOURCE>` to select the source directory. Default is `.` (the current dir). You can specify multiple source locations, even outside the program tree.
* `--build <BUILD>` to select the build directory. Default: `BUILD/` inside your program.
* `--profile <PATH_TO_BUILD_PROFILE>` to select a path to a build profile configuration file. Example: mbed-os/tools/profiles/debug.json
* `-c or --clean` to clean the build directory before compiling,
* `--test-spec <TEST_SPEC>` to set the path for the test spec file used when building and running tests (the default path is the build directory).
* `-v` or `--verbose` for verbose diagnostic output.
* `-vv` or `--very_verbose` for very verbose diagnostic output.

The compiled binaries and test artifacts can be found in the `BUILD/tests/<TARGET>/<TOOLCHAIN>` directory of your program.

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
mbedgt: test specification file '.\build\tests\K64F\ARM\test_spec.json' (specified with --test-spec option)
mbedgt: using '.\build\tests\K64F\ARM\test_spec.json' from current directory!
mbedgt: available tests for built 'K64F-ARM', location '.\build\tests\K64F\ARM'
        test 'TESTS-functional-test1'
        test 'TESTS-functional-test2'
        test 'TESTS-functional-test3'
```

#### Compiling and running tests

You can specify to only **build** the tests by using the `--compile` option:

```
$ mbed test -m K64F -t GCC_ARM --compile
```

You can specify to only **run** the tests by using the `--run` option:

```
$ mbed test -m K64F -t GCC_ARM --run
```

If you don't specify any of these `mbed test` will first compile all available tests and then run them.

#### Limiting the test scope

You can limit the scope of the tests built and ran by using the `-n` option. This takes a comma separated list of test names as an argument:

```
$ mbed test -m K64F -t GCC_ARM -n TESTS-functional-test1,TESTS-functional-test2
```

You can use the wildcard character `*` to run a group of tests that share a common prefix without specifying each test individually. For instance, if you only want to run the three tests `TESTS-functional-test1`, `TESTS-functional-test2`, and `TESTS-functional-test3` but you have other tests in your project, you can run:

```
$ mbed test -m NUCLEO_F429ZI -t GCC_ARM -n TESTS-functional*
```

**Note:** Some shells will try to expand the wildcard character `*` into filenames that exist in your working directory. To prevent this behavior, please see your shell's documentation.


### Test directory structure

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
 `- build                 # Build directory
     |- <TARGET>          # Target directory
     | `- <TOOLCHAIN>     # Toolchain directory
     |   |- TestCase1.bin # Test binary
     |   `- TestCase2.bin
     | ....
```

As shown above, tests exist inside ```TESTS\testgroup\testcase\``` directories. Please note that `TESTS` is a special upper case directory that is excluded from module sources while compiling.

<span class="notes">**Note:** This feature does not work in applications that contain a  ```main``` function that is outside of a `TESTS` directory.</span>

## Publishing your changes

### Checking status

As you develop your program, you'll edit parts of it - either your own code or code in some of the libraries that it depends on. You can get the status of all the repositories in your program (recursively) by running `mbed status`. If a repository has uncommitted changes, this command will display these changes. 

Here's an example:

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

You can then commit or discard these changes.

### Pushing upstream

To push the changes in your local tree upstream, run `mbed publish`. `publish` works recursively, pushing the leaf dependencies first, then updating the dependents and pushing them too. 

This is best explained by an example. Let's assume that the list of dependencies of your program (obtained by running `mbed ls`) looks like this:

```
my-mbed-os-example (a5ac4bf2e468)
|- mbed-os (5fea6e69ec1a)
`- my-libs (e39199afa2da)
   |- my-libs/iot-client (571cfef17dd0)
   `- my-libs/test-framework (cd18b5a50df4)
```

Let's assume that you make changes to `ot-client`. `publish` detects the change on the leaf `ot-client` dependency and asks you to commit it. Then it detects that `my-libs` depends on `iot-client`, updates the `my-libs` dependency on `iot-client` to its latest version (by updating the `iot-client.lib` file) and asks you to commit it. This propagates up to `my-libs` and finally to your program `my-mbed-os-example`.

### Forking workflow

Git enables asymmetric workflow where the publish/push repository might be different than the original ("origin") one. This allows new revisions to land in a fork repository, while maintaining an association with the original repository.

To achieve this, first import an mbed OS program or mbed OS itself and then associate the push remote with your fork. For example:

```
$ git remote set-url --push origin https://github.com/screamerbg/repo-fork
```

Each time you `git` commit and push, or use `mbed publish`, the new revisions will be pushed against your fork. You can fetch from the original repository using `mbed update` or `git pull`. If you explicitly want to fetch or pull from your fork, then you can use `git pull https://github.com/screamerbg/repo-fork [branch]`.

Through the workflow explained above, mbed CLI will maintain association to the original repository (which you might want to send pull request to), and will record references with the revision hashes that you push to your fork. Until your pull request is accepted, all recorded references will be invalid. Once the PR is accepted, all revision hashes from your fork will become part the original repository, so all references will become valid.

## Updating programs and libraries

You can update programs and libraries on your local machine so that they pull in changes from the remote sources (GitHub or Mercurial). 

There are two main scenarios when updating:

* Update to a *moving* revision, like the tip of a branch.
* Update to a *specific* revision that is identified by a revision hash or tag name.

Each scenario has two cases:

* Update with local uncommitted changes - *dirty* update.
* Update without local uncommitted changes - *clean* update.

As with any mbed CLI command, `mbed update` uses the current directory as a working context, meaning that before calling `mbed update` you should change your working directory to the one you want to update.For example, if you're updating mbed-os, use `cd mbed-os` before you begin updating.

<span class="tips">**Tip: Synchronizing library references:** Before triggering an update, you might want to synchronize any changes that you've made to the program structure by running ``mbed sync``, which will update the necessary library references and get rid of the invalid ones.</span>

### Protection against overwriting local changes

The update command will fail if there are changes in your program or library that will be overwritten as a result of running `update`. This is by design: mbed CLI does not run operations that would result in overwriting local changes that are not yet committed. If you get an error, take care of your local changes (commit or use one of the options below), then re-run `update`.

### Updating to an upstream version

___Updating a program___

To update your program to another upstream version, go to the root folder of the program and run:

```
$ mbed update [branch|tag|revision]
```

This fetches new revisions from the remote repository, updating the program to the specified branch, tag or revision. If none of these are specified, then it updates to the latest revision in the current branch. This series of actions is performed recursively against all dependencies and sub-dependencies in the program tree.

___Updating a library___

You can change the working directory to a library folder and use `mbed update` to update that library and its dependencies to a different revision than the one referenced in the parent program or library. This allows you to experiment with different versions of libraries/dependencies in the program tree, without having to change the parent program or library.

### Update examples

To help understand what options you can use with mbed CLI, check the examples below.

**Case 1: I want to update a program or a library to the latest version in a specific or current branch**

__I want to preserve my uncommitted changes__ 

Run `mbed update [branch]`. You might have to commit or stash your changes if the source control tool (Git or Mercurial) throws an error that the update will overwrite local changes.

__I want a clean update (and discard uncommitted changes)__

Run `mbed update [branch] --clean`

Specifying a branch to `mbed update` will only check out that branch, and won't automatically merge or fast-forward to the remote/upstream branch. You can run `mbed update` to merge (fast-forward) your local branch with the latest remote branch. On git you can do `git pull`

<span class="warnings">**Warning**: The `--clean` option tells mbed CLI to update that program or library and its dependencies, and discard all local changes. This action cannot be undone; use with caution.</span>

**Case 2: I want to update a program or a library to a specific revision or a tag**
 
__I want to preserve my uncommitted changes__ 

Run `mbed update <tag_name|revision>`. You might have to commit or stash your changes if they conflict with the latest revision.

__I want a clean update (discard changes)__

Run `mbed update <tag_name|revision> --clean`

__When you have unpublished local libraries__

There are three additional options that define how unpublished local libraries are handled:

* `mbed update --clean-deps` - update the current program or library and its dependencies, and discard all local unpublished repositories. Use this with caution, as your local unpublished repositories cannot be restored unless you have a backup copy.

* `mbed update --clean-files` - update the current program or library and its dependencies, discard local uncommitted changes and remove any untracked or ignored files. Use this with caution, as your local unpublished repositories cannot be restored unless you have a backup copy.

* `mbed update --ignore` - update the current program or library and its dependencies, and ignore any local unpublished libraries (they won't be deleted or modified, just ignored).

__Combining update options__

You can combine the options above for the following scenarios:

* `mbed update --clean --clean-deps --clean-files` - update the current program or library and its dependencies, remove all local unpublished libraries, discard local uncommitted changes, and remove all untracked or ignored files. This wipes every single change that you made in the source tree and restores the stock layout.

* `mbed update --clean --ignore` - update the current program or library and its dependencies, but ignore any local repositories. mbed CLI will update whatever it can from the public repositories.

Use these with caution as your uncommitted changes and unpublished libraries cannot be restored.

## mbed CLI configuration

Many options in mbed CLI can be streamlined with global and local configuration.

The mbed CLI configuration syntax is:
```
mbed config [--global] <var> [value] [--unset]
```

* The **global** configuration (via `--global` option) defines the default behavior of mbed CLI across programs unless overridden by *local* settings.
* The **local** configuration (without `--global`) is per mbed program and allows overriding of global or default mbed CLI settings within the scope of a program or library and its dependencies.
* If **no value** is specified then mbed CLI will print the currently set value for this settings from either the local or global scope.
* The `--unset` option allows removing of a setting.
* The `--list` option allows to list global and local configuration.

Here is a list of currently implemented configuration settings:

 * `target` - defines the default target for `compile`, `test` and `export`; an alias of `mbed target`. Default: none.
 * `toolchain` - defines the default toolchain for `compile` and `test`; can be set through `mbed toolchain`. Default: none.
 * `ARM_PATH`, `GCC_ARM_PATH`, `IAR_PATH` - defines the default path to ARM Compiler, GCC ARM and IAR Workbench toolchains. Default: none.
 * `protocol` - defines the default protocol used for importing or cloning of programs and libraries. The possible values are `https`, `http` and `ssh`. Use `ssh` if you have generated and registered SSH keys (Public Key Authentication) with a service like GitHub, GitLab, Bitbucket, etc. Read more about SSH keys [here](https://help.github.com/articles/generating-an-ssh-key/) Default: `https`.
 * `depth` - defines the *clone* depth for importing or cloning and applies only to *Git* repositories. Note that while this option may improve cloning speed, it may also prevent you from correctly checking out a dependency tree when the reference revision hash is older than the clone depth. Read more about shallow clones [here](https://git-scm.com/docs/git-clone). Default: none.
 * `cache` (EXPERIMENTAL) - defines the local path that will be used to store minimalistic copies of the imported or cloned repositories, and attempts to use them to minimize traffic and speed up future importing. This feature is still under development, so this should not be used within a production environment. Default: none (disabled).
 
## Troubleshooting

#### Unable to import Mercurial based (mbed.org) programs or libraries.
1. Check whether you have Mercurial installed in your system path by  running `hg` in command prompt. If you're receiving "command not found" or similar message, then you need to install Mercurial and add it to your system path.

2. Try to clone a Mercurial repository directly, e.g. `hg clone https://developer.mbed.org/teams/mbed/code/mbed_blinky/`. If you're receiving error similar to `abort: error: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.:590)` then your system certificates are very old. You need to update your system certificates and possibly add the host certificate fingerprint of `mbed.com` and `mbed.org`. Read more about Mercurial's certificate management [here](https://www.mercurial-scm.org/wiki/CACertificates).

#### Various issues when running mbed CLI in cygwin environment
Currently mbed CLI is not compatible with cygwin environment and cannot be executed inside it (https://github.com/ARMmbed/mbed-cli/issues/299)
