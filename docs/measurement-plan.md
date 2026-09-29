# Measurement plan

Primary methodology document. Defines what is measured, how, with what
accuracy, and under what conditions. Every experiment in
`docs/experiments/` references sections here.

## 1. Purpose and non-goals

Establish an evidence-based methodology for characterising the engine
and vehicle at each staged milestone (see
[staged plan](project/staged-plan.md)). The goal is to detect and
quantify the effect of one-variable-at-a-time subsystem changes with a
known error budget, using only road-test instrumentation and no dyno.

Non-goals:

- Absolute peak-power claims traceable to any external standard.
- Racing-grade timing precision.
- Certified measurement traceability.

## 2. Measurement objectives per phase

End-quantities produced at each staged milestone.

- **Phase 3 (ECU fixed-timing baseline):** power-at-wheel curve vs.
  RPM, fuel consumption at fixed cruise speeds, EGT vs. throttle vs.
  RPM, standing-start acceleration curves per gear, top-gear roll-on
  times.
- **Phase 4 (ECU mapped timing):** delta on all phase-3 quantities
  against the phase-3 baseline session.
- **Phase 5 (carburettor optimisation):** same set as phase 3, plus
  fuel consumption at multiple cruise speeds to characterise economy
  vs. jetting trade-offs.
- **Phase 6 (ignition refinement — load compensation, dwell):** same
  set, plus per-cycle ignition-diagnostic aggregates from CAN
  `ignition_diag`.
- **Phase 7 (crank-dynamics exploration):** exploratory. Not defined
  against a fixed end-quantity set; success criterion is whether the
  per-cycle Δω signal carries usable information about load,
  combustion phasing or misfire.

## 3. Test protocols

Each protocol is a repeatable procedure written to be executed
identically across sessions by a rider following the doc. All protocols
begin only after the session-acceptance criteria in §7 are met and the
engine is thermally soaked (CHT ≥ 60 °C for ≥ 60 s).

### 3.1 Coastdown

**Purpose:** fit the road-load function `F_road(v) = a + b·v + c·v²`
from measured vehicle deceleration in neutral coast. This function is
the foundation of every acceleration-based power inference — it is
executed at the start of every measurement campaign and re-executed
after any change plausibly affecting road load (tyre change,
significant mass change, fairing/bodywork modification).

**Procedure:**

1. Warm-up complete; enter the test stretch in the direction of the
   first run.
2. Accelerate to peak run speed (target 55-60 km/h or as high as legal
   and safe on the chosen stretch).
3. Simultaneously: pull the clutch in **and** shift to neutral. Both
   actions to eliminate any engine-braking contribution.
4. Coast, hands off throttle, rider posture fixed (upright, hands
   loose on the bars but on).
5. Continue to walking pace (5 km/h) or full stop.
6. Turn around, repeat in the opposite direction with the same peak
   speed target.
7. Repeat pairs until at least **4 valid pairs (8 runs)** logged.
8. Reject any run where the rider had to touch throttle or brake,
   another vehicle interfered, or peak-speed variation exceeded ± 10 %.

**Logged channels (event-driven capture from the ongoing session):**
wheel speed at 100 Hz, RPM (should be idle), GPS speed, IMU
acceleration (grade cross-check), ambient conditions, direction flag
manually entered before the run.

**Analysis:**

- For each run, compute `a(v) = dv/dt` with a 5 Hz low-pass filter
  applied to the wheel-speed trace.
- With vehicle+rider+fuel mass `m` (recorded per session), instantaneous
  deceleration force is `F(v) = -m·a(v)`.
- Combine all valid runs across directions; fit the quadratic
  `F_road(v) = a + b·v + c·v²` by least squares.
- Report fit residual and 95 % confidence bounds on each coefficient.
- If residual > 5 % of maximum force, reject the fit and re-run.

**Output:** road-load coefficients `a`, `b`, `c` and their
uncertainties, valid for the vehicle configuration at the time of
measurement. Stamped with a session ID that must match subsequent
acceleration runs to be used with them.

### 3.2 Standing-start acceleration

**Purpose:** wide-RPM-range power-at-wheel curves via `F_wheel = m·a +
F_road(v)`. Also characterises drivability (gear-change response, engine
transient recovery).

**Procedure:**

1. Position stationary at a marked start line on the test stretch.
2. Engine at idle, first gear engaged, clutch out (bike held on
   brakes).
