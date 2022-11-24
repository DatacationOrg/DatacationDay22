import datetime as _dt
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
import pandas as pd

import pickle as pkl

import database.database as _database
import database.models as _models
import database.schemas as _schemas

def create_database():
    return _database.Base.metadata.create_all(bind=_database.engine)

def get_db():
    """
    Setup database session, which is always closed after use.

    Yields:
        db: database session
    """
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_auction_presence(db:_orm.Session, companyName, auctionStart, auctionEnd):
    """
    Check if the requested auction company already has an auction overlapping the start and end date.

    Args:
        db (_orm.Session): Database session.
        companyName: The name of the related company.
        auctionStart: The start date and time of the auction.
        auctionEnd: The end date and time of the auction.
    """
    return db.query(_models.Auction).filter(
        _sql.and_(
            _models.Auction.relatedCompany == companyName,
            _sql.or_(  # Test whether start or end falls within other auction of same company
                _sql.and_(
                    _models.Auction.auctionStart <= auctionStart,
                    _models.Auction.auctionEnd >= auctionStart
                    ),
                _sql.and_(
                    _models.Auction.auctionStart <= auctionEnd,
                    _models.Auction.auctionEnd >= auctionEnd
                    )
                )
            )
        ).first()
    
def get_auctions(db:_orm.Session, skip:int, limit:int):
    """
    Retrieve the given number of auctions from the database

    Args:
        db (_orm.Session): Database session.
        skip (int): The amount of records skipped before start of retrieval
        limit (int): The maximum amount of records returned
    """
    return db.query(_models.Auction).offset(skip).limit(limit).all()

def create_auction(db:_orm.Session, auction:_schemas.AuctionCreate):
    """
    Create an auction, automatically generating the id

    Args:
        db (_orm.Session): Database session.
        auction (_schemas.AuctionCreate): Schema for auction creation.
    """
    db_auction = _models.Auction(
        relatedCompany=auction.relatedCompany,
        auctionStart=auction.auctionStart,
        auctionEnd=auction.auctionEnd,
        branchCategory=auction.branchCategory
        )
    db.add(db_auction)
    db.commit()
    db.refresh(db_auction)
    return db_auction

def get_auction_by_ID(db:_orm.Session, auctionID:int):
    """
    Retrieve auction given auction id, used to check if lot creation is valid

    Args:
        db (_orm.Session): Database session.
        auctionID (int): ID of auction to be retrieved.

    Returns:
        first record found of the given auctionID
    """
    return db.query(_models.Auction).filter(_models.Auction.id == auctionID).first()

def create_lot(db:_orm.Session, lot:_schemas.LotCreate):
    """
    Create a lot, automatically generating a lot number by incrementing the number of the last created lot

    Args:
        db (_orm.Session): Database session.
        lot (_schemas.LotCreate): Schema for lot creation.
    """
    queryRes = db.query(_models.Lots).filter(_models.Lots.auctionID == lot.auctionID).order_by(_models.Lots.lotNr.desc()).first()
    if queryRes:
        lotnumber=queryRes.lotNr + 1
    else:
        lotnumber=1

    auctionDuration = get_auction_duration(db=db, auctionID=lot.auctionID)
    print(auctionDuration)
    startingBid = get_starting_bid(
        numberOfItems=lot.numberOfItems,
        estimatedValue=lot.estimatedValue,
        reserveBid=lot.reserveBid,
        auctionDuration=auctionDuration,
        category=lot.mainCategory
        )

    db_lot = _models.Lots(
        auctionID=lot.auctionID,
        lotNr=lotnumber,
        numberOfItems=lot.numberOfItems, 
        estimatedValue=lot.estimatedValue,
        startingBid=startingBid,
        reserveBid=lot.reserveBid,
        mainCategory=lot.mainCategory,
        countryCode='NL',
        VAT=21,
        suffix='N/A',
        saleDate=_dt.datetime(year=1000, month=1, day=1, hour=0, minute=0, second=0),
        buyerAccountID=99999,
        currentBid=99999,
        sold=False
        )

    db.add(db_lot)
    db.commit()
    db.refresh(db_lot)
    return db_lot

def get_lots_by_auctionID(db:_orm.Session, auctionID:int, skip:int, limit:int):
    """
    Retrieve all lots belonging to the given auction id

    Args:
        db (_orm.Session): Database session.
        auctionID (int): ID of the auction to be searched.

    Returns:
        A list of all lots belonging to the given auction
    """
    return db.query(_models.Lots).filter(_models.Lots.auctionID == auctionID).offset(skip).limit(limit).all()

