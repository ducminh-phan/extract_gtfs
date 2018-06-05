import subprocess


def find_close_nodes(args):
    output_file = 'close_nodes'
    compile_cmd = ['g++', '-Wall', '-O3',
                   'merge_graph/close_nodes.cpp', 'merge_graph/csv_reader.hpp',
                   '-o', output_file]

    print('Compiling C++...')

    proc = subprocess.run(compile_cmd)
    if proc.returncode:
        raise RuntimeError('Error occured when compiling C++ files')

    proc = subprocess.run([output_file, args.stops_file, args.nodes_file, args.graph_file])
    if proc.returncode:
        raise RuntimeError('Error occured when running compiled C++')