3. Rider signals start; opens throttle to full and releases clutch at
   a defined RPM (target 3500 RPM — recorded in session log).
4. Hold full throttle in first gear until reaching a defined shift
   RPM (initially set at 6500 RPM; adjustable per bike config).
5. Upshift to second at the shift RPM; hold full throttle to the same
   shift RPM.
6. Continue through gears until reaching the fifth-gear shift point
   or the test-stretch end-line, whichever comes first.
7. Close throttle, brake to stop before end of stretch.
8. Turn around, repeat in opposite direction.
9. Repeat pairs until at least **3 valid pairs per configuration**.
   Wheelspin at launch, mis-shifts, or interference invalidate a run.

**Analysis:**

- For each run: extract v(t) trace, compute `a(v)` with 5 Hz filter.
- Compute `F_wheel(v) = m·a(v) + F_road(v)` using the coefficients from
  §3.1 for the same vehicle configuration.
- Compute `P_wheel(v) = F_wheel(v)·v`.
- Compute `P_engine ≈ P_wheel / η_drivetrain` using an assumed drivetrain
  efficiency (initial value 0.9; revisit if we ever measure it).
- Convert `v` to RPM using measured gearing per gear.
- Overlay curves from paired both-direction runs; per-direction curves
  should agree within run-to-run scatter (validate that grade/wind
  cancellation worked).
- Publish power vs. RPM curves per gear, and the aggregate envelope
  across all gears.

### 3.3 Fixed-throttle steady-state

**Purpose:** engine output at defined throttle openings across an RPM
range. Complements standing-start (transient) with steady-state data
that isolates open-loop mixture and timing effects from transient
enrichment or acceleration dynamics.

**Procedure:**

1. In a chosen gear, accelerate to a target RPM at a defined throttle
   opening (initial set: 25 %, 50 %, 75 %, 100 %).
2. Hold throttle opening constant; let vehicle speed settle.
3. Once speed variation is within ± 2 % over a 5 s window, log a
   **30 s steady segment** with all channels at their normal rates.
4. Move to the next RPM or throttle setting by re-accelerating.
5. Cover the RPM range in each gear by choosing gears that put steady
   speed within the road's legal envelope.
6. Repeat all conditions in the opposite direction.

**Analysis:**

- At steady state, engine power to wheel equals road-load power at
  that speed: `P_wheel_steady(v) = F_road(v)·v`.
- Combine with instantaneous EGT, CHT, TPS, timing (all logged) to
  produce steady-state map slices vs. RPM at each throttle opening.
- Compare directions; discard any 30 s window where speed drifted more
  than ± 2 %.

### 3.4 Top-gear roll-on

**Purpose:** fast, low-effort acceleration measurement at cruising
speeds. Useful for repeat A/B tests where the full standing-start
protocol is too heavy.

**Procedure:**

1. In top gear at a start speed of **30 km/h** (± 2 km/h).
2. Open throttle from cruise setting to full.
3. Hold full throttle to end speed of **55 km/h** (or the stretch
   end-line, whichever comes first).
4. Close throttle, brake to stop.
5. Turn around, repeat.
6. Repeat pairs until at least **5 valid pairs**.

**Analysis:**

- Extract v(t); compute time from 30→55 km/h per run.
- Report mean and standard deviation across paired runs.
- Compute `P_wheel(v)` at 40 km/h (mid-range point) as a single-point
  summary for quick A/B comparison.

### 3.5 Fuel-consumption cruise runs

**Purpose:** economy characterisation at fixed cruise speeds. Bench-
marked pre/post any change plausibly affecting fuel consumption
(jetting, ignition timing, ambient conditions).

**Procedure:**

1. Refuel the tank to the fill neck; record time and initial fuel
   mass (via workshop scale between runs, or by refilling to same
   line between runs).
2. Cruise the test stretch at target speed (initial set: 30 km/h,
   45 km/h, 60 km/h), repeated in both directions for at least 5
   round-trips per target speed.
3. Distance from wheel-speed integration and cross-checked against
   GPS.
4. On stretch end, brake and turn around promptly to keep run time
   dominated by steady-state cruise, not turnaround.
5. On session end, weigh remaining fuel; compute `L/100 km` per
   cruise speed.

**Analysis:**

- `L/100 km` at each cruise speed with 95 % confidence interval from
  run-to-run scatter.
- Cross-check consumed mass (start − end) against integrated
  consumption estimate from logged instantaneous throttle × idle-
  and full-map assumptions (order-of-magnitude sanity only).

