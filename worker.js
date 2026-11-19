importScripts("https://cdn.jsdelivr.net/pyodide/v0.27.2/full/pyodide.js");

const PY_FILES = ["gamemechanics.py", "strategy.py", "simulator.py"];

async function init() {
  const pyodide = await loadPyodide();

  // Copy your unchanged .py files into Pyodide's virtual filesystem.
  for (const name of PY_FILES) {
    const response = await fetch(name);
    if (!response.ok) throw new Error(`Could not load ${name}`);
    pyodide.FS.writeFile(name, await response.text());
  }

  // Small adapter: calls your run_monte_carlo and returns JSON for the page.
  pyodide.runPython(`
import json
from simulator import run_monte_carlo

def run_json(num_rounds, strategy, seed):
    r = run_monte_carlo(num_rounds=num_rounds, strategy=strategy, seed=seed)
    r.pop("rules", None)  # dataclass, not JSON-serialisable
    if r["shoe_count"] < 30:  # NaN is not valid JSON
        r["house_edge_ci_95_pct"] = None
        r["player_return_ci_95_pct"] = None
    return json.dumps(r)
`);
  return pyodide.globals.get("run_json");
}

const ready = init();
ready.then(
  () => postMessage({ type: "ready" }),
  (err) => postMessage({ type: "error", message: String(err) })
);

onmessage = async ({ data }) => {
  try {
    const runJson = await ready;
    const started = performance.now();
    const json = runJson(data.numRounds, data.strategy, data.seed);
    postMessage({ type: "result", json, elapsedMs: performance.now() - started });
  } catch (err) {
    postMessage({ type: "error", message: String(err) });
  }
};
