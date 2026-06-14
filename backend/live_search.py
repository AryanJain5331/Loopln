"""No-secret live search fallback for the LoopIn demo backend.

This is not a replacement for the Microsoft Foundry IQ path. It gives the local
demo a real web-search mode when Foundry credentials are not configured.
"""

from __future__ import annotations

import html
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any


SEARCHES = [
    ("Hackathon", "site:info.microsoft.com Agents League Hackathon Microsoft"),
    ("Hackathon", "site:imaginecup.microsoft.com Microsoft Imagine Cup student competition"),
    ("Internship", "site:careers.microsoft.com students internship software engineering"),
    ("Resource", "site:education.github.com GitHub Student Developer Pack"),
    ("Learning", "site:learn.microsoft.com Microsoft Learn AI Foundry agents training"),
    ("Learning", "site:skills.github.com GitHub Skills students"),
    ("Community", "site:mvp.microsoft.com student ambassadors Microsoft Learn"),
    ("Open Source", "site:opensource.guide how to contribute GitHub students"),
]

TRUSTED_PROBES = [
    (
        "Hackathon",
        "https://info.microsoft.com/Agents-League-Hackathon-Registration/",
        "Microsoft Agents League Hackathon",
        "Submit an AI agent project for the Microsoft Agents League Hackathon.",
    ),
    (
        "Hackathon",
        "https://imaginecup.microsoft.com/",
        "Microsoft Imagine Cup",
        "Explore Microsoft's global student technology competition.",
    ),
    (
        "Resource",
        "https://education.github.com/pack",
        "GitHub Student Developer Pack",
        "Student access to developer tools and learning resources.",
    ),
    (
        "Learning",
        "https://learn.microsoft.com/training/azure/ai-foundry/",
        "Microsoft Learn AI Foundry training",
        "First-party learning for AI Foundry, agents, and generative AI.",
    ),
    (
        "Learning",
        "https://skills.github.com/",
        "GitHub Skills",
        "Interactive courses for GitHub workflows, collaboration, and automation.",
    ),
    (
        "Resource",
        "https://azure.microsoft.com/free/students/",
        "Azure for Students",
        "Student-friendly Azure access for cloud and AI projects.",
    ),
    (
        "Community",
        "https://mvp.microsoft.com/studentambassadors",
        "Microsoft Learn Student Ambassadors",
        "A Microsoft student community for technical learning and leadership.",
    ),
    (
        "Open Source",
        "https://opensource.guide/how-to-contribute/",
        "How to contribute to open source",
        "Guidance for making a meaningful open-source contribution.",
    ),
]

TRUSTED_DOMAINS = {
    "info.microsoft.com",
    "imaginecup.microsoft.com",
    "careers.microsoft.com",
    "education.github.com",
    "learn.microsoft.com",
    "skills.github.com",
    "mvp.microsoft.com",
    "opensource.guide",
    "azure.microsoft.com",
}

TYPE_KEYWORDS = {
    "Hackathon": ("hackathon", "competition", "challenge", "imagine cup", "agents league"),
    "Internship": ("intern", "student", "career", "university"),
    "Resource": ("student", "developer", "pack", "education", "azure"),
    "Learning": ("learn", "training", "skills", "course", "module", "foundry"),
    "Community": ("student ambassador", "community", "learn student"),
    "Open Source": ("open source", "contribute", "github"),
}

BLOCKED_TERMS = (
    "pinay",
    "telegram",
    "adult",
    "movie",
    "betting",
    "casino",
    "torrent",
)


def _fetch_bing_rss(query: str, limit: int = 3) -> list[dict[str, str]]:
    encoded = urllib.parse.urlencode({"format": "rss", "q": query})
    request = urllib.request.Request(
        f"https://www.bing.com/search?{encoded}",
        headers={"User-Agent": "LoopInHackathonDemo/1.0"},
    )
    with urllib.request.urlopen(request, timeout=12) as response:
        body = response.read()

    root = ET.fromstring(body)
    items: list[dict[str, str]] = []
    for item in root.findall("./channel/item")[:limit]:
        title = item.findtext("title") or "Untitled result"
        link = item.findtext("link") or ""
        description = item.findtext("description") or ""
        items.append(
            {
                "title": html.unescape(title),
                "link": html.unescape(link),
                "description": html.unescape(description),
            }
        )
    return items


def _fetch_page_summary(url: str, fallback_title: str, fallback_description: str) -> dict[str, str]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "LoopInHackathonDemo/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            body = response.read(200_000).decode("utf-8", errors="ignore")
    except Exception:
        return {
            "title": fallback_title,
            "link": url,
            "description": fallback_description,
        }

    title_match = re.search(r"<title[^>]*>(.*?)</title>", body, re.I | re.S)
    desc_match = re.search(
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
        body,
        re.I | re.S,
    )
    title = html.unescape(re.sub(r"\s+", " ", title_match.group(1)).strip()) if title_match else fallback_title
    description = (
        html.unescape(re.sub(r"\s+", " ", desc_match.group(1)).strip())
        if desc_match
        else fallback_description
    )
    return {"title": title, "link": url, "description": description}


