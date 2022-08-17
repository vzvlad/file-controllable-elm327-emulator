from os import path

from elm import EcuTasks


with open('./path.config') as inp:
    MOCK_RESPONSES_PATH = inp.readline().strip()

DTC_FLAG_PATH = path.join(MOCK_RESPONSES_PATH, "dtc.txt")
RESP_ADDRESS = "7E8" # Response sent by Engine Control Module (ECM)


class Task(EcuTasks):
    def run(self, cmd, *_):
        if cmd not in ['03', '04']:
            #TODO: warning
            return EcuTasks.RETURN.PASSTHROUGH(cmd)

        if self.emulator.scenario == 'engineoff':
            return EcuTasks.RETURN.ANSWER("<writeln>NO DATA</writeln>")

        if cmd == '03':
            return self.process_read_dtc(cmd)
        elif cmd == '04':
            return self.process_clear_dtc(cmd)

    def process_read_dtc(self, cmd):
        # File might not exist, which is OK
        try:
            with open(DTC_FLAG_PATH) as f:
                val = f.readline()
        except FileNotFoundError:
            #TODO: logging.debug
            return EcuTasks.RETURN.PASSTHROUGH(cmd)
        except OSError as e:
            self.logging.error(
                f"Can't open {DTC_FLAG_PATH}: {e}. Falling back to default "
                f"response from obdDictionary."
            )
            return EcuTasks.RETURN.PASSTHROUGH(cmd)

        if not len(val):
            return EcuTasks.RETURN.PASSTHROUGH(cmd)

        self.logging.debug(
            f'Mocking DTC, because flag is set in {DTC_FLAG_PATH}'
        )

        return EcuTasks.RETURN.ANSWER(
            self.HD(RESP_ADDRESS) + self.SZ('07') + self.DT('43 01 43 00 00 00 00')
        )

    def process_clear_dtc(self, cmd):
        # File might not exist, which is OK
        try:
            open(DTC_FLAG_PATH, 'w').close() # CLear file
        except FileNotFoundError:
            #TODO: logging.warning
            return EcuTasks.RETURN.PASSTHROUGH(cmd)
        except OSError as e:
            self.logging.error(
                f"Can't open {DTC_FLAG_PATH}: {e}. Falling back to default "
                f"response from obdDictionary."
            )
            return EcuTasks.RETURN.PASSTHROUGH(cmd)

        self.logging.debug(
            f'Flag in {DTC_FLAG_PATH} unset'
        )

        return EcuTasks.RETURN.PASSTHROUGH(cmd)
