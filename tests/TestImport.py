import pytest

def test_Import():
    from PyUSMC import StepperMotorController
    try:
        controller = StepperMotorController()
    except OSError:
        pass
    