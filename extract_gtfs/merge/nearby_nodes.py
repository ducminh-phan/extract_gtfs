import os
import subprocess

from extract_gtfs.config import config


def find_nearby_nodes():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, "cpp")

    input_files = [os.path.join(path, file) for file in os.listdir(path)]
    output_file = os.path.join(".", "close_nodes")
    compile_cmd = (
        ["g++", "-std=c++11", "-Wall", "-O3"] + input_files + ["-o", output_file]
    )

    print("\nCompiling C++...")

    proc = subprocess.run(compile_cmd)
    if proc.returncode:
        raise RuntimeError("Error occured when compiling C++ files")

    proc = subprocess.run(
        [
            output_file,
            config.tmp_folder,
            config.stops_file,
            config.nodes_file,
            config.edges_file,
        ]
    )
    if proc.returncode:
        raise RuntimeError("Error occured when running compiled C++")
