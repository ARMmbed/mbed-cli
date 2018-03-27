
#!/usr/bin/env python2

# Copyright (c) 2016 ARM Limited, All Rights Reserved
# SPDX-License-Identifier: Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.


# pylint: disable=too-many-arguments, too-many-locals, too-many-branches, too-many-lines, line-too-long,
# pylint: disable=too-many-nested-blocks, too-many-public-methods, too-many-instance-attributes, too-many-statements
# pylint: disable=invalid-name, missing-docstring, bad-continuation

def mbed_cdc(port, reset=False, sterm=False, baudrate=9600, timeout= 10, print_term_header=True):
    try:
        from serial import Serial, SerialException
        import serial.tools.miniterm as miniterm
    except (IOError, ImportError, OSError):
        return False

    def get_instance(*args, **kwargs):
        try:
            serial_port = Serial(*args, **kwargs)
            serial_port.flush()
        except Exception as e:
            error("Unable to open serial port connection to \"%s\"" % port)
            return False
        return serial_port

    def cdc_reset(serial_instance):
        try:
            serial_instance.sendBreak()
        except:
            try:
                serial_instance.setBreak(False) # For Linux the following setBreak() is needed to release the reset signal on the target mcu.
            except:
                return False
        return True

    def cdc_term(serial_instance):
        term = miniterm.Miniterm(serial_instance, echo=True)
        term.exit_character = '\x03'
        term.menu_character = '\x14'
        term.set_rx_encoding('UTF-8')
        term.set_tx_encoding('UTF-8')

        def console_print(text):
            term.console.write('--- %s ---\n' % text)

        def input_handler():
            menu_active = False
            while term.alive:
                try:
                    c = term.console.getkey()
                except KeyboardInterrupt:
                    c = '\x03'
                if not term.alive:
                    break
                if menu_active:
                    term.handle_menu_key(c)
                    menu_active = False
                elif c == term.menu_character:
                    console_print('[MENU]')
                    menu_active = True # next char will be for menu
                elif c == '\x02' or  c == '\x12': # ctrl+b/ctrl+r sendbreak
                    console_print('[RESET]')
                    cdc_reset(term.serial)
                elif c == '\x03' or c == '\x1d': # ctrl+c/ctrl+]
                    console_print('[QUIT]')
                    term.stop()
                    term.alive = False
                    break
                elif c == '\x05': # ctrl+e
                    console_print('[ECHO %s]' % ('OFF' if term.echo else 'ON'))
                    term.echo = not term.echo
                elif c == '\x08': # ctrl+e
                    print term.get_help_text()
                elif c == '\t': # tab/ctrl+i
                    term.dump_port_settings()
                else:
                    text = c
                    for transformation in term.tx_transformations:
                        text = transformation.tx(text)
                    term.serial.write(term.tx_encoder.encode(text))
                    if term.echo:
                        echo_text = c
                        for transformation in term.tx_transformations:
                            echo_text = transformation.echo(echo_text)
                        term.console.write(echo_text)
        term.writer = input_handler

        if print_term_header:
            console_print('Terminal on {p.name} - {p.baudrate},{p.bytesize},{p.parity},{p.stopbits}'.format(p=term.serial))
            console_print('Quit: CTRL+C | Reset: CTRL+B | Echo: CTRL+E')
            console_print('Info: TAB    | Help:  Ctrl+H | Menu: Ctrl+T')

        term.start()

        try:
            term.join(True)
        except KeyboardInterrupt:
            pass
        term.join()
        term.close()

        return True


    result = False
    serial_port = get_instance(port, baudrate=baudrate, timeout=timeout)
    if serial_port:
        serial_port.reset_input_buffer()
        if reset:
            result = cdc_reset(serial_port)

        if sterm:
            if not serial_port.is_open:
                serial_port = get_instance(port, baudrate=baudrate, timeout=timeout)
            try:
                result = cdc_term(serial_port)
            except:
                pass

    return result
