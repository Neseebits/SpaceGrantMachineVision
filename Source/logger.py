from datetime import datetime
from time import sleep
import threading
from numba import jit

class Logger:
    shouldThreadJoin = False
    
    buffer = []
    
    logToConsole = True
    logToFile = False
    filepath = ""
    
    @classmethod
    def setLogToConsole(cls, enable):
        """DO NOT DIRECTLY CALL - Tells the Logger whether to print to the console

        Args:
            enable (boolean): Whether to print to the console
        """
        cls.logToConsole = enable
    
    @classmethod
    def openFile(cls, filepath):
        """DO NOT DIRECTLY CALL - Confirms that the file can be opened and prints an opening message
        
        Args:
            filepath (str): The file that the log should be written to
        """
        cls.settingsLock.acquire()
        
        cls.logToFile = True
        if filepath == "":
            cls.logToFile = False
            return
        
        cls.bufferLock.acquire()
        try:
            cls.filepath = filepath
            file = open(filepath, "a")
            file.write("\n\nStarting log at [" + datetime.now().strftime("%H:%M:%S") + "]\n")
            file.close()
        except IOError:
            print("ERROR: unable to log to file at: " + filepath)
            cls.logToFile = False
        cls.bufferLock.release()
        
        cls.settingsLock.release()
    
    @classmethod
    def close(cls):
        """DO NOT DIRECTLY CALL - If logger is open, output a closing message to the file
        """
        if cls.logToFile:
            try:
                file = open(cls.filepath, "a")
                file.write("Closing log at [" + datetime.now().strftime("%H:%M:%S") + "]\n\n\n")
                file.close()
            except IOError:
                return
    
    @classmethod
    def log(cls, message, toFile=True):
        """Adds the message to the buffer, then the logger thread logs the provided string to the console and file if it is configured to

        Args:
            message (str): The message to be output to the console and/or file
        """
        # enables .log to handle Exception types directly
        if isinstance(message, Exception):
            message = str(message)
        cls.buffer.append(message)
    
    @classmethod
    def init(cls, filepath = ""):
        """Start the logger thread, will log to file if specified
        """
        cls.settingsLock = threading.Lock()
        cls.bufferLock = threading.Lock()
        cls.shouldThreadJoin = False
        cls.logThread = threading.Thread(target=Logger.runLogThread, args=(filepath,))
        cls.logThread.start()
        return
    
    @classmethod
    def shutdown(cls):
        """Stops the logger thread
        """
        cls.settingsLock.acquire()
        cls.shouldThreadJoin = True
        cls.settingsLock.release()
        cls.logThread.join()
    
    @classmethod
    def runLogThread(cls, filepath = ""):
        """Function used by the logger thread
        """
        Logger.openFile(filepath)
        while True:
            cls.settingsLock.acquire()
            cls.bufferLock.acquire()
            if len(cls.buffer) != 0:
                
                for str in cls.buffer:
                    finalMessage = "[" + datetime.now().strftime("%H:%M:%S") + "] " + str + "\n"
                    if cls.logToConsole:
                        print(finalMessage, end="")
                    if cls.logToFile:# and toFile:
                        try:
                            file = open(cls.filepath, "a")
                            file.write(finalMessage)
                            file.close()
                        except IOError:
                            return
                        
                cls.buffer = []
            cls.bufferLock.release()
            
            if cls.shouldThreadJoin:
                break
            cls.settingsLock.release()
            
            sleep(0.1)
        
        Logger.close()