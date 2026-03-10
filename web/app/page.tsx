import { EvaluationForm } from "../components/EvaluationForm";

export default function HomePage() {
  return (
    <>
      <div className="page-mesh" />
      <nav className="topbar">
        <a className="nav-logo" href="/">
          EthosGuard
        </a>
        <div className="nav-links">
          <a className="nav-link" href="#demo">
            Demo
          </a>
          <a className="nav-link" href="#engine">
            Engine
          </a>
          <a className="nav-cta" href="#demo">
            Run Evaluation
          </a>
        </div>
      </nav>
      <main>
        <div className="max-w">
          <section className="hero" id="top">
            <div className="hero-card">
              <div className="sec-tag">Rules-first AI alignment middleware</div>
              <h1 className="hero-title">
                Check agent actions before execution with <em>inspectable ethics decisions.</em>
              </h1>
              <p className="hero-desc">
                EthosGuard blocks harmful, deceptive, or exploitative actions before an
                autonomous system proceeds. Every verdict includes provenance, triggered
                principles, and extracted signals.
              </p>
              <div className="hero-actions">
                <a className="nav-cta" href="#demo">
                  Open Demo
                </a>
                <a className="ghost-cta" href="#engine">
                  How It Works
                </a>
              </div>
              <div className="hero-meta">
                <div className="meta-pill">No Harm</div>
                <div className="meta-pill">Radical Honesty</div>
                <div className="meta-pill">Protect the Vulnerable</div>
              </div>
            </div>
            <aside className="toc-card">
              <h2>Start Here</h2>
              <ul className="toc-links">
                <li>
                  <a href="#demo">1. Run the demo</a>
                </li>
                <li>
                  <a href="#engine">2. Review the engine</a>
                </li>
                <li>
                  <a href="#demo">3. Compare blocked and allowed cases</a>
                </li>
              </ul>
              <div className="notice">
                <strong>Best fit</strong>
                <p>
                  Demo mode is rules-first. The strongest portfolio path is to show one
                  blocked case, one risky case, and one allowed case with provenance.
                </p>
              </div>
            </aside>
          </section>

          <section className="section-block" id="engine">
            <div className="highlight-grid">
              <article className="highlight-card">
                <span className="highlight-stat">Stage 1</span>
                <h3>Normalize the request into inspectable signals.</h3>
                <p>
                  Scenario, action, and stakeholders are reduced into concrete cues for
                  harm, deception, privacy misuse, power asymmetry, and vulnerability.
                </p>
              </article>
              <article className="highlight-card">
                <span className="highlight-stat">Stage 2</span>
                <h3>Apply deterministic ethics rules first.</h3>
                <p>
                  Obvious harmful or deceptive cases are scored and blocked immediately
                  without needing model judgment.
                </p>
              </article>
              <article className="highlight-card">
                <span className="highlight-stat">Stage 3</span>
                <h3>Escalate only ambiguous cases to LLM fallback.</h3>
                <p>
                  Gray-zone scenarios use model assistance, while every response still
                  returns one stable contract with provenance.
                </p>
              </article>
            </div>
          </section>

          <section className="section-block" id="demo">
            <div className="section-head">
              <div className="sec-tag">Live Demo</div>
              <h2 className="section-title">
                Evaluate an AI action and inspect <em>why the verdict happened.</em>
              </h2>
              <p className="section-desc">
                Use the seeded examples for a clean demo flow. The strongest sequence is
                blocked first, then allowed, with the provenance panel visible in both.
              </p>
            </div>
            <EvaluationForm />
          </section>
        </div>
      </main>
    </>
  );
}
