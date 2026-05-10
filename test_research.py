import unittest

from research import (
    _build_key_points,
    _build_research_brief,
    _confidence_label,
    _dedupe_references,
)


class ResearchHelpersTest(unittest.TestCase):
    def test_dedupe_references_by_url(self) -> None:
        refs = [
            {"title": "A", "url": "https://x"},
            {"title": "A duplicate", "url": "https://x"},
            {"title": "B", "url": "https://y"},
        ]
        deduped = _dedupe_references(refs)
        self.assertEqual(len(deduped), 2)
        self.assertEqual(deduped[0]["url"], "https://x")
        self.assertEqual(deduped[1]["url"], "https://y")

    def test_key_points_extract_from_sentences(self) -> None:
        summary = "First point. Second point. Third point. Fourth point."
        key_points = _build_key_points(summary)
        self.assertEqual(len(key_points), 3)
        self.assertEqual(key_points[0], "First point")

    def test_confidence_label_thresholds(self) -> None:
        self.assertEqual(_confidence_label(0.8), "high")
        self.assertEqual(_confidence_label(0.6), "medium")
        self.assertEqual(_confidence_label(0.3), "low")

    def test_research_brief_contains_core_sections(self) -> None:
        result = {
            "topic": "test topic",
            "summary": "A summary",
            "key_point_evidence": [{"point": "One"}, {"point": "Two"}],
            "references": [{"title": "Ref 1", "url": "https://ref1"}],
            "confidence": {"score": 0.7, "label": "medium"},
        }
        brief = _build_research_brief(result)
        self.assertIn("Topic: test topic", brief)
        self.assertIn("Key points:", brief)
        self.assertIn("References:", brief)


if __name__ == "__main__":
    unittest.main()
