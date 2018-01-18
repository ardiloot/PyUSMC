"""This is a wrapper module to control Standa 8SMC1-USBhF stepper motor
controllers (http://www.standa.lt/products/catalog/motorised_positioners?item=175)
from Python. The module requires C/C++ developement package (MicroSMC) to be
installed and USMCDLL.dll in path.

"""
import time
from ctypes import WinDLL, c_int, c_float, c_char_p, POINTER, \
    c_char, Structure, wintypes, create_string_buffer, c_size_t

__all__ = ["StepperMotorController", "RotationalStage"]

#===============================================================================
# Helper structures
#===============================================================================

class USMC_Devices(Structure):
    """Wrapper class for USMC_Devices structure.
    
    Attributes
    ----------
    NOD : int
        Number of stepper motor controllers (axes).
    Serial : list of strings
        List containing the serial numbers of all controllers.
    Version : list of string
        List containing the version number of all controllers.
    
    """
    _fields_ = [
        ("NOD", wintypes.DWORD),
        ("Serial", POINTER(c_char_p)),
        ("Version", POINTER(c_char_p)),
        ]


class _SettingsBase(Structure):
    """Helper base class for  simplifying the setting and updating the settings.
    
    Parameters
    ----------
    motor : `Motor`
        Instance of the motor whose settings are being controlled.
        
    """

    def __init__(self, motor):
        self._motor = motor
        self._controller = motor._controller
        self._dll = motor._dll
        Structure.__init__(self)
        
        self.Refresh()
        
    def Refresh(self):
        """This method updates the setting values by requesting up-to-date
        information from the controller. 
        
        """
        raise NotImplementedError()
    
    def Apply(self):
        """This method transfers the modified settings to the controller
        
        """
        raise NotImplementedError()
    
    def Set(self, **kwargs):
        """Helper function to set parameters. Sam functionality could be
        achived also by modifying the member and then calling `Apply` method. 
        
        """
        allowedKeys, _ = zip(*self._fields_)
        for key, value in kwargs.items():
            if not key in allowedKeys:
                raise Exception("No such key %s in %s" % (key, self))
            self.__setattr__(key, value)
        self.Apply()
        self.Refresh()
        
    def Get(self, variable):
        """Helper method to get latest value of `variable`. Internally calls
        `Refresh` method and then returns the value.
        
        Returns
        -------
        The value of the `variable`.
        
        """
        allowedKeys, _ = zip(*self._fields_)
        if not variable in allowedKeys:
            raise ValueError("No such key %s in %s" % (variable, self))
        self.Refresh()
        return getattr(self, variable)

    def ProcessErrorCode(self, errCode):
        self._controller.ProcessErrorCode(errCode)

    def __str__(self):
        res = ["---Settings---:"]
        for member, _ in self._fields_:
            res.append("%s = %s" % (member, getattr(self, member)))
        return "\n".join(res)


class USMC_Parameters(_SettingsBase):
    """Wrapper class for `USMC_Parameters` structure.
    
    Attributes
    ----------
        See the user manual of the controller
        http://www.standa.lt/files/usb/8SMC1-USBhF%20User%20Manual.pdf
    
    """
    _fields_ = [
        ("AccelT", c_float),
        ("DecelT", c_float),
        ("PTimeout", c_float),
        ("BTimeout1", c_float),
        ("BTimeout2", c_float),
        ("BTimeout3", c_float),
        ("BTimeout4", c_float),
        ("BTimeoutR", c_float),
        ("BTimeoutD", c_float),
        ("MinP", c_float),
        ("BTO1P", c_float),
        ("BTO2P", c_float),
        ("BTO3P", c_float),
        ("BTO4P", c_float),
        ("MaxLoft", wintypes.WORD),
        ("StartPos", wintypes.DWORD),
        ("RTDelta", wintypes.WORD),
        ("RTMinError", wintypes.WORD),
        ("MaxTemp", c_float),
        ("SynOUTP", wintypes.BYTE),
        ("LoftPeriod", c_float),
        ("EncMult", c_float),
        ("Reserved", wintypes.BYTE * 16),
        ]
    
    def Refresh(self):
        errCode = self._dll.USMC_GetParameters(self._motor.index, self)
        self.ProcessErrorCode(errCode)
        
    def Apply(self):
        errCode = self._dll.USMC_SetParameters(self._motor.index, self)
        self.ProcessErrorCode(errCode)

    
