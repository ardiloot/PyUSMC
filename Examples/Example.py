from PyUSMC import Motors
from time import sleep

if __name__ == "__main__":
    motors = Motors()
    motors.Init()
    
    m1 = motors.motor[0]
    m2 = motors.motor[1]
    print(m1.parameters)
    print(m1.state)
    print(m1.mode)
    sleep(2)
    print(m1.GetPos())
    m1.Start(m1.GetPos() + 10.0)
    m1.WaitToStop()
    print(m1.GetPos())
    
    sleep(2)
    print(m2.GetPos())
    m2.Start(m2.GetPos() + 10.0)
    m2.WaitToStop()
    print(m2.GetPos())
    
    sleep(10)
    motors.StopMotors(True)
    motors.Close()
    