## 4. Instrumentation

### 4.1 On-board sensor set (phase 1)

| Channel | Sensor | Sample rate | Notes |
|---|---|---|---|
| Front wheel speed | Hall + toothed target on brake hub | 100 Hz | Undriven wheel; no slip |
| Crank position | 36-1 Hall on crank trigger wheel | Event-driven | Up to ~4.8 kHz at 8000 RPM |
| RPM (derived) | — | 100 Hz normal, event-rate for high-detail | |
| EGT | K-type + weld-in bung, ~50 mm from exhaust port | 5 Hz | MAX31855, on-chip cold-junction |
| CHT | Plug-washer thermocouple or head-fin thermistor | 1 Hz | MAX31855 (K-type) unified with EGT if thermocouple used |
| Ambient T / P / RH | BME280 | 1 Hz | In cool airflow, vented port on ECU enclosure |
| Throttle position | AS5600 magnetic rotary at twistgrip | 100 Hz | Commanded, not slide position |
| Battery voltage | Divider on ECU | 10 Hz | |
| Bus voltage | Divider on ECU | 10 Hz | |
| GPS | u-blox NEO-M9N class, active antenna | 5 Hz position, 1 Hz fix state | Wired to handlebar controller |
| IMU | ICM-42688 or equivalent, on ECU PCB | 200 Hz | 6-axis |
| Ignition primary | On-driver sense of coil-drive V and I | 100 kHz windowed, event-triggered | ~2 ms per spark event |

### 4.2 Off-board / manual

- Handheld anemometer (~€50 class) — logged manually per session.
- Workshop scale (± 5 g) — fuel mass before and after fuel-
  consumption sessions; also total vehicle+rider mass at least once
  per session.
- Digital thermometer / IR — road-surface temperature at session
  start.
- Tyre-pressure gauge (± 0.1 bar) — read cold, before first run.
- Handheld GPS or phone app — as backup ground-track record.

### 4.3 Deferred sensors

- Wideband lambda — deferred beyond phase 4; two-stroke exhaust
  contamination shortens sensor life.
- MAP — deferred; unclear value on a naturally aspirated piston-port
  two-stroke.
- On-bike anemometer — deferred; handheld sufficient for phase 1.

## 5. Ambient and condition logging

Per-session record — logged automatically by the ECU wherever possible,
manually otherwise.

**Automatic (via ECU logs):**

- Ambient temperature, pressure, humidity — continuous 1 Hz.
- Bus and battery voltages.
- IMU-derived roll/pitch (grade cross-check).

**Manual (entered into a session-metadata form and stored with the
session):**

- Ambient wind mean and estimated gust, at site.
- Road-surface visual state (dry / damp / wet).
- Road-surface temperature (IR thermometer).
- Time-of-day range of the session (start, end).
- Fuel level at start and end.
- Rider clothed mass (± 0.5 kg).
- Tyre pressure front and rear (cold, ± 0.1 bar).
- Engine warm-up state before first run (CHT threshold met).
- Location: fixed test-stretch identifier (see §8).
- Vehicle configuration ID (a short tag identifying which subsystem
  build is under test — e.g. `p3-baseline-2026-10-15`).

The session-metadata form is a small YAML file the rider fills in
before the session; the ECU reads it via USB before the first run and
prepends it to the log session header.

## 6. Data schema and log format

### 6.1 On-device format

Custom binary append-only, written to the ECU's SPI NAND. Details in
[firmware.md §7](architecture/firmware.md). Summary:

- **Session header** at start of each session: session ID, start-of-
  session wall clock (from GPS if available, otherwise last-known),
  ECU FW version, handlebar FW version, channel table (name, type,
  scale, offset, unit, rate), session-metadata YAML blob.
- **Record blocks** of one NAND erase-block each: sequence number,
  record stream, trailer CRC.
- **Records:** timestamped in ECU monotonic microseconds. Two flavours:
  - Fixed-rate rows grouping all channels sharing a rate.
  - Event rows carrying a single event (fault, session boundary,
    manual mark from the rider).

### 6.2 Off-device conversion

Downloaded via USB (loader app). Converted to **MCAP** by a Python
tool in `tools/log-analysis/`. MCAP was chosen for the analysis side
because:

- Open format with a well-documented spec.
- Tool support: `foxglove` for visualisation, `mcap` Python bindings
  for programmatic analysis.
- Schema-per-channel is a natural fit for our channel table.
- Rich enough to carry the session metadata alongside the data.

