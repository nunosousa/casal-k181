# Sensor installation

Physical installation procedures for the on-engine and on-handlebar
sensors that are not covered in their own documents. Covers EGT bung,
CHT thermocouple, TPS satellite PCB, ambient sensor vent, and IMU
orientation calibration.

Trigger wheel and front wheel-speed target have dedicated docs:

- [Trigger wheel](trigger-wheel.md)
- [Wheel-speed target](wheel-speed-target.md)

## 1. EGT thermocouple

### 1.1 Location

- **On the exhaust pipe, ~50 mm downstream of the exhaust flange.**
  Close enough to the port that response time is short and the
  reading reflects combustion; far enough that the bung's local
  metal mass doesn't cool the tip significantly.
- Rejected: inside the pipe closer than 25 mm (excessive thermal
  cycling stresses the thermocouple; harder to weld a bung there).
- Rejected: at the muffler outlet (too cool, too slow, unrepresentative).

### 1.2 Bung

- **Thread:** M8 × 1 preferred (compatible with common EGT probes
  including automotive VDO and PWM types). 1/8" NPT acceptable for
  US-sourced probes.
- **Material:** 304 or 316 stainless steel. Not mild steel — the
  bung sees repeated thermal cycling to 700+ °C.
- **Angle:** perpendicular to the pipe axis, with the bung centreline
  pointing radially inward through the pipe wall.
- **Depth:** the tip of the installed thermocouple should protrude
  5-10 mm into the gas flow. The bung's inside face is flush with the
  pipe inner wall.

### 1.3 Welding

- **TIG-weld** the bung to the pipe with 308L filler (for 304/316 SS).
- **All-around** weld — no gaps.
- **Post-weld inspection:** visual for undercut or porosity; pressure
  test the completed exhaust system with soapy water and shop air.

Do not braze or silver-solder — sustained temperature exceeds
solder-joint strength.

### 1.4 Thermocouple

- **Type:** K-type (chromel–alumel), sheathed grounded-junction
  probe, 1/16" (1.6 mm) diameter tip.
- **Sheath material:** Inconel 600 or 316 SS. Inconel is preferred
  for the sustained-temperature life.
- **Compression fitting** built into the bung side of the probe seals
  and clamps the probe at the desired insertion depth.
- **Cable:** K-type compensating cable, twisted-shielded, PTFE or
  fibreglass insulation for local high-temperature routing. Length
  sufficient to reach the ECU harness connector.

### 1.5 Wiring

- **K-type polarity:** chromel positive (yellow in ANSI, green in
  IEC 60584), alumel negative (red in ANSI, white in IEC 60584).
  Verify at install — swapped polarity causes very wrong readings.
- **Route the cable** away from the exhaust pipe once past the bung;
  running it along the pipe damages insulation.

## 2. CHT thermocouple

Two candidate installations. Choice deferred to phase 1 bench
comparison; provisional preference is (A).

### 2.1 Option A: Spark-plug washer thermocouple

- **Form:** ring thermocouple with an inside diameter matching the
  sparkplug thread OD (~10 mm ID for the standard sparkplug), thin
  (~1.5 mm thick), K-type leads exiting radially.
- **Install:** under the sparkplug, on the head. The plug's crush
  washer is either omitted (ring replaces it) or retained above the
  ring.
- **Cable exit:** angled away from the exhaust side; secured with a
  small P-clip to the head to prevent snagging.
- **Response time:** ~5 s to 63 % of a step — fast enough for our
  1 Hz sampling.

### 2.2 Option B: Head-fin thermistor

- **Form:** NTC thermistor (100 kΩ at 25 °C, e.g. Vishay NTCLE100)
  in a small brass or aluminium pill.
- **Install:** threaded into an M6 tapped hole in a cooling fin near
  the sparkplug. Head machining required.
- **Response time:** ~30 s to 63 % — slower, but adequate.
- **Trade-off:** more thermal isolation from combustion (measures
  metal temperature at the fin, not near the plug); requires head
  machining that is not otherwise necessary.

**Working preference:** Option A. Bench-compare in phase 1 and revise
if response is inadequate.

## 3. TPS satellite PCB

### 3.1 Function

Contactless magnetic rotary sensor at the throttle twistgrip.
Measures the twistgrip angle (0-90° typical) and reports over I2C to
the handlebar controller. See
[handlebar-controller §7](../architecture/handlebar-controller.md).

### 3.2 Components

- **Sensor IC:** AS5600 12-bit magnetic rotary encoder (or AS5600L
  for the 5V variant if the local rail is 5V).
- **Small PCB:** 15 × 15 mm, sensor centred, JST-GH 4-pin connector
  on the edge (VCC, SDA, SCL, GND).
- **Magnet:** 6 mm diameter × 2.5 mm thick, N42 grade, diametrically
  magnetised (poles across the diameter, not axial).

### 3.3 Mechanical

- **Bracket:** small aluminium or 3D-printed piece bolted to the
  handlebar clamp, positioning the AS5600 sensor face parallel to
  the axis of the twistgrip, ~1 mm from the magnet.
