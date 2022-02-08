# Built in python libs

# Additional libs

# Custom imports
try:
    from logger.logger import Logger
except ImportError:
    from logger.logger import Logger

# takes an array of times and returns the average over a size
def getAvgTimeArr(arr, size):
    return round((sum(arr) / size) * 1000, 1)