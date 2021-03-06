# -*- coding: utf-8 -*-
"""Generating Article Trajectory Extensions

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Y92-NJ1gE59bYONwsXr2pnZ3H9SEBw6N
"""

import networkx as nx
import requests
import json
import matplotlib.pyplot as plt
import statistics
import pandas as pd
import pickle
import math

"""# Graph Creation Functions"""

def get_article_revisions(title, class_index):
    revisions = []
    # create a base url for the api and then a normal url which is initially
    # just a copy of it
    # The following line is what the requests call is doing, basically.
    # "http://en.wikipedia.org/w/api.php/?action=query&titles={0}&prop=revisions&rvprop=flags|timestamp|user|size|ids&rvlimit=500&format=json&continue=".format(title)
    wp_api_url = "http://en.wikipedia.org/w/api.php/"

    title_parameters = {'action' : 'query',
                  'titles' : title,
                  'prop' : 'revisions',
                  'rvprop' : 'flags|timestamp|user|size|ids',
                  'rvlimit' : 500,
                  'format' : 'json',
                  'continue' : '' }
    while True:
        # the first line open the urls but also handles unicode urls
        call = requests.get(wp_api_url, params=title_parameters)
        # call = requests.get(wp_api_url, params=list_parameters)
        api_answer = call.json()

        # get the list of pages from the json object
        pages = api_answer["query"]["pages"]

        # for every page, (there should always be only one) get its revisions:
        for page in pages.keys():
            if ('revisions' in pages[page]): #
                query_revisions = pages[page]["revisions"]

                # Append every revision to the revisions list
                for rev in query_revisions:
                    revisions.append(rev)

            else:
            # means article has been deleted
            # find a new article in class, return that article's revisions
                new_title = find_article_in_class()
                return get_article_revisions(new_title, class_index)
                # find new article

        # 'continue' tells us there's more revisions to add
        if 'continue' in api_answer:
            # replace the 'continue' parameter with the contents of the
            # api_answer dictionary.
            title_parameters.update(api_answer['continue'])
            # list_parameters.update(api_answer['continue'])
        else:
            break

    for r in revisions:
      if 'anon' in r:
        r['user'] = "Anon:" + r['user']
      if 'userhidden' in r:
        r['user'] = "Hidden"

    return (title, revisions)

def create_article_trajectory_graph(revisions):
  g = nx.DiGraph()

  for i in range(len(revisions)):
    if g.has_edge(revisions[i]['user'], revisions[i-1]['user']):
      g[revisions[i]['user']][revisions[i-1]['user']]['count'] += 1
    else:
      g.add_edge(revisions[i]['user'], revisions[i-1]['user'])
      g[revisions[i]['user']][revisions[i-1]['user']]['count'] = 1

  return g

def find_article_in_class(class_index):
    S = requests.Session()
    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS_RAND = {
        "action" : "query",
        "generator" : "random",
        "grnnamespace" : 0,
        "prop" : "pageassessments",
        "grnlimit" : 1,
        "format" : "json"
    }
    while True:
        R = S.get(url = URL, params=PARAMS_RAND)
        DATA = R.json()

        generated_pages = []
        PAGES = DATA['query']['pages']
        for page in PAGES:
            if 'pageassessments' in PAGES[page]:
                category = list(PAGES[page]['pageassessments'].keys())[0]
                ranking = PAGES[page]['pageassessments'][category]['class']
                generated_pages.append((PAGES[page]['title'], ranking))

        for page in generated_pages:
            if page[1] == classes[class_index] and (page[0] not in lsts[class_index]) and not len(lsts[class_index]) == 1000 :

                return page[0]

#titles = [item for sublist in lsts for item in sublist]
#assert(len(titles) == 6000)

#with open('./data/directed_network_dictionary.pkl', 'rb') as f:
#   directed_graphs = pickle.load(f)

# with open('./data/undirected_network_dictionary.pkl', 'rb') as f:
#    undirected_graphs = pickle.load(f)

classes = ['FA', 'GA', 'B', 'C', 'ST', 'SB']
with open('./data/class_lists.pkl', 'rb') as f:
  lsts = pickle.load(f)

for i in range(len(classes)):
    graph_dict = {}
    revision_dict = {}
    titles = lsts[i]
    for j in range(len(titles)):
        title = titles[j]
        print(i, j, title)
        #if (title not in directed_graphs or title not in undirected_graphs):
        #if (title not in directed_graphs):
        new_title, revisions = get_article_revisions(title, i)
        lsts[i][j] = new_title

        revision_dict[new_title] = revisions
        graph_dict[new_title] = create_article_trajectory_graph(revisions)
        # undirected_graphs[title] = create_article_trajectory_graph(revisions, directed=False, weighted=True)

    # possibly need to change the file paths:
    with open('./graph_dictionary_{}.pkl'.format(classes[i]), 'wb') as f:
       pickle.dump(graph_dict, f)

    with open('./revision_dictionary_{}.pkl'.format(classes[i]), 'wb') as f:
       pickle.dump(revision_dict, f)   

    with open('./article_titles_{}.pkl'.format(classes[i]), 'wb') as f:
       pickle.dump(lsts[i], f)   

with open ('./article_titles_all.pkl', 'wb') as f:
    pickle.dump(lsts, f)
