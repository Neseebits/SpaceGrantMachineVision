from datetime import datetime

class Logger:
    logToConsole = True
    logToFile = False
    filepath = ""
    
    @classmethod
    def setLogToConsole(cls, enable):
        cls.logToConsole = enable
    
    @classmethod
    def open(cls, filepath):
        cls.logToFile = True
        if filepath == "":
            cls.logToFile = False
            return
        
        try:
            cls.filepath = filepath
            file = open(filepath, "a")
            file.write("\n\nStarting log at [" + datetime.now().strftime("%H:%M:%S") + "]\n")
            file.close()
        except IOError:
            print("ERROR: unable to log to file at: " + filepath)
            cls.logToFile = False
    
    @classmethod
    def log(cls, str):
        message = "[" + datetime.now().strftime("%H:%M:%S") + "] " + str + "\n"
        if cls.logToConsole:
            print(message, end="")
        if cls.logToFile:
            try:
                file = open(cls.filepath, "a")
                file.write(message)
                file.close()
            except IOError:
                return
    
    @classmethod
    def close(cls):
        if cls.logToFile:
            try:
                file = open(cls.filepath, "a")
                file.write("Closing log at [" + datetime.now().strftime("%H:%M:%S") + "]\n\n\n")
                file.close()
            except IOError:
                return