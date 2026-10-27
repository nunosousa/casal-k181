import unittest
from pathlib import Path

import yaml


class ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = Path(__file__).resolve().parents[1] / "protocol" / "messages.yaml"
        cls.protocol = yaml.safe_load(source.read_text(encoding="utf-8"))
        cls.messages = cls.protocol["messages"]
        cls.by_name = {message["name"]: message for message in cls.messages}
        cls.nodes = {node["name"] for node in cls.protocol["nodes"]}

    def test_four_unique_nodes_and_version(self):
        self.assertEqual(self.protocol["version"], 2)
        self.assertEqual(
            self.nodes, {"ecu", "speedometer", "tachometer", "warning_cluster"}
        )
        self.assertEqual(len(self.protocol["nodes"]), 4)
        self.assertEqual(
            {node["name"]: node["address"] for node in self.protocol["nodes"]},
            {"ecu": 0x01, "warning_cluster": 0x02, "speedometer": 0x03, "tachometer": 0x04},
        )
        self.assertEqual(self.protocol["bus"]["bitrate"], 500000)
        self.assertFalse(self.protocol["bus"]["can_fd"])
        self.assertEqual(self.protocol["bus"]["identifier_width"], 11)
        self.assertEqual(self.protocol["bus"]["termination_ohms"], 120)

    def test_unique_ids_names_and_valid_participants(self):
        self.assertEqual(len(self.by_name), len(self.messages))
        self.assertEqual(
            len({message["id"] for message in self.messages}), len(self.messages)
        )
        for message in self.messages:
            with self.subTest(message=message["name"]):
                self.assertIn(message["producer"], self.nodes | {"any"})
                self.assertTrue(message["consumers"])
                self.assertTrue(set(message["consumers"]) <= self.nodes | {"any"})
                self.assertTrue(0 <= message["id"] <= 0x7FF)

    def test_signals_fit_classic_frame_without_overlap(self):
        for message in self.messages:
            occupied = set()
            names = set()
            for signal in message["signals"]:
                with self.subTest(message=message["name"], signal=signal["name"]):
                    self.assertNotIn(signal["name"], names)
                    names.add(signal["name"])
                    start, length = signal["start_bit"], signal["length_bits"]
                    self.assertGreaterEqual(start, 0)
                    self.assertGreater(length, 0)
                    self.assertLessEqual(start + length, 64)
                    bits = set(range(start, start + length))
                    self.assertFalse(bits & occupied)
                    occupied |= bits

    def test_shared_inputs_belong_to_warning_cluster(self):
        for name, period in (
            ("user_input_fast", 10), ("handlebar_switches", 10),
            ("gps_position", 200), ("gps_speed_alt", 200),
            ("gps_fix_state", 1000), ("dashboard_brightness", 100),
        ):
            with self.subTest(message=name):
                self.assertEqual(self.by_name[name]["producer"], "warning_cluster")
                self.assertEqual(self.by_name[name]["period_ms"], period)
        self.assertEqual(
            set(self.by_name["dashboard_brightness"]["consumers"]),
            {"speedometer", "tachometer"},
        )
        self.assertEqual(self.by_name["user_input_fast"]["consumers"], ["ecu"])
        self.assertEqual(self.by_name["handlebar_switches"]["consumers"], ["ecu"])

    def test_gauge_inputs_are_direct_from_ecu(self):
        for message, gauge in (
            ("vehicle_state_fast", "speedometer"),
            ("engine_state_fast", "tachometer"),
        ):
            with self.subTest(gauge=gauge):
                self.assertEqual(self.by_name[message]["producer"], "ecu")
                self.assertIn(gauge, self.by_name[message]["consumers"])
                self.assertEqual(self.by_name[message]["period_ms"], 10)

    def test_each_node_has_heartbeat_fault_and_diagnostics(self):
        for node in self.nodes:
            with self.subTest(node=node):
                heartbeat = self.by_name[f"{node}_heartbeat"]
                self.assertEqual(heartbeat["producer"], node)
                self.assertEqual(heartbeat["period_ms"], 1000)
                layout = {
                    signal["name"]: signal["start_bit"]
                    for signal in heartbeat["signals"]
                }
                self.assertEqual(
                    layout,
                    {"fw_major": 0, "fw_minor": 8, "fw_patch": 16,
                     "fault_summary": 24, "uptime_s": 32},
                )
                self.assertEqual(self.by_name[f"{node}_fault_event"]["producer"], node)
                self.assertEqual(self.by_name[f"diag_request_{node}"]["consumers"], [node])
                self.assertEqual(self.by_name[f"diag_response_{node}"]["producer"], node)
        for gauge in ("speedometer", "tachometer"):
            self.assertIn(
                "warning_cluster", self.by_name[f"{gauge}_heartbeat"]["consumers"]
            )
            self.assertIn(gauge, self.by_name["ecu_heartbeat"]["consumers"])
            self.assertIn(gauge, self.by_name["warning_cluster_heartbeat"]["consumers"])

    def test_transport_pairs_cover_all_nodes_without_collisions(self):
        pairs = self.protocol["transport"]["iso_tp"]
        self.assertEqual({pair["target"] for pair in pairs}, self.nodes)
        self.assertEqual(len(pairs), 4)
        self.assertEqual(
            {pair["target"]: (pair["request_id"], pair["response_id"]) for pair in pairs},
            {"ecu": (0x780, 0x781), "warning_cluster": (0x782, 0x783),
             "speedometer": (0x784, 0x785), "tachometer": (0x786, 0x787)},
        )
        identifiers = [
            pair[field] for pair in pairs for field in ("request_id", "response_id")
        ]
        self.assertEqual(len(set(identifiers)), 8)
        self.assertEqual(set(identifiers), set(range(0x780, 0x788)))
        self.assertFalse(set(identifiers) & {message["id"] for message in self.messages})

    def test_documented_periodic_bus_budget(self):
        frames_per_second = sum(
            1000 / message["period_ms"]
            for message in self.messages
            if message["kind"] == "periodic"
        )
        self.assertEqual(frames_per_second, 556)
        self.assertLess(frames_per_second * 135 / self.protocol["bus"]["bitrate"], 0.16)


if __name__ == "__main__":
    unittest.main()
