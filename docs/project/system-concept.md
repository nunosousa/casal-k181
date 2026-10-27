# System concept description

Status: draft operational concept. See the [engineering framework](engineering.md)
for document authority and the [requirements](requirements.md) for acceptance
statements.

## Intended use and boundary

A restored Casal K181 for occasional Sunday riding and repeatable engineering
experiments. Preserve its mechanical and visual character while exploring
performance, drivability, efficiency, reliability and refinement. This is not
a race vehicle or a certification programme.

The system includes the M151-derived piston-port two-stroke, Eurocilindro
top end, five-speed gearbox, induction and ignition, charging and battery,
PDM, ECU, three instrument controllers, dashboard, lamps, sensors and harness.
Rider, workshop tools, HIL controller and analysis host are external actors.
Mechanical condition, lubrication, rider behaviour and weather remain
important external conditions for electronic control and measurements.

Four intelligent nodes communicate over CAN: ECU, speedometer/odometer,
tachometer and warning cluster. Each instrument controller is inside its
own stock-style enclosure. The speedometer owns its display and odometer;
the tachometer owns its RPM display. Remaining dashboard/handlebar functions
(switchgear, twistgrip TPS, GPS, ambient light and shared brightness) belong
to the warning cluster. The ECU retains engine and exterior-lamp logic;
PDM retains power switching/distribution without another MCU. See
[ADR-0012](decisions/0012-distributed-dashboard-can-nodes.md) and the
[system architecture](../architecture/system.md).

## Objectives

| ID | Objective |
|---|---|
| OBJ-01 | Preserve the K181's character and committed engine architecture. |
| OBJ-02 | Establish ECU-controlled ignition and progress from a fixed-timing baseline to calibrated control. |
| OBJ-03 | Provide predictable startup, fault handling and recovery without relying on the dashboard for continued engine control. |
| OBJ-04 | Provide electrical power, lighting and rider information appropriate to the intended use. |
| OBJ-05 | Preserve reproducible datasets to assess each subsystem change. |
| OBJ-06 | Explore crank-dynamics estimation, adaptive ignition and throttle-body injection without presuming benefit. |
| OBJ-07 | Support maintainable software, calibration and service operations. |

## Operational modes

These are behavioural modes, not a mandated software enumeration. Detailed
entry guards, deadlines and transition implementation remain SAD work.

| Mode | Entry / exit | Required behaviour and open issues |
|---|---|---|
| Off | Rider shutdown or absent power; leave on a valid power/start request | Engine outputs inactive; standby budget and wake semantics require definition. |
| Boot | Stable rail/reset; leave when control is ready or recovery is selected | Initialise safe outputs, validate configuration/image and arm acquisition; engine readiness must not wait for CAN discovery. |
| Cranking | Valid crank activity below running criteria; leave on confirmed running, stop or fault | Acquire synchronisation; permit scheduled ignition only with valid state. Injection requires its own pressure and calibration readiness. |
| Running | Valid running criteria; leave on stop, stall, fault or loss of supply | Apply the selected validated calibration; acquire, log and broadcast state. |
| Degraded | A classified fault permits continued operation; leave on recovery or shutdown | Warn and apply only a validated fallback. Not every fault is ride-through capable. |
| Stopped / stalled | Engine-stop request or cessation of crank activity; restart through cranking | Cancel engine outputs; injection pump/prime exceptions and stop detection latency are unresolved. |
| Service / recovery | Deliberate service selection or unusable application images; leave via controlled restart | Engine actuation inhibited; support update, diagnosis and calibration. |

Running/cranking thresholds, stall timeout, recovery hysteresis and
mode-transition priorities are open in the [requirements parameter register](requirements.md#open-acceptance-parameters).
Loss of crank synchronisation may occur while the engine is still rotating;
it must not be confused with ordinary off mode.

## Representative scenarios

- After seasonal storage, inspect the vehicle, then kick-start with a
  healthy battery. Validate the separate flat/BMS-isolated battery scenario
  on the bench before claiming emergency starting capability.
- Ride with required exterior lighting and dashboard information.
  A lost dashboard link must be handled without blindly using stale
  control inputs; rider-stop availability needs explicit review.
- An individual gauge reset/update does not stop the other instruments.
  Warning-cluster loss also removes rider inputs, TPS and GPS; test that
  case separately from a gauge loss and from a shorted common bus.
- On a calibration fault, continue only with a validated applicable
  fallback. An ignition-only fallback does not establish injection safety.
- In the workshop, enter service mode with engine outputs inhibited,
  update software/calibration and recover from an interrupted update.
- For an experiment, preserve the reference configuration, change one
  subsystem where possible and compare accepted sessions.

## Experiments, not promised outcomes

| ID | Hypothesis / question | Decision evidence |
|---|---|---|
| EXP-01 | Does crank angular-velocity variation provide useful engine-state information? | Define signal quality, reference measurements and usefulness criteria before phase 7; a negative result is valid. |
| EXP-02 | Does model-based/adaptive ignition improve on the validated mapped configuration? | Phase-7 evidence, bounded control behaviour and paired phase-8 comparisons; retain mapped control if not justified. |
| EXP-03 | Does throttle-body injection improve starting, response, economy or other measured behaviour over the carburettor? | Phase-9 feasibility and safety gates followed by controlled comparisons with unchanged ignition and engine hardware. |

The [staged plan](staged-plan.md) orders these investigations. Their safety
and data-preservation requirements apply even if the hypothesis is rejected.
