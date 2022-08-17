@echo off

set /p MOCK_PATH=< path.config
set ENGINEOFF_FLAG_PATH=%MOCK_PATH%\engineoff.txt

echo Running ELM327-emulator in batch mode, output is saved to ``out.txt''.
echo Open it, to make sure, that Elm is running.
echo.
echo To stop, Ctrl+C.

echo while True:\n    with open(r'%ENGINEOFF_FLAG_PATH%') as f:\n        flag = f.readline()\n        if len(flag) and emulator.scenario != "engineoff":\n            emulator.scenario = "engineoff"\n            emulator.logger.debug("Control flag for engineoff received")\n        elif not len(flag) and emulator.scenario == "engineoff":\n            emulator.scenario = "car"\n            emulator.logger.debug("Control flag for engineoff received") | python -m elm -s car -b out.txt