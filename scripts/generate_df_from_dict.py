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

def diameter(g, w=None):
  if (w == None):
    return nx.algorithms.distance_measures.diameter
  dicts = nx.algorithms.shortest_paths.weighted.all_pairs_dijkstra_path_length(g,weight=w).values()
  return max([x for x in dicts.values()])

def average_closeness(g, w=None):
  return statistics.mean(nx.algorithms.centrality.closeness_centrality(g, distance=w).values())

def average_clustering(g, w=None):
  return statistics.mean(nx.algorithms.cluster.clustering(g, weight=w).values())

def average_betweenness(g, w=None):
  return statistics.mean(nx.networkx.algorithms.centrality.betweenness_centrality(g, weight=w).values())

""" Network Stats 2 """
density = nx.classes.function.density

radius = nx.algorithms.distance_measures.radius

def average_eccentricity(g):
  return statistics.mean( nx.algorithms.distance_measures.eccentricity(g).values() )

def number_of_edges(g):
  return len(g.edges)

global_clustering = nx.algorithms.cluster.transitivity

"""# Data Frame Constrution"""

stat_functions = {
  'diameter': diameter,
  'closeness' : average_closeness,
  'avg clustering' : average_clustering,
  'betweenness' : average_betweenness,
  'density' : density,
  'radius' : radius,
  'avg eccentricity' : average_eccentricity,
  'm' : number_of_edges,
  'global clustering' : global_clustering
}

# cannot do anything that requires the revision history
def create_article_row(index, stat_names, directed):
  title = titles[index]
  print(index, title)

  graph = graph_dict[title]
  if not directed:
    graph = graph.to_undirected()

  return (title, *(stat_functions[stat](graph) for stat in stat_names))

def construct_dataframe(article_titles, stat_names, directed):
  return pd.DataFrame(
    [create_article_row(i, stat_names, directed) for i in range(len(article_titles))],
    columns = ['title', *stat_names] ).set_index('title')

""" Main Method Section """

with open('../data/graph_dictionary_all.pkl', 'rb') as f:
  graph_dict = pickle.load(f)

with open('../data/article_titles_all.pkl', 'rb') as f:
  class_lists = pickle.load(f)

stats1 = ['diameter', 'closeness', 'avg clustering', 'betweenness']
stats2 = ['density', 'radius', 'avg eccentricity', 'm', 'global clustering']

titles = [item for sublist in class_lists for item in sublist]
dir = True

df = construct_dataframe(titles, stats2, dir)

with open('../data/df_directed_stats2.pkl', 'wb') as f:
  pickle.dump(df, f)
