import streamlit as st 
import sidebar as s
import pandas as pd
from random import random, randint
import filtering as f
import template as t
import utils as u
import process as p
import numpy as np 
import pickle
import sklearn
import math

st.set_page_config(layout="wide")

if 'start' not in st.session_state:
    st.session_state['start'] = True
    st.session_state["reg"] = False
    st.session_state["logged_in"] = False
    st.session_state["users_data"] = pd.read_csv("data/users.csv")
    st.session_state["watched_data"] = pd.read_csv("data/watched_data.csv")
    st.session_state["buffer_evaluation"] = []
    st.session_state["counter"] = -1
    st.session_state["num_users"] = len(st.session_state["users_data"])
    st.session_state["num_nbhd"] = 5
    st.session_state["need_filtering"] = False
    st.session_state['to_select'] = -1
    st.session_state["flag_chosen"] = False
    st.session_state["cmin"] = 5
    st.session_state["pmode"] = False
    st.session_state["flags"] = {"diversity":False, "transparency":False, "autonomy":False, "utility":False, "privacy":False}
    with open('clusters.pickle',"rb") as ft:
        st.session_state["pickle"] = pickle.load(ft)
    st.session_state["ratings"] = []
    st.session_state["flag_slider"] = True
    st.session_state["flag_shuffle"] = False

s.authenticate()

def change_clusters():
    num_min = st.session_state.num_cls
    st.session_state["cmin"] = num_min
    
    labels = st.session_state["pickle"][num_min - 4]
    st.session_state["tips"] = st.session_state["tips"].sort_values(by = ["shows"])
    st.session_state["tips"]["label"] = labels
    st.session_state["tips"] = st.session_state["tips"].sort_values(by = ["preds"])
    l =  st.session_state["tips"].loc[st.session_state["tips"].index == st.session_state["film_index"], "label"].item()
    p =  st.session_state["tips"].loc[st.session_state["tips"].index == st.session_state["film_index"], "preds"].item()
    st.session_state["info"] = [str(l), str(p)] 

def get_rmse(l):
    actual = []
    predicted = []
    for vals in l:
        actual.append(vals[0])
        predicted.append(vals[1])

    mse = sklearn.metrics.mean_squared_error(actual, predicted)

    rmse = math.sqrt(mse)
    return rmse

def update_pmode():
    if st.session_state["pmode"]:
        st.session_state["pmode"] = False
    else:
        st.session_state["pmode"] = True
def shuffle_mode():
    st.session_state["flag_shuffle"] = True

def update_ratings():
    st.session_state["ratings"].append([float(st.session_state["rate_movie"]), float(st.session_state["info"][1])])
    
