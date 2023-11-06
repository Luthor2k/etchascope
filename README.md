# EtchaSkope
Supercon 2023 Badge Expansion
![](https://github.com/Luthor2k/etchaskope/blob/main/PXL_20231105_184911557.jpg)

## Two bodge wires needed!
The high speed DAQ on the badge was the wrong choice, reroute the linear pot to the RP2040 ADC. Also need to bring 3.3V to a pull up because of a routing mistake.
![](https://github.com/Luthor2k/etchaskope/blob/main/PXL_20231105_184545390.jpg)
![](https://github.com/Luthor2k/etchaskope/blob/main/PXL_20231105_184605957.jpg)

### Critical Features
* badge; round LCD so polar coordinate system
  * one rotary potentiometer
  * one linear potentiometer
* mechnically attaches to supercon badge so header isn't destroyed
* red PCB incase the case doesnt print / get designed in time
* white printed/spray painted control knobs
* flip-to-erase
  * accelerometer with available micropython library
  * simple tilt switch if $$ getting $$$
* header pass through presents same mounting points / spacing for additional expansion boards

### TODO
* component selectionDONE
* pcb designDONE
* pcb submissionDONE
* enclosure designNOTHAPPENING
* print enclosures; Knobs printed last minute in white PLA by SethK, thanks Seth!
* spray knobsNOTREQ