class USMC_StartParameters(_SettingsBase):
    """Wrapper class for `USMC_StartParameters` structure.
    
    Attributes
    ----------
        See the user manual of the controller
        http://www.standa.lt/files/usb/8SMC1-USBhF%20User%20Manual.pdf
    
    """
    _fields_ = [
        ("SDivisor", wintypes.BYTE),
        ("DefDir", wintypes.BOOL),
        ("LoftEn", wintypes.BOOL),
        ("SlStart", wintypes.BOOL),
        ("WSyncIN", wintypes.BOOL),
        ("SyncOUTR", wintypes.BOOL),
        ("ForceLoft", wintypes.BOOL),
        ("Reserved", wintypes.BOOL * 4),
        ]
    
    def Refresh(self):
        errCode = self._dll.USMC_GetStartParameters(self._motor.index, self)
        self.ProcessErrorCode(errCode)
        
    def Apply(self):
        pass

    
class USMC_Mode(_SettingsBase):
    """Wrapper class for `USMC_Mode` structure.
    
    Attributes
    ----------
        See the user manual of the controller
        http://www.standa.lt/files/usb/8SMC1-USBhF%20User%20Manual.pdf
    
    """
    _fields_ = [
        ("PMode", wintypes.BOOL),
        ("PReg", wintypes.BOOL),
        ("ResetD", wintypes.BOOL),
        ("EMReset", wintypes.BOOL),
        ("Tr1T", wintypes.BOOL),
        ("Tr2T", wintypes.BOOL),
        ("RotTrT", wintypes.BOOL),
        ("TrSwap", wintypes.BOOL),
        ("Tr1En", wintypes.BOOL),
        ("Tr2En", wintypes.BOOL),
        ("RotTeEn", wintypes.BOOL),
        ("RotTrOp", wintypes.BOOL),
        ("Butt1T", wintypes.BOOL),
        ("Butt2T", wintypes.BOOL),
        ("ResetRT", wintypes.BOOL),
        ("SyncOUTEn", wintypes.BOOL),
        ("SyncOUTR", wintypes.BOOL),
        ("SyncINOp", wintypes.BOOL),
        ("SyncCount", wintypes.DWORD),
        ("SyncInvert", wintypes.BOOL),
        ("EncoderEn", wintypes.BOOL),
        ("EncoderInv", wintypes.BOOL),
        ("ResBEnc", wintypes.BOOL),
        ("ResEnc", wintypes.BOOL),
        ("Reserved", wintypes.BYTE * 8),
        ]
    
    def Refresh(self):
        errCode = self._dll.USMC_GetMode(self._motor.index, self)
        self.ProcessErrorCode(errCode)
        
    def Apply(self):
        errCode = self._dll.USMC_SetMode(self._motor.index, self)
        self.ProcessErrorCode(errCode)
        
    def PowerOn(self):
        """Helper method to power on the stepper motor.
        
        """
        self.Set(ResetD = False)

    def PowerOff(self):
        """Helper method to power off the stepper motor.
        
        """
        self.Set(ResetD = True)

    def LimitSwitchEn(self, value):
        """Helper method to disable/enable limit switches.
        
        """
        self.Set(Tr1En = value, Tr2En = value)

    
class USMC_State(_SettingsBase):
    """Wrapper class for `USMC_State` structure.
    
    Attributes
    ----------
        See the user manual of the controller
        http://www.standa.lt/files/usb/8SMC1-USBhF%20User%20Manual.pdf
    
    """
    _fields_ = [
        ("CurPos", c_int),
        ("Temp", c_float),
        ("SDivisor", wintypes.BYTE),
        ("Loft", wintypes.BOOL),
        ("FullPower", wintypes.BOOL),
        ("CW_CCW", wintypes.BOOL),
        ("Power", wintypes.BOOL),
        ("FullSpeed", wintypes.BOOL),
        ("AReset", wintypes.BOOL),
        ("RUN", wintypes.BOOL),
        ("SyncIN", wintypes.BOOL),
        ("SyncOUT", wintypes.BOOL),
        ("RotTr", wintypes.BOOL),
        ("RotTrErr", wintypes.BOOL),
        ("EmReset", wintypes.BOOL),
        ("Trailer1", wintypes.BOOL),
        ("Trailer2", wintypes.BOOL),
        ("Voltage", c_float),
        ("Reserved", wintypes.BYTE * 8),
        ]
    
    def Refresh(self):
        errCode = self._dll.USMC_GetState(self._motor.index, self)
        self.ProcessErrorCode(errCode)

    def Running(self):
        """Helper method to get the state (moving or not) of the motor.
        
        """
        return self.Get("RUN")