if st.session_state["logged_in"]:
    if st.session_state["counter"] > -1:
        pass
    if st.session_state["need_filtering"]:
        st.session_state["tips"] = f.filter_items(st.session_state["watched_data"],st.session_state["num_users"], st.session_state["num_nbhd"], st.session_state['id'], st.session_state["cmin"]) 
        st.session_state["need_filtering"] = False
   
    temp = st.session_state["watched_data"]
    
    buttons, cover, info = st.columns([1,1,1])
    with buttons:
        if st.session_state["flags"]["utility"] and not st.session_state["pmode"]:
            x = st.slider('Rate the movie!',1,5, key = "rate_movie", on_change = update_ratings, disabled = st.session_state["flag_slider"])
            if len(st.session_state["ratings"]) > 0 and ("info" in st.session_state):
                st.caption("Current RMSE: " + str(round(get_rmse(st.session_state["ratings"]), 2)))
        if st.session_state["flags"]["privacy"]:
            st.button("Turn on/off privacy mode", on_click = update_pmode)
            st.caption("Privacy mode: " + str(st.session_state["pmode"]))
            if st.session_state["pmode"]:
                st.caption("We do not currently gather your viewing history and ratings.")
    with info:
        if st.session_state["flags"]["autonomy"]:
            st.slider("Choose number of clusters", value=(st.session_state["cmin"]), min_value = 4, max_value = 10, on_change = change_clusters, key = "num_cls")
            st.button("Shuffle me", on_click = shuffle_mode)
        else:
            st.caption("No autonomy features present for you")

    df = st.session_state["tips"].loc[st.session_state["tips"].preds >= 1, :]
    if "cover" in st.session_state:
        with cover:
            film = st.session_state["watched_data"].loc[st.session_state["cover"] == st.session_state["watched_data"].description]
            st.session_state["film_index"] = film.index[0]
            st.image(film['image'].item().replace("{recipe}", "352x198"))
            st.markdown(str(film['title'].item()))
            st.markdown("Label: " + st.session_state["info"][0])
            st.markdown("Predicted rating: " + str(round(float(st.session_state["info"][1]), 2)))
    else:
        with cover:
            film = st.session_state["watched_data"].loc[st.session_state["watched_data"].index == df.index[0],:]
            st.session_state["film_index"] = df.index[0]
            st.image(film['image'].item().replace("{recipe}", "352x198"))
            st.markdown(str(film['title'].item()))

    num_first = 20
    bk, bd, wk, wd = u.split_data(df, int(st.session_state["film_index"]), num_first)

    
    temp = temp.loc[temp.index != st.session_state["film_index"], :]
    bkex = temp.iloc[temp.index.isin(bk.shows.values), st.session_state["num_users"]:]
    bdex = temp.iloc[temp.index.isin(bd.shows.values), st.session_state["num_users"]:]
    wkex = temp.iloc[temp.index.isin(wk.shows.values), st.session_state["num_users"]:]
    wdex = temp.iloc[temp.index.isin(wd.shows.values), st.session_state["num_users"]:]
    
    num_to = 5
    if st.session_state["flag_shuffle"]:
        bkex["preds"] = bk.head(len(bkex)).preds.values
        bdex["preds"] = bd.head(len(bdex)).preds.values
        wkex["preds"] = wk.head(len(wkex)).preds.values
        wdex["preds"] = wd.head(len(wdex)).preds.values

        bkex["l"] = bk.head(len(bkex)).label.values
        bdex["l"] = bd.head(len(bdex)).label.values
        wkex["l"] = wk.head(len(wkex)).label.values
        wdex["l"] = wd.head(len(wdex)).label.values
        st.session_state["flag_shuffle"] = False

    else:
        bkex["preds"] = bk.tail(len(bkex)).preds.values
        bdex["preds"] = bd.tail(len(bdex)).preds.values
        wkex["preds"] = wk.tail(len(wkex)).preds.values
        wdex["preds"] = wd.tail(len(wdex)).preds.values

        bkex["l"] = bk.tail(len(bkex)).label.values
        bdex["l"] = bd.tail(len(bdex)).label.values
        wkex["l"] = wk.tail(len(wkex)).label.values
        wdex["l"] = wd.tail(len(wdex)).label.values

    
    if st.session_state["flags"]["diversity"] == 0:
        if st.session_state["flags"]["transparency"]:
            st.caption("Best collaborative filtering and same cluster")
        else:
            st.caption("Recommendations for you!")
        t.recommendations(bkex.tail(num_to))
        if st.session_state["flags"]["transparency"]:
            st.caption("Best collaborative filtering and different cluster")
        t.recommendations(bdex.tail(num_to))
    else:
        if st.session_state["flags"]["transparency"]:
            st.caption("Best collaborative filtering and same cluster")
        else:
            st.caption("Recommendations for you!")
        t.recommendations(bkex.tail(num_to))
        if st.session_state["flags"]["transparency"]:
            st.caption("Best collaborative filtering and different cluster")
        t.recommendations(bdex.tail(num_to))
        if st.session_state["flags"]["transparency"]:
            st.caption("Worst collaborative filtering and same cluster")
        t.recommendations(wkex.head(num_to))
        if st.session_state["flags"]["transparency"]:
            st.caption("Worst collaborative filtering and different cluster")
        t.recommendations(wdex.head(num_to))
