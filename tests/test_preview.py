import unittest

from retrostudio.assets import ResourceUsage
from retrostudio.model import Diagnostic
from retrostudio.preview import (
    PreviewFact,
    TargetPreview,
    build_quality_report,
    guidance_for_diagnostic,
    usage_percent,
)
from retrostudio.workspace import CreatorGuidance


class TargetPreviewTests(unittest.TestCase):
    def test_preview_requires_target(self):
        preview = TargetPreview("", "assets/hero.png")
        with self.assertRaises(ValueError):
            preview.validate()

    def test_preview_keeps_creator_facts_target_neutral(self):
        preview = TargetPreview(
            "example-target",
            "assets/hero.png",
            "Backend preview ready",
            [PreviewFact("Palette", "optimized")],
        )
        preview.validate()
        self.assertEqual(preview.facts[0].value, "optimized")


class QualityReportTests(unittest.TestCase):
    def test_budget_overflow_becomes_error_and_guidance(self):
        report = build_quality_report(
            "example-target",
            usages=[ResourceUsage("graphics memory", 120, 100, "KiB", "assets/hero.png")],
        )
        self.assertFalse(report.ok)
        self.assertEqual(report.error_count, 1)
        self.assertEqual(report.diagnostics[0].code, "budget.exceeded")
        self.assertEqual(report.guidance[0].diagnostic_code, "budget.exceeded")
        self.assertTrue(report.guidance[0].suggestions)

    def test_backend_guidance_overrides_generic_guidance_for_same_code(self):
        custom = CreatorGuidance("palette.loss", "Colors will be reduced.", ("Use a smaller palette.",))
        report = build_quality_report(
            "example-target",
            diagnostics=[Diagnostic("warning", "palette.loss", "palette will be reduced")],
            guidance=[custom],
        )
        self.assertEqual(report.warning_count, 1)
        self.assertEqual(report.guidance, [custom])

    def test_generic_warning_guidance_is_actionable(self):
        guidance = guidance_for_diagnostic(Diagnostic("warning", "preview.loss", "quality loss"))
        self.assertIn("preview", guidance.suggestions[0].lower())

    def test_usage_percent(self):
        self.assertEqual(usage_percent(ResourceUsage("ram", 50, 100)), 50.0)
        self.assertEqual(usage_percent(ResourceUsage("ram", 1, 0)), 100.0)


if __name__ == "__main__":
    unittest.main()
