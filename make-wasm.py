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

def insert_mem_dump(output_dir):
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".js"):
                with open(os.path.join(root, file), 'r') as js_file:
                    jsFileName = os.path.splitext(file)[0]
                    js_code = js_file.read()
                    post_run_pos = js_code.find("postRun()")
                    if post_run_pos != -1:
                        # Find the position of the opening brace of the postRun function
                        opening_brace_pos = js_code.find("{", post_run_pos) + 1

                        # Insert the instrumentation code after the opening brace
                        instrumentation_code = f"""
    // Instrumentation code
    let nonZeroCount = 0;
    const loads = [];
    const memoryData = {{}};
    let wasmMemory = new Uint8Array(wasmExports['memory'].buffer);

    for (let i = 0; i < wasmMemory.length; i++) {{
        if (wasmMemory[i] !== 0) {{
            // console.log(i);
            nonZeroCount++;
            loads.push(i);
            memoryData[i] = wasmMemory[i];
        }}
    }}
    console.log("Number of non-zero elements in memory:", nonZeroCount);

    const result = JSON.stringify(memoryData);
    fs.writeFileSync(`./run-stats/{jsFileName}.json`, result);
    """
                        js_code = js_code[:opening_brace_pos] + instrumentation_code + js_code[opening_brace_pos:]
                        with open(os.path.join(root, file), 'w') as js_file:
                            js_file.write(js_code)

def clean(path):
    try:
        os.remove(path + "/CMakeLists.txt")
        os.remove(path + "/CMakeCache.txt")
        os.remove(path + "/cmake_install.cmake")
        os.remove(path + "/Makefile")
        shutil.rmtree(path + "/CMakeFiles")
    except OSError:
        pass

def generate(path, output_dir):
    shutil.copy(root_dir + "/CMakeLists.txt", path)
    # Invoke build via emcc to output Wasm and JS files for each test case.
    retcode = subprocess.Popen(["emcmake", "cmake", "-DOUTPUT_DIR:STRING=" + output_dir, "."], cwd=path).wait()
    if retcode != 0:
        juliet_print("error generating " + path + " - stopping")
        exit()

def make(path):
    retcode = subprocess.Popen(["make", "-j6"], cwd=path).wait()
    if retcode != 0:
        juliet_print("error making " + path + " - stopping")
        exit()

def run(CWE, output_dir, timeout):
    subprocess.Popen([root_dir + "/" + output_dir + "/wasm-run.sh", str(CWE), timeout]).wait()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="build and run Juliet test cases for targeted CWEs")
    parser.add_argument("CWEs", metavar="N", type=int, nargs="*", help="a CWE number to target")
    parser.add_argument("-c", "--clean", action="store_true", help="clean all CMake and make files for the targeted CWEs")
    parser.add_argument("-i", "--instrument", action="store_true", help="instrument the generated JS glue code with memory information")
    parser.add_argument("-g", "--generate", action="store_true", help="use CMake to generate Makefiles for the targeted CWEs")
    parser.add_argument("-m", "--make", action="store_true", help="use make to build test cases for the targeted CWES")
    parser.add_argument("-r", "--run", action="store_true", help="run tests for the targeted CWEs")
    parser.add_argument("-o", "--output-dir", action="store", default="wasm_bin", help="specify the output directory relative to the directory containing this script (default: wasm_bin)")
    parser.add_argument("-t", "--run-timeout", action="store", default=".01", type=float, help="specify the default test run timeout in seconds (type: float, default: .01)")
    args = parser.parse_args()

    args.CWEs = set(args.CWEs)

    testcases = root_dir + "/testcases"

    if not os.path.exists(testcases):
        juliet_print("no testcases directory")
        exit()

    if args.generate and not os.path.exists(root_dir + "/CMakeLists.txt"):
        juliet_print("no CMakeLists.txt")
        exit()

    if args.run and not os.path.exists(root_dir + "/wasm-run.sh"):
        juliet_print("no wasm-run.sh")
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
                    generate(path, args.output_dir)
                if args.make:
                    juliet_print("making " + path)
                    make(path)
                if args.instrument:
                    # The following is for instrumenting the JS glue code
                    insert_mem_dump(args.output_dir)
                if args.run:
                    juliet_print("running " + path)
                    run(parsed_CWE, args.output_dir, str(args.run_timeout) + "s")

    sys.exit(0)
