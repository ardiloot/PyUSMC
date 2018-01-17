import pytest

def test_Import():
    from PyUSMC import Motors
    try:
        motors = Motors()
    except OSError:
        pass
    