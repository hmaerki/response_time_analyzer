"""
Response simulator implemented in PIO at full speed.
"""

import machine
import rp2


# Update these pins to match your wiring.
GPIO_STIMULI = "GPIO0"
GPIO_RESPONSE = "GPIO1"


@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def pio_response():
    wrap_target()
    # Wait for STIMULI to go high
    wait(1, pin, 0)
    # Set response high
    set(pins, 1)
    # Wait for STIMULI to go low
    wait(1, pin, 1)
    # Set response low
    set(pins, 0)
    wrap()


stimuli = machine.Pin(GPIO_STIMULI, machine.Pin.IN, machine.Pin.PULL_UP)
response = machine.Pin(GPIO_RESPONSE, machine.Pin.OUT)

sm = rp2.StateMachine(
    0,
    pio_response,
    freq=machine.freq(),
    in_base=stimuli,
    set_base=response,
)
sm.active(1)

print("response_simulator_pio running")

while True:
    pass
