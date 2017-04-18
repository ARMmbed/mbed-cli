# Install Guide

## System-wide Installation (root)

- Copy or link the bash completion script, `mbed`,  into your `/etc/bash_completion.d` or `/usr/local/etc/bash_completion.d` directory.
- Reopen terminal

## Local Installation

- `mkdir ~/.bash_completion.d && cp mbed ~/.bash_completion.d/`
- `echo "source ~/.bash_completion.d/mbed" >> ~/.bash_profile`
- logout and login

