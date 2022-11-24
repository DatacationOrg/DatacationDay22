import sqlalchemy as _sql
import sqlalchemy.orm as _orm

import database.database as _database


class Auction(_database.Base):
    __tablename__ = "auctions"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    relatedCompany = _sql.Column(_sql.String, index=True)
    auctionStart = _sql.Column(_sql.DateTime, index=True)
    auctionEnd = _sql.Column(_sql.DateTime, index=True)
    branchCategory = _sql.Column(_sql.String, index=True)


class Lots(_database.Base):
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

class Bids(_database.Base):
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