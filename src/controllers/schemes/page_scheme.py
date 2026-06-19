from pydantic import BaseModel
from typing import Literal, Optional

class Metadata(BaseModel):

    source: Literal[None]
    file_path: Literal[None]
    page: Literal[None]
    page_summary: str
    total_pages: Literal[None]
    content_format: Literal["text", "image", "mixed"]

    document_language: str
    document_type: Literal["لوائح", "خطة دراسية", "مقررات", "جداول", "اعلانات", "قرارات", "احصائيات", "اخرى"]
    university_name: Literal["جامعة المنيا"]
    faculty: Literal["كلية الهندسة"]
    department: Literal[
    "الهندسة المعمارية",
    "الهندسة المدنية",
    "هندسة القوى الميكانيكية والطاقة",
    "هندسة السيارات والجرارات",
    "هندسة الإنتاج والتصميم",
    "الهندسة الكيميائية",
    "الهندسة الكهربية",
    "هندسة الحاسبات والنظم",
    "الهندسة الطبية",
    "هندسة البترول",
    "هندسة الميكاترونيات"]
    academic_year: str
    semester: str
    contains_tables: bool
    contains_charts: bool
    contains_diagrams: bool
    keywords: list[str]

class PageScheme(BaseModel):
    content: str
    metadata: Metadata
    