class USMC_EncoderState(_SettingsBase):
    """Wrapper class for `USMC_EncoderState` structure.
    
    Attributes
    ----------
        See the user manual of the controller
        http://www.standa.lt/files/usb/8SMC1-USBhF%20User%20Manual.pdf
    
    """
    _fields_ = [
        ("EncoderPos", c_int),
        ("ECurPos", c_int),
        ("Reserved", wintypes.BYTE * 8),
        ]
    
    def Refresh(self):
        errCode = self._dll.USMC_GetEncoderState(self._motor.index, self)
        self.ProcessErrorCode(errCode)


class USMC_Info(_SettingsBase):
    """Wrapper class for `USMC_Info` structure.
    
    Attributes
    ----------
        See the user manual of the controller
        http://www.standa.lt/files/usb/8SMC1-USBhF%20User%20Manual.pdf
    
    """
    _fields_ = [
        ("serial", c_char * 17),
        ("dwVersion", wintypes.DWORD),
        ("DevName", c_char * 32),
        ("CurPos", c_int),
        ("DestPos", c_int),
        ("Speed", c_float),
        ("ErrState", wintypes.BOOL),
        ("Reserved", wintypes.BYTE * 16),
        ]

#===============================================================================
# Stage classes
#===============================================================================

class _StageBaseClass:
    """Helper base class to handle conversion between ticks and real units (
    degrees in case of rotational stage and millimeters in case of linear
    actuators).
    
    """
    
    def ToUSMCPos(self, value):
        """Converts units to number of stepper motor ticks.
        
        Parameters
        ----------
        value : float
            The position in units.
            
        Returns
        -------
        int
            The position of stepper motor in ticks.
             
        """
        raise NotImplementedError()

    def ToUSMCSpeed(self, value):
        """Converts speed to speed in ticks.
        
        Parameters
        ----------
        value : float
            The speed in units per second.
        
        Returns
        -------
        float
            Speed in ticks per second.
        
        """
        raise NotImplementedError()

    def FromUSMCPos(self, value):
        """Inverse of `ToUSMCPos`.
        
        Parameters
        ----------
        value : int
            Position in ticks.
            
        Returns
        -------
        float
            Position in units.
        
        """
        raise NotImplementedError()

    def GetMaxSpeed(self):
        """Returns maximum speed of the motor in ticks per second.
        
        Returns
        -------
        float
            Maximum speed (ticks/second).
        
        """
        return self.maxSpeed / self._motor.startParameters.SDivisor

class RotationalStage(_StageBaseClass):
    """This class helps to convert the angle of the rotational stage to the
    ticks of the stepper motor and the other way around.
    
    Parameters
    ----------
    motor : `Motor`
        Instance of the motor.
    degreeInTicks : float
        Number of ticks in one degree. Default 800.
    maxSpeed : float
        Maximum speed of the rotational stage (full steps per second). Default
        48.0.
    
    """
    
    def __init__(self, motor, degreeInTicks = 800.0, maxSpeed = 48.0):
        self._motor = motor
        self.degreeInTicks = degreeInTicks
        self.maxSpeed = maxSpeed  # fullsteps / sec

    def ToUSMCPos(self, angle):
        """Converts units (usually degrees) to number of stepper motor ticks.
        
        Parameters
        ----------
        angle : float
            The angle of the rotational stage.
            
        Returns
        -------
        int
            The position of stepper motor in ticks.
             
        """
        res = int(angle * self.degreeInTicks)
        return res

    def ToUSMCSpeed(self, angularSpeed):
        """Converts angular speed to speed in ticks.
        
        Parameters
        ----------
        angularSpeed : float
            The speed in degrees per second.
        
        Returns
        -------
        float
            Speed in ticks per second.
        
        """
        res = float(self.ToUSMCPos(angularSpeed)) / 8.0 * self._motor.startParameters.SDivisor
        return res

    def FromUSMCPos(self, value):
        """Inverse of `ToUSMCPos`.
        
        Parameters
        ----------
        value : int
            Position in ticks.
            
        Returns
        -------
        float
            Position in degrees.
        
        """
        res = float(value) / self.degreeInTicks 
        return res

