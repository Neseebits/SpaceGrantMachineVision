# Built in python libs
import sys
from typing import Dict

# Additional libs
import platform

# Custom imports
try:
    from logger import Logger
except ImportError:
    from logger.logger import Logger


def logSysteminfo(Logger):
    # Log system information
    Logger.log("SYSTEM INFORMATION:")
    Logger.log(f"   Python Version: {sys.version}")
    uname = platform.uname()
    Logger.log(f"   System: {uname.system}")
    Logger.log(f"   Node Name: {uname.node}")
    Logger.log(f"   Release: {uname.release}")
    Logger.log(f"   Version: {uname.version}")
    Logger.log(f"   Machine: {uname.machine}")
    Logger.log(f"   Processor: {uname.processor}")

def logArguments(Logger, args: Dict):
    Logger.log("ARGUMENTS:")
    for arg, val in args.items():
        Logger.log(f"    {arg}: {val}")