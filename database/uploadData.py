import sqlite3
import pandas as pd
from tqdm import tqdm
import os

import database.models as _models

class uploadData:
    def __init__(self, db_name='database.db'):
        self.db_name = db_name
        self.tables = ['auctions', 'lots', 'bids']
        self.dfs = {
            'auctions': 'auctions.csv',
            'lots': 'lots.csv',
            'bids': 'bids.csv'
            }
        self.queries = {
            'auctions': '''INSERT INTO auctions(id, relatedCompany, auctionStart, auctionEnd, branchCategory) VALUES(?,?,?,?,?) ''',
            'lots': '''INSERT INTO lots(countryCode, saleDate, auctionID, lotNr, suffix, numberOfItems, buyerAccountID, estimatedValue, startingBid, reserveBid, currentBid, VAT, mainCategory, sold) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            'bids': '''INSERT INTO bids(auctionID, lotNr, bidNr, lotID, isCombination, accountID, isCompany, bidPrice, biddingDateTime, closingDateTime) VALUES (?,?,?,?,?,?,?,?,?,?)'''
        }
        self.create_connection()

        self.push_data()

        self.close_connection()

    def create_connection(self):
        self.conn = sqlite3.connect(f"{os.getcwd().split('DatacationDay2022')[0]}DatacationDay2022/data/{self.db_name}")
        self.cur = self.conn.cursor()
    
    def push_data(self):
        for table in self.tables:
            df = pd.read_csv(f"{os.getcwd().split('DatacationDay2022')[0]}DatacationDay2022/data/{self.dfs[table]}")
            
            err_cntr = 0

            for idx, data in tqdm(df.iterrows(), total=df.shape[0]):
                try:
                    self.cur.execute(self.queries[table], data)
                    if idx%100000 == 0:
                        self.conn.commit()
                except sqlite3.IntegrityError:
                    err_cntr += 1

            self.conn.commit()
            
            print(f'--- Finished upload {table} data. ---')
            print(f'\t ({len(df)-err_cntr}/{err_cntr}) (Success/Failed) \n')
    
    def close_connection(self):
        self.conn.close()


uploadData()