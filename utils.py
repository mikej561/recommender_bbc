import pandas as pd

def find_similar_user(user, df, values):
    temp = df
    
    #find users of same country
    if len(df.loc[user["country"] == df.country, ]) != 0:
        temp = df.loc[user["country"] == df.country, ]
    
    #find users with same values
    for val in values:
        if len(temp.loc[user[val] == temp[val], ]) != 0:
            temp = temp.loc[user[val] == temp[val], ]
    
    #find users of the most similar age
    df_sorted = temp.iloc[(temp['age'] - user["age"]).abs().argsort()[:1]]
    
    return df_sorted

def split_data(data, chosen_content_index, num_adds):
    label = data.loc[data.index == chosen_content_index, "label"].item()
    data_best_same_k = data.loc[data.label == label, :].tail(num_adds)
    data_best_dif_k = data.loc[data.label != label, :].tail(num_adds)
    data_wst_same_k = data.loc[data.label == label, :].head(num_adds)
    data_wst_dif_k = data.loc[data.label != label, :].head(num_adds)
    return data_best_same_k, data_best_dif_k, data_wst_same_k, data_wst_dif_k