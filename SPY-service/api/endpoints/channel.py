import os
from datetime import datetime
import xlsxwriter
from fastapi.responses import FileResponse
from schemas.channel import Channel
from fastapi import APIRouter, HTTPException
from youtube_parser.parser import YouTubeParser
from database.db_API import DBAPI
from schemas.channel import ChannelCreate

router = APIRouter()


@router.post("/", response_model=Channel)
def create_channel_endpoint(channel: ChannelCreate):
    with DBAPI() as db_api:
        return db_api.create_channel(channel)


@router.get("/{channel_id}", response_model=Channel)
def get_channel_endpoint(channel_id: str):
    with DBAPI() as db_api:
        db_channel = db_api.get_channel(channel_id)
        if not db_channel:
            raise HTTPException(status_code=404, detail="Channel not found")
        return db_channel


@router.get("/", response_model=list[Channel])
def get_channels_endpoint(skip: int = 0, limit: int = 100):
    with DBAPI() as db_api:
        return db_api.get_channels(skip=skip, limit=limit)


@router.post("/parse-channel/")
def parse_channel_endpoint(channel_url: str):
    YouTubeParser().parse_channel(channel_url)


@router.post("/fetch-ads/")
def fetch_ads(channel_url: str): #, date_range: str
    #try:
    #    start_date_str, end_date_str = date_range.split("-")
    #    start_date = datetime.strptime(start_date_str, "%d:%m:%y")
    #    end_date = datetime.strptime(end_date_str, "%d:%m:%y")
    #except ValueError:
    #    raise HTTPException(status_code=400, detail="Invalid date format. Use dd:mm:yy-dd:mm:yy.")

    #if start_date > end_date:
    #    raise HTTPException(status_code=400, detail="Start date cannot be after end date.")

    parse_channel_endpoint(channel_url)

    with DBAPI() as db_api:
        channel_id = YouTubeParser().extract_channel_id(channel_url)
        channel = db_api.get_channel(channel_id)

        advertisements = db_api.get_advertisements()
        ads_from_channel = []
        for ad in advertisements:
            video = db_api.get_video(ad.video_id)
            if video.channel_id == channel_id:
                ads_from_channel.append({
                    "video_title": video.title,
                    "published_at": video.published_at,
                    "brand_name": ad.product.brand_name,
                    "product_name": ad.product_name,
                    "ad_link": ad.short_link,
                })

    file_name = f"{channel.name}.xlsx" #f"{channel.name}-{start_date_str}_to_{end_date_str}.xlsx"
    file_path = f"/tmp/{file_name}"

    with xlsxwriter.Workbook(file_path) as workbook:
        worksheet = workbook.add_worksheet()

        worksheet.set_column(0, 0, 120)
        worksheet.set_column(1, 1, 30)
        worksheet.set_column(2, 2, 30)
        worksheet.set_column(3, 3, 200)
        worksheet.set_column(4, 4, 60)

        headers = ["Название видео", "Дата публикации", "Бренд", "Продукт", "Ссылка на продукт"]
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header)

        for row_num, ad in enumerate(ads_from_channel, start=1):
            worksheet.write(row_num, 0, ad["video_title"])
            worksheet.write(row_num, 1, ad["published_at"].strftime("%Y-%m-%d %H:%M:%S"))
            worksheet.write(row_num, 2, ad["brand_name"])
            worksheet.write(row_num, 3, ad["product_name"])
            worksheet.write(row_num, 4, ad["ad_link"])

    if os.path.exists(file_path):
        return FileResponse(file_path, filename=file_name,
                            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        raise HTTPException(status_code=500, detail="Failed to create the Excel file.")
