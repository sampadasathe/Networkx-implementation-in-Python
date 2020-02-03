import pandas as pd
import networkx as nx
from itertools import groupby

paths_df = pd.DataFrame(columns=['path','length'])
states_network = nx.Graph()
usstates = pd.DataFrame()

def load_states(reg_filename,border_filename):
    global paths_df,states_network
    # Read the data only once
    usstates = pd.read_csv(reg_filename, header = None, usecols = [1, 3], squeeze = True, index_col = 0).sort_values(ascending=False)
    border_data = pd.read_csv(border_filename, usecols=[1], squeeze=True, dtype=str).str.split("-", expand=True)

    # Create a network using border_data
    states_network = nx.Graph()
    edges = list(border_data.itertuples(index=False,name=None))
    states_network.add_edges_from(edges)

    # Populate the globals for n = 1 case, and subsequently prep it for next value of n
    temp = pd.DataFrame(columns=['path','length'])
    temp['path'] = [[x] for x in list(usstates.index)]
    temp['length'] = 1

    paths_df = pd.concat([paths_df, temp],axis=0)
    return usstates,states_network

def new_nation_n_states(n,reg_filename,border_filename):
    global usstates,states_network,paths_df

    if n == 1:
        usstates,states_network = load_states(reg_filename,border_filename)

    max_pop = 0
    max_path = ''

    # Use this dataframe to populate paths for next iteration of n
    # Assign this value to paths_df at the end iteration for the current n.
    temp_path = pd.DataFrame(columns=['path','length'])
    temp_path_list = list()

    for path in paths_df['path'].values:
        # Each path is valid and constructed in the previous
        # iteration of n. Iterate over all the paths and:
        # 1. Find the one with maximum population
        # 2. Construct the path for next iteration using the current path
        try:
            neighbours = set()
            for state in path:
                neighbours.update(set(states_network.neighbors(state)))
            neighbours = neighbours.difference(set(path))
            for x in neighbours:
                temp = path + [x]
                temp.sort()
                temp_path_list.append(temp)

            # This is the code relevant to current iteration
            # if nx.is_connected(states_network.subgraph(path)):
            pop = usstates[list(path)].sum()
            if pop > max_pop:
                max_pop = pop
                max_path = path
        except nx.NetworkXError:
            # The path doesn't lead to a nation
            # We encountered states with no borders.
            pass

    # De duplicate the list entries.
    temp_path_list.sort()
    temp_path_list = list(k for k, _ in groupby(temp_path_list))
    temp_path['path'] = temp_path_list
    temp_path['length'] = n + 1

    paths_df = temp_path

    return tuple(max_path),max_pop
