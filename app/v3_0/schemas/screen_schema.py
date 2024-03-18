from typing import Optional, List

from pydantic import BaseModel

from app.enums.screen_enums import DataTypeEnum


class BuildScreen(BaseModel):
    isMobile: bool


class TileData(BaseModel):
    title_key: str
    subtitle_key: str
    avatar_key: Optional[str] = None
    status_key: Optional[str] = None


class DynamicListTileSchema(BaseModel):
    screen_name: str
    tile_data: TileData
    view_data: Optional[list] = None


class TableColumns(BaseModel):
    column_title: str
    data_key: str
    data_type: DataTypeEnum
    column_width: Optional[float] = None


class DynamicTableSchema(BaseModel):
    table_name: str
    columns: List[TableColumns]
    view_data: Optional[list] = []
