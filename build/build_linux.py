import subprocess
import os
import sys
import shutil
import _winreg

clang_linux_root    = os.path.join(os.environ["LINUX_MULTIARCH_ROOT"], "x86_64-unknown-linux-gnu")
clang_exe           = clang_linux_root + "/bin/clang.exe"
clang_ar_exe        = clang_linux_root + "/bin/x86_64-unknown-linux-gnu-ar.exe"
clang_ranlib_exe    = clang_linux_root + "/bin/x86_64-unknown-linux-gnu-ranlib.exe"
clang_intermediate  = "_clang_tmp"
library_path        = "../libprotobuf/lib/linux"
library_file        = "libprotobuf.a"
protobuf_src_path   = "../protobuf-source"
libproto_files      = []
listOfFile = os.listdir(protobuf_src_path+"/src/google/protobuf/")

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
        if "test" in entry:
            pass
        elif "mock" in entry:
            pass
        elif "java" in entry:
            pass
        elif "csharp" in entry:
            pass
        elif "objectivec" in entry:
            pass
        elif "ruby" in entry:
            pass
        elif "gunzip" in entry:
            pass
        elif "field_mask_util" in entry:
            pass
        elif os.path.isdir(fullPath):
            # print("11111:" + fullPath)
            __appendAllFiles(fullPath)
        elif entry.endswith(".cc"):
            # print("22222:" + fullPath)
            fullPath = fullPath.replace("\\", "/")
            libproto_files.append(fullPath)
        else:
            # print("33333:" + fullPath)
            pass

def get_unreal_source():
    try:
        #get unreal engine builds key
        reg_key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, "SOFTWARE\\Epic Games\\Unreal Engine\\Builds")
        reg_index=0
        while(True):
            reg_name, reg_value, reg_type = _winreg.EnumValue(reg_key, reg_index)
            if(reg_type != _winreg.REG_SZ):
                continue;
            unreal_source_path = os.path.join(reg_value, "Engine/Source")
            if(os.path.exists(unreal_source_path) and os.path.exists(os.path.join(unreal_source_path, "UE4Editor.Target.cs"))):
                _winreg.CloseKey(reg_key);
                return unreal_source_path
        _winreg.CloseKey(reg_key);
        return None
    except:
        return None
    
    return ;
    
def clang_build(source_files, intermediate_path):
    for cpp_file_path in source_files:
        #output file
        cpp_file = os.path.split(cpp_file_path)[1];
        out_file = intermediate_path + "/" + os.path.splitext(cpp_file)[0] + ".o"
        cmd_line=[clang_exe, "-c", "-o", out_file]

        #stdand c++ library
        cmd_line.append("-nostdinc++")
        cmd_line.append("-I"+unreal_source+"/ThirdParty/Linux/LibCxx/include/")
        cmd_line.append("-I"+unreal_source+"/ThirdParty/Linux/LibCxx/include/c++/v1")
        cmd_line.append("-I"+clang_linux_root+"/usr/include")

        #add c++ compiler flags
        cmd_line.extend(["-Wall", "-Werror", "-funwind-tables", "-Wsequence-point", "-fno-math-errno", "-fno-rtti", "-fdiagnostics-format=msvc"])
        cmd_line.extend(["-Wdeprecated-register", "-Wno-unused-private-field", "-Wno-tautological-compare", "-Wno-undefined-bool-conversion", "-Wno-unused-local-typedef"])
        cmd_line.extend(["-Wno-inconsistent-missing-override", "-Wno-undefined-var-template", "-Wno-delete-non-virtual-dtor", "-Wno-expansion-to-defined", "-Wno-null-dereference"])
        cmd_line.extend(["-Wno-literal-conversion", "-Wno-unused-variable", "-Wno-unused-function", "-Wno-switch", "-Wno-unknown-pragmas", "-Wno-invalid-offsetof"]) 
        cmd_line.extend(["-Wno-gnu-string-literal-operator-template", "-Wshadow", "-Wno-error=shadow", "-Wno-deprecated-register"]) 
        cmd_line.extend(["-gdwarf-3", "-O2", "-fno-exceptions"]) 

        #add target define 
        cmd_line.extend(["-DPLATFORM_EXCEPTIONS_DISABLED=1", "-D_LINUX64"])
        cmd_line.append("--target=x86_64-unknown-linux-gnu")
        cmd_line.append("--sysroot=\""+ clang_linux_root +"\"")

        #c++ 11
        cmd_line.extend(["-x", "c++", "-std=c++11"]) 
        
        #google protobuf source include
        cmd_line.append("-I"+protobuf_src_path+"/src")
        #google protobuf defines
        cmd_line.append("-DGOOGLE_PROTOBUF_NO_RTTI=1")
        
        #pthread
        cmd_line.extend(["-pthread", "-DHAVE_PTHREAD=1"])

        
        #finaly, add source file
        cmd_line.append(cpp_file_path)
        print("compiler " + cpp_file + "...")
        
        #run clang++
        if(subprocess.call(cmd_line) !=0 ):
            return 1
    return 0

def clang_archive(source_files, intermediate_path):
    object_files=[]
    lib_file_path=intermediate_path+"/"+library_file
    
    for cpp_file_path in source_files:
        #object file
        cpp_file = os.path.split(cpp_file_path)[1];
        out_file = intermediate_path + "/" + os.path.splitext(cpp_file)[0] + ".o"
        object_files.append(out_file)
    
    ar_cmd_line=[clang_ar_exe,  "sru", lib_file_path]
    ar_cmd_line.extend(object_files)
    print("archive to " + library_file)
    if(subprocess.call(ar_cmd_line)!=0 or subprocess.call([clang_ranlib_exe, lib_file_path])!=0):
        return 1
    return 0

def copy_library(intermediate_path, target_path):
    source_lib_file_path = intermediate_path+"/"+library_file
    target_lib_file_path = target_path+"/"+library_file
    if(not os.path.exists(target_path)):
        os.makedirs(target_path)
    print("Copy " + source_lib_file_path + " to " + target_lib_file_path)
    shutil.copy(source_lib_file_path, target_lib_file_path)

##################################################
getAllFiles()

#check unreal source folder
unreal_source = get_unreal_source()
if unreal_source==None:
    print("unreal source folder not found!")
    sys.exit(1)

#create intermediate path
if os.path.exists(clang_intermediate):
    shutil.rmtree(clang_intermediate, True)
os.mkdir(clang_intermediate)

#build
if(clang_build(libproto_files, clang_intermediate) != 0):
    printf("compiler error!")
    sys.exit(1)

#archive
if(clang_archive(libproto_files, clang_intermediate) != 0):
    print("archive error!")
    sys.exit(1)

#copy to lib path
copy_library(clang_intermediate, library_path)

print("**Done!**")
sys.exit(0)
