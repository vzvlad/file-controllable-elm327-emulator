python-ELM
==========

A python simulator for the ELM327 OBD-II adapter. Built for testing [python-OBD](https://github.com/brendanwhitfield/python-OBD).

This simulator can process basic examples in [*python-OBD* documentation](https://python-obd.readthedocs.io/en/latest/) and reproduces a limited message flow
generated by a Toyota Auris Hybrid car, including some custom messages.

Run with:

```shell
python -m elm
```

Tested with python 3.7.

The serial port to be used by the application interfacing the simulator is displayed in the first output line. E.g.,:

    Running on /dev/pts/1

Logging is controlled through `elm.yaml` (in the current directory by default). Its path can be set through the *ELM_LOG_CFG* environment variable.