Introduction
============




.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/whimsee/CircuitPython_PMW3360/workflows/Build%20CI/badge.svg
    :target: https://github.com/whimsee/CircuitPython_PMW3360/actions
    :alt: Build Status


.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

CircuitPython library for the PMW3360 motion sensor.


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Bus Device <https://github.com/adafruit/Adafruit_CircuitPython_BusDevice>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install pmw3360

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

.. code-block:: python
    
    import PMW3360
    import board, time
    from digitalio import DigitalInOut, Direction

    sensor = PMW3360.PMW3360(board.CLK, board.MOSI, board.MISO, board.D10)

    mt_pin = DigitalInOut(board.A0)
    mt_pin.direction = Direction.INPUT

    sensor.begin()
    
    while True:
        if mt_pin.value == 0:
        print(dx)
        print(dy)
        print("")

Documentation
=============
API documentation for this library can be found on `Read the Docs <https://circuitpython-pmw3360.readthedocs.io/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/whimsee/CircuitPython_PMW3360/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
