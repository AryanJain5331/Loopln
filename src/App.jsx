import { useMemo, useState } from "react";
import { goalOptions, interestOptions, stackOptions } from "./data/opportunities";
import { runLoopInAgent, stages } from "./lib/agent";

const defaultProfile = {
  name: "",
  year: "Second year",
  location: "India",
  stacks: ["React", "Python"],
  goals: ["Prepare for internships", "Win hackathons"],
  interests: ["Hackathons", "AI agents", "Portfolio"],
};

function TogglePill({ active, children, onClick }) {
  return (
    <button
      type="button"
      className={`toggle-pill ${active ? "active" : ""}`}
      aria-pressed={active}
      onClick={onClick}
    >
      <span className="toggle-dot" />
      {children}
    </button>
  );
}

function ProfileForm({ profile, setProfile, onSubmit, busy }) {
  const toggle = (field, value) => {
    setProfile((current) => {
      const values = current[field];
      return {
        ...current,
        [field]: values.includes(value)
          ? values.filter((item) => item !== value)
          : [...values, value],
      };
    });
  };

  return (
    <form className="profile-panel" onSubmit={onSubmit}>
      <div className="panel-kicker">
        <span>01</span>
        Student profile
      </div>
      <h2>Tell LoopIn what matters to you.</h2>
      <p className="panel-copy">
        The agent uses your year, stack, goals, interests, and location to filter
        opportunities like a senior who knows your context.
      </p>

      <div className="field-grid">
        <label>
          <span>Your name</span>
          <input
            value={profile.name}
            onChange={(event) =>
              setProfile((current) => ({ ...current, name: event.target.value }))
            }
            placeholder="e.g. Aanya"
            maxLength={40}
          />
        </label>
        <label>
          <span>Current stage</span>
          <select
            value={profile.year}
            onChange={(event) =>
              setProfile((current) => ({ ...current, year: event.target.value }))
            }
          >
            <option>First year</option>
            <option>Second year</option>
            <option>Third year</option>
            <option>Final year</option>
            <option>Postgraduate</option>
            <option>Self-taught</option>
          </select>
        </label>
        <label>
          <span>Location</span>
          <select
            value={profile.location}
            onChange={(event) =>
              setProfile((current) => ({ ...current, location: event.target.value }))
            }
          >
            <option>India</option>
            <option>United States</option>
            <option>Europe</option>
            <option>Global</option>
          </select>
        </label>
      </div>

      <fieldset>
        <legend>Your toolkit</legend>
        <div className="toggle-grid">
          {stackOptions.map((stack) => (
            <TogglePill
              key={stack}
              active={profile.stacks.includes(stack)}
              onClick={() => toggle("stacks", stack)}
            >
              {stack}
            </TogglePill>
          ))}
        </div>
      </fieldset>

      <fieldset>
        <legend>Your goals</legend>
        <div className="toggle-grid">
          {goalOptions.map((goal) => (
            <TogglePill
              key={goal}
              active={profile.goals.includes(goal)}
              onClick={() => toggle("goals", goal)}
            >
              {goal}
            </TogglePill>
          ))}
        </div>
      </fieldset>

      <fieldset>
        <legend>Things you want to hear about</legend>
        <div className="toggle-grid">
          {interestOptions.map((interest) => (
            <TogglePill
              key={interest}
              active={profile.interests.includes(interest)}
              onClick={() => toggle("interests", interest)}
            >
              {interest}
            </TogglePill>
          ))}
        </div>
      </fieldset>

      <button
        className="primary-button"
        type="submit"
        disabled={
          busy ||
          profile.stacks.length === 0 ||
          profile.goals.length === 0 ||
          profile.interests.length === 0
        }
      >
        {busy ? "Finding your signals..." : "Loop me in"}
        <span aria-hidden="true">→</span>
      </button>
      <p className="privacy-note">No login · no stored history · sources stay attached</p>
    </form>
  );
}

