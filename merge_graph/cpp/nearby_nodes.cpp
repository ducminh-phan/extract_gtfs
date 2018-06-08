#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <limits>
#include <map>
#include <unordered_set>
#include <vector>

#include "csv_reader.hpp"
#include "progress_bar.hpp"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

using coordinates_t = std::pair<int64_t, int64_t>;
using coor_table_t = std::map<int64_t, coordinates_t>;
using node_set_t = std::unordered_set<int64_t>;


// Parse the mapping node_id -> (node_lon, node_lat) from co files
coor_table_t parse_coordinates(const char* path) {
    std::fstream nodes_co {path};

    coor_table_t table;
    for (CSVIterator<int64_t> iter {&nodes_co, false, ' '}; iter != CSVIterator<int64_t>(); ++iter) {
        table.insert({(*iter)[1], {(*iter)[2], (*iter)[3]}});
    }

    return table;
}


// Find all the nodes in the gr files
node_set_t parse_nodes(const char* path) {
    std::fstream nodes_gr {path};

    node_set_t node_set;
    for (CSVIterator<int64_t> iter {&nodes_gr, false, ' '}; iter != CSVIterator<int64_t>(); ++iter) {
        node_set.insert((*iter)[1]);
        node_set.insert((*iter)[2]);
    }

    return node_set;
}

// Approximate the great-circle distance given the coordinates of two points.
// Reference: https://www.movable-type.co.uk/scripts/latlong.html
double distance(coordinates_t p1, coordinates_t p2) {
    static const double R {63710000};
    auto lon_1 = p1.first;
    auto lon_2 = p2.first;
    auto lat_1 = p1.second;
    auto lat_2 = p2.second;

    double phi_m = (lat_1 + lat_2) / 2e6;
    double x = (lon_2 - lon_1) * cos(M_PI * phi_m / 180);
    double y = lat_2 - lat_1;

    double res = sqrt(x * x + y * y) * R * M_PI / 180 / 1e6;
    return res;
}


void find_nearby_nodes(const std::string& tmp_folder,
                       const std::string& out_folder,
                       const coor_table_t* const stops_co,
                       const coor_table_t* const nodes_co,
                       const node_set_t* const nodes) {
    std::ofstream identical_nodes {tmp_folder + "/identical_nodes.csv"};
    std::ofstream nearby_nodes {tmp_folder + "/nearby_nodes.csv"};
    std::ofstream isolated_stops {out_folder + "/isolated_stops.csv"};

    ProgressBar prog_bar {std::cout, stops_co->size(), 80u};
    size_t count {0};

    for (const auto& stop: *stops_co) {
        auto stop_id = stop.first;
        auto stop_coor = stop.second;

        auto min_dist = std::numeric_limits<double>::max();
        int64_t closest_node_id {-1};

        // The mapping distance -> node_id, keep 10 nodes closest to the stop,
        // whose distances to the stop are between 50 and 1000.
        std::map<double, int64_t> close_nodes_map;

        for (const auto& node_id: *nodes) {
            auto node_coor = nodes_co->at(node_id);

            auto dist = distance(stop_coor, node_coor);

            if (dist < min_dist) {
                min_dist = dist;
                closest_node_id = node_id;
            }

            if (50 < dist && dist < 1000) {
                if (close_nodes_map.size() < 5) {
                    close_nodes_map.emplace(dist, node_id);
                } else if (dist < std::prev(close_nodes_map.end())->first) {
                    // Replace the last pair (distance, node_id), i.e., the pair with max distance
                    // in the map, by the current pair if the current dist is smaller than the max
                    // distance in close_nodes_map
                    close_nodes_map.erase(std::prev(close_nodes_map.end()));
                    close_nodes_map.emplace(dist, node_id);
                }
            }
        }

        if (min_dist <= 50) {
            identical_nodes << stop_id << ',' << closest_node_id << std::endl;
        } else if (!close_nodes_map.empty()) {
            for (const auto& pair: close_nodes_map) {
                nearby_nodes << stop_id << ',' << pair.second << ',' << std::llround(pair.first) << std::endl;
            }
        } else {
            isolated_stops << stop_id << std::endl;
        }

        ++count;
        prog_bar.write(count);
    }
}


int main(int argc, char* argv[]) {
    std::cout << "\nParsing the graph files..." << std::endl;

    std::string tmp_folder {argv[1]};
    std::string arg_folder {argv[2]};
    auto stops_co = parse_coordinates(argv[3]);
    auto nodes_co = parse_coordinates(argv[4]);
    auto nodes = parse_nodes(argv[5]);

    std::cout << "\nFinding the nearby nodes for each stops..." << std::endl;

    find_nearby_nodes(tmp_folder, arg_folder, &stops_co, &nodes_co, &nodes);

    return 0;
}
