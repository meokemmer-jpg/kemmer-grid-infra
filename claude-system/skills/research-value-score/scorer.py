"""
research-value-score v0.1.0 -- Welle-12 Gray-Killer Scorer.

Scored Research-Output auf 5-Dim-rho-Skala:
  D1 Decision-Delta   (0-3)  aendert Output eine Kemmer-Entscheidung?
  D2 Predictive-Gain  (0-3)  bessere Vorhersagen ueber K_0/Q_0?
  D3 Compression      (0-3)  verdichtetes Terrain statt Prosa?
  D4 Transfer         (0-3)  Insight jenseits aktuellem Thema?
  D5 Robustness       (0-3)  haelt gegen adversariale Perturbation?

Total 0-15, Zonen LOW (0-5) / MID (6-10) / HIGH (11-15).

CRUX-MK. Alle Heuristiken Signal-basiert (keine LLM-Self-Rating).
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal


# [CRUX-MK] Runtime-Gate (Layer 0)
try:
    import sys as _crux_sys, pathlib as _crux_path
    _crux_sys.path.insert(0, str(_crux_path.Path.home() / ".claude" / "scripts"))
    import crux_runtime as _crux_rt  # auto-checks kill-switch on import
except (ImportError, SystemExit):
    import sys as _crux_sys
    _crux_kf = _crux_path.Path.home() / ".kemmer-grid" / "killed.flag" if '_crux_path' in dir() else None
    if _crux_kf and _crux_kf.exists(): _crux_sys.exit(1)
# /[CRUX-MK] Runtime-Gate

SCORER_VERSION = "0.1.0"


# -----------------------------------------------------------------------------
# Datenmodell
# -----------------------------------------------------------------------------


@dataclass
class ResearchValueScore:
    decision_delta: int
    predictive_gain: int
    compression: int
    transfer: int
    robustness: int
    justifications: dict[str, str]
    timestamp: str
    thema: str
    output_length_chars: int
    scorer_version: str = SCORER_VERSION

    @property
    def total(self) -> int:
        return (
            self.decision_delta
            + self.predictive_gain
            + self.compression
            + self.transfer
            + self.robustness
        )

    @property
    def zone(self) -> Literal["LOW", "MID", "HIGH"]:
        t = self.total
        if t <= 5:
            return "LOW"
        if t <= 10:
            return "MID"
        return "HIGH"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["total"] = self.total
        d["zone"] = self.zone
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


# -----------------------------------------------------------------------------
# Heuristik-Funktionen pro Dimension
# -----------------------------------------------------------------------------


def _lower(s: str) -> str:
    return s.lower()


def _count_matches(text_lower: str, patterns: list[str]) -> int:
    """Zaehlt wieviele patterns in text_lower vorkommen (case-insensitive)."""
    return sum(1 for p in patterns if p in text_lower)


def _has_numeric_parameter(text: str) -> bool:
    """Entscheidungs-Signal: konkrete Zahlen (Thresholds, Parameter)."""
    # Zahlen mit Einheit oder Prozent oder Währung oder Multiplikator
    patterns = [
        r"\d+\.?\d*\s*%",
        r"\d+\.?\d*x\b",
        r"eur|usd|\$",
        r"\d+\.?\d*\s*(min|h|tage|wochen|monate|jahr)",
        r"threshold",
        r"cap\b",
        r"floor\b",
        r"0\.\d+",
    ]
    combined = "|".join(patterns)
    return bool(re.search(combined, text, re.IGNORECASE))


# -----------------------------------------------------------------------------
# D1: Decision-Delta
# -----------------------------------------------------------------------------


def _score_decision_delta(text: str, thema: str) -> tuple[int, str]:
    """
    0 = keine Entscheidungs-Relevanz
    1 = bestaetigt bestehende Entscheidung
    2 = modifiziert bestehende Entscheidung
    3 = zwingt Entscheidungs-Umkehr / neue Entscheidungs-Klasse
    """
    text_l = _lower(text)

    # Signal 1: Decision-Card-Format
    decision_markers = [
        "decision-card", "decision card", "go/no-go", "go / no-go",
        "pro/contra", "pro contra", "martin-approval", "approval-pflicht",
        "entscheidung:", "entscheidungs-option",
    ]
    has_decision_format = _count_matches(text_l, decision_markers) >= 1

    # Signal 2: Umkehr-Marker
    reversal_markers = [
        "superseded", "supersedes", "ersetzt ", "rejected", "reject",
        "stattdessen", "anstelle", "zurueckziehen", "revise",
    ]
    has_reversal = _count_matches(text_l, reversal_markers) >= 1

    # Signal 3: Modify-Marker
    modify_markers = [
        "modify", "modifikation", "patch", "revision ", "anpassung",
        "aendert sich", "neu kalibriert", "parameter-update",
    ]
    has_modify = _count_matches(text_l, modify_markers) >= 1

    # Signal 4: Kemmer-Themen-Nennung
    kemmer_topics = [
        "kemmer", "heylou", "9dots", "cape coral", "cape-coral", "lexvance",
        "graphity", "kpm", "sae", "mews", "workday", "wegzugsbesteuerung",
        "gerdi", "thomas", "martin",
    ]
    kemmer_mentions = _count_matches(text_l, kemmer_topics)

    # Signal 5: konkrete Parameter
    has_params = _has_numeric_parameter(text)

    # Signal 6: rho-Bezug (Zeitwertverfassung)
    has_rho = any(m in text_l for m in ["rho(", "rho-gain", "rho-rechnung", "rho-impact"])

    # Bewertung
    score = 0
    reasons = []

    if has_decision_format:
        score += 1
        reasons.append("Decision-Format erkannt")
    if has_params and kemmer_mentions >= 1:
        score += 1
        reasons.append(f"Konkrete Parameter + {kemmer_mentions} Kemmer-Themen")
    if has_modify and not has_reversal:
        score = max(score, 2)
        reasons.append("Modify-Signal ohne Umkehr -> D1=2")
    if has_reversal:
        score = 3
        reasons.append("Umkehr-/SUPERSEDED-Signal -> D1=3")
    if has_rho:
        score = min(3, score + 1)
        reasons.append("rho-Rechnung expliziert")

    score = max(0, min(3, score))

    justification = "; ".join(reasons) if reasons else "keine Entscheidungs-Signale erkannt"
    return score, justification


# -----------------------------------------------------------------------------
# D2: Predictive-Gain
# -----------------------------------------------------------------------------


def _score_predictive_gain(text: str, thema: str) -> tuple[int, str]:
    """
    0 = keine Prognose
    1 = Backward-Erklaerung
    2 = falsifizierbare Vorhersage
    3 = Vorhersage + Mess-Prozedur + Falsifikations-Bedingung
    """
    text_l = _lower(text)

    # Signal 1: Falsifikations-Bedingung explizit
    falsif_markers = [
        "falsifikations-bedingung", "falsifizierbar", "falsification",
        "falsifiziert wenn", "widerlegbar", "replacement-trigger",
        "revisions-trigger", "revision-trigger",
    ]
    has_falsif = _count_matches(text_l, falsif_markers) >= 1

    # Signal 2: Mess-Prozedur
    measurement_markers = [
        "brier-score", "brier score", "messfenster", "messung nach",
        "n_samples", "n=", "n =", "holdout", "backtest",
        "ab woche", "nach ", "credence_interval", "konfidenz-intervall",
    ]
    has_measurement = _count_matches(text_l, measurement_markers) >= 2

    # Signal 3: Wenn-Dann mit messbaren Bedingungen
    # Regex: "wenn X > Y dann Z" oder "bei X > Y"
    conditional_pattern = re.compile(
        r"(wenn|falls|bei)\s+[^.]{0,40}(>=?|<=?|==|ueber|unter|mehr als|weniger als)\s*[\d\w\.]+",
        re.IGNORECASE,
    )
    conditional_count = len(conditional_pattern.findall(text))
    has_conditionals = conditional_count >= 2

    # Signal 4: Zukunfts-Zeit
    future_markers = [
        "in 30 tagen", "in 4 wochen", "in 3 monaten", "nach q", "nach monat",
        "prognose", "vorhersage", "wird X sein", "erwartet", "projected",
    ]
    has_future = _count_matches(text_l, future_markers) >= 1

    # Signal 5: Backward-Erklaerung (niedriger als Prognose)
    backward_markers = [
        "ursache", "weil", "erklaert", "rueckblick", "historisch zeigt",
        "in der vergangenheit", "aus erfahrung",
    ]
    has_backward = _count_matches(text_l, backward_markers) >= 2

    # Bewertung
    score = 0
    reasons = []

    if has_backward and not has_future:
        score = 1
        reasons.append("Backward-Erklaerung erkannt, keine Vorhersage")
    if has_conditionals and has_future:
        score = max(score, 2)
        reasons.append(f"{conditional_count} Wenn-Dann + Zukunfts-Ref -> D2=2")
    if has_falsif and has_measurement:
        score = 3
        reasons.append("Falsifikations-Bedingung + Mess-Prozedur -> D2=3")
    if has_falsif and not has_measurement:
        score = max(score, 2)
        reasons.append("Falsifikations-Bedingung ohne Mess-Prozedur -> D2=2")

    score = max(0, min(3, score))

    justification = "; ".join(reasons) if reasons else "keine prognostischen Signale"
    return score, justification


# -----------------------------------------------------------------------------
# D3: Compression
# -----------------------------------------------------------------------------


def _score_compression(text: str, thema: str) -> tuple[int, str]:
    """
    0 = aufgeblaht, kein Kern
    1 = moderate Verdichtung
    2 = dichter Kern + klare Abgrenzung
    3 = extrem dicht (Formel/Invariante)
    """
    text_l = _lower(text)
    total_chars = len(text)

    # Signal 1: Formeln / Code-Blocks / Tabellen
    formula_markers = [
        "```", "rho(a", "rho =", "h =", "lambda =", "formel:",
        "invariante:", "theorem", "lemma",
    ]
    formula_count = _count_matches(text_l, formula_markers)
    has_table = text.count("|") >= 10  # Markdown-Tabelle
    has_code_block = text.count("```") >= 2

    # Signal 2: Kern-Strukturen
    core_markers = [
        "kernregel", "kernthese", "kernsatz", "kern-", "kernaussage",
        "tldr", "zusammenfassung", "wesentliches:", "invariante",
    ]
    has_core = _count_matches(text_l, core_markers) >= 1

    # Signal 3: Filler-Phrases (negativ)
    filler_markers = [
        "es ist wichtig zu beachten", "in diesem zusammenhang",
        "es sei darauf hingewiesen", "selbstverstaendlich",
        "wie bereits erwaehnt", "im grunde genommen",
    ]
    filler_count = _count_matches(text_l, filler_markers)

    # Signal 4: Laenge-Dichte-Verhaeltnis
    # Groessere Outputs brauchen mehr Verdichtung um hoch zu scoren
    structural_markers = text_l.count("##") + text_l.count("- ") + text.count("\n\n")
    structure_density = structural_markers / max(total_chars, 1) * 1000

    # Signal 5: Zahl-Dichte (Parameter, Thresholds)
    numbers = re.findall(r"\d+[\.,]?\d*", text)
    number_density = len(numbers) / max(total_chars, 1) * 1000

    # Bewertung
    score = 0
    reasons = []

    if has_core:
        score = 1
        reasons.append("Kern-Struktur erkannt")
    if has_code_block or has_table:
        score = max(score, 2)
        reasons.append("Code-Block / Tabelle verdichtet")
    if formula_count >= 2:
        score = max(score, 2)
        reasons.append(f"{formula_count} Formel-Marker")
    if has_core and (has_code_block or has_table) and formula_count >= 1:
        score = 3
        reasons.append("Kern + Formel + Tabelle -> D3=3")
    if filler_count >= 3:
        score = max(0, score - 1)
        reasons.append(f"{filler_count} Filler -> Penalty")
    if total_chars > 20000 and score < 3:
        # Sehr lange Texte muessen mehr Dichte zeigen
        if structure_density < 3.0:
            score = max(0, score - 1)
            reasons.append("Laenge > 20k chars mit niedriger Struktur-Dichte -> Penalty")

    score = max(0, min(3, score))

    justification = (
        f"structure_density={structure_density:.2f}, number_density={number_density:.2f}, "
        + "; ".join(reasons)
        if reasons
        else "keine Verdichtungs-Signale"
    )
    return score, justification


# -----------------------------------------------------------------------------
# D4: Transfer
# -----------------------------------------------------------------------------


def _score_transfer(text: str, thema: str) -> tuple[int, str]:
    """
    0 = nur aktuelles Micro-Thema
    1 = anwendbar auf verwandte Themen
    2 = anwendbar auf andere Kategorien
    3 = strukturelle Invariante / Meta-Ebene
    """
    text_l = _lower(text)

    # Signal 1: SAE-Isomorphie explizit
    isomorphy_markers = [
        "sae-isomorphie", "sae isomorphie", "isomorph zu", "isomorphie",
        "entspricht sae", "analog zu", "uebertragung auf",
    ]
    has_isomorphy = _count_matches(text_l, isomorphy_markers) >= 1

    # Signal 2: Multi-Domain-Nennung
    domains = {
        "hotel": ["hotel", "heylou", "mews", "rms", "pms"],
        "trading": ["kpm", "trading", "portfolio", "kelly", "drawdown"],
        "familie": ["familie", "gerdi", "martin", "q_0"],
        "code": ["sae", "trinity", "myzel", "myz-", "governance"],
        "medizin": ["blutpanel", "labor", "mbsr", "gesundheit"],
        "steuer": ["steuer", "wegzug", "e-2", "visa"],
        "meta": ["meta-lern", "fixpunkt", "e3", "e4", "e5"],
    }
    domain_hits = set()
    for domain_name, keywords in domains.items():
        if _count_matches(text_l, keywords) >= 1:
            domain_hits.add(domain_name)
    multi_domain = len(domain_hits) >= 2
    triple_domain = len(domain_hits) >= 3

    # Signal 3: Prinzip vs Rezept
    principle_markers = [
        "prinzip", "invariante", "regel", "gesetz", "generalisiert",
        "abstrakt", "pattern", "meta-ebene", "strukturelle",
    ]
    has_principle = _count_matches(text_l, principle_markers) >= 2

    # Signal 4: Myzel-/Trinity-/Pattern-Verweis
    pattern_markers = [
        "trinity-pattern", "myz-", "hamilton", "toc ", "shannon",
        "f_cum", "pontryagin",
    ]
    has_pattern_ref = _count_matches(text_l, pattern_markers) >= 1

    # Signal 5: Spezifisch vs. abstrakt - wenn sehr spezifisch (ein Thema, viele Zahlen, wenig Prinzip): D4=0
    specific_only = (
        _count_matches(text_l, principle_markers) == 0
        and len(domain_hits) <= 1
        and not has_isomorphy
    )

    # Bewertung
    score = 0
    reasons = []

    if specific_only:
        score = 0
        reasons.append("stark kontextgebunden, kein Transfer")
    elif multi_domain and not has_principle:
        score = 1
        reasons.append(f"2+ Domaenen ({sorted(domain_hits)}) aber kein Prinzip")
    elif (triple_domain or (multi_domain and has_isomorphy)) and has_principle:
        score = 3
        reasons.append(f"Prinzip + Multi-Domain ({sorted(domain_hits)}) + Isomorphie -> D4=3")
    elif multi_domain or has_isomorphy or has_pattern_ref:
        score = 2
        reasons.append(f"Cross-Category erkannt: {sorted(domain_hits)}")
    if has_isomorphy:
        score = max(score, 2)
        reasons.append("SAE-Isomorphie explizit")

    score = max(0, min(3, score))

    justification = "; ".join(reasons) if reasons else "kein Transfer-Signal"
    return score, justification


# -----------------------------------------------------------------------------
# D5: Robustness
# -----------------------------------------------------------------------------


def _score_robustness(text: str, thema: str) -> tuple[int, str]:
    """
    0 = kippt bei Challenge
    1 = haelt einfache Gegenfragen
    2 = Stresstest bestanden
    3 = konvergent-stabil 3+ Modell-Familien + Szenario-Shift
    """
    text_l = _lower(text)

    # Signal 1: Cross-LLM-Verdict
    verdict_markers = [
        "cross-llm-2of3-hardened", "cross-llm-simulation-hardened",
        "hardened", "conditional", "statistical-stable",
        "fixpunkt-hardened",
    ]
    verdict_hits = _count_matches(text_l, verdict_markers)

    # Signal 2: Cross-LLM-File-Verweis
    cross_llm_refs = [
        "cross-llm/", "branch-hub/cross-llm", "2026-04-", "codex",
        "gemini", "grok", "adversarial",
    ]
    cross_llm_count = _count_matches(text_l, cross_llm_refs)

    # Signal 3: Wargame-Durchfuehrung
    wargame_markers = [
        "red-team", "blue-team", "purple-team", "gray-team",
        "red/blue/purple", "4-team-wargame", "wargame", "adversarial-test",
    ]
    wargame_hits = _count_matches(text_l, wargame_markers)

    # Signal 4: Anti-Patterns explizit
    anti_pattern_markers = [
        "anti-pattern", "anti pattern", "anti-muster", "verbotene muster",
        "falsifikation", "revision-trigger", "goodhart",
    ]
    has_anti_patterns = _count_matches(text_l, anti_pattern_markers) >= 1

    # Signal 5: Multi-Modell-Nennungen
    models = ["claude", "codex", "gemini", "grok", "perplexity", "copilot", "gpt-"]
    model_mentions = _count_matches(text_l, models)

    # Signal 6: Verdict-Begruendung (z.B. "3/3 MODIFY")
    verdict_pattern = re.compile(r"\d+/\d+\s*(modify|adopt|reject|conditional|hardened)", re.IGNORECASE)
    verdict_ratios = verdict_pattern.findall(text)

    # Bewertung
    score = 0
    reasons = []

    if has_anti_patterns:
        score = 1
        reasons.append("Anti-Patterns / Falsifikation benannt")
    if wargame_hits >= 2 and has_anti_patterns:
        score = max(score, 2)
        reasons.append(f"Wargame-Durchfuehrung ({wargame_hits} Signale) + Anti-Patterns")
    if verdict_hits >= 1:
        score = max(score, 2)
        reasons.append(f"Cross-LLM-Verdict explizit ({verdict_hits} Marker)")
    if (
        verdict_hits >= 1
        and model_mentions >= 3
        and (cross_llm_count >= 2 or verdict_ratios)
    ):
        score = 3
        reasons.append(
            f"Multi-Model ({model_mentions}) + Verdict + Cross-LLM-Refs -> D5=3"
        )

    score = max(0, min(3, score))

    justification = "; ".join(reasons) if reasons else "keine Robustness-Signale"
    return score, justification


# -----------------------------------------------------------------------------
# Haupt-API
# -----------------------------------------------------------------------------


def score_research_output(
    output_text: str,
    thema: str,
    kemmer_kontext: dict | None = None,
) -> ResearchValueScore:
    """Hauptfunktion: scored Research-Output auf 5-Dim-Skala.

    Argumente:
        output_text: Voller Text des Research-Outputs.
        thema: Kemmer-Thema (z.B. 'KPM-Sizing').
        kemmer_kontext: Optional, Dict mit decision_pending/invariants/domain.

    Rueckgabe:
        ResearchValueScore mit 5 Dims + Total + Zone + Justifications.
    """
    _ = kemmer_kontext  # v0.1.0 nutzt Kontext nicht aktiv, v0.2.0 plant Integration

    d1, j1 = _score_decision_delta(output_text, thema)
    d2, j2 = _score_predictive_gain(output_text, thema)
    d3, j3 = _score_compression(output_text, thema)
    d4, j4 = _score_transfer(output_text, thema)
    d5, j5 = _score_robustness(output_text, thema)

    return ResearchValueScore(
        decision_delta=d1,
        predictive_gain=d2,
        compression=d3,
        transfer=d4,
        robustness=d5,
        justifications={
            "decision_delta": j1,
            "predictive_gain": j2,
            "compression": j3,
            "transfer": j4,
            "robustness": j5,
        },
        timestamp=datetime.now(timezone.utc).isoformat(),
        thema=thema,
        output_length_chars=len(output_text),
    )


def score_from_file(path: str, thema: str) -> ResearchValueScore:
    """Liest Datei und scored den Inhalt."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Datei nicht gefunden: {path}")
    text = p.read_text(encoding="utf-8", errors="replace")
    return score_research_output(text, thema)


# -----------------------------------------------------------------------------
# CLI-Entry
# -----------------------------------------------------------------------------


def _cli_main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(
            "Usage: python scorer.py <file_path> <thema>\n"
            "       python scorer.py --text '<text>' <thema>",
            file=sys.stderr,
        )
        return 2

    if argv[1] == "--text":
        if len(argv) < 4:
            print("--text erfordert <text> und <thema>", file=sys.stderr)
            return 2
        text = argv[2]
        thema = argv[3]
        score = score_research_output(text, thema)
    else:
        file_path = argv[1]
        thema = argv[2]
        score = score_from_file(file_path, thema)

    print(score.to_json())
    return 0


if __name__ == "__main__":
    sys.exit(_cli_main(sys.argv))
