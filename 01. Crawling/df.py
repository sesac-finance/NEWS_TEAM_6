import pandas as pd
import os


CSV_DIR = './csv/'

def news_csv():
    news_df = pd.read_csv(CSV_DIR + 'news_6.csv')

    return news_df


def comment_csv():
    comment_df = pd.read_csv(CSV_DIR + 'comment_6.csv')
    
    return comment_df



