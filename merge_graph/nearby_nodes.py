import os
import subprocess

from merge_graph.settings import config


def find_nearby_nodes(args):
    path = os.path.join('.', 'merge_graph', 'cpp')
    input_files = [os.path.join(path, file) for file in os.listdir(path)]
    output_file = os.path.join('.', 'close_nodes')
    compile_cmd = ['g++', '-std=c++11', '-Wall', '-O3'] + input_files + ['-o', output_file]

    print('\nCompiling C++...')

    proc = subprocess.run(compile_cmd)
    if proc.returncode:
        raise RuntimeError('Error occured when compiling C++ files')

    proc = subprocess.run([output_file, args.stops_file, config.nodes_file, config.graph_file])
    if proc.returncode:
        raise RuntimeError('Error occured when running compiled C++')
