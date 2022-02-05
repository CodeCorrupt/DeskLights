import atexit
from colorsys import rgb_to_hls
import colour
import time
import typing
import serial

SERIAL_PORT = '/dev/cu.usbmodem22301'
SERIAL_BAUDRATE = 57600
SERIAL_TIMEOUT = 1
FPS = 20

RED = [255, 0, 0, 0]
GREEN = [0, 255, 0, 0]
BLUE = [0, 0, 255, 0]
WHITE = [0, 0, 0, 255]


class Pixel():
    _start_marker = "|"

    def __init__(self, i: int, r: int, g: int, b: int, w: int) -> None:
        self.i = i
        self.r = r
        self.g = g
        self.b = b
        self.w = w

    def __str__(self) -> str:
        return f'{self.i}.{self.r},{self.g},{self.b},{self.w}\n'

    def encode(self) -> bytes:
        str_repr = self._start_marker + str(self)
        return bytes(str_repr, 'utf-8')


class Animation():
    def __init__(self, num_pixels: int) -> None:
        self.num_pixels = num_pixels
        self.frame_counter = 0

    def next_frame(self) -> typing.List[Pixel]:
        XYZ = [0.21638819, 0.12570000, 0.03847493]
        illuminant_XYZ = [0.34570, 0.35850]
        illuminant_RGB = [0.31270, 0.32900]
        chromatic_adaptation_transform = 'Bradford'
        matrix_XYZ_to_RGB = [
            [3.24062548, -1.53720797, -0.49862860],
            [-0.96893071, 1.87575606, 0.04151752],
            [0.05571012, -0.20402105, 1.05699594]
        ]
        c = colour.XYZ_to_RGB(
            XYZ,
            illuminant_XYZ,
            illuminant_RGB,
            matrix_XYZ_to_RGB,
            chromatic_adaptation_transform
        )
        pixels = [
            Pixel(
                i, c[0] * 255, c[1] * 255, c[2] * 255, 0
            ) for i in range(self.num_pixels)
        ]
        self.frame_counter += 1
        return pixels


class LightShow():
    def __init__(self, port: int = None, baudrate: int = None, timeout: float = None) -> None:
        try:
            self.arduino = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout
            )
        except IOError:
            print("Invalid comm port!")
            raise

    def print_metrics(self, fps_last_100: typing.List[int], fps_last_100_i: int) -> None:
        fps_avg_100 = (sum(fps_last_100) / len(fps_last_100))
        print("\033c\033[%d;%dH" % (2, 2))
        print(f"FPS        : {fps_last_100[fps_last_100_i]: 3.2f}")
        print(f"FPS AVG-100: {fps_avg_100: 3.2f}")

    def main(self) -> None:
        print(f"Starting show on: {self.arduino.name}")
        animation = Animation(5)

        # Timing shit
        start_time = 0
        end_time = 0
        fps_last_100 = [FPS for _ in range(100)]
        fps_last_100_i = 0
        while True:
            # Timing shit
            end_time = time.perf_counter_ns()
            elapsed_time = (end_time - start_time) / 1_000_000_000
            if elapsed_time < (1 / FPS):
                sleep_time = (1 / FPS) - elapsed_time
                elapsed_time += sleep_time
                time.sleep(sleep_time)
            start_time = time.perf_counter_ns()
            fps_last_100[fps_last_100_i] = 1 / elapsed_time
            self.print_metrics(fps_last_100, fps_last_100_i)
            fps_last_100_i = (fps_last_100_i + 1) % 100

            # Run and snow frame
            frame = animation.next_frame()
            for p in frame:
                self.arduino.write(p.encode())
            self.arduino.flush()

    def on_exit(self) -> None:
        print("Exiting gracefully 🥰")
        self.arduino.close()


if __name__ == "__main__":
    ls = LightShow(
        port=SERIAL_PORT,
        baudrate=SERIAL_BAUDRATE,
        timeout=SERIAL_TIMEOUT
    )
    atexit.register(ls.on_exit)
    ls.main()