#===============================================================================
# StepperMotorController
#===============================================================================

class StepperMotorController:
    """Main class for connecting to Standa 8SMC1-USBhF controllers. This class
    connects to USMCDLL.dll module and initializes all motors. By default, all
    motors are asuumed to be rotational stages Standa 8MR190-2, however it
    could be reconfigured by `position` attribute of the `Motor` class.
    
    Attributes
    ----------
    N : int
        Number of motors connected to PC.
    motors : list
        List of instances to `Motor` class
    
    """
    
    def __init__(self):
        # Init variables
        self.motors = []
        
        # DLL
        self._dll = WinDLL(r"USMCDLL.dll")
        
        self._dll.USMC_Init.argtypes = [USMC_Devices]
        self._dll.USMC_Init.restype = wintypes.DWORD
        
        self._dll.USMC_GetState.argtypes = [wintypes.DWORD, USMC_State]
        self._dll.USMC_GetState.restype = wintypes.DWORD
        
        self._dll.USMC_SaveParametersToFlash.argtypes = [wintypes.DWORD]
        self._dll.USMC_SaveParametersToFlash.restype = wintypes.DWORD
        
        self._dll.USMC_SetCurrentPosition.argtypes = [wintypes.DWORD, c_int]
        self._dll.USMC_SetCurrentPosition.restype = wintypes.DWORD
        
        self._dll.USMC_GetMode.argtypes = [wintypes.DWORD, USMC_Mode]
        self._dll.USMC_GetMode.restype = wintypes.DWORD
        
        self._dll.USMC_SetMode.argtypes = [wintypes.DWORD, USMC_Mode]
        self._dll.USMC_SetMode.restype = wintypes.DWORD
        
        self._dll.USMC_GetParameters.argtypes = [wintypes.DWORD, USMC_Parameters]
        self._dll.USMC_GetParameters.restype = wintypes.DWORD
        
        self._dll.USMC_SetParameters.argtypes = [wintypes.DWORD, USMC_Parameters]
        self._dll.USMC_SetParameters.restype = wintypes.DWORD
        
        self._dll.USMC_GetStartParameters.argtypes = [wintypes.DWORD, USMC_StartParameters]
        self._dll.USMC_GetStartParameters.restype = wintypes.DWORD
        
        self._dll.USMC_Start.argtypes = [wintypes.DWORD, c_int, POINTER(c_float), USMC_StartParameters]
        self._dll.USMC_Start.restype = wintypes.DWORD
        
        self._dll.USMC_Stop.argtypes = [wintypes.DWORD]
        self._dll.USMC_Stop.restype = wintypes.DWORD
        
        self._dll.USMC_GetLastErr.argtypes = [c_char_p, c_size_t]
        
        self._dll.USMC_Close.argtypes = []
        self._dll.USMC_Close.restype = wintypes.DWORD
        
        self._dll.USMC_GetEncoderState.argtypes = [wintypes.DWORD, USMC_EncoderState]
        self._dll.USMC_GetEncoderState.restype = wintypes.DWORD
        
    def Init(self):
        """Initializes all stepper motor axes. Must be called before any other
        method to populate the `motors` list. 
        
        """
        self._devices = USMC_Devices()
        errCode = self._dll.USMC_Init(self._devices)
        self.ProcessErrorCode(errCode)
        
        # Create Motor instances
        for i in range(self.N):
            self.motors.append(Motor(self, i))
                        
    def Close(self):
        """Closes connection to stepper motor controllers.
        
        """
        if len(self.motors) > 0:
            errCode = self._dll.USMC_Close()
            self.ProcessErrorCode(errCode)

    def WaitToStop(self):
        """This method blocks until all motors are stopped.
        
        """
        for m in self.motors:
            m.WaitToStop()

    def StopMotors(self, powerOff = False):
        """Stops all motors.
        
        Parameters
        ----------
        powerOff : bool
            If True, then the power of all motors will be disconnected after
            stopping. By default False.
        
        """
        for m in self.motors:
            m.Stop(powerOff)
            
    def Running(self):
        """Checks if at least one of the motor is moving.
        
        Returns
        -------
        bool
            True if at least one motor is moving.
        
        """
        for m in self.motors:
            if m.state.Running():
                return True
        return False
            
    def ProcessErrorCode(self, errCode):
        """Helper function to postprocess the error codes. If error code is not
        0, the RuntimeError is raised.
        
        """
        if errCode != 0:
            errorStr = create_string_buffer(100)
            self._dll.USMC_GetLastErr(errorStr, len(errorStr))
            raise RuntimeError("Error: %d, %s" % (errCode, errorStr.value))
        
    @property
    def N(self):
        return self._devices.NOD
      
