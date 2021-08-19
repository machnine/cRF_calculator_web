from fastapi import FastAPI, Query
from sqlalchemy import create_engine, engine, or_
from sqlalchemy.orm import sessionmaker, declarative_base


SQLALCHEMY_DATABASE_URL = "sqlite:///./crf_donors.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base(engine)

class Donor(Base):
    __tablename__ = 'donors'
    __table_args__ = {'autoload': True}


def crf_cal(bg: str, ags: list, ver: int, com: bool=False) -> float:
    """
    calculate CRF given the blood group, antibodies and version number
    NB: according to the ODT definition the calculation is based on 
    blood group COMPATIBILITY, however, both official versions were
    based on blood group IDENTITY! 
    """
    with SessionLocal() as session:

        if com:
            compatible = {'A':['A', 'O'], 'B':['B', 'O'], 'O': ['O'], 'AB': ['A', 'B', 'O', 'AB']}
            com_filter = or_(*[Donor.BG == g for g in compatible[bg]])
            total = session.query(Donor).filter(com_filter)
        else:
            total = session.query(Donor).filter(Donor.BG == bg)

        if ver:
            total = total.filter(Donor.VER == ver)

        pos_filter = or_(*[Donor.__dict__[ag] == 1 for ag in ags])
        pos = total.filter(pos_filter)

        return pos.count() / total.count() * 100


api = FastAPI()


@api.get("/")
async def get_crf(
    bg: str = Query('', min_length=1, max_length=2, regex="^[ABO]$|^AB$"),
    ags: str = Query('', min_length=2, regex="^([ABCD][QRPW]?\d{1,3},?)+$"),
    ver: int = Query(2, ge=0, le=2), 
    com: bool = False):
    if ags:
        crf = crf_cal(bg=bg, ags=ags.split(','), ver=ver, com=com)
    else:
        crf = 0.0
    return {'crf': crf}