Downstream analysis lives in Jupyter notebooks under
`tools/log-analysis/notebooks/` — one notebook per protocol, replicable
against any session log by pointing at its MCAP file.

### 6.3 Session identification

Each session gets a monotonically-increasing session ID from the
ECU's config store. External naming is `YYYYMMDD-HHMM-<config-tag>`
constructed by the download tool from the session header. Original
session ID retained for cross-reference.

## 7. Session acceptance criteria

A session is only used for cross-configuration comparison if all
conditions hold. Failing sessions may still be logged but are excluded
from published deltas.

| Condition | Threshold | Rationale |
|---|---|---|
| Ambient wind (mean) | ≤ 2 m/s | Aero-force error < ~10 % single-direction, < ~3 % paired |
| Wind gusts (peak − mean over 1 min) | ≤ 1 m/s | Uncancelled component in paired runs |
| Ambient temperature | 10–25 °C | Below: warm-up dominates, oil viscosity, tyre compound. Above: cooling margin, jetting drift |
| Ambient pressure | 980–1030 hPa | Extremes correlate with unstable weather |
| Relative humidity | ≤ 80 % | Above: road may be damp without visible moisture |
| Road surface | Visibly dry, no standing water | Rolling resistance and grip |
| Road grade (coastdown) | ≤ 0.5 % | Bounds gravitational error |
| Road grade (accel runs) | Any if paired both-ways and measured | Cancels |
| Engine thermal state before run | CHT ≥ 60 °C soaked | Excludes warm-up transient |
| Fuel level | Recorded ± 250 mL start and end | Mass known within ± 0.2 kg |
| Rider mass + gear | Recorded ± 0.5 kg per session | Mass known |
| Session duration | ≤ 3 h | Bounds surface-temp and ambient drift |

## 8. Test-stretch definition

### 8.1 Criteria for a suitable stretch

A test stretch is characterised **once**, then referred to by ID
forever. Requirements:

- **Legally rideable** at ≥ 60 km/h. Portuguese national and municipal
  road-speed rules apply.
- **Low traffic** on Sunday mornings, verified by rider observation
  across multiple visits.
- **Length:** ≥ 1500 m of usable straight-line running plus turnaround
  areas at each end.
- **Grade:** total elevation change over the measurement zone ≤ 0.5 %
  (± 7.5 m over 1500 m). Measured with GPS altitude cross-checked
  against a topographic map or a levelled reference.
- **Surface:** consistent asphalt, no seams, patches, or gravel
  transitions within the measurement zone.
- **Straight** enough that steering inputs during measurement are
  minimal (measurement zone deviation from a straight line ≤ 5 m
  transverse).
- **Sky view** for GPS (no dense tree canopy or urban canyons).
- **Turnaround areas** at each end wide enough to U-turn without
  disturbing residents or traffic.
- **Not near buildings, tunnels, bridges** that create wind shadows or
  local weather artefacts.

### 8.2 Site record

For each accepted stretch, produce a record under
`docs/experiments/sites/<site-id>.md` containing:

- Site ID (short kebab-case).
- Description and access notes.
- Start and end waypoints (GPS coordinates).
- Elevation profile (from GPS or topographic).
- Photos of markers (start, mid, end).
- Reference bearings and length as measured.
- Surface characterisation notes.
- Any known site-specific quirks.

### 8.3 Primary site

**TBD** — to be selected by rider inspection before the first
measurement session. One primary site expected to serve for all phase
1–4 measurement campaigns. Later phases may need additional sites
(e.g. a hill for altitude/density sensitivity).

## 9. Error budget

### 9.1 Sensor-level uncertainties (targets)

| Quantity | Uncertainty (± 1σ) | Source |
|---|---|---|
| Wheel speed (at reading) | 0.5 % | Timer capture resolution, tooth geometry |
| Vehicle+rider+fuel mass | 1 % | Scale, unaccounted items (tools, water bottle) |
| Grade (measured, per run) | 0.2 % | Cross-check between GPS altitude and IMU pitch |
| Uncancelled wind (paired) | 0.5 m/s | Gusts within acceptance window |
| Ambient density (post-J1349 correction) | 1 % | BME280 accuracy, model residual |
| Acceleration a(v) (5 Hz low-pass) | 2 % of a | Differentiation of filtered speed; filter phase lag |
| Fuel mass consumed | 5 g on 500 g (1 %) | Workshop scale |
| Ignition timing (measured, on bike) | 0.7° | Trigger geometry + Hall delay + firmware jitter + sync-calibration offset |
| EGT (K-type + MAX31855) | 5 °C + 0.5 % of reading | Thermocouple grade and cold-junction |

