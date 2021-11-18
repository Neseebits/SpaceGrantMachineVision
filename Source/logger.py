from datetime import datetime

class Logger:
    logToConsole = True
    logToFile = False
    filepath = ""
    
    @classmethod
    def setLogToConsole(cls, enable):
        """Tells the Logger whether to print to the console

        Args:
            enable (boolean): Whether to print to the console
        """
        cls.logToConsole = enable
    
    @classmethod
    def open(cls, filepath):
        """Confirms that the file can be opened and prints an opening message

        Args:
            filepath (str): The file that the log should be written to
        """
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
    def log(cls, message, toFile=True):
        """Logs the provided string to the console and file if it is configured to

        Args:
            message (str): The message to be output to the console and/or file
        """
        finalMessage = "[" + datetime.now().strftime("%H:%M:%S") + "] " + message + "\n"
        if cls.logToConsole:
            print(finalMessage, end="")
        if cls.logToFile and toFile:
            try:
                file = open(cls.filepath, "a")
                file.write(finalMessage)
                file.close()
            except IOError:
                return
    
    @classmethod
    def close(cls):
        """If logger is open, output a closing message to the file
        """
        if cls.logToFile:
            try:
                file = open(cls.filepath, "a")
                file.write("Closing log at [" + datetime.now().strftime("%H:%M:%S") + "]\n\n\n")
                file.close()
            except IOError:
                return
