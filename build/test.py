import subprocess
import os
import sys
import shutil
import _winreg

protobuf_src_path   = "../protobuf-source"
libproto_files      = []

def getAllFiles():
    return __appendAllFiles(protobuf_src_path+"/src/google/protobuf/")

def __appendAllFiles(basePath):
    listOfFile = os.listdir(basePath)
    # print(listOfFile)
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(basePath, entry)
        # If entry is a directory then get the list of files in this directory
        # print(fullPath)
        if os.path.isdir(fullPath):
            # print("11111:" + fullPath)
            __appendAllFiles(fullPath)
        elif entry.endswith(".cc"):
            # print("22222:" + fullPath)
            fullPath = fullPath.replace("\\", "/")
            libproto_files.append(fullPath)
        else:
            # print("33333:" + fullPath)
            pass

##################################################
getAllFiles()

print(libproto_files)