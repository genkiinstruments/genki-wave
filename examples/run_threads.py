import time

from genki_wave.data_organization import ButtonEvent
from genki_wave.wave_threading import ReaderThreadSerial

# with WaveReaderBluetoothThread.from_address("EE:16:6F:7D:70:2A") as wave:
with ReaderThreadSerial.from_port() as wave:
    counter = 0
    last_time = None
    while counter < 50:
        counter += 1
        val = wave.queue.pop_all()
        print(len(val))
        if val:
            for v in val:
                if isinstance(v, ButtonEvent):
                    print(v)
            print(val[-1])
        curr_time = time.time()
        if last_time is None:
            last_time = curr_time
        sleep_time = 0.1 - (last_time - curr_time)
        time.sleep(sleep_time)
        # print(time.time())
        last_time = time.time()

print("Done")
