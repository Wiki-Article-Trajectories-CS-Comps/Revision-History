# -*- coding: utf-8 -*-
"""Generate DF from Dictionary

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1cZWQ6Aia2rB4NWmGLG8gl32B4VW1bvMd
"""

import networkx as nx
import requests
import json
import matplotlib.pyplot as plt
import statistics
import pandas as pd
import pickle
import math

""" Original Network Stats """

def get_eccentricities(g, weighted=False):
  w = none
  if (weighted):
    w = "length"
  dicts = nx.algorithms.shortest_paths.weighted.all_pairs_dijkstra_path_length(g,weight=w).values()
  return [max(d.values()) for d in dicts]

def diameter(g, weighted=False):
  if (not weighted):
    return nx.algorithms.distance_measures.diameter(g)
  dicts = nx.algorithms.shortest_paths.weighted.all_pairs_dijkstra_path_length(g,weight=w).values()
  return max([x for x in dicts.values()])

def average_closeness(g, weighted=False):
  w = none
  if (weighted):
    w = "length"
  return statistics.mean(nx.algorithms.centrality.closeness_centrality(g, distance=w).values())

def average_clustering(g, weighted=False):
  w = none
  if (weighted):
    w = "strength"
  return statistics.mean(nx.algorithms.cluster.clustering(g, weight=w).values())

def average_betweenness(g, weighted=False):
  w = none
  if (weighted):
    w = "length"
  return statistics.mean(nx.networkx.algorithms.centrality.betweenness_centrality(g, weight=w).values())

""" Network Stats 2 """
density = nx.classes.function.density

def radius(g, weighted=False):
  if (not weighted):
    return nx.algorithms.distance_measures.radius(g)
  return min(get_eccentricities(g, weighted=True))

def average_eccentricity(g, weighted=False):
  if (not weighted):
    return statistics.mean( nx.algorithms.distance_measures.eccentricity(g).values() )
  return statistics.mean(get_eccentricities(g, weighted=True))

def number_of_edges(g):
  return len(g.edges)

global_clustering = nx.algorithms.cluster.transitivity

""" Network Stats 3 """
# the following 3 stats do not accept weights or directed graphs

def smallworld_omega(g):
  return nx.algorithms.smallworld.omega(g.to_undirected())

def smallworld_sigma(g):
  return nx.algorithms.smallworld.sigma(g.to_undirected())

node_connectivity = nx.algorithms.connectivity.connectivity.node_connectivity

# this stat admits directed graphs but not edge weights
edge_connectivity = nx.algorithms.connectivity.connectivity.edge_connectivity

"""# Data Frame Constrution"""

def get_log_weighted_graph(input_graph, directed=True):
  if (directed):
    g = nx.DiGraph()
    for u, v, count in list(input_graph.edges.data("count")):
      g.add_edge(u, v, strength= math.log2(count), length= (1/(math.log2(1+count))) )

  else:
    g = nx.Graph()
    for u, v, count in list(input_graph.edges.data("count")):
      transpose_count = input_graph[v][u]["count"]
      g.add_edge(u, v, strength= math.log2(count + transpose_count), length= (1/(math.log2(1+ count + transpose_count))) )

  return g

stat_functions = {
  'diameter': diameter,
  'closeness' : average_closeness,
  'avg clustering' : average_clustering,
  'betweenness' : average_betweenness,
  'density' : density,
  'radius' : radius,
  'avg eccentricity' : average_eccentricity,
  'm' : number_of_edges,
  'global clustering' : global_clustering,
  'smallworld omega': smallworld_omega,
  'smallworld sigma': smallworld_sigma,
  'node connectivity': node_connectivity,
  'edge connectivity': edge_connectivity
}

# cannot do anything that requires the revision history
def create_article_row(index, stat_names, directed, weighted):
  title = titles[index]
  print(index, title)

  graph = graph_dict[title]
  if not directed:
    graph = graph.to_undirected()
  if (weighted):
    graph = get_log_weighted_graph(graph, directed=directed)

  return (title, *(stat_functions[stat](graph, weighted=weighted) for stat in stat_names))

def construct_dataframe(article_titles, stat_names, directed, weighted):
  return pd.DataFrame(
    [create_article_row(i, stat_names, directed, weighted) for i in range(len(article_titles))],
    columns = ['title', *stat_names] ).set_index('title')

""" Main Method Section """

with open('../data/graph_dictionary_all.pkl', 'rb') as f:
  graph_dict = pickle.load(f)

with open('../data/article_titles_all.pkl', 'rb') as f:
  class_lists = pickle.load(f)

stats1 = ['diameter', 'closeness', 'avg clustering', 'betweenness']
stats2 = ['density', 'radius', 'avg eccentricity', 'm', 'global clustering']
stats_smallworld = ['smallworld omega', 'smallworld sigma']
stats_connectivity = ['node connectivity', 'edge connectivity']
weighted_stats1 = ['diameter', 'closeness', 'avg clustering', 'betweenness', 'radius', 'avg eccentricity']

titles = [item for sublist in class_lists for item in sublist]
dir = False
weighted = True

df = construct_dataframe(titles, weighted_stats, dir, weighted)

with open('../data/df_directed_stats_log_weighted1.pkl', 'wb') as f:
  pickle.dump(df, f)
