from typing import List
import fastapi as _fastapi
import sqlalchemy.orm as _orm

import database.services as _services
import database.schemas as _schemas

app = _fastapi.FastAPI()
_services.create_database()

@app.post("/auctions/", response_model=_schemas.Auction)
def create_auction(
    auction:_schemas.AuctionCreate, db:_orm.Session=_fastapi.Depends(_services.get_db)
):
    """
    # Create auction if the related company does not already have an auction that overlays another of their auctions.

    ## Args:
        - auction (_schemas.AuctionCreate): The schema used to send data to/receive data from the auction table.
        - db (_orm.Session, optional): Database session.

    ## Raises:
        - _fastapi.HTTPException: Overlay found in auction of the given related company.

    ## Returns:
        - Auction created trigger.
    """
    
    db_auction = _services.check_auction_presence(
        db=db, 
        companyName=auction.relatedCompany, 
        auctionStart=auction.auctionStart,
        auctionEnd=auction.auctionEnd
        )

    # Only create auction if does not already exists.
    if db_auction:
        raise _fastapi.HTTPException(
            status_code=400, detail="Auction already exists"
        )
    else:
        return _services.create_auction(db=db, auction=auction)

@app.get("/auctions/", response_model=List[_schemas.Auction])
def read_auctions(
    skip:int=0,
    limit:int=10,
    db:_orm.Session = _fastapi.Depends(_services.get_db)
):
    """
    # Retrieve auctions from the auction table using the given skip and limit boundaries.

    ## Args:
        - skip (int, optional): Number of records to skip before starting retrieval process. Defaults to 0.
        - limit (int, optional): Maximal number of records to retrieve. Defaults to 10.
        - db (_orm.Session, optional): Database session.

    ## Returns:
        - List of auctions retrieved.
    """
    auctions = _services.get_auctions(db=db, skip=skip, limit=limit)
    return auctions

@app.post("/lots/", response_model=_schemas.Lot)
def create_lot(
    lot:_schemas.LotCreate, db:_orm.Session=_fastapi.Depends(_services.get_db)
):
    """
    # Create a lot for the given auction.

    ## Args:
        - lot (_schemas.LotCreate): The schema used to send data to/receive data from the lots table.
        - db (_orm.Session, optional): Database Session.

    ## Raises:
        - _fastapi.HTTPException: Given auction ID has no reference in the auction table (Foreign key relation).

    ## Returns:
        - Lot created trigger.
    """
    db_auction = _services.get_auction_by_ID(db=db, auctionID=lot.auctionID)
    if not db_auction:
        raise _fastapi.HTTPException(
            status_code=500, detail= "Requested auction does not exist"
        )
    
    else:
        return _services.create_lot(db=db, lot=lot)

@app.get("/lots/", response_model=List[_schemas.Lot])
def read_lots(
    auctionID:int,
    skip:int=0,
    limit:int=10,
    db:_orm.Session = _fastapi.Depends(_services.get_db)
):
    """
    # Retrieve lots from the lots table of the given auction, using the given skip and limit boundaries.

    ## Args:
        - auctionID (int): ID reference of the auction of which the lots are desired to be retrieved.
        - skip (int, optional): Number of records to skip before starting retrieval process. Defaults to 0.
        - limit (int, optional): Maximal number of records to retrieve. Defaults to 10.
        - db (_orm.Session, optional): Database session.

    ## Raises:
        - _fastapi.HTTPException: Given auction ID has no reference in the auction table (Foreign key relation).

    ## Returns:
        - List of lots retrieved.
    """
    db_auction = _services.get_auction_by_ID(db=db, auctionID=auctionID)
    if not db_auction:
        raise _fastapi.HTTPException(
            status_code=500, detail= "Requested auction does not exist"
        )
    else:
        return _services.get_lots_by_auctionID(db=db, auctionID=auctionID, skip=skip, limit=limit)

@app.get("/bids/", response_model=List[_schemas.Bid])
def read_bids(
    auctionID:int,
    lotNr:int,
    skip:int=0,
    limit:int=10,
    db:_orm.Session = _fastapi.Depends(_services.get_db)
):
    """
    # Retrieve bids from the bids table of the concerning auction and lot, using the given skip and limit boundaries

    ## Args:
        - auctionID (int): ID reference of the auction of which (in combination with the lotID) bids need to be retrieved.
        - lotID (int): ID reference of the lot of which (in combination with the auctionID) bids need to be retrieved.
        - skip (int, optional): Number of records to skip before starting retrieval process. Defaults to 0.
        - limit (int, optional): Maximal number of records to retrieve. Defaults to 10.
        - db (_orm.Session, optional): Database session.
    
    ## Raises:
        - _fastapi.HTTPException: Given Lot does not exist within the given auction.

    ## Returns:
        - List of bids retrieved.
    """
    db_bids = _services.get_bids_by_IDs(db=db, auctionID=auctionID, lotNr=lotNr, skip=skip, limit=limit)
    if not db_bids:
        raise _fastapi.HTTPException(
            status_code=500, detail= "Given LotID and/or AuctionID do not exist"
        )
    else:
        return db_bids

@app.post("/bids/", response_model=_schemas.Bid)
def create_bid(
    bid:_schemas.BidCreate, db:_orm.Session=_fastapi.Depends(_services.get_db)
):
    """
    # Create a bid for the given auction and lot combination.

    ## Args:
        - bid (_schemas.BidCreate): The schema used to send data to/receive data from the lots table.
        - db (_orm.Session, optional): Database Session.

    ## Raises:
        - _fastapi.HTTPException: Given Lot does not exist within the given auction.

    ## Returns:
        - Bid created trigger.
    """
    db_lot = _services.get_auction_lot_combination(db=db, auctionID=bid.auctionID, lotNr=bid.lotNr)
    if not db_lot:
        raise _fastapi.HTTPException(
            status_code=500, detail= "Given LotID and/or AuctionID do not exist"
        )
    else:
        return _services.create_bid(db=db, bid=bid)