function ReasoningPanel({ activeStage, trace }) {
  const currentIndex = stages.findIndex((stage) => stage.key === activeStage?.key);
  const complete = Boolean(trace);

  return (
    <section className="reasoning-panel" aria-live="polite">
      <div className="panel-kicker dark">
        <span>02</span>
        Reasoning pipeline
      </div>
      <div className="reasoning-heading">
        <div>
          <h2>{complete ? "Your signal brief is ready." : "Doing the senior-friend homework."}</h2>
          <p>
            {complete
              ? "The agent searched, ranked, synthesized, and attached sources."
              : activeStage?.detail || "Waiting for your profile."}
          </p>
        </div>
        <div className={`pulse-orb ${complete ? "complete" : ""}`}>
          <span>{complete ? "✓" : "AI"}</span>
        </div>
      </div>

      <div className="stage-list">
        {stages.map((stage, index) => {
          const isDone = complete || index < currentIndex;
          const isActive = index === currentIndex && !complete;
          const completedStage = trace?.find((item) => item.key === stage.key);
          return (
            <div
              key={stage.key}
              className={`stage-row ${isDone ? "done" : ""} ${isActive ? "active" : ""}`}
            >
              <span className="stage-state">{isDone ? "✓" : index + 1}</span>
              <div>
                <strong>{stage.label}</strong>
                <small>{completedStage?.decision || stage.detail}</small>
              </div>
              <span className="agent-tool">{stage.agent}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function InsightCard({ insight, onOpen }) {
  return (
    <article className="insight-card">
      <div className="card-topline">
        <span className={`type-icon type-${insight.type.toLowerCase().replace(" ", "-")}`}>
          {insight.type.slice(0, 1)}
        </span>
        <span className="card-type">{insight.type}</span>
        <span className="match-score">{insight.score}% match</span>
      </div>
      <p className="greeting">{insight.greeting}</p>
      <h3>{insight.title}</h3>
      <p className="card-summary">{insight.summary}</p>
      <div className="why-box">
        <span>Why this matters to you</span>
        <p>{insight.why}</p>
      </div>
      <div className="card-footer">
        <div>
          <small>Timing</small>
          <strong>{insight.deadline}</strong>
        </div>
        <button type="button" onClick={() => onOpen(insight)}>
          See next step <span>↗</span>
        </button>
      </div>
    </article>
  );
}

function DetailDrawer({ insight, onClose }) {
  if (!insight) return null;

  return (
    <div className="drawer-backdrop" role="presentation" onMouseDown={onClose}>
      <aside
        className="detail-drawer"
        role="dialog"
        aria-modal="true"
        aria-label={`${insight.title} details`}
        onMouseDown={(event) => event.stopPropagation()}
      >
        <button className="close-button" type="button" onClick={onClose} aria-label="Close">
          ×
        </button>
        <div className="drawer-label">{insight.type}</div>
        <h2>{insight.title}</h2>
        <p className="drawer-summary">{insight.summary}</p>

        <div className="drawer-section action-section">
          <span>Your next move</span>
          <p>{insight.action}</p>
        </div>
        <div className="drawer-section">
          <span>Why LoopIn selected it</span>
          <p>{insight.why}</p>
        </div>
        <div className="drawer-section">
          <span>Source check</span>
          <p>{insight.proof}</p>
        </div>

        <a className="source-button" href={insight.sourceUrl} target="_blank" rel="noreferrer">
          Open official source
          <span>↗</span>
        </a>
        <p className="source-caption">
          Verify dates and eligibility on {insight.source} before acting.
        </p>
      </aside>
    </div>
  );
}

function App() {
  const [profile, setProfile] = useState(defaultProfile);
  const [result, setResult] = useState(null);
  const [activeStage, setActiveStage] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(null);
  const [filter, setFilter] = useState("All");

  const types = useMemo(() => {
    if (!result) return [];
    return ["All", ...new Set(result.insights.map((insight) => insight.type))];
  }, [result]);

  const visibleInsights = useMemo(() => {
    if (!result || filter === "All") return result?.insights || [];
    return result.insights.filter((insight) => insight.type === filter);
  }, [filter, result]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setResult(null);
    setError("");
    setFilter("All");
    setActiveStage(stages[0]);

    try {
      setResult(await runLoopInAgent(profile, setActiveStage));
    } catch (agentError) {
      setError(agentError.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="site-header">
        <a className="brand" href="#top" aria-label="LoopIn home">
          <span className="brand-mark">L</span>
          <span>LoopIn</span>
        </a>
        <div className="header-note">
          <span className="status-dot" />
          Always in the loop, so you do not have to be
        </div>
        <a className="text-link" href="#workflow">
          Reasoning flow
        </a>
      </header>

      <main id="top">
        <section className="hero">
          <div className="eyebrow">
            <span>AI senior friend</span>
            <i />
            <span>Student opportunity intelligence</span>
          </div>
          <h1>
            Stay in the loop.
            <br />
            <em>Skip the noise.</em>
          </h1>
          <p>
            LoopIn finds hackathons, internships, tools, learning updates, and communities
            that match your profile, then explains why they matter in a senior-friend tone.
          </p>
          <div className="hero-proof">
            <span>Profile-aware ranking</span>
            <span>Visible reasoning</span>
            <span>Source-linked cards</span>
          </div>
        </section>

        <section className="workspace" id="workflow">
          <ProfileForm
            profile={profile}
            setProfile={setProfile}
            onSubmit={handleSubmit}
            busy={busy}
          />
          <ReasoningPanel activeStage={activeStage} trace={result?.trace} />
        </section>

        {error && <div className="error-banner">{error}</div>}

        {result && (
          <section className="results-section">
            <div className="results-heading">
              <div>
                <div className="panel-kicker">
                  <span>03</span>
                  Personalized brief
                </div>
                <h2>
                  {profile.name ? `${profile.name}, here’s` : "Here’s"} what deserves
                  your attention.
                </h2>
                <p>
                  Ranked against your year, stack, goals, interests, and location. Open
                  any card for evidence and a concrete next step.
                </p>
              </div>
              <div className="result-meta">
                <strong>{result.insights.length}</strong>
                <span>signals found</span>
                <small>{result.mode}</small>
              </div>
            </div>

            <div className="filter-row" aria-label="Filter insights">
              {types.map((type) => (
                <button
                  key={type}
                  type="button"
                  className={filter === type ? "active" : ""}
                  onClick={() => setFilter(type)}
                >
                  {type}
                </button>
              ))}
            </div>

            <div className="insight-grid">
              {visibleInsights.map((insight) => (
                <InsightCard key={insight.id} insight={insight} onOpen={setSelected} />
              ))}
            </div>

            <section className="safety-section">
              <div className="panel-kicker">
                <span>✓</span>
                Reliability and safety
              </div>
              {result.safety.map((item) => (
                <p key={item}>{item}</p>
              ))}
            </section>
          </section>
        )}
      </main>

      <footer>
        <div className="brand muted">
          <span className="brand-mark">L</span>
          <span>LoopIn</span>
        </div>
        <p>Opportunity should depend on potential, not proximity to the right network.</p>
        <span>Prototype · 2026</span>
      </footer>

      <DetailDrawer insight={selected} onClose={() => setSelected(null)} />
    </div>
  );
}

export default App;
