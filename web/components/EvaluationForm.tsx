"use client";

import { useEffect, useState, useTransition } from "react";

import { ExamplePicker } from "./ExamplePicker";
import { ResultCard } from "./ResultCard";
import {
  evaluateScenario,
  fetchExamples,
  type EthicalCheckResponse,
  type ExampleScenario,
} from "../lib/api";

const DEFAULT_STATE = {
  scenario: "",
  action: "",
  stakeholders: "user, company",
};

export function EvaluationForm() {
  const [form, setForm] = useState(DEFAULT_STATE);
  const [examples, setExamples] = useState<ExampleScenario[]>([]);
  const [result, setResult] = useState<EthicalCheckResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  useEffect(() => {
    fetchExamples()
      .then(setExamples)
      .catch(() => setError("Could not load examples from the API."));
  }, []);

  function selectExample(exampleItem: ExampleScenario) {
    setForm({
      scenario: exampleItem.scenario,
      action: exampleItem.action,
      stakeholders: exampleItem.stakeholders.join(", "),
    });
    setResult(null);
    setError(null);
  }

  function updateField(field: "scenario" | "action" | "stakeholders", value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    startTransition(async () => {
      try {
        const response = await evaluateScenario({
          scenario: form.scenario,
          action: form.action,
          stakeholders: form.stakeholders
            .split(",")
            .map((item) => item.trim())
            .filter(Boolean),
        });
        setResult(response);
      } catch (submissionError) {
        console.error(submissionError);
        setResult(null);
        setError(
          submissionError instanceof Error
            ? submissionError.message
            : "The API could not evaluate this scenario.",
        );
      }
    });
  }

  return (
    <section className="grid">
      <div className="panel">
        <div className="panel-inner">
          <form className="stack" onSubmit={onSubmit}>
            <ExamplePicker examples={examples} onSelect={selectExample} />
            <p className="empty compact-note">
              Demo mode is rules-first. LLM fallback is only used for ambiguous cases when an
              OpenAI key is configured.
            </p>

            <div>
              <label className="label" htmlFor="scenario">
                Scenario
              </label>
              <textarea
                id="scenario"
                className="textarea"
                value={form.scenario}
                onChange={(event) => updateField("scenario", event.target.value)}
                placeholder="Describe the context the AI is operating in."
              />
            </div>

            <div>
              <label className="label" htmlFor="action">
                Planned action
              </label>
              <textarea
                id="action"
                className="textarea"
                value={form.action}
                onChange={(event) => updateField("action", event.target.value)}
                placeholder="Describe the exact action the agent wants to take."
              />
            </div>

            <div>
              <label className="label" htmlFor="stakeholders">
                Stakeholders
              </label>
              <input
                id="stakeholders"
                className="field"
                value={form.stakeholders}
                onChange={(event) => updateField("stakeholders", event.target.value)}
                placeholder="user, customer, company"
              />
            </div>

            {error ? <p className="error">{error}</p> : null}
            <button className="button" disabled={isPending} type="submit">
              {isPending ? "Evaluating..." : "Evaluate"}
            </button>
          </form>
        </div>
      </div>

      <ResultCard result={result} />
    </section>
  );
}
