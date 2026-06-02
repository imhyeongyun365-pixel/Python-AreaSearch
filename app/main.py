from pathlib import Path
from pydantic import BaseModel
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
import re
from app.models.__init__ import mongodb
from app.models.area import AreaModel
from app.area_scraper import NaverAreaScraper

def clean_html(text: str):
    return re.sub(r"<.*?>", "", text)

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR /"static"),name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    
    return templates.TemplateResponse(
        request,
        "index.html",
        {"title": "지역탐색"}
    )


@app.get("/search",response_class=HTMLResponse)
async def read_item(request:Request,q:str):
    keyword=q

    naver_area_scraper=NaverAreaScraper()
    areas = await naver_area_scraper.search(keyword,10)


    favorite_areas = await mongodb.engine.find(
        AreaModel,
        AreaModel.is_favorite==True
        )

    
    favorite_titles =[area.title for area in favorite_areas]

    area_models=[]

    for area in areas:
        print(area)
        area_model=AreaModel(
            keyword=keyword,
            title=area.get("title", ""),
            link=area.get("link", ""),
            category=area.get("category", ""),
            description=area.get("description", ""),
            telephone=area.get("telephone", ""),
            address=area.get("address", ""),
            roadAddress=area.get("roadAddress", ""),
            mapx=area.get("mapx", ""),
            mapy=area.get("mapy", "")
        )

        if area_model.title in favorite_titles:
           area_model.is_favorite=True

        area_models.append(area_model)

  

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context= {"keyword":q,"areas":area_models,"next_url":f"/search?q={q}"}
    )


@app.post("/favorites")
async def toggle_favorite(
    request:Request,
    keyword:str=Form(...),
    title:str =Form(...),
    link:str=Form("/"),
    category:str=Form("/"),
    description:str=Form(...),
    telephone:str=Form(...),
    address:str=Form(...),
    roadAddress:str=Form(...),
    mapx:str=Form(...),
    mapy:str=Form(...),
    
    next_url:str=Form("/")
):
    favorite_area =await mongodb.engine.find_one(
        AreaModel,
        (AreaModel.keyword==keyword)
        & (AreaModel.title==title)
        & (AreaModel.address==address)
        &(AreaModel.is_favorite==True)
    )    
    if favorite_area:
        await mongodb.engine.delete(favorite_area)

    else:
        area=AreaModel(
            keyword=keyword,
            title=title,
            link=link,
            category=category,
            description=description,
            telephone=telephone,
            address=address,
            roadAddress=roadAddress,
            mapx=mapx,
            mapy=mapy,
            is_favorite=True

        )
        await mongodb.engine.save(area)

    return RedirectResponse(url=next_url,status_code=303)

@app.get("/favorites",response_class=HTMLResponse)
async def favorites(request:Request):
    areas = await mongodb.engine.find(AreaModel,AreaModel.is_favorite==True)


    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title":"즐겨찾기 목록",
            "areas":areas,
            "next_url":"/favorites"
        }
    )

@app.on_event("startup")
async def on_app_start():
    print("hello server")
    mongodb.connect()

@app.on_event("shutdown")
async def on_app_shutdown():
    print("goodbye server")
    mongodb.close()