- **Magnet mount:** an aluminium end-cap fits over the inner end of
  the throttle grip's cable-drum extension, glued to it, with the
  magnet epoxied into a recess in the end-cap centred on the drum's
  axis of rotation.
- **Air gap:** 1.0-2.0 mm nominal; magnet-to-sensor gap tolerated by
  AS5600 up to ~3 mm.

### 3.4 Wiring

- **Cable:** 4-conductor shielded, JST-GH-terminated satellite side,
  connector-appropriate handlebar-controller side.
- **Length:** ~30 cm from twistgrip to handlebar controller in the
  headlight nacelle.
- **Routing:** through the switchgear housing on the handlebar,
  down the handlebar tube, into the headlight nacelle.

### 3.5 Calibration

At first install:

1. Rotate throttle to closed position (idle stop).
2. In handlebar service view, read `tps_raw_deg` — record as
   `tps_zero_deg`.
3. Rotate throttle to fully open (against the WFO stop).
4. Read `tps_raw_deg` — record as `tps_full_deg`.
5. Store both in the handlebar config store.

TPS percentage = `(raw − zero) / (full − zero) × 100`, clamped to
[0, 100].

Re-calibrate any time the throttle cable is adjusted, the twistgrip
is disassembled, or the magnet position changes.

## 4. Ambient sensor (BME280)

### 4.1 Location

- **On the ECU PCB**, inside the enclosure.
- Not on the vehicle exterior directly. The ECU enclosure provides
  the mechanical mount; a vented port equalises to outside conditions.

### 4.2 Vent

- **Small hooded port** on the enclosure, ~5 mm diameter aperture.
- **Membrane:** Gore-Tex PTFE microporous film or equivalent (e.g.
  Gore PMF Series). Allows pressure and vapour equalisation, blocks
  liquid water.
- **Hood:** small rain cap over the aperture, oriented downward,
  prevents direct splash.
- **Placement on ECU enclosure:** on a side that is not the direct
  spray direction and not adjacent to the engine (avoiding heat
  soak).

### 4.3 Airflow inside the enclosure

- The BME280 sits ideally on a small standoff above the PCB, not
  buried in dense components.
- **Heat sources inside the ECU** (buck converter, IGBT gate driver,
  MCU) can locally heat the BME280 by several °C. Firmware applies
  a static calibration correction; if that's not enough, phase 2
  work may relocate the sensor.

### 4.4 Calibration

- **Temperature offset:** measured at first install against an
  external reference thermometer. Store as `ambient_temp_offset_c`.
- **Pressure:** cross-check against a known-good reference on a
  quiet-air day; store `ambient_pressure_offset_pa`. Typically zero
  for BME280.
- **Humidity:** no calibration for phase 1.

## 5. IMU orientation

The IMU (ICM-42688) is soldered to the ECU PCB. Its orientation on the
vehicle depends on how the ECU is mounted, which depends on frame
geometry.

### 5.1 Frame calibration

At first install:

1. Position the vehicle on level ground with the front wheel aligned
   forward.
2. Rider absent; vehicle held vertical by a stand.
3. In ECU service view, log 5 seconds of IMU output.
4. Solve for the rotation matrix that maps ECU-frame accel to vehicle-
   frame `[0, 0, -9.81]` at rest.
5. Store the 3×3 rotation matrix as `imu_vehicle_rotation` in the
   config store.

Firmware applies this rotation on every IMU sample before use in
grade correction and log output.

### 5.2 Re-calibration

Required after any ECU-enclosure re-mount. Not required for enclosure
re-open with same mount.

## 6. Cable management

- **Sensor cables run in the vehicle harness**, sharing a single
  cloth-over-braided loom where visible for the period aesthetic.
- **All connectors sealed** at the ECU and handlebar controller
  entry points per the connector specifications in
  [ecu.md §9](../architecture/ecu.md) and
  [handlebar-controller.md §11](../architecture/handlebar-controller.md).
- **No exposed sensor wiring** on the outside of the vehicle beyond
  the immediate sensor-to-bracket run.

## 7. Verification

Each sensor installation is verified before the vehicle is closed up:

- **EGT:** heat the bung with a torch briefly (up to ~200 °C); verify
  ECU reads consistent rising values.
- **CHT:** touch the sparkplug or head with a hot soldering iron
  briefly; verify reading response.
- **TPS:** rotate throttle full range; verify smooth 0-100 %
  reporting, no discontinuities.
- **Ambient:** compare against a room thermometer at power-on.
- **IMU:** roll and pitch the vehicle by hand; verify the IMU frame
  output matches expected vehicle-frame accelerations.

## 8. Open questions

- **CHT sensor option** (A vs B) — pinned after bench comparison.
- **BME280 heat-soak correction** — may need active handling in
  firmware if the static offset proves inadequate.
- **Whether to add an ambient light sensor** to the handlebar (for
  auto-dim) or to the ECU. Handlebar makes more sense; captured in
  [handlebar-controller.md open questions](../architecture/handlebar-controller.md).

## 9. Related

- [ECU subsystem §5](../architecture/ecu.md)
- [Handlebar controller §7-8](../architecture/handlebar-controller.md)
- [Trigger wheel](trigger-wheel.md)
- [Wheel-speed target](wheel-speed-target.md)
