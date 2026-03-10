import type { EthicalCheckResponse } from "../lib/api";

type ResultCardProps = {
  result: EthicalCheckResponse | null;
};

export function ResultCard({ result }: ResultCardProps) {
  if (!result) {
    return (
      <section className="panel">
        <div className="panel-inner">
          <p className="empty">
            Submit a scenario to inspect the verdict, risk score, triggered principles,
            provenance, and extracted signals.
          </p>
        </div>
      </section>
    );
  }

  const signals = result.extracted_signals
    ? Object.entries(result.extracted_signals).filter(([, value]) => value)
    : [];

  return (
    <section className="panel">
      <div className="panel-inner stack">
        <div className="meta">
          <span className={`badge ${result.ethical_verdict}`}>{result.ethical_verdict}</span>
          <div className="metric">
            <span className="metric-label">Risk score</span>
            <span className="metric-value">{result.risk_score.toFixed(2)}</span>
          </div>
        </div>

        <div className="metric">
          <span className="metric-label">Principles triggered</span>
          <ul className="list">
            {result.principles_triggered.length > 0 ? (
              result.principles_triggered.map((principle) => (
                <li key={principle} className="pill">
                  {principle}
                </li>
              ))
            ) : (
              <li className="pill">None</li>
            )}
          </ul>
        </div>

        <div className="kv">
          <div className="kv-row">
            <strong>Explanation</strong>
            <span>{result.explanation}</span>
          </div>
          <div className="kv-row">
            <strong>Recommended action</strong>
            <span>{result.recommended_action}</span>
          </div>
          <div className="kv-row">
            <strong>Provenance</strong>
            <span>
              Mode: {result.provenance.evaluation_mode} | Confidence:{" "}
              {result.provenance.confidence.toFixed(2)} | Policy:{" "}
              {result.provenance.policy_version}
            </span>
            <br />
            <span>
              LLM used: {String(result.provenance.llm_used)}
              {result.provenance.llm_model ? ` (${result.provenance.llm_model})` : ""}
            </span>
            <ul className="list" style={{ marginTop: 10 }}>
              {result.provenance.rules_matched.length > 0 ? (
                result.provenance.rules_matched.map((rule) => (
                  <li key={rule} className="pill">
                    {rule}
                  </li>
                ))
              ) : (
                <li className="pill">No deterministic rule hit</li>
              )}
            </ul>
          </div>
          <div className="kv-row">
            <strong>Extracted signals</strong>
            <ul className="list">
              {signals.length > 0 ? (
                signals.map(([key]) => (
                  <li key={key} className="pill">
                    {key}
                  </li>
                ))
              ) : (
                <li className="pill">No active signals</li>
              )}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
