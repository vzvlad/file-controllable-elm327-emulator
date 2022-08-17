File-controllable ELM327-emulator
=================================

Manipulate ELM327-emulator behaviour by writing to files in mock files directory.

You might want to read [ELM327-emulator README](https://github.com/Ircama/ELM327-emulator) first.

# Before first launch
In `path.config`, provide absolute path to the directory with mock files.

# Usage
From command prompt in current directory:
```
run.bat
```
Now you can do 3 things:

#### 1. Provide mock values for PIDs

To manipulate output value on PID `$PID$` of ECU `$ECU`, create file `$ECU$_$PID.txt` and flush desired value in it. Both `$ECU$` and `$PID$` are lowercase hexadecimals without spaces. For example, if file `7e0-010c.txt` content is:
```
2327
```
then engine speed will be set to 2327 rpm. This is because engine speed is controlled by PID 0x0C at Mode 0x01, hence `010c` in filename. Also, this is configured for ECU 0x7E0, hence `7e0` in filename.

More PIDs are on a dedicated [Wikipedia page.](https://en.wikipedia.org/wiki/OBD-II_PIDs)

#### 2. Provide mock values for DTCs

When `dtc.txt` is not empty, emulator will respond to "Read DTC" request with an error C0300. Don't block `dtc.txt`, because on "Clear DTC" request it will be flushed.

#### 3. Turn engine on or off

When `engineoff.txt` is not empty, emulator will behave as if engine is turned off.

# Troubleshooting
Look in `elm.log`, it might contain polite error messages, explaining, how to fix them. If log doesn't help, contact author via email: zahrevskiy@gmail.com
