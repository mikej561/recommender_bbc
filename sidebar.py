import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from random import random
import utils as u

values = ['Autonomy', 'Transparency', 'Diversity', 'Utility', 'Privacy']
def register():
    st.session_state.reg = True
    values = ['Autonomy', 'Transparency', 'Diversity', 'Utility', 'Privacy']
    data = st.session_state["users_data"]
    dic = {'name': st.session_state.usr, 'id' : int(data.tail(1)['id'].item()) + 1, 'pass':st.session_state.pwd, 'country':st.session_state.opts_country, "age":st.session_state.age}
    for val in values:
        if val in st.session_state.opts_vals:
            dic[val] = 1
        else:
            dic[val] = 0
    sim_user_id  = u.find_similar_user(dic, data, values)["id"].item()
    st.session_state["counter"] = 10
    data = data.append(dic, ignore_index = True)
    data.to_csv("data/users.csv", index = False)
    st.session_state["users_data"] = data
    watched = st.session_state["watched_data"]
    col = watched[str(sim_user_id)].values 
    watched.insert(st.session_state["num_users"], str(st.session_state["num_users"]), col)
    watched.to_csv("data/watched_data.csv", index = False)
    st.session_state["watched_data"] = watched
    st.session_state["num_users"] += 1

def authenticate():
    #0. Load users
    
    df_users = st.session_state["users_data"]
    #1. retrieve user credentials
    names = df_users['name'].tolist()
    passwords = df_users['pass'].tolist()

    #2. create a hash for each passwords so that we do not send these in the clear
    hashed_passwords = stauth.Hasher(passwords).generate()

    #3. create the authenticator which will create an authentication session cookie with an expiry interval
    authenticator = stauth.Authenticate(names, names, hashed_passwords, 'streamlit-auth-6','streamlit-auth-6-key',cookie_expiry_days=1)

    #4. display the login form in the sidebar 
    name, authentication_status, username = authenticator.login('Login','sidebar')

    #5. the streamlit_authenticator library keeps state of the authentication status in streamlit's st.session_state['authentication_status']
    # > if the authentication succeeded (i.e. st.session_state['authentication_status'] == True)
    if st.session_state['authentication_status']:
        # display name on the sidebar
        
        # set user id in session state
        t = df_users[df_users['name'] == name]
        user_id = int(t.index[0])
        if st.session_state["logged_in"] == False:
            st.session_state["need_filtering"] = True
            
        st.session_state['logged_in'] = True
        st.session_state['id'] = user_id
        st.session_state["flags"]["transparency"] = df_users["Transparency"][user_id]
        st.session_state["flags"]["diversity"] = df_users["Diversity"][user_id]
        st.session_state["flags"]["privacy"] = df_users["Privacy"][user_id]
        st.session_state["flags"]["utility"] = df_users["Utility"][user_id]
        st.session_state["flags"]["autonomy"] = df_users["Autonomy"][user_id]
        with st.sidebar:
            t2 = df_users.loc[df_users["id"] == user_id, ]
            s = ""
            for col in t2.columns:
                if col in values and t2[col].item() == 1:
                    s += col + " "
            st.text("Name: " + name)
            st.text("Desired values:")
            for v in s.split():
                st.text(v)
            if st.session_state["flags"]["transparency"]:
                st.caption("Why these movies were chosen?")
                st.markdown("The recommendations were created for you based on collaborative and content based filtering. Collaborative filtering looks at the things you have seen and based on similar users' ratings provides recommendations. The content based filtering is based on clustering similar descriptions to produce similar or unsimilar movies.")

        

    # > if the authentication failed
    elif st.session_state['authentication_status'] == False:
        # write an error message on the sidebar
        with st.sidebar:
            if st.session_state['reg'] is not None: 
                st.error('Username/password is incorrect')
                if st.session_state.reg == False:
                    visualize_register()
                else:
                    st.warning("Please log in above")
            else:
                st.warning('You registered succesfully, please log in')
                st.session_state.reg = True
            
      

    # > if there are no authentication attempts yet (e.g., first time visitors)
    elif st.session_state['authentication_status'] == None:
        # write an warning message on the sidebar
        with st.sidebar:
            if st.session_state.reg == False:
                visualize_register()
            else:
                st.warning('Please log in above')           
                
                
def visualize_register():
    st.warning('Please enter your username and password to log in or register below')
    st.text_input('Enter user name', key = "usr")
    st.text_input('Enter password', type = "password", key = "pwd")
    st.multiselect(
'What values would you like to see in the recommender system?',
['Autonomy', 'Transparency', 'Diversity', 'Utility', 'Privacy'], key = 'opts_vals')
    st.selectbox('Where are you from?', ('Europe', 'Asia', 'Africa', 'North America', 'South America', 'Australia'), key = "opts_country")
    st.number_input('Tell me your age!', min_value = 8, max_value = 100, key = "age")
    st.button('Register me!', key=random, on_click=register)
