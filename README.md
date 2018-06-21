# Extract GTFS

A tool to extract and modify information from GTFS transfit feed to use with
[RAPTOR algorithm](https://github.com/ducminh-phan/RAPTOR).

This tool performs the following extraction and modifition:

1. The day with the maximum number of trips will be extracted from the transit feed.

2. The trips in the transit feed will be regrouped into routes (these routes might differ from the original routes
in the transit feed) so that the following two conditions are satisfied:

    a. In a route, every trip has the same stop sequence.
    
    b. The trips of each route can be ordered so that the departure times at each stop of a trip is after that of the
    previous trip at the same stop. For example, if we organize the departure times of a route into a table as below,
    where `s[0], s[1], s[2]` are the stops, `t[0], t[1], t[2]` are the trips after being ordered, `dep[i, j]` is the
    departure time of the trip `t[i]` at stop `s[j]`, then `dep[i+1, j] >= dep[i, j]` for all `i, j`.

|        | `s[0]`      | `s[1]`      | `s[2]`      |
| ------ | ----------- | ----------- | ----------- |
| `t[0]` | `dep[0, 0]` | `dep[0, 1]` | `dep[0, 2]` |
| `t[1]` | `dep[1, 0]` | `dep[1, 1]` | `dep[1, 2]` |
| `t[2]` | `dep[2, 0]` | `dep[2, 1]` | `dep[2, 2]` |

3. The transfers graph is made transitively closed: For any two stops `u, v`, if there are transfers
`(u, v_1), (v_1, v_2),..., (v_n, v)`, then `(u, v)` is also an available transfer, with the transfer time is the
minimum sum of the tranfer times of such possible intermediate transfers.

4. The stops (trips) are relabelled, so that their ids are integers from 0 to #stops - 1 (#trips - 1). The routes are
also numbered from 0 to #routes - 1.

5. The stops are merged to the provided walking graph. There are three cases for each stop:

    a. If there is a node in the walking graph whose distance to the stop is smaller than 5 metres, then we identify
    the stop with this node. All the neighbours of the node are connected to the stop using the same distance and
    direction.
    
    b. If the distance of the closest node in the walking graph to the stop is between 5 and 100 metres, we connect the
    stop to the 5 closest nodes in the walking graph.
    
    c. If the distance of the closest node in the walking graph to the stop is larger than 100 metres, we do not add the
    stop to the walking graph.

## Setup

1. Python 3.5+

2. The additional packages can be installed using the command `pip3 install -r requirements.txt`

## Usage

The tool can be run using CLI:

```
python3 -m extract_gtfs [-h] [--no-relabel]
                        in_folder out_folder nodes_file graph_file
```

```
positional arguments:
  in_folder     The folder containing the GTFS files to extract
  out_folder    The folder to write the outout files
  nodes_file    The file containing the coordinates of the nodes of the
                walking graph
  graph_file    The file containing the edges of the walking graph

optional arguments:
  -h, --help    show this help message and exit
  --no-relabel  Do not relabel the stops and trips.
```
