# Report schema

Skills that produce a visual report write a `report-data.json` file and render it with the bundled template:

```bash
python3 scripts/render_report.py report-data.json report.html
```

Paths are relative to the skill folder (`scripts/` and `assets/` sit next to `SKILL.md`). Without Python, copy `assets/report-template.html` and paste the JSON in place of `/*__REPORT_DATA__*/` (escape any `</` as `<\/`). The HTML is self-contained: no CDN, no fonts, no tracking. It works offline, in light and dark mode, and prints to PDF.

Write reports to `./sei-reports/<yyyy-mm-dd>-<skill>/` in the user's working directory unless they name another place. That folder holds company data: never commit it to a public repository.

## Top level

```json
{
  "eyebrow": "Build scorecard",
  "title": "Engineering effectiveness, Q3 2026",
  "subtitle": "Where we stand on AI leverage, effectiveness and return on engineering",
  "scope": { "teams": "All engineering (14 teams)", "timeframe": "Jul 1 – Sep 30, 2026", "comparison": "Previous quarter" },
  "summary": ["Three to five findings, most important first. **Bold** the number."],
  "decision": "The one decision this report asks the reader to make.",
  "kpis": [],
  "sections": [],
  "method": { "sources": [], "caveats": [], "links": [{ "text": "PR cycle time in Swarmia", "href": "https://app.swarmia.com/..." }] },
  "generatedAt": "2026-10-22"
}
```

`method` is required. Links must point at the real source page (a Swarmia `BuildAppLink`, a dashboard, a document in `company/`), never a guessed URL.

## KPI tiles

```json
{ "label": "PR cycle time (median)", "value": "19", "unit": "h", "delta": "−6 h vs Q2", "deltaDirection": "down-good", "status": "great", "note": "n = 1,240 PRs" }
```

- `deltaDirection`: `up-good`, `up-bad`, `down-good`, `down-bad`, `flat`. The colour follows whether the move is good, not its sign.
- `status`: `great`, `good`, `attention`, `unknown`. Always rendered with a label, never colour alone.
- Four to six tiles. One per decision-relevant number.

## Sections

```json
{ "title": "Where delivery waits", "body": "Markdown-lite: paragraphs, - bullets, **bold**, [links](https://...).", "charts": [], "after": "Optional text after the charts." }
```

## Chart types

Pick the form by the job (magnitude, composition, trend, status). One y-axis per chart, never two. Up to 8 series; fold the rest into "Other".

### `bar`: one value per category, optional benchmark bands

```json
{ "type": "bar", "title": "Median PR cycle time by team", "caption": "Last 90 days, weekends excluded",
  "unit": "h", "lowerIsBetter": true, "bands": { "great": 24, "good": 120 }, "colorByStatus": false,
  "categoryLabel": "Team", "valueLabel": "Median cycle time",
  "data": [ { "label": "Payments", "value": 18.2, "n": 210 }, { "label": "Platform", "value": 41, "n": 96, "note": "Two long-running migrations" } ] }
```

`bands` draws the Great / Good thresholds as reference lines and labels each bar. `reference: { "value": 30, "label": "Org median" }` adds one more line.

### `stacked`: composition per row (investment balance, cycle-time stages)

```json
{ "type": "stacked", "title": "Investment balance by team", "percent": true, "unit": "FTE",
  "series": ["New things", "Improving things", "Productivity", "KTLO"],
  "rows": [ { "label": "Payments", "values": [4.1, 1.2, 0.4, 2.3] } ] }
```

`percent: true` normalises each row to 100% and keeps raw values in the tooltip and table.

### `line`: trend over time

```json
{ "type": "line", "title": "AI-assisted share of merged PRs", "unit": "%", "x": ["Apr", "May", "Jun"],
  "series": [ { "name": "AI-assisted", "values": [54, 61, 70] } ], "reference": { "value": 82, "label": "Top quartile" } }
```

### `scorecard`: Build framework pillars

```json
{ "type": "scorecard", "title": "Build scorecard",
  "pillars": [ { "name": "AI leverage", "question": "Are we creating conditions for success for AI tools?",
    "groups": [ { "name": "AI adoption", "status": "good", "headline": "70% of merged PRs AI-assisted (top quartile: 82%)" } ] } ] }
```

### `table`

```json
{ "type": "table", "title": "Slowest pull requests",
  "columns": [ { "label": "PR", "link": true }, { "label": "Repository" }, { "label": "Cycle time", "num": true, "unit": "h" }, { "label": "Benchmark", "status": true } ],
  "rows": [ [ { "text": "#4211 Migrate billing jobs", "href": "https://github.com/..." }, "billing", 212, "attention" ] ] }
```

Every chart except `scorecard` and `table` gets a "Show table" toggle automatically, so no value depends on reading a colour.

## Units

`unit` accepts `h`, `d`, `min`, `s` (seconds, auto-humanised), `%`, `×` (multiplier), `$`, `€`, or any short label (`FTE`, `PRs`, `lines`). Convert MCP durations (seconds) before choosing `h` or `d`, or pass seconds with `"unit": "s"`.
