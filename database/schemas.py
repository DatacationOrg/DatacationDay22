import datetime as _dt
import pydantic as _pydantic

class _AuctionBase(_pydantic.BaseModel):
    relatedCompany: str
    auctionStart: _dt.datetime
    auctionEnd: _dt.datetime
    branchCategory: str

class AuctionCreate(_AuctionBase):
    pass

class Auction(_AuctionBase):
    id: int

    class Config:
        orm_mode = True


class _LotBase(_pydantic.BaseModel):
    auctionID: int
    numberOfItems: int
    estimatedValue: float
    startingBid: float
    reserveBid: float
    mainCategory: str

class LotCreate(_LotBase):
    pass

class Lot(_LotBase):
    lotNr: int
    countryCode: str
    saleDate: _dt.datetime
    suffix: str
    buyerAccountID: int
    currentBid: float
    VAT: int
    sold: bool

    class Config:
        orm_mode = True


class _BidBase(_pydantic.BaseModel):
    auctionID: int
    lotNr: int
    isCombination: bool
    accountID: int
    isCompany: bool
    bidPrice: float
    biddingDateTime: _dt.datetime

class BidCreate(_BidBase):
    pass

class Bid(_BidBase):
    bidNr: int
    closingDateTime: _dt.datetime

    class Config:
        orm_mode = True

