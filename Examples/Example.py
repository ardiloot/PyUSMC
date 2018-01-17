"""Example code showing how to controll two rotational stages

"""

from PyUSMC import StepperMotorController
from time import sleep

if __name__ == "__main__":
    # Init controller
    controller = StepperMotorController()
    controller.Init()
    
    # Set parameters for all motors and power on
    for motor in controller.motors:
        # Configure rotational stages (Standa 8MR190-2)
        motor.position.degreeInTicks = 800.0
        motor.position.maxSpeed = 48.0
        
        # Set controller parameters
        motor.parameters.Set(
            MaxTemp = 70.0,
            AccelT = 200.0,
            DecelT = 200.0,
            BTimeout1 = 0.0,
            BTimeout2 = 1000.0,
            BTimeout3 = 1000.0,
            BTimeout4 = 1000.0,
            BTO1P = 10.0,
            BTO2P = 100.0,
            BTO3P = 400.0,
            BTO4P = 800.0,
            MinP = 500.0,
            BTimeoutR = 500.0,
            LoftPeriod = 500.0,
            RTDelta = 200,
            RTMinError = 15,
            EncMult = 2.5,
            MaxLoft = 32,
            PTimeout = 100.0,
            SynOUTP = 1)

        # Set start parameters
        motor.startParameters.Set(
            SDivisor = 8,
            DefDir = False,
            LoftEn = False,
            SlStart = False,
            WSyncIN = False,
            SyncOUTR = False,
            ForceLoft = False)
        
        # Power on
        motor.mode.PowerOn()
    
    # Helper variables
    m1 = controller.motor[0]
    m2 = controller.motor[1]
    
    # Move first motor by +10 degrees
    print("Current position of motor 1", m1.GetPos())
    m1.Start(m1.GetPos() + 10.0)
    m1.WaitToStop()
    print("Motor 1 position is now", m1.GetPos())
    sleep(2)
    
    # Set current position of the motor 2 to zero and then move the motor to
    # angle 30 deg
    print("Initial position of motor 2", m2.GetPos())
    m2.SetCurrentPosition(0.0)
    print("New position of motor 2", m2.GetPos())
    m2.Start(30.0)
    m2.WaitToStop()
    print("Final position of motor 2", m2.GetPos())
    sleep(2)
    
    # Power off motors and close connection
    controller.StopMotors(True)
    controller.Close()
    
