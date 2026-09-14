"""Creator-facing target preview and quality primitives.

RetroStudio keeps these types target-neutral. AmiStudio, AtariStudio and future
backends supply target-specific diagnostics, resource usages and preview metadata;
the core turns that data into stable creator-facing summaries.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .assets import ResourceUsage, budget_diagnostics
from .model import Diagnostic
from .workspace import CreatorGuidance


@dataclass(frozen=True)
class PreviewFact:
    label: str
    value: str


@dataclass
class TargetPreview:
    target: str
    source_asset: str = ""
    summary: str = ""
    facts: list[PreviewFact] = field(default_factory=list)

    def validate(self) -> None:
        if not self.target:
            raise ValueError("target preview requires a target")


@dataclass
class QualityReport:
    target: str
    diagnostics: list[Diagnostic] = field(default_factory=list)
    usages: list[ResourceUsage] = field(default_factory=list)
    guidance: list[CreatorGuidance] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(item.level == "error" for item in self.diagnostics)

    @property
    def warning_count(self) -> int:
        return sum(item.level == "warning" for item in self.diagnostics)

    @property
    def error_count(self) -> int:
        return sum(item.level == "error" for item in self.diagnostics)


def guidance_for_diagnostic(diagnostic: Diagnostic) -> CreatorGuidance:
    """Translate stable diagnostics into creator-facing next actions.

    Backends may provide richer guidance in future. These generic fallbacks never
    encode knowledge of a particular machine or graphics chipset.
    """

    if diagnostic.code == "budget.exceeded":
        suggestions = (
            "Reduce, crop or reuse source assets that contribute most to this budget.",
            "Try a less expensive target conversion setting when the backend offers one.",
            "Consider a target profile with more capacity if the game design allows it.",
        )
        summary = "This target is over one of its resource budgets."
    elif diagnostic.level == "error":
        suggestions = (
            "Open the referenced asset or scene and fix the reported issue.",
            "Re-run target validation after the change.",
        )
        summary = "This issue must be fixed before a reliable target build."
    elif diagnostic.level == "warning":
        suggestions = (
            "Review the affected content and preview it on the selected target.",
            "Keep it if the visual result is intentional and the target backend accepts it.",
        )
        summary = "This may reduce quality or target compatibility."
    else:
        suggestions = ("No action is required unless the result looks wrong in preview.",)
        summary = "Target information."
    return CreatorGuidance(diagnostic.code, summary, suggestions)


def build_quality_report(
    target: str,
    diagnostics: Iterable[Diagnostic] = (),
    usages: Iterable[ResourceUsage] = (),
    guidance: Iterable[CreatorGuidance] = (),
) -> QualityReport:
    usage_list = list(usages)
    combined = list(diagnostics)
    combined.extend(budget_diagnostics(usage_list))
    supplied = list(guidance)
    supplied_codes = {item.diagnostic_code for item in supplied}
    supplied.extend(
        guidance_for_diagnostic(item)
        for item in combined
        if item.code not in supplied_codes
    )
    return QualityReport(target, combined, usage_list, supplied)


def usage_percent(usage: ResourceUsage) -> float:
    if usage.limit <= 0:
        return 100.0 if usage.used > 0 else 0.0
    return (usage.used / usage.limit) * 100.0
