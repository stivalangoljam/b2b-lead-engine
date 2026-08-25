from __future__ import annotations

import hashlib
import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:4173,http://127.0.0.1:4173,"
        "http://localhost:8080,http://127.0.0.1:8080,"
        "http://localhost:5500,http://127.0.0.1:5500",
    ).split(",")
    if origin.strip()
]

app = FastAPI(
    title="B2B Lead Scraping & Outreach Engine",
    description="Simulated scrape-and-outreach pipeline for B2B lead generation.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
    expose_headers=["Content-Type", "X-Request-Id"],
    max_age=600,
)


class SearchRequest(BaseModel):
    industry: str = Field(..., min_length=1, examples=["HVAC"])
    location: str = Field(..., min_length=1, examples=["Austin, TX"])


class Lead(BaseModel):
    business_name: str
    website: HttpUrl
    phone: str
    industry: str
    location: str
    outreach_script: str


class SearchResponse(BaseModel):
    industry: str
    location: str
    lead_count: int
    leads: List[Lead]


MOCK_BUSINESS_SEEDS = [
    {
        "suffix": "Partners",
        "slug": "partners",
        "phone_prefix": "512",
        "tone_hook": "the way you show up locally",
    },
    {
        "suffix": "Collective",
        "slug": "collective",
        "phone_prefix": "737",
        "tone_hook": "how tight your operation looks from the outside",
    },
    {
        "suffix": "Works",
        "slug": "works",
        "phone_prefix": "214",
        "tone_hook": "the kind of reputation you have in town",
    },
]


def _stable_index(value: str, modulo: int) -> int:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % modulo


def _slugify(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value)
    return "-".join(part for part in cleaned.split("-") if part) or "lead"


def _format_phone(prefix: str, industry: str, location: str, slot: int) -> str:
    seed = _stable_index(f"{industry}|{location}|{slot}", 9000) + 1000
    return f"+1 ({prefix}) {seed:04d}-{2000 + slot * 111:04d}"


def scrape_mock_businesses(industry: str, location: str) -> list[dict]:
    """Simulate a high-performance scrape that yields three local businesses."""
    city_slug = _slugify(location.split(",")[0])
    industry_label = industry.strip()
    leads: list[dict] = []

    for slot, seed in enumerate(MOCK_BUSINESS_SEEDS):
        brand = f"{industry_label} {seed['suffix']}"
        leads.append(
            {
                "business_name": brand,
                "website": f"https://www.{_slugify(industry_label)}-{seed['slug']}-{city_slug}.com",
                "phone": _format_phone(seed["phone_prefix"], industry, location, slot),
                "industry": industry_label,
                "location": location.strip(),
                "tone_hook": seed["tone_hook"],
            }
        )

    return leads


def generate_outreach_script(business: dict) -> str:
    """Simulate an AI prompt loop that writes a hyper-casual, non-robotic script."""
    name = business["business_name"]
    industry = business["industry"]
    location = business["location"]
    website = business["website"]
    hook = business["tone_hook"]

    prompt_passes = [
        (
            f"Write a short outreach note for {name} in {location}. Industry: {industry}.",
            f"Hey — stumbled on {name} while looking at {industry.lower()} shops around {location}.",
        ),
        (
            "Keep it human: no 'I hope this finds you well', no feature dumps, no fake urgency.",
            f" Not pitching a deck or anything, just liked {hook}.",
        ),
        (
            f"Anchor on {hook} and mention their site {website} only if it feels natural.",
            " If you ever want a second set of eyes on inbound leads "
            "(the messy, real ones, not the CRM fairy tale), I would love a 10-minute chat. "
            "If now is a bad time, no stress — I will not chase you down. "
            f"Either way, cool site at {website}.",
        ),
    ]

    drafted_parts: list[str] = []
    for _prompt, fragment in prompt_passes:
        drafted_parts.append(fragment.strip())

    return " ".join(drafted_parts)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/search", response_model=SearchResponse)
def search_leads(payload: SearchRequest) -> SearchResponse:
    raw_businesses = scrape_mock_businesses(payload.industry, payload.location)
    leads: list[Lead] = []

    for business in raw_businesses:
        script = generate_outreach_script(business)
        leads.append(
            Lead(
                business_name=business["business_name"],
                website=business["website"],
                phone=business["phone"],
                industry=business["industry"],
                location=business["location"],
                outreach_script=script,
            )
        )

    return SearchResponse(
        industry=payload.industry.strip(),
        location=payload.location.strip(),
        lead_count=len(leads),
        leads=leads,
    )
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)