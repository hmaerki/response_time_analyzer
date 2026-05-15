# Response Time Analyzer

The analyzer measures response time repeatedly and then displays the results.

**Use**

```bash
$ mpremote run response_time_analyser.py
20 1
19 2
18 45
17 128
16 2
BIN_WIDTH_S: 3.2ns
```

The program `response_time_analyser.py` runs for some time and then prints a histogram of the measured response times.

## Output format

* Histogram rows use the format `<bin_index> <count>`.
* `bin_index` is the measured-time bin.
* `count` is the number of measurements in that bin.
* `BIN_WIDTH_S` is the bin width in seconds; it may be displayed in ns for readability.

**Response Time Simulator**

To test the analyzer, run this on a second Pico:

```bash
$ mpremote run response_simulator_isr_soft.py
```

* `response_simulator_isr_soft.py` implements a MicroPython interrupt service routine using `Pin.irq` with `hard=False`.
* `response_simulator_isr_hard.py` implements a MicroPython interrupt service routine using `Pin.irq` with `hard=True`.
* `response_simulator_pio.py` implements a MicroPython PIO-based responder at full speed.

## Prerequisites

* Two Raspberry Pi Pico-class boards (RP2040 or RP2350): one analyzer board and one simulator board.
* A recent MicroPython build on both boards.
* Host connection via USB and `mpremote`.
* No required firmware pre-installed in flash; scripts are executed from the host.

## Wiring

* Connect analyzer signal `GPIO_STIMULI` to the simulator input that receives the stimulus signal.
* Connect simulator response output to analyzer signal `GPIO_RESPONSE`.
* Connect board grounds (`GND`) together.
* Use only 3.3 V logic-level GPIO signals.
* Choose concrete GPIO numbers in your scripts and keep them consistent on both boards.

## Measurement principle

Output: `GPIO_STIMULI`
Input: `GPIO_RESPONSE`

The Pico raises `GPIO_STIMULI` and waits until `GPIO_RESPONSE` goes high. The PIO measures the elapsed time with a resolution of `BIN_WIDTH_S`.

## Choosing the frequency for the PIO state machine

`machine.freq()` is typically `125_000_000` (RP2040) or `150_000_000` (RP2350), depending on board and firmware configuration.

```python
FREQ_DIVIDER = 2
BIN_WIDTH_S = FREQ_DIVIDER / machine.freq()
```

## Implementation

* MicroPython: Prepare `dict_histogram: dict[int, int]`. The key is the bin number, and the value is the number of measurements in that bin.
* MicroPython: Loop for the measurement duration:
  * MicroPython: Set `GPIO_STIMULI` to 0.
  * MicroPython: Wait until `GPIO_RESPONSE` is 0.
  * MicroPython: Start the PIO state machine.
    * PIO: Set `GPIO_STIMULI` to 1.
    * PIO: Wait until `GPIO_RESPONSE` is 1.
    * PIO: Push measured time to the FIFO.
  * MicroPython: `dict_histogram[measured_time] += 1`
* MicroPython: Print `dict_histogram`.
* MicroPython: Return.

## Limitations

* The described loop waits for GPIO state changes and does not define a timeout path; if the response signal never changes, the measurement loop can block.
* Results depend on GPIO wiring quality, board clock configuration, and simulator implementation (`isr_soft`, `isr_hard`, `pio`).
