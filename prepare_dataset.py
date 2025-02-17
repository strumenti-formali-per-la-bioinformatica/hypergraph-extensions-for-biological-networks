import torch_geometric
import torch_geometric.datasets
import matplotlib.pyplot as plt
import numpy as np
import torch_geometric.datasets
import torch_geometric.utils
from itertools import combinations
import networkx as nx
import pickle
import os.path as osp
import argparse

def parse_graph(data, score_function):
    G = nx.from_scipy_sparse_array(torch_geometric.utils.to_scipy_sparse_matrix (data.edge_index))
    cliques = [clique for clique in nx.find_cliques(G)]
    jc = np.array([sum(map(lambda i: i [2], score_function(G, list(combinations(clique, 2))))) / len(clique) for clique in cliques])
    score_mean = jc.mean()
    hyperedges = [clique for clique, score in zip(cliques, jc) if score > score_mean]
    # hyperedges = cliques
    # incidence_matrix = np.zeros((G.number_of_nodes(), len(hyperedges)))
    edge_index = np.array([
        [n for e in hyperedges for n in e],
        [i for i, e in enumerate(hyperedges) for _ in e]
    ])
    # incidence_matrix[edge_index[0], edge_index[1]] = 1
    return edge_index

def main(score_function):
    path = osp.join(osp.dirname(osp.realpath(__file__)), 'data', 'PPI')
    data_train = torch_geometric.datasets.PPI(root=path, split='train')
    pickle.dump(parse_graph(data_train, score_function), open("data/train_edge_index.pkl", "wb"))
    data_val = torch_geometric.datasets.PPI(root=path, split='val')
    pickle.dump(parse_graph(data_val, score_function), open("data/val_edge_index.pkl", "wb"))
    data_test = torch_geometric.datasets.PPI(root=path, split='test')
    pickle.dump(parse_graph(data_test, score_function), open("data/test_edge_index.pkl", "wb"))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--score_function', type=str, choices=['jc', 'aa', 'ra'], required=True)
    args = parser.parse_args()

    score_function = args.score_function

    if score_function == 'jc':
        score_function = nx.jaccard_coefficient
    elif score_function == 'aa':
        score_function = nx.adamic_adar_index
    elif score_function == 'ra':
        score_function = nx.resource_allocation_index

    main(score_function)
