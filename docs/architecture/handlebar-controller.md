# Former handlebar controller architecture

The central handlebar controller is superseded by
[ADR-0012](../project/decisions/0012-distributed-dashboard-can-nodes.md).
This path is retained to make older references discoverable, not as an
alternative current design.

See [dashboard controllers](dashboard.md) for the speedometer, tachometer
and warning-cluster controllers, each inside its own stock-style enclosure
and each connected directly to CAN.

The warning cluster owns shared switchgear, twistgrip TPS, GPS and ambient
light sensing. The speedometer owns odometer persistence. Exterior-lamp
logic and switching remain in the ECU/PDM respectively.
