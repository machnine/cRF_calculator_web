from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, engine, or_
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./crf_donors.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base(engine)


class Donor(Base):
    __tablename__ = "donors"
    __table_args__ = {"autoload": True}


class Antigen(Base):
    __tablename__ = "antigens"
    __table_args__ = {"autoload": True}


def crf_calculate(bg: str, ags: list, ver: int, com: bool = False) -> float:
    """
    calculate CRF given the blood group, antibodies and version number
    NB: according to the ODT definition the calculation is based on
    blood group COMPATIBILITY, however, both official versions were
    based on blood group IDENTITY!
    """
    with SessionLocal() as session:

        if com:
            compatible = {
                "A": ["A", "O"],
                "B": ["B", "O"],
                "O": ["O"],
                "AB": ["A", "B", "O", "AB"],
            }
            com_filter = or_(*[Donor.bg == g for g in compatible[bg]])
            total = session.query(Donor).filter(com_filter)
        else:
            total = session.query(Donor).filter(Donor.bg == bg)

        if ver:
            total = total.filter(Donor.ver == ver)

        pos_filter = or_(*[Donor.__dict__[ag] == 1 for ag in ags])
        pos = total.filter(pos_filter)

        return pos.count() / total.count() * 100


def get_list_of_antigens() -> list:
    with SessionLocal() as session:
        antigens = session.query(Antigen).all()
    return antigens


api = FastAPI()
api.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# view function
@api.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    antigens = get_list_of_antigens()
    return templates.TemplateResponse(
        "home.html", {"antigens": antigens, "request": request}
    )


# htmx
@api.post("/crf_calc/")
async def post_crf_cal(request: Request):
    data = await request.form()
    bg = data.get("abo")
    ver = int(data.get("ver"))
    com = False

    if "com" in data.keys():
        com = True

    spec_list = [x for x in data.keys() if x not in ("abo", "ver", "com")]

    if spec_list and bg:
        crf = crf_calculate(bg=bg, ags=spec_list, ver=ver, com=com)
    else:
        crf = 0

    return round(crf, 2)

# main API
@api.get("/crf/")
async def get_crf(
    bg: str = Query("", min_length=1, max_length=2, regex="^[ABO]$|^AB$"),
    ags: str = Query("", min_length=2, regex="^([ABCD][QRPW]?\d{1,3},?)+$"),
    ver: int = Query(2, ge=0, le=2),
    com: bool = False,
):
    if ags:
        crf = crf_calculate(bg=bg, ags=ags.split(","), ver=ver, com=com)
    else:
        crf = 0.0
    return {"crf": crf}


@api.get("/antigens/")
async def get_antigens():
    antigens = get_list_of_antigens()
    return {"antigens": antigens}