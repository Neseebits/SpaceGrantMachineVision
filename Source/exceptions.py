# Built in python libs

# Additional libs

# Custom  imports


# CAMERA EXCEPTIONS

# Raise/Raised when image is not acquired upon camera read, takes the camera number or name as parameter.
# Message is a default parameter, but can have custom message to denote context
class CameraReadError(Exception):
    def __init__(self, camera, message="Cannot read camera: "):
        self.camera = camera
        self.message = message
        super().__init__(self.message + str(camera))


# GENERAL EXCEPTIONS

# Raise/Raised when keyword interrupt occurs
# Used to restart control flow loop of robot
# Might be redunant?? OpenCV could have a matching interrupt we could have stolen, but this is made already
class KeyboardInterrupt(Exception):
    def __init__(self, key, message="Restarting control loop of program: "):
        self.key = key
        self.message = message
        super().__init__(self.message + str(key))