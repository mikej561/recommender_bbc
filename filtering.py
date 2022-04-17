from sklearn.neighbors import NearestNeighbors
import pandas as pd
import numpy as np
import process as p
import pickle
import streamlit as st


def predict_rating(user_id, ISBN, neighbours, df):
    
    if ISBN not in neighbours:
        print("no data")
        
    neighbours = neighbours[ISBN]
    
    nn = neighbours['nn']
    dist = neighbours['dist']
    
    numerator = 0
    denominator = 0
    
    for i in range(0, len(nn)):
        
        isbn = nn[i]
        user_rating = df.loc[isbn, str(user_id)]
            
        numerator += user_rating * dist[i]
        denominator += dist[i]
            
    if denominator > 0:
        
        return numerator / denominator
    
    else: 
        
        return 0


def filter_items(df, num_users, num_nbhd, user, k): 
    knn = NearestNeighbors(metric='cosine', algorithm='brute')


    temp = df.iloc[:, 0:num_users]
    noise = np.random.normal(0, 0.1, temp.shape) # add noise to the data to simulate implicit feedback - implicit feedback
    temp = temp + noise
    knn.fit(temp.values)

    distances, indices = knn.kneighbors(temp.values, n_neighbors = num_nbhd)
    neighbours = {}
    for i in range(0, len(indices)):
        nn = indices[i]
        dist = distances[i]    
        e = nn[0]
        tep = temp.index[e]  
        neighbours[tep] = {"nn": [temp.index[n] for n in nn[1:]], "dist": [1 - x for x in dist[1:]]}

    all_shows = temp.index.tolist()
    res = {"preds":[], "shows":[], "label" : []}
    labels = st.session_state["pickle"][st.session_state["cmin"] - 4]
    counter = 0
    for s in all_shows:
        pr = predict_rating(user, s, neighbours, temp)
        
        res["shows"].append(s)
        res["preds"].append(pr)
        res["label"].append(labels[counter])
        counter += 1 
    data = pd.DataFrame(res).sort_values(by = ["preds"])  
    return data
