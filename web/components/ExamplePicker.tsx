"use client";

type ExampleScenario = {
  id: string;
  title: string;
  scenario: string;
  action: string;
  stakeholders: string[];
  expected_verdict: "allowed" | "risky" | "blocked";
};

type ExamplePickerProps = {
  examples: ExampleScenario[];
  onSelect: (exampleItem: ExampleScenario) => void;
};

export function ExamplePicker({ examples, onSelect }: ExamplePickerProps) {
  return (
    <div className="stack">
      <span className="label">Seeded examples</span>
      <div className="examples">
        {examples.map((exampleItem) => (
          <button
            key={exampleItem.id}
            className="chip"
            type="button"
            onClick={() => onSelect(exampleItem)}
          >
            {exampleItem.title}
          </button>
        ))}
      </div>
    </div>
  );
}
