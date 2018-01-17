import time
from ctypes import WinDLL, c_int, c_float, c_char_p, POINTER, \
    c_char, Structure, wintypes, create_string_buffer, c_size_t


class USMC_Devices(Structure):
    _fields_ = [
        ("NOD", wintypes.DWORD),
        ("Serial", POINTER(c_char_p)),
        ("Version", POINTER(c_char_p)),
        ]

class _SettingsBase(Structure):
    
    def __init__(self, motor):
        self.motor = motor
        self.dll = motor.dll
        Structure.__init__(self)
        
        self.Refresh()
        
    def Refresh(self):
        raise NotImplementedError()
    
    def Apply(self):
        raise NotImplementedError()
    
    def Set(self, **kwargs):
        allowedKeys, _ = zip(*self._fields_)
        for key, value in kwargs.iteritems():
            if not key in allowedKeys:
                raise Exception("No such key %s in %s" % (key, self))
            self.__setattr__(key, value)
        self.Apply()
        self.Refresh()
        
    def Get(self, variable):
        allowedKeys, _ = zip(*self._fields_)
        if not variable in allowedKeys:
            raise ValueError("No such key %s in %s" % (variable, self))
        self.Refresh()
        return getattr(self, variable)

    def __str__(self, *args, **kwargs):
        res = ["---Settings---:"]
        for member, _ in self._fields_:
            res.append("%s = %s" % (member, getattr(self, member)))
        return "\n".join(res)

class USMC_Parameters(_SettingsBase):
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
        self.dll.USMC_GetParameters(self.motor.index, self)
        
    def Apply(self):
        self.dll.USMC_SetParameters(self.motor.index, self)
    
class USMC_StartParameters(_SettingsBase):
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
        self.dll.USMC_GetStartParameters(self.motor.index, self)
        
    def Apply(self):
        pass
    
class USMC_Mode(_SettingsBase):
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
        self.dll.USMC_GetMode(self.motor.index, self)
        
    def Apply(self):
        self.dll.USMC_SetMode(self.motor.index, self)
        
    def PowerOn(self):
        self.Set(ResetD = False)

    def PowerOff(self):
        self.Set(ResetD = True)

    def LimitSwitchEn(self, value):
        self.Set(Tr1En=value, Tr2En=value)

    
class USMC_State(_SettingsBase):
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
        self.dll.USMC_GetState(self.motor.index, self)

    def Running(self):
        return self.Get("RUN")

class USMC_EncoderState(_SettingsBase):
    _fields_ = [
        ("EncoderPos", c_int),
        ("ECurPos", c_int),
        ("Reserved", wintypes.BYTE * 8),
        ]
    
    def Refresh(self):
        self.dll.USMC_GetEncoderState(self.motor.index, self)

class USMC_Info(_SettingsBase):
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

class RotationalStage:
    def __init__(self, motor):
        self.motor = motor
        self.unitInTicks = 800.0
        self.maxSpeed = 48.0 # fullsteps / sec

    def ToUSMCPos(self, value):
        res = int(value * self.unitInTicks)
        return res

    def ToUSMCSpeed(self, value):
        res = float(self.ToUSMCPos(value)) / 8.0 * self.motor.startParameters.SDivisor
        return res

    def FromUSMCPos(self, value):
        res = float(value) / self.unitInTicks 
        return res

    def GetMaxSpeed(self):
        return self.maxSpeed / self.motor.startParameters.SDivisor


