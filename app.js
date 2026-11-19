const $ = (id) => document.getElementById(id);
const fmt = (n, d = 2) =>
  n.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
const signed = (n, d = 2) => (n > 0 ? "+" : "") + fmt(n, d);
const int = (n) => n.toLocaleString("en-US");

const NOTES = {
  basic_strategy: "Rule-matched basic strategy for this table. It is not a GTO solver.",
  aggressive: "Experimental heuristic: splits every eligible pair, doubles hard totals 9–11, and otherwise hits below 17.",
  conservative: "Experimental heuristic: never splits, doubles 11, and stands on 15+.",
};

const worker = new Worker("worker.js");
let chart = null;

function setStatus(text) { $("status").textContent = text; }

$("rounds").addEventListener("input", () => {
  $("rounds-value").textContent = int(Number($("rounds").value));
});
$("strategy").addEventListener("change", () => {
  $("strategy-note").textContent = NOTES[$("strategy").value];
});
$("strategy-note").textContent = NOTES[$("strategy").value];

worker.onmessage = ({ data }) => {
  if (data.type === "ready") {
    $("run").disabled = false;
    setStatus("Ready.");
  } else if (data.type === "result") {
    $("run").disabled = false;
    setStatus(`Finished in ${fmt(data.elapsedMs / 1000, 1)} s.`);
    render(JSON.parse(data.json));
  } else if (data.type === "error") {
    $("run").disabled = false;
    setStatus(`Error: ${data.message}`);
  }
};

$("run").addEventListener("click", () => {
  const numRounds = Number($("rounds").value);
  const seed = Number($("seed").value);
  if (!Number.isInteger(seed) || seed < 0) {
    setStatus("Seed must be a whole number ≥ 0.");
    return;
  }
  $("run").disabled = true;
  setStatus(`Simulating ${int(numRounds)} starting rounds...`);
  worker.postMessage({ numRounds, strategy: $("strategy").value, seed });
});

function render(r) {
  const metrics = [
    ["Starting rounds", int(r.rounds)],
    ["Hand win rate", `${fmt(r.hand_win_rate)}%`],
    ["Net units won", signed(r.net_units_won)],
    ["Total wagered", fmt(r.total_wagered)],
    ["Hand wins", int(r.hand_wins)],
    ["Hand losses", int(r.hand_losses)],
    ["Hand pushes", int(r.hand_pushes)],
    ["Positive-net rounds", int(r.round_positive)],
    ["Negative-net rounds", int(r.round_negative)],
    ["Zero-net rounds", int(r.round_zero)],
    ["House edge / initial bet", `${signed(r.house_edge_pct, 3)}%`],
    ["House return / total action", `${signed(r.return_on_total_action_pct, 3)}%`],
  ];
  const grid = $("metrics");
  grid.replaceChildren();
  for (const [label, value] of metrics) {
    const card = document.createElement("div");
    card.className = "metric";
    const l = document.createElement("span");
    l.className = "label";
    l.textContent = label;
    const v = document.createElement("span");
    v.className = "value";
    v.textContent = value;
    card.append(l, v);
    grid.append(card);
  }

  if (r.house_edge_ci_95_pct) {
    const [low, high] = r.house_edge_ci_95_pct;
    $("ci").textContent =
      `Approximate 95% interval for house edge per initial bet: ${signed(low, 3)}% to ` +
      `${signed(high, 3)}%. Calculated across ${int(r.shoe_count)} shuffled shoes; ` +
      `this is not a guarantee.`;
  } else {
    $("ci").textContent =
      `Only ${r.shoe_count} shuffled shoes were used. Run more rounds for a useful uncertainty interval.`;
  }

  $("edge-text").textContent = `${signed(r.house_edge_pct, 3)}%`;
  $("action-text").textContent = fmt(r.total_wagered);
  $("results").hidden = false;
  drawChart(r.cumulative_player_return);
}

function drawChart(points) {
  if (chart) chart.destroy();
  const first = points[0][0];
  const last = points[points.length - 1][0];
  chart = new Chart($("chart"), {
    type: "line",
    data: {
      datasets: [
        {
          label: "Cumulative player return",
          data: points.map(([x, y]) => ({ x, y })),
          borderWidth: 1.5,
          pointRadius: 0,
        },
        {
          label: "Break-even",
          data: [{ x: first, y: 0 }, { x: last, y: 0 }],
          borderDash: [6, 4],
          borderWidth: 1,
          pointRadius: 0,
        },
      ],
    },
    options: {
      animation: false,
      maintainAspectRatio: false,
      scales: {
        x: { type: "linear", title: { display: true, text: "Starting rounds" } },
        y: { title: { display: true, text: "Player return per initial bet (%)" } },
      },
    },
  });
}
