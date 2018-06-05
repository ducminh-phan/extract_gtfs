#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

#include "csv_reader.hpp"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

using coordinates_t = std::pair<uint64_t, uint64_t>;
using coor_table_t = std::unordered_map<uint64_t, coordinates_t>;
using node_set_t = std::unordered_set<uint64_t>;


// Parse the mapping node_id -> (node_lon, node_lat) from co files
coor_table_t parse_coordinates(const char* path) {
    std::fstream nodes_co {path};

    coor_table_t table;
    for (CSVIterator<uint64_t> iter {&nodes_co, false, ' '}; iter != CSVIterator<uint64_t>(); ++iter) {
        table.insert({(*iter)[1], {(*iter)[2], (*iter)[3]}});
    }

    return table;
}


// Find all the nodes in the gr files
node_set_t parse_nodes(const char* path) {
    std::fstream nodes_gr {path};

    node_set_t node_set;
    for (CSVIterator<uint64_t> iter {&nodes_gr, false, ' '}; iter != CSVIterator<uint64_t>(); ++iter) {
        node_set.insert((*iter)[1]);
        node_set.insert((*iter)[2]);
    }

    return node_set;
}


double distance(coordinates_t p1, coordinates_t p2) {
    static const double R {6371000.0};
    auto x1 = p1.first;
    auto x2 = p2.first;
    auto y1 = p1.second;
    auto y2 = p2.second;

    double phi_m = (y1 + y2) / 2 / 1000000.0;
    double x = (x2 - x1) * cos(M_PI * phi_m / 180);
    double y = y2 - y1;

    double res = sqrt(x * x + y * y) * R * M_PI / 180 / 1000000.0;
    return res;
}


int main(int argc, char* argv[]) {
    std::cout << "\nParsing the graph files..." << std::endl;

    auto stops_co = parse_coordinates(argv[1]);
    auto nodes_co = parse_coordinates(argv[2]);
    auto nodes = parse_nodes(argv[3]);

    std::cout << stops_co.size() << std::endl;
    std::cout << nodes_co.size() << std::endl;
    std::cout << nodes.size() << std::endl;

    return 0;
}
