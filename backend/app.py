"""FastAPI boundary for the LoopIn Foundry workflow."""

from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from foundry_workflow import run_foundry_workflow
from live_search import run_live_search_workflow


class LearnerProfile(BaseModel):
    name: str = Field(default="", max_length=40)
    year: Literal[
        "First year",
        "Second year",
        "Third year",
        "Final year",
        "Postgraduate",
        "Self-taught",
    ]
    location: Literal["India", "United States", "Europe", "Global"]
    stacks: list[str] = Field(min_length=1, max_length=8)
    goals: list[str] = Field(min_length=1, max_length=8)
    interests: list[str] = Field(min_length=1, max_length=10)


class PlanRequest(BaseModel):
    profile: LearnerProfile


app = FastAPI(title="LoopIn Foundry API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "loopin-foundry"}


@app.post("/api/plan")
async def create_plan(request: PlanRequest):
    try:
        profile = request.profile.model_dump()
        try:
            return await run_foundry_workflow(profile)
        except RuntimeError:
            return await run_live_search_workflow(profile)
    except Exception as exc:
        # Avoid leaking credentials, endpoints, or SDK internals to browser clients.
        raise HTTPException(
            status_code=502,
            detail="The Microsoft Foundry workflow could not complete the plan.",
        ) from exc