class Motors:
    def __init__(self):
        self.motor = []
        self.N = None
        
        # DLL
        self.dll = WinDLL(r"USMCDLL.dll")
        
        self.dll.USMC_Init.argtypes = [USMC_Devices]
        self.dll.USMC_Init.restype = wintypes.DWORD
        
        self.dll.USMC_GetState.argtypes = [wintypes.DWORD, USMC_State]
        self.dll.USMC_GetState.restype = wintypes.DWORD
        
        self.dll.USMC_SaveParametersToFlash.argtypes = [wintypes.DWORD]
        self.dll.USMC_SaveParametersToFlash.restype = wintypes.DWORD
        
        self.dll.USMC_SetCurrentPosition.argtypes = [wintypes.DWORD, c_int]
        self.dll.USMC_SetCurrentPosition.restype = wintypes.DWORD
        
        self.dll.USMC_GetMode.argtypes = [wintypes.DWORD, USMC_Mode]
        self.dll.USMC_GetMode.restype = wintypes.DWORD
        
        self.dll.USMC_SetMode.argtypes = [wintypes.DWORD, USMC_Mode]
        self.dll.USMC_SetMode.restype = wintypes.DWORD
        
        self.dll.USMC_GetParameters.argtypes = [wintypes.DWORD, USMC_Parameters]
        self.dll.USMC_GetParameters.restype = wintypes.DWORD
        
        self.dll.USMC_SetParameters.argtypes = [wintypes.DWORD, USMC_Parameters]
        self.dll.USMC_SetParameters.restype = wintypes.DWORD
        
        self.dll.USMC_GetStartParameters.argtypes = [wintypes.DWORD, USMC_StartParameters]
        self.dll.USMC_GetStartParameters.restype = wintypes.DWORD
        
        self.dll.USMC_Start.argtypes = [wintypes.DWORD, c_int, POINTER(c_float), USMC_StartParameters]
        self.dll.USMC_Start.restype = wintypes.DWORD
        
        self.dll.USMC_Stop.argtypes = [wintypes.DWORD]
        self.dll.USMC_Stop.restype = wintypes.DWORD
        
        self.dll.USMC_GetLastErr.argtypes = [c_char_p, c_size_t]
        
        self.dll.USMC_Close.argtypes = []
        self.dll.USMC_Close.restype = wintypes.DWORD
        
        self.dll.USMC_GetEncoderState.argtypes = [wintypes.DWORD, USMC_EncoderState]
        self.dll.USMC_GetEncoderState.restype = wintypes.DWORD
        
    def Init(self):
        self._devices = USMC_Devices()
        errCode = self.dll.USMC_Init(self._devices)
        self.ProcessErrorCode(errCode)
        
        self.N = self._devices.NOD
        for i in range(self.N):
            self.motor.append(Motor(self, i))
            
        for m in self.motor:
            m.parameters.Set(MaxTemp=70.0, AccelT=200.0, DecelT=200.0, BTimeout1=0.0, BTimeout2=1000.0, \
                          BTimeout3=1000.0, BTimeout4=1000.0, BTO1P=10.0, BTO2P=100.0, BTO3P=400.0, BTO4P=800.0, \
                          MinP=500.0, BTimeoutR=500.0, LoftPeriod=500.0, RTDelta=200, RTMinError=15, EncMult=2.5, \
                          MaxLoft=32, PTimeout=100.0, SynOUTP=1)
            
            m.startParameters.Set(SDivisor=8, DefDir=False, LoftEn=False, SlStart=False, WSyncIN=False, \
                               SyncOUTR=False, ForceLoft=False)
            
            m.mode.PowerOn()
            
    def Close(self):
        if self.N != None:
            errCode = self.dll.USMC_Close()
            self.ProcessErrorCode(errCode)

    def WaitToStop(self):
        for m in self.motor:
            m.WaitToStop()

    def StopMotors(self, powerOff = False):
        for m in self.motor:
            m.Stop(powerOff)
            
    def Running(self):
        for m in self.motor:
            if m.state.Running():
                return True
        return False
            
    def ProcessErrorCode(self, errCode):
        if errCode != 0:
            errorStr = create_string_buffer(100)
            self.dll.USMC_GetLastErr(errorStr, len(errorStr))
            raise RuntimeError("Error: %d, %s" % (errCode, errorStr.value))
            
            
class Motor:
    def __init__(self, motors, index):
        self.dll = motors.dll
        self.motors = motors
        self.index = index
        self.position = RotationalStage(self)
        
        self.parameters = USMC_Parameters(self)
        self.mode = USMC_Mode(self)
        self.state = USMC_State(self)
        self.startParameters = USMC_StartParameters(self)
        self.encoderState = USMC_EncoderState(self)

    def SetCurrentPosition(self, position):
        self.dll.USMC_SetCurrentPosition(self.index, self.position.ToUSMCPos(position))

    def Start(self, destPos, speed=None):
        if speed == None:
            tmpSpeed = self.position.GetMaxSpeed() / 2
        else:
            tmpSpeed = speed
            
        if destPos == float("inf"):
            destPos = self.GetPos() + 1000.0
            
        if destPos == float("-inf"):
            destPos = self.GetPos() - 1000.0
            
        speed = c_float(self.position.ToUSMCSpeed(tmpSpeed))
        self.dll.USMC_Start(self.index, self.position.ToUSMCPos(destPos), \
            speed, self.startParameters)

    def Stop(self, powerOff = False):        
        if powerOff:
            self.mode.PowerOff()
        
        self.dll.USMC_Stop(self.index)
        
    def GetPos(self):
        return self.position.FromUSMCPos(self.state.Get("CurPos"))
        
    def WaitToStop(self):     
        time.sleep(0.05)
        while self.state.Running():
            time.sleep(0.01)

    def SaveParametersToFlash(self):
        self.dll.USMC_SaveParametersToFlash(self.index)

    @property
    def serial(self):
        return self.motors._devices.Serial[self.index]
    
    @property
    def version(self):
        return self.motors._devices.Version[self.index]
        
    
if __name__ == "__main__":
    pass