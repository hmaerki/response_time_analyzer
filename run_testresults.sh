#
# Connect to picos and connect as in README.md
#
# run this script to measure and update the diagram
#
set -euox pipefail

mpremote a1 reset
sleep 1
mpremote a1 run response_simulator_isr_hard.py
mpremote a0 run response_time_analyser.py > testresults/response_simulator_isr_hard.txt

mpremote a1 reset
sleep 1
mpremote a1 run response_simulator_isr_soft.py
mpremote a0 run response_time_analyser.py > testresults/response_simulator_isr_soft.txt

mpremote a1 reset
sleep 1
mpremote a1 run response_simulator_pio.py
mpremote a0 run response_time_analyser.py > testresults/response_simulator_pio.txt

cd testresults
python draw_diagrams.py