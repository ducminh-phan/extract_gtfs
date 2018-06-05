import os
import subprocess


def find_close_nodes(args):
    path = os.path.join('.', 'merge_graph', 'cpp')
    input_files = [os.path.join(path, file) for file in os.listdir(path)]
    output_file = 'close_nodes'
    compile_cmd = ['g++', '-std=c++11', '-Wall', '-O3'] + input_files + ['-o', output_file]

    print('Compiling C++...')

    proc = subprocess.run(compile_cmd)
    if proc.returncode:
        raise RuntimeError('Error occured when compiling C++ files')

    proc = subprocess.run([output_file, args.stops_file, args.nodes_file, args.graph_file])
    if proc.returncode:
        raise RuntimeError('Error occured when running compiled C++')
