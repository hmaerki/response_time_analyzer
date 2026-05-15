"""
Response simulator using Pin.irq with hard=False (soft IRQ).
"""

import machine
import time


# Update these pins to match your wiring.
GPIO_STIMULI = "GPIO0"
GPIO_RESPONSE = "GPIO1"


stimuli = machine.Pin(GPIO_STIMULI, machine.Pin.IN, machine.Pin.PULL_UP)
response = machine.Pin(GPIO_RESPONSE, machine.Pin.OUT, value=0)


def on_stimulus(_: machine.Pin) -> None:
    response.value(1)
    time.sleep_us(1)
    response.value(0)


stimuli.irq(trigger=machine.Pin.IRQ_RISING, handler=on_stimulus, hard=False)

print("response_simulator_isr_soft running")

while True:
    response.value(0)
    pass
