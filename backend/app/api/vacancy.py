from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import httpx

from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/vacancy", tags=["vacancy"])

HH_API_BASE = "https://api.hh.ru"


class VacancyParseRequest(BaseModel):
    url: str  # https://hh.ru/vacancy/12345678


class VacancyData(BaseModel):
    title: str
    company: str
    description: str
    key_skills: list[str]
    salary_from: int | None
    salary_to: int | None
    currency: str | None


def _extract_vacancy_id(url: str) -> str | None:
    import re
    match = re.search(r"/vacancy/(\d+)", url)
    return match.group(1) if match else None


@router.post("/parse", response_model=VacancyData)
async def parse_vacancy(
    body: VacancyParseRequest,
    user: User = Depends(get_current_user),
):
    vacancy_id = _extract_vacancy_id(body.url)
    if not vacancy_id:
        raise HTTPException(status_code=400, detail="Не удалось извлечь ID вакансии из URL")

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{HH_API_BASE}/vacancies/{vacancy_id}",
            headers={"User-Agent": "JobAI/1.0 (support@jobai.ru)"},
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="HH API недоступен")

    data = resp.json()
    description_raw = data.get("description", "")
    # Убираем HTML-теги
    import re
    description = re.sub(r"<[^>]+>", " ", description_raw).strip()

    skills = [s["name"] for s in data.get("key_skills", [])]
    salary = data.get("salary") or {}

    return VacancyData(
        title=data.get("name", ""),
        company=data.get("employer", {}).get("name", ""),
        description=description[:5000],  # обрезаем под промпт
        key_skills=skills,
        salary_from=salary.get("from"),
        salary_to=salary.get("to"),
        currency=salary.get("currency"),
    )