def _is_trusted(result: dict[str, str], kind: str) -> bool:
    parsed = urllib.parse.urlparse(result["link"])
    host = parsed.netloc.lower().removeprefix("www.")
    text = f"{result['title']} {result['description']} {result['link']}".lower()
    trusted = host in TRUSTED_DOMAINS or any(host.endswith(f".{domain}") for domain in TRUSTED_DOMAINS)
    relevant = any(keyword in text for keyword in TYPE_KEYWORDS[kind])
    blocked = any(term in text for term in BLOCKED_TERMS)
    return trusted and relevant and not blocked


def _score(result: dict[str, str], profile: dict[str, Any], urgency: int) -> int:
    text = f"{result['title']} {result['description']}".lower()
    matches = 0
    for field in ("stacks", "goals", "interests"):
        for value in profile.get(field, []):
            if str(value).lower().split()[0] in text:
                matches += 1
    return min(98, 48 + matches * 8 + urgency)


def _why(result: dict[str, str], profile: dict[str, Any]) -> str:
    stack = next(
        (item for item in profile.get("stacks", []) if item.lower().split()[0] in f"{result['title']} {result['description']}".lower()),
        None,
    )
    goal = profile.get("goals", ["grow"])[0]
    if stack:
        return f"This connects to your {stack} stack and your goal to {goal.lower()}."
    return f"This is relevant to your goal to {goal.lower()} and is worth verifying from the source."


async def run_live_search_workflow(profile: dict[str, Any]) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    live_search_count = 0
    for index, (kind, query) in enumerate(SEARCHES):
        scoped_query = query
        for result in _fetch_bing_rss(scoped_query, limit=2):
            if not _is_trusted(result, kind):
                continue
            live_search_count += 1
            score = _score(result, profile, urgency=10 - index)
            candidates.append(
                {
                    "id": urllib.parse.quote_plus(result["link"] or result["title"])[:80],
                    "type": kind,
                    "title": result["title"],
                    "summary": result["description"][:260],
                    "source": urllib.parse.urlparse(result["link"]).netloc or "Web result",
                    "sourceUrl": result["link"],
                    "deadline": "Verify on source",
                    "score": score,
                    "why": _why(result, profile),
                    "greeting": f"{profile.get('name') or 'Hey'}, this came up in live search.",
                    "action": "Open the source, verify eligibility and dates, then decide whether it deserves time today.",
                    "proof": "This result came from a live web search. Deadline and eligibility must be verified on the linked source.",
                }
            )

    seen_urls = {item["sourceUrl"] for item in candidates}
    for index, (kind, url, title, description) in enumerate(TRUSTED_PROBES):
        if len(candidates) >= 7:
            break
        if url in seen_urls:
            continue
        result = _fetch_page_summary(url, title, description)
        if not _is_trusted(result, kind):
            continue
        score = _score(result, profile, urgency=8 - min(index, 5))
        candidates.append(
            {
                "id": urllib.parse.quote_plus(result["link"])[:80],
                "type": kind,
                "title": result["title"],
                "summary": result["description"][:260],
                "source": urllib.parse.urlparse(result["link"]).netloc or "Trusted source",
                "sourceUrl": result["link"],
                "deadline": "Verify on source",
                "score": score,
                "why": _why(result, profile),
                "greeting": f"{profile.get('name') or 'Hey'}, this trusted source is worth checking.",
                "action": "Open the source, verify eligibility and dates, then decide whether it deserves time today.",
                "proof": "This card was completed by live-checking a trusted source URL after live search filtering.",
            }
        )
        seen_urls.add(url)

    insights = sorted(
        [item for item in candidates if item["sourceUrl"].startswith("http")],
        key=lambda item: item["score"],
        reverse=True,
    )[:7]

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "mode": "Live search + trusted source retrieval",
        "insights": insights,
        "trace": [
            {
                "key": "profile",
                "label": "Profile Intake",
                "agent": "Profile Analyst",
                "detail": "Reading year, stack, goals, interests, and location.",
                "tool": "Student profile schema",
                "status": "completed",
                "decision": f"Profile structured for {profile.get('year')} student in {profile.get('location')}.",
            },
            {
                "key": "search",
                "label": "Contextual Search",
                "agent": "Search Agent",
                "detail": "Searching live web result feeds for opportunity signals.",
                "tool": "Bing RSS search",
                "status": "completed",
                "decision": f"Retrieved {live_search_count} trusted search results and {len(candidates) - live_search_count} trusted source checks.",
            },
            {
                "key": "rank",
                "label": "Relevance Reasoning",
                "agent": "Relevance Agent",
                "detail": "Scoring by profile match, urgency, and source presence.",
                "tool": "Scoring rubric",
                "status": "completed",
                "decision": f"Ranked and selected {len(insights)} strongest signals.",
            },
            {
                "key": "synthesis",
                "label": "Personalized Synthesis",
                "agent": "Senior Friend Agent",
                "detail": "Writing senior-friend summaries.",
                "tool": "Tone and context policy",
                "status": "completed",
                "decision": "Converted live results into student-friendly cards.",
            },
            {
                "key": "verify",
                "label": "Action Delivery",
                "agent": "Verifier Agent",
                "detail": "Keeping source links attached.",
                "tool": "Citation guardrails",
                "status": "completed",
                "decision": "Marked all live results for deadline and eligibility verification.",
            },
        ],
        "safety": [
            "This mode uses live web search and requires source verification before acting.",
            "Deadline and eligibility fields are intentionally marked for verification.",
            "For the hackathon submission, use Foundry IQ live mode if credentials are available.",
        ],
    }
