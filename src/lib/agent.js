import { opportunities } from "../data/opportunities";

export const stages = [
  {
    key: "profile",
    label: "Profile Intake",
    detail: "Reading year, stack, goals, interests, and location.",
    agent: "Profile Analyst",
    tool: "Student profile schema",
  },
  {
    key: "search",
    label: "Contextual Search",
    detail: "Looking for hackathons, internships, tools, news, and learning updates.",
    agent: "Search Agent",
    tool: "Web Search / Foundry IQ",
  },
  {
    key: "rank",
    label: "Relevance Reasoning",
    detail: "Scoring by urgency, alignment, actionability, and source trust.",
    agent: "Relevance Agent",
    tool: "Scoring rubric",
  },
  {
    key: "synthesis",
    label: "Personalized Synthesis",
    detail: "Writing clear, senior-friend explanations instead of generic headlines.",
    agent: "Senior Friend Agent",
    tool: "Tone and context policy",
  },
  {
    key: "verify",
    label: "Action Delivery",
    detail: "Keeping source links attached and recommending the next move.",
    agent: "Verifier Agent",
    tool: "Citation guardrails",
  },
];

const wait = (duration) =>
  new Promise((resolve) => window.setTimeout(resolve, duration));

function intersectionCount(left, right) {
  return left.filter((value) => right.includes(value)).length;
}

function scoreOpportunity(item, profile) {
  const stackMatches = intersectionCount(item.stacks, profile.stacks);
  const goalMatches = intersectionCount(item.goals, profile.goals);
  const interestMatches = intersectionCount(item.interests, profile.interests);
  const locationMatch =
    item.locations.includes("Global") || item.locations.includes(profile.location);
  const yearBoost =
    profile.year === "First year" && ["Learning", "Community", "Resource"].includes(item.type)
      ? 2
      : 0;

  return Math.min(
    98,
    38 +
      stackMatches * 10 +
      goalMatches * 9 +
      interestMatches * 7 +
      (locationMatch ? 6 : 0) +
      item.urgency * 2 +
      yearBoost,
  );
}

function reasonFor(item, profile) {
  const stack = item.stacks.find((value) => profile.stacks.includes(value));
  const goal = item.goals.find((value) => profile.goals.includes(value));
  const interest = item.interests.find((value) => profile.interests.includes(value));

  if (stack && goal) {
    return `This lines up with your ${stack} skills and your goal to ${goal.toLowerCase()}.`;
  }
  if (interest && stack) {
    return `You marked ${interest.toLowerCase()}, and this connects directly to your ${stack} work.`;
  }
  if (goal) {
    return `This supports your goal to ${goal.toLowerCase()} without adding a lot of noise.`;
  }
  return "This is a credible, actionable signal for your current student profile.";
}

function buildBrief(profile) {
  return opportunities
    .map((item) => ({
      ...item,
      score: scoreOpportunity(item, profile),
      why: reasonFor(item, profile),
      greeting: `${profile.name || "Hey"}, this is worth your attention.`,
    }))
    .sort((a, b) => b.score - a.score || b.urgency - a.urgency)
    .slice(0, 7);
}

function buildDemoResponse(profile, mode = "Curated demo reasoning") {
  const insights = buildBrief(profile);

  return {
    generatedAt: new Date().toISOString(),
    mode,
    insights,
    trace: stages.map((stage, index) => ({
      ...stage,
      status: "completed",
      decision:
        index === 0
          ? `Profile structured for ${profile.year} student in ${profile.location}.`
          : index === 1
            ? `Retrieved ${opportunities.length} candidate signals across opportunities, tools, learning, and community.`
            : index === 2
              ? `Ranked by profile fit, urgency, actionability, and trusted sources.`
              : index === 3
                ? `Converted top matches into ${insights.length} senior-friend cards.`
                : "Attached source links and next actions so the student can verify before acting.",
    })),
    safety: [
      "Every card includes a source link for verification.",
      "Deadline-sensitive recommendations tell the student to verify official pages before applying.",
      "No login, history, or sensitive profile data is stored in demo mode.",
    ],
  };
}

export async function runLoopInAgent(profile, onStage) {
  const endpoint = import.meta.env.VITE_LOOPIN_API_URL;

  if (endpoint) {
    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ profile }),
      });

      if (!response.ok) {
        throw new Error("The LoopIn agent endpoint could not complete this brief.");
      }

      return response.json();
    } catch (error) {
      console.warn("LoopIn backend unavailable; using curated demo reasoning.", error);
      return buildDemoResponse(profile, "Curated demo reasoning (backend unavailable)");
    }
  }

  for (const stage of stages) {
    onStage(stage);
    await wait(540);
  }

  return buildDemoResponse(profile);
}
