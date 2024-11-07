#!/usr/bin/env python3

import argparse
import pathlib
import subprocess
import shutil
import sys
import re
import os

root_dir = str(pathlib.Path(__file__).parent)

def juliet_print(string):
    print("========== " + string + " ==========")

def clean(path):
    try:
        os.remove(path + "/CMakeLists.txt")
        os.remove(path + "/CMakeCache.txt")
        os.remove(path + "/cmake_install.cmake")
        os.remove(path + "/Makefile")
        shutil.rmtree(path + "/CMakeFiles")
    except OSError:
        pass

def generate(path, output_dir, enable_sanitizers=False):
    """
    Run CMake to generate Makefiles for the specified path.
    """
    shutil.copy(root_dir + "/CMakeLists.txt", path)
    cmake_command = ["emcmake", "cmake", "-DOUTPUT_DIR:STRING=" + output_dir, "."]
    if enable_sanitizers:
        cmake_command.insert(3, "-DENABLE_SANITIZERS=ON")  # Enable sanitizers

    retcode = subprocess.Popen(cmake_command, cwd=path).wait()
    if retcode != 0:
        juliet_print("error generating " + path + " - stopping")
        exit()

def compile_with_sanitizers(path):
    retcode = subprocess.Popen(["make", "-j6"], cwd=path).wait()
    if retcode != 0:
        juliet_print("error making " + path + " - stopping")
        exit()

def run_test_case(js_file, log_file):
    """
    Executes the JavaScript file in Node and captures its output in a log file.
    """
    with open(log_file, "w") as log:
        result = subprocess.run(["node", js_file], stdout=log, stderr=log)
        return result.returncode
    
def find_control_flow_violations(log_directory):
    """
    Filters log files to identify cases with control-flow or data corruption violations.
    """
    applicable_cases = []
    keywords = ["control flow integrity violation", "invalid pointer", "out-of-bounds pointer"]

    for log_file in os.listdir(log_directory):
        log_path = os.path.join(log_directory, log_file)
        with open(log_path, 'r') as f:
            content = f.read()
            if any(keyword in content for keyword in keywords):
                applicable_cases.append(log_file.replace(".log", ""))
    return applicable_cases

def process_test_cases(source_directory, log_directory, output_directory):
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for subdir in os.listdir(source_directory):
        match = re.search("^CWE(\d+)", subdir)
        if match:
            path = os.path.join(source_directory, subdir)
            juliet_print("Running test cases in " + path)

            # Find all JavaScript files in the output directory that correspond to each CWE
            for root, dirs, files in os.walk(os.path.join(output_directory, subdir)):
                for file in files:
                    if file.endswith(".js") and "-bad" in file:  # Ensure we only run "bad" cases
                        js_file = os.path.join(root, file)
                        log_file = os.path.join(log_directory, f"{file}.log")
                        juliet_print(f"Running {js_file} and capturing output in {log_file}")
                        run_test_case(js_file, log_file)

    print("Filtering logs for control flow and data corruption violations...")
    applicable_cases = find_control_flow_violations(log_directory)
    print("Test cases with potential control flow or data corruption:", applicable_cases)
    return applicable_cases

def make(path):
    retcode = subprocess.Popen(["make", "-j6"], cwd=path).wait()
    if retcode != 0:
        juliet_print("error making " + path + " - stopping")
        exit()
    _ = subprocess.Popen(["npm", "install", "ws"], cwd=path).wait()

# def run(CWE, output_dir, timeout):
#     subprocess.Popen([root_dir + "/" + output_dir + "/wasm-run.sh", str(CWE), timeout]).wait()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build and run Juliet test cases for targeted CWEs")
    parser.add_argument("CWEs", metavar="N", type=int, nargs="*", help="a CWE number to target")
    parser.add_argument("-c", "--clean", action="store_true", help="clean all CMake and make files for the targeted CWEs")
    parser.add_argument("-g", "--generate", action="store_true", help="use CMake to generate Makefiles for the targeted CWEs")
    parser.add_argument("-m", "--make", action="store_true", help="use make to build test cases for the targeted CWES")
    parser.add_argument("-r", "--run", action="store_true", help="Run tests for the targeted CWEs")
    parser.add_argument("-s", "--sanitizers", action="store_true", help="enable sanitizers for AddressSanitizer, and UBSan")
    parser.add_argument("-o", "--output-dir", action="store", default="wasm_bin", help="specify the output directory")
    
    args = parser.parse_args()
    args.CWEs = set(args.CWEs)

    testcases = os.path.join(root_dir, "testcases")

    if not os.path.exists(testcases):
        juliet_print("no testcases directory")
        exit()

    if args.generate and not os.path.exists(root_dir + "/CMakeLists.txt"):
        juliet_print("no CMakeLists.txt")
        exit()

    for subdir in os.listdir(testcases):
        match = re.search("^CWE(\d+)", subdir)
        if match != None:
            parsed_CWE = int(match.group(1))
            if (parsed_CWE in args.CWEs):
                path = testcases + "/" + subdir
                if args.clean:
                    juliet_print("cleaning " + path)
                    clean(path)
                if args.generate:
                    juliet_print("generating " + path)
                    generate(path, args.output_dir, enable_sanitizers=args.sanitizers)
                if args.make:
                    juliet_print("making " + path)
                    make(path)

    # Only call process_test_cases if --run was specified
    if args.run:
        applicable_cases = process_test_cases(testcases, args.log_dir, args.output_dir)
        print("Applicable cases:", applicable_cases)

    sys.exit(0)
