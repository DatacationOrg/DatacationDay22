import sqlalchemy as _sql
import sqlalchemy.ext.declarative as _declarative
import sqlite3

from tqdm import tqdm
import pandas as pd
import os

class Database:
    def __init__(self, db_name="AuctionData.db", overwrite_db=False):
        # Initialize all database variables and directory references
        self.directory = 'DatacationDay22'
        self.db_name = db_name
        self.working_dir = os.path.join(os.getcwd().split(self.directory)[0], self.directory, "src")
        self.data_dir = os.path.join(os.getcwd().split(self.directory)[0], self.directory, "data")
        self.database_location = os.path.join(self.working_dir, self.db_name)
        self.SQLALCHEMY_DATABASE_URL = f"sqlite:///{self.database_location}"

        # Only create new database if it either not exists or it is explicitly said to be overwritten.
        if not os.path.exists(self.database_location) or overwrite_db:

            # Create database object with Auction, Lots en Bids tables
            self.create_database()

            # Define tables, datasets and insertion queries and push data into sql database
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
            self.push_data()

    def setup_environment(self) -> None:
        """
        Create the database engine and the declarative base.
        """
        # If the database file already exists, delete file
        if os.path.exists(self.database_location):
            os.remove(self.database_location)

        self.engine = _sql.create_engine(
            self.SQLALCHEMY_DATABASE_URL, 
            connect_args={"check_same_thread": False})

        self.Base = _declarative.declarative_base()
    
    def initiate_tables(self) -> None:
        """
        Initiate tables that comprise the database.
        """
        class Auction(self.Base):
            __tablename__ = "auctions"
            id = _sql.Column(_sql.Integer, primary_key=True, index=True)
            relatedCompany = _sql.Column(_sql.String, index=True)
            auctionStart = _sql.Column(_sql.DateTime, index=True)
            auctionEnd = _sql.Column(_sql.DateTime, index=True)
            branchCategory = _sql.Column(_sql.String, index=True)

        class Lots(self.Base):
            __tablename__ = "lots"
            countryCode = _sql.Column(_sql.String, index=True)
            saleDate = _sql.Column(_sql.DateTime, index=True)
            auctionID = _sql.Column(_sql.Integer, _sql.ForeignKey("auctions.id"), primary_key=True)
            lotNr = _sql.Column(_sql.Integer, primary_key=True, index=True)
            suffix = _sql.Column(_sql.String, index=True)
            numberOfItems = _sql.Column(_sql.Integer, index=True)
            buyerAccountID = _sql.Column(_sql.Integer, index=True)
            estimatedValue = _sql.Column(_sql.Float, index=True)
            startingBid = _sql.Column(_sql.Float, index=True)
            reserveBid = _sql.Column(_sql.Float, index=True)
            currentBid = _sql.Column(_sql.Float, index=True)
            VAT = _sql.Column(_sql.Integer, index=True)
            mainCategory = _sql.Column(_sql.String, index=True)
            sold = _sql.Column(_sql.Boolean, index=True)

        class Bids(self.Base):
            __tablename__ = "bids"
            auctionID = _sql.Column(_sql.Integer, _sql.ForeignKey("lots.auctionID"), primary_key=True)
            lotNr = _sql.Column(_sql.Integer, _sql.ForeignKey("lots.lotNr"), primary_key=True)
            bidNr = _sql.Column(_sql.Integer, primary_key=True, index=True)
            lotID = _sql.Column(_sql.Integer, index=True)
            isCombination = _sql.Column(_sql.Boolean, index=True)
            accountID = _sql.Column(_sql.Integer, index=True)
            isCompany = _sql.Column(_sql.Boolean, index=True)
            bidPrice = _sql.Column(_sql.Float, index=True)
            biddingDateTime = _sql.Column(_sql.DateTime, index=True)
            closingDateTime = _sql.Column(_sql.DateTime, index=True)

    def create_database(self) -> None:
        """ 
        Initiate the database, creating its environment and the tables it is comprised of.
        """
        self.setup_environment()
        self.initiate_tables()
        self.Base.metadata.create_all(bind=self.engine)

    def push_data(self) -> None:
        """
        Create connection to SQLite database, insert data and close database connection.
        """
        # Create database connection
        conn = sqlite3.connect(self.database_location)
        cur = conn.cursor()

        # Loop over csv files containing the data and insert them into the database
        for table in self.tables:
            df = pd.read_csv(os.path.join(self.data_dir, self.dfs[table]))
            err_cntr = 0
            for idx, data in tqdm(df.iterrows(), total=df.shape[0]):
                try:
                    cur.execute(self.queries[table], data)

                    # Only commit every 100.000 records to lower computation time.
                    if idx%100000 == 0:
                        conn.commit()

                # If not possible to insert data, integrity error is found.
                except sqlite3.IntegrityError:
                    err_cntr += 1

            # Execute final commit to ensure all data is pushed to the database
            conn.commit()
            
            print(f'--- Finished upload {table} data. ---')
            print(f'\t ({len(df)-err_cntr}/{err_cntr}) (Success/Failed) \n')
        
        # Close database connection
        conn.close()

    def execute_query(self, query:str) -> pd.DataFrame:
        """
        Establish database connection, execute the query and close database connection.

        Args:
            query (str): String representation of the query to be executed.

        Returns:
            pd.DataFrame: Output of the executed query formatted in a DataFrame.
        """
        # Execute query and retrieve results
        conn = sqlite3.connect(self.database_location)
        cursor = conn.execute(query)
        data = cursor.fetchall()

        # Transform results into DataFrame
        cols = list(map(lambda x: x[0], cursor.description))
        data = pd.DataFrame(data, columns=cols)

        # Close database connection an return query results
        conn.close()
        return data