def get_auction_lot_combination(db:_orm.Session, auctionID:int, lotNr:int):
    """
    Retrieve auction and lot to test whether this combination exists

    Args:
        db (_orm.Session): Database session.
        auctionID (int): ID reference of the auction.
        lotNr (int): Lot number refering to the product to be sold in the given auction.
    """
    return db.query(_models.Lots).filter(
                _sql.and_(
                    _models.Lots.auctionID==auctionID,
                    _models.Lots.lotNr==lotNr
                    )
                ).first()

def get_bids_by_IDs(db:_orm.Session, auctionID:int, lotNr:int, skip:int, limit:int):
    """
    Retrieve all lots belonging to the given auction id

    Args:
        db (_orm.Session): Database session.
        auctionID (int): ID of the auction to be searched.

    Returns:
        A list of all lots belonging to the given auction
    """
    return db.query(_models.Bids).filter(
                    _sql.and_(
                        _models.Bids.auctionID == auctionID,
                        _models.Bids.lotNr == lotNr
                        )        
                    ).offset(skip).limit(limit).all()

def create_bid(db:_orm.Session, bid:_schemas.BidCreate):
    """
    Create a bid, automatically generating a lot number by incrementing the number of the last created bid

    Args:
        db (_orm.Session): Database Session.
        bid (_schemas.BidCreate): Schema for bid creation.
    """
    # Retrieve bid number for reference incrementation
    queryRes = db.query(_models.Bids).filter(
        _sql.and_(
            _models.Bids.auctionID == bid.auctionID,
            _models.Bids.lotNr == bid.lotNr
            )
        ).order_by(_models.Bids.bidNr.desc()).first()
    
    if queryRes:
        bidnumber=queryRes.bidNr + 1
    else:
        bidnumber=1

    # Retrieve auction for closingDateTime
    relatedAuction = db.query(_models.Auction).filter(_models.Auction.id==bid.auctionID).first()

    db_bid = _models.Bids(
        auctionID=bid.auctionID,
        lotNr=bid.lotNr,
        bidNr=bidnumber,
        isCombination=bid.isCombination,
        accountID=bid.accountID,
        isCompany=bid.isCompany,
        bidPrice=bid.bidPrice,
        biddingDateTime=_dt.datetime.now(),
        closingDateTime=relatedAuction.auctionEnd
        )
    
    db.add(db_bid)
    db.commit()
    db.refresh(db_bid)
    return db_bid

def get_auction_duration(db:_orm.session, auctionID:int) -> int:
    """
    Retrieve the duration of a given auction.

    Args:
        db (_orm.session): Database Session.
        auctionID (int): ID reference of an auction.

    Returns:
        int: The duration of the auction in hours.
    """
    auction = get_auction_by_ID(db=db, auctionID=auctionID)
    return int((auction.auctionEnd - auction.auctionStart) / _dt.timedelta(hours=1))

def get_starting_bid(numberOfItems:int, estimatedValue:int, reserveBid:int, auctionDuration:int, category:str) -> int:
    """
    Return the optimal starting bid (highest with prediction sale) for the given auction lot.

    Args:
        numberOfItems (int): The number of items in the concerning lot.
        estimatedValue (int): The estimated values of the items comprising the lot.
        reserveBid (int): The minimal amount accepted as a sale by the seller.
        auctionDuration (int): The total duration of the auction.
        category (str): The branch category in which the auction will take place.

    Returns:
        int: Proposed starting bid value.
    """

    model = pkl.load(open("./src/SavedModels/model.pkl", "rb"))
    scl = pkl.load(open("./src/SavedModels/scaler.pkl", "rb"))
    OHcols = pkl.load(open("./src/SavedModels/OHcols.pkl", "rb"))

    startingBids = list(range(100, 200, 10))

    def onehotencode(df, category):
        dfc = df.copy(deep=True)
        NrOfRows = len(dfc)
        for cat in OHcols:
            if category == cat:
                dfc[f'BC_{cat}'] = [1] * NrOfRows
            else:
                dfc[f'BC_{cat}'] = [0] * NrOfRows
        return dfc

    trialdf = pd.DataFrame(data={
        'numberOfItems': [numberOfItems] * len(startingBids),
        'estimatedValue': [estimatedValue] * len(startingBids),
        'startingBid': startingBids,
        'reserveBid': [reserveBid] * len(startingBids),
        'auctionDuration': [auctionDuration] * len(startingBids),
    })

    trialdf = onehotencode(df=trialdf, category=category)

    trialdf[['numberOfItems', 'estimatedValue', 'startingBid', 'reserveBid', 'auctionDuration']] = scl.transform(
        trialdf[['numberOfItems', 'estimatedValue', 'startingBid', 'reserveBid', 'auctionDuration']]) 

    trialdf['saleNoSale'] = model.predict(trialdf)
    idx = trialdf[trialdf['saleNoSale'] == 1.0].index.tolist()
    startingBid = startingBids[max(idx)]

    return startingBid