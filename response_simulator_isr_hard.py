"""
Response simulator using Pin.irq with hard=True (hard IRQ).
"""

import machine
import micropython
import time

# Update these pins to match your wiring.
GPIO_STIMULI = "GPIO0"
GPIO_RESPONSE = "GPIO1"

# Keep this small for near-minimum latency.
PULSE_SPIN = 20


micropython.alloc_emergency_exception_buf(100)

stimuli = machine.Pin(GPIO_STIMULI, machine.Pin.IN, machine.Pin.PULL_UP)
response = machine.Pin(GPIO_RESPONSE, machine.Pin.OUT, value=0)


def on_stimulus(_: machine.Pin) -> None:
    response.value(1)
    time.sleep_us(1)
    response.value(0)


stimuli.irq(trigger=machine.Pin.IRQ_RISING, handler=on_stimulus, hard=True)

print("response_simulator_isr_hard running")

while True:
    pass
