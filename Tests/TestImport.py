import pytest

def test_Init():
    from PyUSMC import Motors
    motors = Motors()
    
    try:
        motors.Init()
    except RuntimeError as ex:
        if str(ex) != "Error: 4294967295, b'NO Devices Found'":
            raise
    
    