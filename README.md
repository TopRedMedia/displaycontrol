# Displaycontrol

python package to control projectors and displays via serial or ethernet connection.

## short track

The package could be used to control displays and projectors by all supported vendors either via serial connection or ethernet. Currently, it is under heavy development which means that more vendors will be added shortly. 

### Connections

As of now, the package only allows communication via serial interface but since the package is refactored from an already existing internal package with working ethernet connection, this will be added shortly.

### Vendors

Currently supported:

* BenQ (especially the LU9235 projector)

Planned to be integrated shortly:

* Philips professional displays
* Samsung signage displays

## Installation

Simply install via ```pip install Displaycontrol```

## Roadmap

* Version 0.0.4 - Finalize BenQ vendor for at least the BenQ LU9235 projector.
* Version 0.0.5 - Migrate existing Philips and Samsung displays vendor classes into this project.
* Version 0.1.0 - Migrate existing Ethernet connection into this project. 


