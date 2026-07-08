import enum


class RegionEnum(str, enum.Enum):
    india = "india"
    uae = "uae"


class IncomeCategoryEnum(str, enum.Enum):
    salary = "salary"
    business = "business"
    rental = "rental"
    other = "other"


class InvestmentTypeEnum(str, enum.Enum):
    mutual_fund = "mutual_fund"
    stocks = "stocks"
    sip = "sip"
    fd = "fd"
    nps = "nps"
    crypto = "crypto"
    other = "other"


class GoldUnitEnum(str, enum.Enum):
    grams = "grams"
    sovereigns = "sovereigns"
