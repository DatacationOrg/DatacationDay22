import sqlalchemy as _sql
import sqlalchemy.ext.declarative as _declarative
import sqlalchemy.orm as _orm
import os

working_dir = os.path.join(os.getcwd().split('DatacationDay2022')[0], "DatacationDay2022", "src")
db_name = "AuctionData.db"
DB_LOC = os.path.join(working_dir, db_name) 
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_LOC}"

engine = _sql.create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = _orm.sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

Base = _declarative.declarative_base()