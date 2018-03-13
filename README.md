## Introduction

Arm Mbed CLI is the name of the Arm Mbed command-line tool, packaged as `mbed-cli`. Mbed CLI enables Git- and Mercurial-based version control, dependencies management, code publishing, support for remotely hosted repositories (GitHub, GitLab and mbed.org), use of the Arm Mbed OS build system and export functions and other operations.

This document covers the installation and usage of Mbed CLI.

## Table of Contents

1. [Using Mbed CLI](#using-mbed-cli)
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
1. [Mbed CLI configuration](#mbed-cli-configuration)
1. [Troubleshooting](#troubleshooting)


## Using Mbed CLI

The basic workflow for Mbed CLI is to:

1. Initialize a new repository, for either a new application (or library) or an imported one. In both cases, this action also adds the Mbed OS codebase.
1. Build the application code.
1. Test your build.
1. Publish your application.

To support long-term development, Mbed CLI offers source control, including selective updates of libraries and the codebase, support for multiple toolchains and manual configuration of the system.

<span class="tips">**Tip:** To list all Mbed CLI commands, use `mbed --help`. A detailed command-specific help is available by using `mbed <command> --help`.</span>

## Installation

Windows, Linux and Mac OS X support Mbed CLI. We're keen to learn about your experience with Mbed CLI on other operating systems at the [Mbed CLI development page](https://github.com/ARMmbed/mbed-cli).

### Requirements

* **Python** - Mbed CLI is a Python script, so you'll need Python to use it. We test Mbed CLI with [version 2.7.11 of Python](https://www.python.org/downloads/release/python-2711/). It is not compatible with Python 3.

* **Git and Mercurial** - Mbed CLI supports both Git and Mercurial repositories, so you need to install both:
    * [Git](https://git-scm.com/) - version 1.9.5 or later.
    * [Mercurial](https://www.mercurial-scm.org/) - version 2.2.2 or later.

The directories of Git and Mercurial executables (`git` and `hg`) need to be in your system's PATH.

* **Command-line compiler or IDE toolchain** - Mbed CLI invokes the [Mbed OS 5](https://github.com/ARMmbed/mbed-os) tools for various features, such as compiling, testing and exporting to industry standard toolchains. To compile your code, you need either a compiler or an IDE:
    * Compilers: GCC ARM, Arm Compiler 5, Arm Compiler 6, IAR.
    * IDE: Keil uVision, DS-5, IAR Workbench.

<span class="tips">**Note:** When installing the Arm Compiler 5 on a 64-bit Linux machine, you may need to also install the i386 architecture package:</span>

```
$ sudo dpkg --add-architecture i386
$ sudo apt-get update
$ sudo apt-get install libc6:i386 libncurses5:i386 libstdc++6:i386
```

### Video tutorial for manual installation

<span class="images">[![Video tutorial](https://img.youtube.com/vi/cM0dFoTuU14/0.jpg)](https://www.youtube.com/watch?v=cM0dFoTuU14)</span>

### Installing Mbed CLI

Windows users can use the [Mbed CLI for Windows installer](https://docs.mbed.com/docs/mbed-os-handbook/en/latest/dev_tools/cli_install/) to install Mbed CLI and all necessary requirements with one installer.

You can get the latest stable version of Mbed CLI through pip by running:

```
$ pip install mbed-cli
```

On Linux or Mac, you may need to run with `sudo`.

Alternatively, you can get the development version of Mbed CLI by cloning the development repository [https://github.com/ARMmbed/mbed-cli](https://github.com/ARMmbed/mbed-cli):

```
$ git clone https://github.com/ARMmbed/mbed-cli
```

Once cloned, you can install Mbed CLI as a Python package:

```
$ python setup.py install
```

On Linux or Mac, you may need to run with `sudo`.

<span class="tips">**Note:** Mbed CLI is compatible with [Virtual Python Environment (virtualenv)](https://pypi.python.org/pypi/virtualenv). You can read more about isolated Python virtual environments [here](http://docs.python-guide.org/en/latest/).</span>

### Updating Mbed CLI

To update an existing installation of Mbed CLI, run:

```
pip install -U mbed-cli
```

### Uninstalling Mbed CLI

To uninstall Mbed CLI, run:

```
pip uninstall mbed-cli
```

### Adding Bash tab completion

To install `mbed-cli` bash tab completion navigate to the `tools/bash_completion` directory. Then, copy the `mbed` script into your `/etc/bash_completion.d/` or `/usr/local/etc/bash_completion.d` directory and reload your terminal.  

[Full documentation here](https://github.com/ARMmbed/mbed-cli/blob/master/tools/bash_completion/install.md)

## Quickstart video

<span class="images">[![Video tutorial](https://img.youtube.com/vi/PI1Kq9RSN_Y/0.jpg)](https://www.youtube.com/watch?v=PI1Kq9RSN_Y)</span>

## Before you begin: understanding the working context and program root

Mbed CLI uses the current directory as a working context, in a similar way to Git, Mercurial and many other command-line tools. This means that before calling any Mbed CLI command, you must first change to the directory containing the code you want to act on. For example, if you want to update the Mbed OS sources in your `mbed-example-program` directory:

```
$ cd mbed-example-program
$ cd mbed-os
$ mbed update master   # This will update "mbed-os", not "my-program"
```

Various Mbed CLI features require a program root, which should be under version control - either [Git](https://git-scm.com/) or [Mercurial](https://www.mercurial-scm.org/). This makes it possible to switch between revisions of the whole program and its libraries, control the program history, synchronize the program with remote repositories, share it with others and so on. Version control is also the primary and preferred delivery mechanism for Mbed OS source code, which allows everyone to contribute to Mbed OS.

<span class="warnings">**Warning**: Mbed CLI stores information about libraries and dependencies in reference files that use the `.lib` extension (such as `lib_name.lib`). Although these files are human-readable, we *strongly* advise that you don't edit these manually - let Mbed CLI manage them instead.</span>

## Creating and importing programs

Mbed CLI can create and import programs based on both Mbed OS 2 and Mbed OS 5.

### Creating a new program for Mbed OS 5

When you create a new program, Mbed CLI automatically imports the latest [Mbed OS release](https://github.com/ARMmbed/mbed-os/). Each release includes all the components: code, build tools and IDE exporters.

With this in mind, let's create a new program (we'll call it `mbed-os-program`):

```
$ mbed new mbed-os-program
[mbed] Creating new program "mbed-os-program" (git)
[mbed] Adding library "mbed-os" from "https://github.com/ARMmbed/mbed-os" at latest revision in the current branch
[mbed] Updating reference "mbed-os" -> "https://github.com/ARMmbed/mbed-os/#89962277c20729504d1d6c95250fbd36ea5f4a2d"
```

This creates a new folder "mbed-os-program", initializes a new repository and imports the latest revision of the `mbed-os` dependency to your program tree.

<span class="tips">**Tip:** You can instruct Mbed CLI to use a specific source control management system or prevent source control management initialization, by using `--scm [name|none]` option.</span>

Use `mbed ls` to list all the libraries imported to your program:

```
$ cd mbed-os-program
$ mbed ls
mbed-os-program (no revision)
`- mbed-os (#182bbd51bc8d, tags: latest, mbed-os-5.6.5)
```

Use `mbed releases` to list all releases in a program or library:

```
$ cd mbed-os
$ mbed releases
mbed-os (#182bbd51bc8d, tags: latest, mbed-os-5.6.5)
  ...
  * mbed-os-5.6.0 
  * mbed-os-5.6.1 
  * mbed-os-5.6.2 
  * mbed-os-5.6.3 
  * mbed-os-5.6.4 
  * mbed-os-5.6.5  <- current
```

<span class="notes">**Note**: If you want to start from an existing folder in your workspace, you can use `mbed new .`, which initializes an Mbed program, as well as a new Git or Mercurial repository in that folder. </span>

### Creating a new program for Mbed OS 2

Mbed CLI is also compatible with Mbed OS 2 programs based on the [Mbed library](https://mbed.org/users/mbed_official/code/mbed/), and it automatically imports the latest [Mbed library release](https://mbed.org/users/mbed_official/code/mbed/) if you use the `--mbedlib` option:

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

You can create plain (empty) programs, without either Mbed OS 5 or Mbed OS 2, by using the `--create-only` option.

### Importing an existing program

Use `mbed import` to clone an existing program and all its dependencies to your machine:

```
$ mbed import https://github.com/ARMmbed/mbed-os-example-blinky
[mbed] Importing program "mbed-os-example-blinky" from "https://github.com/ARMmbed/mbed-os-example-blinky" at latest revision in the current branch
[mbed] Adding library "mbed-os" from "https://github.com/ARMmbed/mbed-os" at rev #dd36dc4228b5
$ cd mbed-os-example-blinky
```

Mbed CLI also supports programs based on Mbed OS 2, which it automatically detects and which do not require additional options:

```
$ mbed import https://mbed.org/teams/mbed/code/mbed_blinky/
[mbed] Importing program "mbed_blinky" from "https://mbed.org/teams/mbed/code/mbed_blinky" at latest revision in the current branch
[mbed] Adding library "mbed" from "http://mbed.org/users/mbed_official/code/mbed/builds" at rev #f9eeca106725
[mbed] Couldn't find build tools in your program. Downloading the mbed 2.0 SDK tools...
$ cd mbed-os-example-blinky
```

You can use the "import" command without specifying a full URL; Mbed CLI adds a prefix (https://github.com/ARMmbed) to the URL if one is not present. For example, this command:

```
$ mbed import mbed-os-example-blinky
```

is equivalent to this command:

```
$ mbed import https://github.com/ARMmbed/mbed-os-example-blinky
```

### Importing from a Git or GitHub clone

If you have manually cloned a Git repository into your workspace and you want to add all missing libraries, then you can use the `deploy` command:

```
$ mbed deploy
[mbed] Adding library "mbed-os" from "https://github.com/ARMmbed/mbed-os" at rev #dd36dc4228b5
```

Don't forget to set the current directory as the root of your program:

```
$ mbed new .
```

## Adding and removing libraries

While working on your code, you may need to add another library to your application or remove existing libraries.

Adding a new library to your program is not the same as cloning the repository. Don't clone a library using `hg` or `git`; use `mbed add` to add the library. This ensures that all libraries and sublibraries are populated as well.

Removing a library from your program is not the same as deleting the library directory. Mbed CLI updates and removes library reference files. Use `mbed remove` to remove the library; don't remove its directory with `rm`.

### Adding a library

Use `mbed add` to add the latest revision of a library:

```
$ mbed add https://developer.mbed.org/users/wim/code/TextLCD/
```

Use the `URL#hash` format to add a library from a URL at a specific revision hash:

```
$ mbed add https://developer.mbed.org/users/wim/code/TextLCD/#e5a0dcb43ecc
```

#### Specifying a destination directory

If you want to specify a directory to which to add your library, you can give an additional argument to ``add``, which names that directory. For example, If you'd rather add the previous library in a directory called "text-lcd" (instead of TextLCD):

```
$ mbed add https://developer.mbed.org/users/wim/code/TextLCD/ text-lcd
```

Although Mbed CLI supports this functionality, we don't encourage it. Adding a library with a name that differs from its source repository can lead to confusion.

### Removing a library

If at any point you decide that you don't need a library any more, you can use `mbed remove` with the path of the library:

```
$ mbed remove text-lcd
```

## Compiling code

### Toolchain selection

After importing a program or creating a new one, you need to tell Mbed CLI where to find the toolchains that you want to use for compiling your source tree.

There are multiple ways to configure toolchain locations:
* `mbed_settings.py` file in the root of your program. The tools will automatically create this file if it doesn't already exist.
* The Mbed CLI configuration.
* Setting an environment variable.
* Adding directory of the compiler binary to your PATH.

Methods for configuring toolchains that appear earlier in the above list override methods that appear later.

#### Through `mbed_settings.py`

Edit `mbed_settings.py` to set your toolchain:

* To use [Arm Compiler 5](https://developer.arm.com/products/software-development-tools/compilers/arm-compiler-5/downloads), set `ARM_PATH` to the *base* directory of your Arm Compiler installation (example: C:\Program Files\ARM\armcc5.06). Use version 5.06 of Arm Compiler 5.
* To use [Arm Compiler 6](https://developer.arm.com/products/software-development-tools/compilers/arm-compiler-6/downloads), set `ARMC6_PATH` to the *binary* directory of your Arm Compiler installation (example: C:\Program Files\ARM\armcc6.8\bin). Use version 6.8 of Arm Compiler 6.
* To use the [GNU Arm Embedded toolchain (GCC) version 6](https://developer.arm.com/open-source/gnu-toolchain/gnu-rm/downloads), set `GCC_ARM_PATH` to the *binary* directory of your GCC Arm installation (example: C:\Program Files\GNU Tools ARM Embedded\6 2017q2\bin). Use version 6 of GCC Arm Embedded; version 5.0 or any older version might be incompatible with the tools.
* To use the [IAR EWARM toolchain](https://www.iar.com/iar-embedded-workbench/#!?architecture=ARM), set `IAR_PATH` to the *base* directory of your IAR installation (example: C:\Program Files (x86)\IAR Systems\Embedded Workbench 7.5\arm). Use versions 7.70 to 7.80.x of the IAR EWARM; newer (or older) versions might be incompatible with the tools.

Because `mbed_settings.py` contains local settings (possibly relevant only to a single OS on a single machine), you should not check it into version control.

#### Through Mbed CLI configuration

You can set the Arm Compiler 5 location via the command:

```
$ mbed config -G ARM_PATH "C:\Program Files\ARM"
[mbed] C:\Program Files\ARM now set as global ARM_PATH
```

The `-G` switch tells Mbed CLI to set this as a global setting, rather than local for the current program.

Supported settings for toolchain paths are `ARM_PATH`, `ARMC6_PATH`, `GCC_ARM_PATH` and `IAR_PATH`.

You can see the active Mbed CLI configuration via:

```
$ mbed config --list
[mbed] Global config:
ARM_PATH=C:\Program Files\ARM\armcc5.06
IAR_PATH=C:\Program Files\IAR Workbench 7.0\arm

[mbed] Local config (D:\temp\mbed-os-program):
No local configuration is set
```

More information about Mbed CLI configuration is available in the [configuration section](#mbed-cli-configuration) of this document.

#### Setting environment variable

For each of the compilers, `mbed compile` checks a corresponding environment variable for the compiler's location. The environment variables are as follows:
* `MBED_ARM_PATH`: The path to the *base* directory of your Arm Compiler installation. This should be the directory containing the directory containing the binaries for `armcc` and friends.
* `MBED_ARMC6_PATH`: The path to the *binary* directory of your Arm Compiler installation. This should be the directory containing the binaries for `armclang` and friends.
* `MBED_IAR_PATH`: The path to the *base* directory of your IAR EWARM Compiler installation. This should be one directory containing the directory containing the binaries for `iccarm` and friends.
* `MBED_GCC_ARM_PATH`: The path to the *binary* directory of your GCC Arm Embedded Compiler installation. This should be the directory containing the binaries for `arm-none-eabi-gcc` and friends.

#### Compiler detection through the `PATH`

If none of the above are configured, the `mbed compile` command will fall back to checking your `PATH` for an executable that is part of the compiler suite in question. This check is the same as a shell would perform to find the executable on the command-line. When `mbed compile` finds the executable it is looking for, it uses the location of that executable as the appropriate path except in the case of GCC, which will not use a path.

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

* `-m <MCU>` to select a target. If `detect` or `auto` parameter is passed to `-m`, then Mbed CLI detects the connected target.
* `-t <TOOLCHAIN>` to select a toolchain (of those defined in `mbed_settings.py`, see above). The value can be `ARM` (Arm Compiler 5), `GCC_ARM` (GNU Arm Embedded) or `IAR` (IAR Embedded Workbench for Arm).
* `--source <SOURCE>` to select the source directory. The default is `.` (the current directory). You can specify multiple source locations, even outside the program tree.
* `--build <BUILD>` to select the build directory. Default: `BUILD/` inside your program root.
* `--profile <PATH_TO_BUILD_PROFILE>` to select a path to a build profile configuration file. Example: `mbed-os/tools/profiles/debug.json`.
* `--library` to compile the code as a [static .a/.ar library](#compiling-static-libraries).
* `--config` to inspect the runtime compile configuration (see below).
* `-S` or `--supported` shows a matrix of the supported targets and toolchains.
* `-f` or `--flash` to flash/program a connected target after successful compile.
* `-c ` to build from scratch, a clean build or rebuild.
* `-j <jobs>` to control the compile processes on your machine. The default value is 0, which infers the number of processes from the number of cores on your machine. You can use `-j 1` to trigger a sequential compile of source code.
* `-v` or `--verbose` for verbose diagnostic output.
* `-vv` or `--very_verbose` for very verbose diagnostic output.

You can find the compiled binary, ELF image, memory usage and link statistics in the `BUILD` subdirectory of your program.

For more information on build profiles, see [our build profiles](https://docs.mbed.com/docs/mbed-os-handbook/en/latest/dev_tools/build_profiles/) and [toolchain profiles](https://docs.mbed.com/docs/mbed-os-handbook/en/latest/advanced/toolchain_profiles/) pages.

### Compiling static libraries

You can build a static library of your code by adding the `--library` argument to `mbed compile`. Static libraries are useful when you want to build multiple applications from the same Mbed OS codebase without having to recompile for every application. To achieve this:

1. Build a static library for `mbed-os`.
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

The [compile configuration system](https://docs.mbed.com/docs/mbed-os-handbook/en/5.3/advanced/config_system/) provides a flexible mechanism for configuring the Mbed program, its libraries and the build target.

#### Inspecting the configuration

You can use `mbed compile --config` to view the configuration:

```
$ mbed compile --config -t GCC_ARM -m K64F
```

To display more verbose information about the configuration parameters, use `-v`:

```
$ mbed compile --config -t GCC_ARM -m K64F -v
```

It's possible to filter the output of `mbed compile --config` by specifying one or more prefixes for the configuration parameters that Mbed CLI displays. For example, to display only the configuration defined by the targets:

```
$ mbed compile --config -t GCC_ARM -m K64F --prefix target
```

You may use `--prefix` more than once. To display only the application and target configuration, use two `--prefix` options:

```
$ mbed compile --config -t GCC_ARM -m K64F --prefix target --prefix app
```

### Compile-time customizations

#### Macros

You can specify macros in your command-line using the -D option. For example:

```
$ mbed compile -t GCC_ARM -m K64F -c -DUVISOR_PRESENT
```

#### Compiling in debug mode

To compile in debug mode (as opposed to the default *develop* mode), use `--profile mbed-os/tools/profiles/debug.json` in the compile command-line:

```
$ mbed compile -t GCC_ARM -m K64F --profile mbed-os/tools/profiles/debug.json
```

<span class="tips">**Tip:** If you have files that you want to compile only in debug mode, put them in a directory called `TARGET_DEBUG` at any level of your tree (then use `--profile` as explained above).
</span>

### Automating toolchain and target selection

Using `mbed target <target>` and `mbed toolchain <toolchain>`, you can set the default target and toolchain for your program. You won't have to specify these every time you compile or generate IDE project files.

You can also use `mbed target detect`, which detects the connected target board and uses it as a parameter to every subsequent compile and export.

## Exporting to desktop IDEs

If you need to debug your code, you can export your source tree to an IDE project file to use the IDE's debugging facilities. Mbed CLI supports exporting to Keil uVision, IAR Workbench, a Makefile using GCC Arm, Eclipse using GCC Arm and other IDEs.

For example, to export to uVision, run:

```
$ mbed export -i uvision -m K64F
```

Mbed CLI creates a `.uvprojx` file in the projectfiles/uvision folder. You can open the project file with uVision.

## Testing

Use the `mbed test` command to compile and run tests.

The arguments to `test` are:
* `-m <MCU>` to select a target for the compilation. If `detect` or `auto` parameter is passed, then Mbed CLI will attempt to detect the connected target and compile against it.
* `-t <TOOLCHAIN>` to select a toolchain (of those defined in `mbed_settings.py`, see above), where `toolchain` can be either `ARM` (Arm Compiler 5), `GCC_ARM` (GNU Arm Embedded), or `IAR` (IAR Embedded Workbench for Arm).
* `--compile-list` to list all the tests that can be built.
* `--run-list` to list all the tests that can be run (they must be built first).
* `--compile` to only compile the tests.
* `--run` to only run the tests.
* `-n <TESTS_BY_NAME>` to limit the tests built or run to a comma separated list (ex. test1,test2,test3).
* `--source <SOURCE>` to select the source directory. Default is `.` (the current directory). You can specify multiple source locations, even outside the program tree.
* `--build <BUILD>` to select the build directory. Default: `BUILD/` inside your program.
* `--profile <PATH_TO_BUILD_PROFILE>` to select a path to a build profile configuration file. Example: `mbed-os/tools/profiles/debug.json`.
* `-c or --clean` to clean the build directory before compiling.
* `--test-spec <TEST_SPEC>` to set the path for the test spec file used when building and running tests (the default path is the build directory).
* `-v` or `--verbose` for verbose diagnostic output.
* `-vv` or `--very_verbose` for very verbose diagnostic output.

Invoke `mbed test`:

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

You can find the compiled binaries and test artifacts in the `BUILD/tests/<TARGET>/<TOOLCHAIN>` directory of your program.

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

If you don't specify any of these, `mbed test` will first compile all available tests and then run them.

#### Limiting the test scope

You can limit the scope of the tests built and run by using the `-n` option. This takes a comma-separated list of test names as an argument:

```
$ mbed test -m K64F -t GCC_ARM -n TESTS-functional-test1,TESTS-functional-test2
```

You can use the wildcard character `*` to run a group of tests that share a common prefix without specifying each test individually. For instance, if you only want to run the three tests `TESTS-functional-test1`, `TESTS-functional-test2` and `TESTS-functional-test3`, but you have other tests in your project, you can run:

```
$ mbed test -m NUCLEO_F429ZI -t GCC_ARM -n TESTS-functional*
```

**Note:** Some shells expand the wildcard character `*` into file names that exist in your working directory. To prevent this behavior, please see your shell's documentation.

### Test directory structure

Test code must follow this directory structure:

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

As shown above, tests exist inside `TESTS\testgroup\testcase\` directories. Please note that `TESTS` is a special upper case directory that is excluded from module sources while compiling.

<span class="notes">**Note:** `mbed test` does not work in applications that contain a  `main` function that is outside of a `TESTS` directory.</span>

## Publishing your changes

### Checking status

As you develop your program, you'll edit parts of it. You can get the status of all the repositories in your program (recursively) by running `mbed status`. If a repository has uncommitted changes, this command displays these changes.

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

You can then commit or discard these changes through that repository's version control system.

### Pushing upstream

To push the changes in your local tree upstream, run `mbed publish`. `mbed publish` works recursively, pushing the leaf dependencies first, then updating the dependents and pushing them too.

Let's assume that the list of dependencies of your program (obtained by running `mbed ls`) looks like this:

```
my-mbed-os-example (#a5ac4bf2e468)
|- mbed-os (#182bbd51bc8d, tags: latest, mbed-os-5.6.5)
`- my-libs (#e39199afa2da)
   |- my-libs/iot-client (#571cfef17dd0)
   `- my-libs/test-framework (#cd18b5a50df4)
```

Let's assume that you make changes to `iot-client`. `mbed publish` detects the change on the leaf `iot-client` dependency and asks you to commit it. Then `mbed publish` detects that `my-libs` depends on `iot-client`, updates the `my-libs` dependency on `iot-client` to its latest version by updating the `iot-client.lib` file and asks you to commit it. This propagates up to `my-libs` and finally to your program, `my-mbed-os-example`.

## Publishing a local program or library

When you create a new (local) version control managed program or library, its revision history exists only locally. The repository is not associated with the remote one. To publish the local repository, please follow these steps:

1. Create a new empty repository on the remote site. This can be on a public repository hosting service (GitHub, Bitbucket, mbed.org), your own service or a different location on your system.
1. Copy the URL/location of the new repository in your clipboard.
1. Open command-line in the local repository directory (for example, change directory to `mbed-os-example/local-lib`).
1. To associate the local repository:
 * For Git, run `git remote add origin <url-or-path-to-your-remote-repo>`.
 * For Mercurial, edit .hg/hgrc and add (or replace if exists):

            ```
            [paths]
            default = <url-or-path-to-your-remote-repo>
            ```

1. Run `mbed publish` to publish your changes.

In a scenario with nested local repositories, start with the leaf repositories first.

### Forking workflow

Git enables a workflow where the publish/push repository may be different than the original ("origin") one. This allows new revisions in a fork repository while maintaining an association with the original repository. To use this workflow, first import an Mbed OS program or Mbed OS itself, and then associate the push remote with your fork. For example:

```
$ git remote set-url --push origin https://github.com/screamerbg/repo-fork
```

Both `git commit & git push` and `mbed publish` push the new revisions to your fork. You can fetch from the original repository using `mbed update` or `git pull`. If you explicitly want to fetch or pull from your fork, then you can use `git pull https://github.com/screamerbg/repo-fork [branch]`.

Through the workflow explained above, Mbed CLI maintains association to the original repository (which you may want to send a pull request to) and records references with the revision hashes that you push to your fork. Until your pull request (PR) is accepted, all recorded references are invalid. Once the PR is accepted, all revision hashes from your fork become part the original repository, making them valid.

## Updating programs and libraries

You can update programs and libraries on your local machine so that they pull in changes from the remote sources (Git or Mercurial).

As with any Mbed CLI command, `mbed update` uses the current directory as a working context. Before calling `mbed update`, you should change your working directory to the one you want to update. For example, if you're updating `mbed-os`, use `cd mbed-os` before you begin updating.

<span class="tips">**Tip: Synchronizing library references:** Before triggering an update, you may want to synchronize any changes that you've made to the program structure by running `mbed sync`, which updates the necessary library references and removes the invalid ones.</span>

### Protection against overwriting local changes

The update command fails if there are changes in your program or library that `mbed update` could overwrite. This is by design. Mbed CLI does not run operations that would result in overwriting uncommitted local changes. If you get an error, take care of your local changes (commit or use one of the options below), and then rerun `mbed update`.

### Updating to an upstream version

Before updating a program or a library, it's good to know the names of the stable releases, usually marked with a tag using a common format, such as `1.2`, `v1.0.1`, `r5.6`, `mbed-os-5.6` and so on. 

You can find stable release versions of a program or a library using the `mbed releases` command:

```
$ cd mbed-os
$ mbed releases
mbed-os (#182bbd51bc8d, tags: latest, mbed-os-5.6.5)
  ...
  * mbed-os-5.6.0 
  * mbed-os-5.6.1 
  * mbed-os-5.6.2 
  * mbed-os-5.6.3 
  * mbed-os-5.6.4 
  * mbed-os-5.6.5  <- current
```

You can also recursively list stable releases for your program and libraries using the `-r` switch, for example `mbed releases -r`.

Lastly, you can list unstable releases, such as release candidates, alphas and betas by using the `-u` switch.

```
$ cd mbed-client
$ mbed releases -u
mbed-client (#31e5ce203cc0, tags: v3.0.0)
  * mbed-os-5.0-rc1 
  * mbed-os-5.0-rc2 
  * r0.5-rc4 
  ...
  * v2.2.0 
  * v2.2.1 
  * v3.0.0  <- current
```

You can use the `-a` switch to print release and revision hash pairs.

Mbed CLI recognizes stable release if the tags are in standard versioning format, such as `MAJOR[.MINOR][.PATCH][.BUILD]`, and optionally prefixed with either `v`, `r` or `mbed-os`. Unstable releases can be suffixed with any letter/number/hyphen/dot combination.

#### Updating a program

To update your program to another upstream version, go to the root folder of the program, and run:

```
$ mbed update [branch|tag|revision]
```

This fetches new revisions from the remote repository, updating the program to the specified branch, tag or revision. If you don't specify any of these, then `mbed update` updates to the latest revision of the current branch. `mbed update` performs this series of actions recursively against all dependencies in the program tree.


#### Updating a library

You can change the working directory to a library folder and use `mbed update` to update that library and its dependencies to a different revision than the one referenced in the parent program or library. This allows you to experiment with different versions of libraries/dependencies in the program tree without having to change the parent program or library.

There are three additional options that modify how unpublished local libraries are handled:

* `mbed update --clean-deps` - Update the current program or library and its dependencies, and discard all local unpublished repositories. Use this with caution because your local unpublished repositories cannot be restored unless you have a backup copy.

* `mbed update --clean-files` - Update the current program or library and its dependencies, discard local uncommitted changes and remove any untracked or ignored files. Use this with caution because your local unpublished repositories cannot be restored unless you have a backup copy.

* `mbed update --ignore` - Update the current program or library and its dependencies, and ignore any local unpublished libraries (they won't be deleted or modified, just ignored).

### Update examples

There are two main scenarios when updating:

* Update with local uncommitted changes: *dirty* update.

Run `mbed update [branch|tag|revision]`. You might have to commit or stash your changes if the source control tool (Git or Mercurial) throws an error that the update will overwrite local changes.

* Discard local uncommitted changes: *clean* update.

Run `mbed update [branch|tag|revision] --clean`

Specifying a branch to `mbed update` will only check out that branch and won't automatically merge or fast-forward to the remote/upstream branch. You can run `mbed update` to merge (fast-forward) your local branch with the latest remote branch. On Git, you can do `git pull`.

<span class="warnings">**Warning**: The `--clean` option tells Mbed CLI to update that program or library and its dependencies and discard all local changes. This action cannot be undone; use with caution.</span>

#### Combining update options

You can combine the options of the Mbed update command for the following scenarios:

* `mbed update --clean --clean-deps --clean-files` - Update the current program or library and its dependencies, remove all local unpublished libraries, discard local uncommitted changes and remove all untracked or ignored files. This wipes every single change that you made in the source tree and restores the stock layout.

* `mbed update --clean --ignore` - Update the current program or library and its dependencies, but ignore any local repositories. Mbed CLI updates whatever it can from the public repositories.

Use these with caution because your uncommitted changes and unpublished libraries cannot be restored.

## Repository caching

To minimize traffic and reduce import times, by default Mbed CLI caches repositories by storing their indexes under the Mbed CLI user config folder - typically `~/.mbed/mbed-cache/` on UNIX systems, or `%userprofile%/.mbed/mbed-cache/` on Windows systems. Compared to a fully checked out repository, indexes are significantly smaller in size and number of files and contain the whole revision history of that repository. This allows Mbed CLI to quickly create copies of previously downloaded repository indexes and pull/fetch only the latest changes from the remote repositories, therefore dramatically reducing network traffic and download times, especially for big repositories such as `mbed-os`.

You can manage the Mbed CLI caching behavior with the following subcommands:

```
mbed cache [on|off|dir <path>|ls|purge|-h|--help]
```

 * `on` - Turn repository caching on. This uses either the user specified cache directory or the default one. See "dir".
 * `off` - Turn repository caching off. Note that this doesn't purge cached repositories. See "purge".
 * `dir` - Set cache directory. Set to "default" to let Mbed CLI determine the cache directory location. Typically, this is `~/.mbed/mbed-cache/` on UNIX systems, or `%%userprofile%%/.mbed/mbed-cache/` on Windows systems.
 * `ls` - List cached repositories and their size.
 * `purge` - Purge cached repositories. Note that this doesn't turn caching off.
 * `-h` or `--help` - Print cache command options.

If no subcommand is specified to `mbed cache`, Mbed CLI prints the current cache setting (ENABLED or DISABLED) and the path to the local cache directory.

For safety reasons, Mbed CLI uses the `mbed-cache` subfolder to a user specified location. This ensures that no user files are deleted during `purge` even if the user has specified root/system folder as a cache location (for example, `mbed cache dir /` or `mbed cache dir C:\`).

**Security notice**: If you use cache location outside your user home/profile directory, then other system users might be able to access the repository cache and therefore the data of the cached repositories.

## Mbed CLI configuration

You can streamline many options in Mbed CLI with global and local configuration.

The Mbed CLI configuration syntax is:

```
mbed config [--global] <var> [value] [--unset]
```

* The **global** configuration (via `--global` option) defines the default behavior of Mbed CLI across programs unless overridden by *local* settings.
* The **local** configuration (without `--global`) is specific to the Mbed program and allows overriding of global or default Mbed CLI settings.
* If you do not specify a value, then Mbed CLI prints the value for this setting in this context.
* The `--unset` option allows you to remove a setting.
* The `--list` option allows you to list global and local configuration.

Here is a list of configuration settings and their defaults:

 * `target` - defines the default target for `compile`, `test` and `export`; an alias of `mbed target`. Default: none.
 * `toolchain` - defines the default toolchain for `compile` and `test`; can be set through `mbed toolchain`. Default: none.
 * `ARM_PATH`, `ARMC6_PATH`, `GCC_ARM_PATH`, `IAR_PATH` - defines the path to Arm Compiler 5 and 6, GCC Arm and IAR Workbench toolchains. Default: none.
 * `protocol` - defines the default protocol used for importing or cloning of programs and libraries. The possible values are `https`, `http` and `ssh`. Use `ssh` if you have generated and registered SSH keys (Public Key Authentication) with a service such as GitHub, GitLab, Bitbucket and so on. Read more about SSH keys [here](https://help.github.com/articles/generating-an-ssh-key/). Default: `https`.
 * `depth` - defines the *clone* depth for importing or cloning and applies only to *Git* repositories. Note that though this option may improve cloning speed, it may also prevent you from correctly checking out a dependency tree when the reference revision hash is older than the clone depth. Read more about shallow clones [here](https://git-scm.com/docs/git-clone). Default: none.

## Troubleshooting

### Unable to import Mercurial (mbed.org) programs or libraries.
1. Check whether you have Mercurial installed in your system path by  running `hg` in command prompt. If you're receiving "command not found" or a similar message, then you need to install Mercurial, and add it to your system path.

2. Try to clone a Mercurial repository directly. For example, `hg clone https://developer.mbed.org/teams/mbed/code/mbed_blinky/`. If you receive an error similar to `abort: error: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.:590)`, then your system certificates are out of date. You need to update your system certificates and possibly add the host certificate fingerprint of `mbed.com` and `mbed.org`. Read more about Mercurial's certificate management [here](https://www.mercurial-scm.org/wiki/CACertificates).

### Various issues when running Mbed CLI in Cygwin environment
Currently Mbed CLI is not compatible with Cygwin environment and cannot be executed inside it (https://github.com/ARMmbed/mbed-cli/issues/299).
