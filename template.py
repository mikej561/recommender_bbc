import streamlit as st
from random import random
import math
# set episode session state
def select_c(id, l, p):
    st.session_state["flag_slider"] = False
    st.session_state['cover'] = id
    st.session_state["info"] = [l, p]
    
def tile_item(column, item):
    with column:
        st.button("K: " + str(item["l"]) + ", Rating: " + str(round(item["preds"], 2)) , key=random(), on_click=select_c, args=(item["description"], str(item["l"]), str(round(item["preds"], 2))))
        st.image(item['image'])
        st.caption(item['title'])


def recommendations(df):

  # check the number of items
    nbr_items = df.shape[0]
    img_size = "288x162"
    df["image"] = [x.replace("{recipe}", img_size) for x in df["image"].values]
    if nbr_items != 0:    
        columns = st.columns(nbr_items)
        items = df.to_dict(orient='records')
    
        any(tile_item(x[0], x[1]) for x in zip(columns, items))