#===============================================================================
# Motor
#===============================================================================      
            
class Motor:
    """Class for controlling single stepper motor. The conversion between the real
    units (degrees/meters) are done by stage class (`position` instance). By
    default ``RotationalStage` is asssumed. This class is usually only
    initialized by `StepperMotorController` class.
    
    Attributes
    ----------
    parameters : USMC_Parameters
    mode : USMC_Mode
    state : USMC_State
    startParameters : USMC_StartParameters
    encoderState : USMC_EncoderState
    
    """
    def __init__(self, controller, index):
        self._dll = controller._dll
        self._controller = controller
        self._index = index
        self.position = RotationalStage(self)
        
        # Settings
        self.parameters = USMC_Parameters(self)
        self.mode = USMC_Mode(self)
        self.state = USMC_State(self)
        self.startParameters = USMC_StartParameters(self)
        self.encoderState = USMC_EncoderState(self)

    def SetCurrentPosition(self, curPos):
        """Sets current position of the rotational stage. See
        http://www.standa.lt/files/usb/8SMC1-USBhF%20User%20Manual.pdf
        
        Parameters
        ----------
        curPos : float
            Desired current position of the motor.
        
        """
        errCode = self._dll.USMC_SetCurrentPosition(self.index, self.position.ToUSMCPos(curPos))
        self._controller.ProcessErrorCode(errCode)
        print("Current to set", self.position.ToUSMCPos(curPos))
        print("State", self.state.Get("CurPos"))

    def Start(self, destPos, speed = None):
        """Moves the stepper motor to `destPos` with speed `speed`. The method
        is non-blocking.
        
        Parameters
        ----------
        destPos : float
            Desired position of the motor.
        speed : float
            Maximum speed of the movement. If None (default), half of the
            maximum speed is used.
        
        """
        if speed == None:
            tmpSpeed = self.position.GetMaxSpeed() / 2
        else:
            tmpSpeed = speed
            
        if destPos == float("inf"):
            destPos = self.GetPos() + 1000.0
            
        if destPos == float("-inf"):
            destPos = self.GetPos() - 1000.0
            
        speed = c_float(self.position.ToUSMCSpeed(tmpSpeed))
        errCode = self._dll.USMC_Start(self.index, self.position.ToUSMCPos(destPos), \
            speed, self.startParameters)
        self._controller.ProcessErrorCode(errCode)

    def Stop(self, powerOff = False):
        """Stops teh movement of the motor.
        
        Parameters
        ----------
        powerOff : bool
            If True, then the power of all motors will be disconnected after
            stopping. By default False.
        
        """    
        
        errCode = self._dll.USMC_Stop(self.index)
        self._controller.ProcessErrorCode(errCode)
        
        if powerOff:
            self.mode.PowerOff()
        
    def GetPos(self):
        """Helper method to get current position of the motor.
        
        Returns
        -------
        float
            Current position of the motor.
        """
        return self.position.FromUSMCPos(self.state.Get("CurPos"))
        
    def WaitToStop(self):
        """This method blocks until all the motor is stopped.
        
        """
        time.sleep(0.05)
        while self.state.Running():
            time.sleep(0.01)

    def SaveParametersToFlash(self):
        """Saves parameters to flash. See
        http://www.standa.lt/files/usb/8SMC1-USBhF%20User%20Manual.pdf
        
        """
        errCode = self._dll.USMC_SaveParametersToFlash(self.index)
        self._controller.ProcessErrorCode(errCode)

    @property
    def serial(self):
        return self._controller._devices.Serial[self.index]
    
    @property
    def version(self):
        return self._controller._devices.Version[self.index]
    
    @property
    def index(self):
        return self._index
    
if __name__ == "__main__":
    pass
