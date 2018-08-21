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

## Example

The package is designed around connections and control classes. To communicate to a projector or display, you have to new up a control class like so:

```python
# import all available vendors
from displaycontrol.vendors import * 

# Create instance of the BenQ LU9235 controller class with default settings
control = BenQLU9235()

# Print the current input channel as human readable string
print control.get_input_channel_hr() 
``` 

Since the controller is created without a connection, it uses the default ```SerialConnection``` on COM1 with 9600 baud / 8N1. You could override this like so:

```python
# import all available vendors
from displaycontrol.vendors import *

# Create a connection with custom values
connection = SerialConnection()
connection.port = '/dev/tty.usbserial' # yeah, we are on a mac
connection.baudrate = 38400 
 
# Create instance of the BenQ LU9235 controller class with overriden custom settings
control = BenQLU9235(connection)

# Print the current input channel as human readable string
print control.get_input_channel_hr() 
``` 
 
## Roadmap

* Version 0.0.4 - Finalize BenQ vendor for at least the BenQ LU9235 projector.
* Version 0.0.5 - Migrate existing Philips and Samsung displays vendor classes into this project.
* Version 0.1.0 - Migrate existing Ethernet connection into this project. 


