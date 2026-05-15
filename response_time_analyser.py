"""
Measure response-time histogram using a PIO loop counter.

Hardware setup (analyzer board):
- GPIO_STIMULI: output to simulator stimulus input
- GPIO_RESPONSE: input from simulator response output
"""

import machine
import rp2
import time


GPIO_STIMULI = "GPIO0"
GPIO_RESPONSE = "GPIO1"

MEASUREMENT_DURATION_MS = 20_000

FREQ_DIVIDER = 1
FREQ_HZ = machine.freq() // FREQ_DIVIDER


class Histogram:
    def __init__(self) -> None:
        self._histogram: dict[int, int] = {}
        self._bin_width_s: float = 1 / FREQ_HZ
        self.total_count: int = 0

    def add(self, measured_time: int) -> None:
        self.total_count += 1
        self._histogram[measured_time] = self._histogram.get(measured_time, 0) + 1

    def merge_bins(self) -> None:
        while max(self._histogram.values()) < self.total_count * 0.05:
            merged_histogram: dict[int, int] = {}
            for bin_index, count in self._histogram.items():
                merged_index = bin_index // 2
                merged_histogram[merged_index] = (
                    merged_histogram.get(merged_index, 0) + count
                )
            self._histogram = merged_histogram
            self._bin_width_s *= 2

    def print(self) -> None:
        print("# Metadata")
        print(f"bin_width_s: {self._bin_width_s * 1e9:.1f}ns")
        print(f"total_count: {self.total_count}")
        print("")
        print("# bin-index, time, count")
        for bin_index in sorted(self._histogram.keys(), reverse=True):
            bin_time_s = (bin_index + 1) * self._bin_width_s
            print(f"{bin_index:02d} {bin_time_s:2.2e}s", self._histogram[bin_index])


@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def pio_measure():
    # One measurement is started by one token written with sm.put(...).
    pull(block)
    set(pins, 1)
    set(x, 0)
    mov(x, invert(x))
    label("wait_response")
    jmp(pin, "done")
    jmp(x_dec, "wait_response")
    label("done")
    mov(isr, invert(x))
    push(block)
    set(pins, 0)


def main() -> None:
    stimuli = machine.Pin(GPIO_STIMULI, machine.Pin.OUT, value=0)
    response = machine.Pin(GPIO_RESPONSE, machine.Pin.IN, machine.Pin.PULL_UP)
    measurement_end_ms = time.ticks_add(time.ticks_ms(), MEASUREMENT_DURATION_MS)

    def wait_for_response_low() -> None:
        """Busy-wait until pin reaches level; raise on timeout."""
        while True:
            end_ms = time.ticks_add(time.ticks_ms(), 1000)
            while time.ticks_diff(end_ms, time.ticks_ms()) > 0:
                if response.value() == 0:
                    return
            print(f"waiting for GPIO_RESPONSE to become low ({end_ms})")

    sm = rp2.StateMachine(
        0,
        pio_measure,
        freq=FREQ_HZ,
        set_base=stimuli,
        jmp_pin=response,
    )
    sm.active(1)

    histogram = Histogram()

    while time.ticks_diff(measurement_end_ms, time.ticks_ms()) > 0:
        stimuli.value(0)
        wait_for_response_low()

        # Trigger one PIO measurement and read one measured bin.
        sm.put(0)
        measured_time = sm.get()
        histogram.add(measured_time)

    sm.active(0)

    histogram.merge_bins()
    histogram.print()


main()
