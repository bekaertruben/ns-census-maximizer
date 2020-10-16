Nationstates Census Maximizer
=================

This is a script that solves a nation's issues by attempting to maximise the world census scales of your choosing

## Requirements
Only tested on python 3.8 but any version 3.5 and higher should work fine.

The required modules can be installed using pip: `pip install -r requirements.txt`

## Configuration
To use one should change the `USER` and `PASSWORD` variables to the nation's login credentials. For use of the Nationstates API you should also provide contact details of some shape or form in `CONTACT`.

To configure what census scales to prioritize, modify the `weights` dictionary. This uses the census id as key and the weight as value.
