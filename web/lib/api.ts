export type ExampleScenario = {
  id: string;
  title: string;
  scenario: string;
  action: string;
  stakeholders: string[];
  expected_verdict: "allowed" | "risky" | "blocked";
};

export type EthicalCheckRequest = {
  scenario: string;
  action: string;
  stakeholders: string[];
};

export type EthicalCheckResponse = {
  ethical_verdict: "allowed" | "risky" | "blocked";
  risk_score: number;
  principles_triggered: string[];
  explanation: string;
  recommended_action: string;
  provenance: {
    evaluation_mode: "rules" | "llm_fallback";
    rules_matched: string[];
    llm_used: boolean;
    llm_model?: string | null;
    policy_version: string;
    confidence: number;
  };
  extracted_signals?: Record<string, boolean> | null;
};

type ApiErrorPayload = {
  detail?: string | { error?: string; message?: string };
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function fetchExamples(): Promise<ExampleScenario[]> {
  const response = await fetch(`${API_BASE_URL}/examples`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to load examples.");
  }
  return response.json();
}

export async function evaluateScenario(
  payload: EthicalCheckRequest,
): Promise<EthicalCheckResponse> {
  const response = await fetch(`${API_BASE_URL}/ethical_check`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    let errorMessage = "Evaluation request failed.";
    try {
      const payload = (await response.json()) as ApiErrorPayload;
      if (typeof payload.detail === "string") {
        errorMessage = payload.detail;
      } else if (payload.detail?.message) {
        errorMessage = payload.detail.message;
      }
    } catch {}
    throw new Error(errorMessage);
  }
  return response.json();
}