### 9.2 Propagated uncertainties on inferred quantities

**Road-load force `F_road(v)` at 20 m/s (~72 km/h)**, dominated by
coefficient uncertainty from the fit:

- Fit residual per coefficient: ~5 % from 8-run coastdown.
- Combined at 20 m/s: ~5 %.

**Force at wheel `F_wheel = m·a + F_road`** during acceleration at
20 m/s (`a` around 1 m/s²):

- Mass term contribution: `m·a` ≈ 100 N. Error ~1 % (mass) + 2 %
  (accel) ≈ 2.2 %.
- Road-load term: ~100 N. Error 5 %.
- Uncorrelated combination: √(2.2² + 5²) / 2 ≈ 2.7 % relative to sum.

**Power at wheel `P_wheel = F_wheel · v`:**

- Speed error 0.5 %, force error 2.7 %.
- Combined: ~2.8 % at 20 m/s.

**Peak power:** Add wind/day-to-day variance (paired runs cancel most).
Realistic reproducibility of peak power reading across sessions:
**± 5-8 %** (1σ).

**Fuel consumption `L/100 km`:** Fuel mass 1 %, distance 1 %,
uncorrelated: ~1.4 % per run. With N=5 paired repeats: ~0.6 %.
**Realistic session-level reproducibility: ± 2-3 %.**

### 9.3 Minimum detectable change

For a paired comparison at 95 % confidence:

- With ~7 % 1σ scatter on peak power and N=5 paired repeats, standard
  error of the mean is ~3.1 %. Minimum detectable effect is ~2·SE ≈
  6 %.
- With ~3 % scatter on fuel consumption and N=5, SE ~1.3 %. Minimum
  detectable effect ~3 %.
- With ~1° scatter on ignition timing accuracy, individual timing
  changes ≥ 2° are reliably detectable.

**Implications for the staged plan:**

- Phase 3 → phase 4 (mapped timing vs fixed): a well-designed map
  should yield ≥ 10 % gain in mid-range power. Well within detection.
- Phase 5 (carb optimisation): jetting changes may yield 2-5 % on
  peak power — near or below detection threshold. Fuel-consumption
  effects (~3-5 %) more likely to be detectable. **Expectation
  management: jetting effects may show best in fuel-consumption data,
  not peak-power curves.**
- Phase 6 (dwell/load-comp): incremental. Detection depends on the
  specific refinement.

If sub-detection changes matter, options are (a) increase N per
condition, (b) improve the coastdown fit with more runs, (c) reduce
wind sensitivity by testing only on very calm days.

## 10. Baseline test session definition per milestone

### 10.1 Phase 3 baseline (ECU fixed-timing)

Executed in **two or three sessions** at the primary site.

Per session:

- 8 coastdown runs (4 pairs).
- 3 pairs standing-start per gear × 5 gears = 30 runs.
- 4 fixed-throttle steady-state settings × 3 gears × 2 directions =
  24 runs.
- 5 pairs top-gear roll-on = 10 runs.
- 5 pairs cruise runs × 3 target speeds = 30 runs (fuel-consumption
  session — may be split into a separate second session).

Total per session ~100 runs. Achievable in a 3 h window if the site is
well-chosen; may split cruise-runs into a second session for less
rider fatigue.

Session is complete when all §7 criteria have been met throughout,
all four protocol families have valid data, and the coastdown fit
residual is ≤ 5 %.

### 10.2 Phase 4 baseline (mapped timing)

Same run set as phase 3, executed at the same primary site under
comparable ambient conditions. Fuel-consumption cruise runs performed
if any timing change plausibly affects economy.

Comparison: paired difference test on power-at-wheel curves at
mid-RPM points, and on fuel-consumption per cruise speed.

### 10.3 Phase 5+ baselines

To be specified as those phases are planned in detail. Same protocol
family expected; specific run counts and target speeds may vary based
on the change under test.

## 11. Related

- [Staged plan](project/staged-plan.md)
- [Constraints](project/constraints.md)
- [System architecture](architecture/system.md)
- [ECU subsystem](architecture/ecu.md)
- [CAN bus](architecture/can-bus.md)
- [Firmware](architecture/firmware.md)
