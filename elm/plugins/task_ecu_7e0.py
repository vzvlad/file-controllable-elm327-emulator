from os import path

from elm import EcuTasks


with open('./path.config') as inp:
    MOCK_RESPONSES_PATH = inp.readline().strip()
    
RESP_ADDRESS = "7E8" # Response sent by Engine Control Module (ECM)


class NoConvertorError(Exception):
    def __init__(self, request):
        super().__init__(
            f"Can't convert decimal value to HEX, because convertor "
            f"for request {request} is not implemented. To fix this, implement "
            f"convertor in {__file__}, in variable ``convertors''. "
            f"To do this, look for {request} in "
            f"https://en.wikipedia.org/wiki/OBD-II_PIDs "
            f"Also, don't forget to implement ``bounds'', if needed."
        )


class OutOfBoundsError(ValueError):
    def __init__(self, request, val, min_val, max_val):
        super().__init__(
            f"Response value for request {request} must be in range "
            f"{min_val}-{max_val}, but {val} found"
        )


class NonNumericValueError(ValueError):
    def __init__(self, request, val):
        super().__init__(
            f"Response value for request {request} should be "
            f"a number, however '{val}' found."
        )


# Inverse functions for ones from 
# https://en.wikipedia.org/wiki/OBD-II_PIDs#Service_01_-_Show_current_data
# 
# Each convertor returns list of up to 4 bytes, depending on PID
#TODO: move to a separate file. Don't forget to change NoConvertorError
convertors = {
    '0104': lambda val: [round(2.55 * val)],
    '0105': lambda val: [round(val + 40)],
    '0106': lambda val: [round((val + 100) * 1.28)],
    '0107': lambda val: [round((val + 100) * 1.28)],
    '0108': lambda val: [round((val + 100) * 1.28)],
    '0109': lambda val: [round((val + 100) * 1.28)],
    '010A': lambda val: [round(val / 3)],
    '010B': lambda val: [round(val)],
    '010C': lambda val: [round(4 * val) // 256, round(4 * val) % 256],
    '010D': lambda val: [round(val)],
    '010E': lambda val: [round(2 * (val + 64))],
    '010F': lambda val: [round(val + 40)],
    '0110': lambda val: [round(100 * val) // 256, round(100 * val) % 256],
    '0111': lambda val: [round(2.55 * val)],
}

# Bounds from
# https://en.wikipedia.org/wiki/OBD-II_PIDs#Service_01_-_Show_current_data
#
# Each tuple is a pair of min and max bounds
bounds = {
    '0104': (0, 100),
    '0105': (-40, 215),
    '0106': (-100, 99.2),
    '0107': (-100, 99.2),
    '0108': (-100, 99.2),
    '0109': (-100, 99.2),
    '010A': (0, 765),
    '010B': (0, 255),
    '010C': (0, 16383.75),
    '010D': (0, 255),
    '010E': (-64, 63.5),
    '010F': (-40, 215),
    '0110': (0, 655.35),
    '0111': (0, 100)
}


class Task(EcuTasks):
    def run(self, cmd, *_):
        if self.emulator.scenario == 'engineoff':
            return EcuTasks.RETURN.ANSWER("<writeln>NO DATA</writeln>")

        request = cmd[:-1]

        # File might not exist, which is OK
        maybe_mock_path = path.join(MOCK_RESPONSES_PATH, f'7e0-{request}.txt')
        try:
            with open(maybe_mock_path) as f:
                val = f.readline().strip()
        except FileNotFoundError:
            # This is fine, as some requests might not need to be mocked
            return EcuTasks.RETURN.PASSTHROUGH(cmd)
        except OSError as e:
            self.logging.error(
                f"Can't open {maybe_mock_path}: {e}. Falling back to default "
                f"response from obdDictionary."
            )
            return EcuTasks.RETURN.PASSTHROUGH(cmd)

        try:
            resp = self._construct_response(request, val)
        except (NoConvertorError, OutOfBoundsError, NonNumericValueError) as e:
            self.logging.error(
                f"Failed to construct mock-response, reason: {e} Falling "
                f"back to default response from obdDictionary."
            )
            return EcuTasks.RETURN.PASSTHROUGH(cmd)
        
        self.logging.debug(
                f"Mocking value {val} for request {request} "
                f"found in {maybe_mock_path}."
            )
        return EcuTasks.RETURN.ANSWER(resp)


    def _construct_response(self, request, val):
        """ Response is constructed in 4 steps:
        Decimal value →
        → decimal bytes →
        → payload = magic_prefix + <decimal bytes as hex> →
        → response = header + size + payload
        """
        if request not in convertors:
            raise NoConvertorError()

        try:
            #TODO: are there responses, which are non-numeric?
            dec_val = float(val)
        except ValueError:
            raise NonNumericValueError(request, dec_val)
            
        #TODO: Deduce bounds from convertors to guarantee that constructed 
        #TODO: response is correct. Don't forget to change message 
        #TODO: in NoConvertorError
        if request in bounds:
            min_val, max_val = bounds[request]
            if not (min_val <= dec_val <= max_val):
                raise OutOfBoundsError(request, val, min_val, max_val)
        else:
            self.logging.warning(
                f"Can't guarantee, that response {dec_val} for request "
                f"{request} is valid, because allowed range is unknown. Consider "
                f"adding min and max values to variable ``bounds'' in {__file__}"
            )

        dec_bytes = convertors[request](dec_val) 
        if any([0 <= byte <= 255 for byte in dec_bytes]):
            #TODO: implement byte type?
            pass
        hex_bytes = [f'{dec_byte:02X}' for dec_byte in dec_bytes]

        # Reverse-engeneered from responses in obd_message.py
        magic_prefix = ['41', request[2:4].upper()]
        payload = magic_prefix + hex_bytes
        return self.HD(RESP_ADDRESS)         \
               + self.SZ(f'0{len(payload)}') \
               + self.DT(' '.join(payload))
