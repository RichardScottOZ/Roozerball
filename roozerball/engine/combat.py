"""Combat system for Roozerball.

Covers Rules G1-G57 (brawling, man-to-man, assault, swoop, combat table).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from roozerball.engine.constants import (
    CombatType, CombatResult, AssaultResult, FigureStatus, FigureType,
    get_brawl_result, get_assault_result, get_skill_check_info,
    MOD_SUPPORTING_FIGURE, MOD_HOLDING_TOW_BAR, MOD_SLOT_ABOVE,
    MOD_BALL_AS_WEAPON, MOD_CONTROLS_SQUARE, MOD_UPPER_HAND,
    MOD_MOVING_VS_STANDING, MOD_SLOT_BEHIND, MOD_RELEASE_TOW_INTO_FIGHT,
    MOD_SWOOP, MOD_SHAKEN, MOD_INJURED, MOD_ATTACK_FALLEN,
    MOD_SKATER_HIT_BIKER, MOD_BIKE_AS_WEAPON,
)
from roozerball.engine import dice

if TYPE_CHECKING:
    from roozerball.engine.board import Board


@dataclass
class CombatOutcome:
    """Result of a combat resolution."""
    combat_type: CombatType
    attacker_total: int = 0
    defender_total: int = 0
    difference: int = 0
    winner_side: str = 'tie'   # 'attacker', 'defender', 'tie'
    brawl_result: Optional[CombatResult] = None
    assault_result: Optional[AssaultResult] = None
    skill_check_results: Dict[int, Tuple[bool, int]] = field(default_factory=dict)
    injuries: Dict[int, Any] = field(default_factory=dict)
    penalties: List[Tuple[Any, str]] = field(default_factory=list)
    man_to_man_pairs: List[Tuple[Any, Any]] = field(default_factory=list)
    messages: List[str] = field(default_factory=list)


def calculate_combat_modifiers(
    attacker_figures: List[Any],
    defender_figures: List[Any],
    combat_type: CombatType,
) -> Tuple[int, int, List[Tuple[str, int]], List[Tuple[str, int]], List[Tuple[Any, str]]]:
    """Calculate all applicable combat modifiers (Rules G44-G57).

    Returns (atk_total, def_total, atk_mods, def_mods, penalties).
    """
    atk_mod = 0
    def_mod = 0
    atk_mods: List[Tuple[str, int]] = []
    def_mods: List[Tuple[str, int]] = []
    penalties: List[Tuple[Any, str]] = []

    # Moving vs standing: +2 (G50)
    atk_has_moving = any(getattr(f, 'has_moved', False) for f in attacker_figures)
    def_has_standing = any(not getattr(f, 'has_moved', False) for f in defender_figures)
    if atk_has_moving and def_has_standing:
        atk_mod += MOD_MOVING_VS_STANDING
        atk_mods.append(('Moving vs standing', MOD_MOVING_VS_STANDING))

    # Team controls square: +1 (G48)
    # (simplified — check if any attacker's square is controlled by their team)

    # Swoop bonus (G53)
    if combat_type == CombatType.SWOOP:
        atk_mod += MOD_SWOOP
        atk_mods.append(('Swoop', MOD_SWOOP))

    # Status penalties (G54)
    for f in attacker_figures:
        status = getattr(f, 'status', FigureStatus.STANDING)
        if status == FigureStatus.SHAKEN:
            atk_mod += MOD_SHAKEN
            atk_mods.append((f'{getattr(f,"name","?")} shaken', MOD_SHAKEN))
        elif status == FigureStatus.BADLY_SHAKEN:
            atk_mod += MOD_INJURED
            atk_mods.append((f'{getattr(f,"name","?")} badly shaken', MOD_INJURED))

    for f in defender_figures:
        status = getattr(f, 'status', FigureStatus.STANDING)
        if status == FigureStatus.SHAKEN:
            def_mod += MOD_SHAKEN
            def_mods.append((f'{getattr(f,"name","?")} shaken', MOD_SHAKEN))
        elif status == FigureStatus.BADLY_SHAKEN:
            def_mod += MOD_INJURED
            def_mods.append((f'{getattr(f,"name","?")} badly shaken', MOD_INJURED))

    # Upper hand in man-to-man (G49)
    if combat_type == CombatType.MAN_TO_MAN:
        for f in attacker_figures:
            if getattr(f, 'upper_hand', False):
                atk_mod += MOD_UPPER_HAND
                atk_mods.append(('Upper hand', MOD_UPPER_HAND))
        for f in defender_figures:
            if getattr(f, 'upper_hand', False):
                def_mod += MOD_UPPER_HAND
                def_mods.append(('Upper hand', MOD_UPPER_HAND))

    # Penalty checks for illegal actions
    for f in attacker_figures:
        # Attacking fallen figure (G55)
        for d in defender_figures:
            if getattr(d, 'status', None) == FigureStatus.FALLEN:
                atk_mod += MOD_ATTACK_FALLEN
                atk_mods.append(('Attack fallen (illegal)', MOD_ATTACK_FALLEN))
                penalties.append((f, 'attack_fallen'))

        # Skater hitting biker (G56)
        if getattr(f, 'is_skater', False) or getattr(f, 'is_catcher', False):
            for d in defender_figures:
                if getattr(d, 'is_biker', False):
                    atk_mod += MOD_SKATER_HIT_BIKER
                    atk_mods.append(('Skater hits biker (illegal)', MOD_SKATER_HIT_BIKER))
                    penalties.append((f, 'skater_attacks_biker'))

    return atk_mod, def_mod, atk_mods, def_mods, penalties


def _apply_skill_checks(
    figures: List[Any], info: dict, outcome: CombatOutcome
) -> None:
    """Apply skill checks and toughness checks to figures based on combat result."""
    for f in figures:
        skill_val = getattr(f, 'skill', 7)

        if info['auto_fall']:
            f.fall()
            outcome.messages.append(f"{getattr(f,'name','?')} auto-falls!")
        else:
            result = dice.skill_check(skill_val, info['skill_mod'])
            outcome.skill_check_results[id(f)] = (result.success, result.roll)
            if not result.success:
                f.fall()
                outcome.messages.append(
                    f"{getattr(f,'name','?')} fails skill check ({result.roll} vs {result.target}) — falls!")

        # Toughness check for fallen figures
        if getattr(f, 'is_fallen', False):
            tough_val = getattr(f, 'toughness', 7)
            tcheck = dice.toughness_check(tough_val, info['toughness_mod'])
            if not tcheck.success:
                injury = dice.roll_injury_dice(
                    fatality=info['fatality'], bdd=info.get('bdd', False))
                outcome.injuries[id(f)] = injury
                outcome.messages.append(
                    f"{getattr(f,'name','?')} fails toughness ({tcheck.roll} vs {tcheck.target}): {injury.details}")


def resolve_brawl(
    attacker_figures: List[Any],
    defender_figures: List[Any],
) -> CombatOutcome:
    """Resolve a brawl (Rules G11-G20)."""
    outcome = CombatOutcome(combat_type=CombatType.BRAWL)

    # Calculate modifiers
    atk_mod, def_mod, atk_mods, def_mods, penalties = calculate_combat_modifiers(
        attacker_figures, defender_figures, CombatType.BRAWL)
    outcome.penalties = penalties

    # Sum combat values + modifiers + 2d6 (G2, G14)
    atk_combat = sum(getattr(f, 'combat', 5) for f in attacker_figures)
    def_combat = sum(getattr(f, 'combat', 5) for f in defender_figures)

    atk_roll = dice.roll_2d6()
    def_roll = dice.roll_2d6()

    outcome.attacker_total = atk_combat + atk_mod + atk_roll
    outcome.defender_total = def_combat + def_mod + def_roll
    outcome.difference = outcome.attacker_total - outcome.defender_total

    if outcome.difference > 0:
        outcome.winner_side = 'attacker'
    elif outcome.difference < 0:
        outcome.winner_side = 'defender'
    else:
        outcome.winner_side = 'tie'

    diff = abs(outcome.difference)
    outcome.brawl_result = get_brawl_result(diff)

    outcome.messages.append(
        f"Brawl: ATK {outcome.attacker_total} vs DEF {outcome.defender_total} "
        f"(diff {outcome.difference}) → {outcome.brawl_result.value}")

    # Skill checks (G5-G10)
    info = get_skill_check_info(diff)
    losers = defender_figures if outcome.winner_side == 'attacker' else attacker_figures
    winners = attacker_figures if outcome.winner_side == 'attacker' else defender_figures

    if info['who'] == 'all':
        _apply_skill_checks(attacker_figures + defender_figures, info, outcome)
    else:
        _apply_skill_checks(losers, info, outcome)

    # Brawl results (G15-G20)
    if outcome.brawl_result == CombatResult.INDECISIVE:
        # All go man-to-man (G15)
        _pair_man_to_man(winners, losers, outcome)
    elif outcome.brawl_result == CombatResult.MARGINAL:
        # Winners may choose man-to-man (G16) — AI always chooses not to
        outcome.messages.append("Marginal — winners may opt for man-to-man")

    return outcome


def resolve_man_to_man(figure1: Any, figure2: Any) -> CombatOutcome:
    """Resolve man-to-man combat (Rules G21-G26)."""
    outcome = CombatOutcome(combat_type=CombatType.MAN_TO_MAN)

    atk_mod, def_mod, _, _, penalties = calculate_combat_modifiers(
        [figure1], [figure2], CombatType.MAN_TO_MAN)
    outcome.penalties = penalties

    c1 = getattr(figure1, 'combat', 5) + atk_mod + dice.roll_2d6()
    c2 = getattr(figure2, 'combat', 5) + def_mod + dice.roll_2d6()

    outcome.attacker_total = c1
    outcome.defender_total = c2
    outcome.difference = c1 - c2

    if outcome.difference > 0:
        outcome.winner_side = 'attacker'
        figure1.upper_hand = True
        figure2.upper_hand = False
    elif outcome.difference < 0:
        outcome.winner_side = 'defender'
        figure2.upper_hand = True
        figure1.upper_hand = False
    else:
        outcome.winner_side = 'tie'

    diff = abs(outcome.difference)
    info = get_skill_check_info(diff)
    loser = figure2 if outcome.winner_side == 'attacker' else figure1

    if info['who'] == 'all':
        _apply_skill_checks([figure1, figure2], info, outcome)
    else:
        _apply_skill_checks([loser], info, outcome)

    # Drift (G22)
    drift1 = getattr(figure1, 'man_to_man_drift', 0)
    if drift1 > 0:
        outcome.messages.append(f"Man-to-man drift: {drift1} squares forward")
        figure1.man_to_man_drift = max(0, drift1 - 1)
        figure2.man_to_man_drift = figure1.man_to_man_drift

    outcome.messages.append(
        f"Man-to-man: {getattr(figure1,'name','?')} {c1} vs "
        f"{getattr(figure2,'name','?')} {c2}")

    return outcome


def resolve_assault(
    attacker_figures: List[Any],
    defender_figures: List[Any],
) -> CombatOutcome:
    """Resolve an assault (Rules G27-G36)."""
    outcome = CombatOutcome(combat_type=CombatType.ASSAULT)

    # Max 4 per side (G28)
    attackers = attacker_figures[:4]
    defenders = defender_figures[:4]

    atk_mod, def_mod, _, _, penalties = calculate_combat_modifiers(
        attackers, defenders, CombatType.ASSAULT)
    outcome.penalties = penalties

    atk_combat = sum(getattr(f, 'combat', 5) for f in attackers)
    def_combat = sum(getattr(f, 'combat', 5) for f in defenders)

    outcome.attacker_total = atk_combat + atk_mod + dice.roll_2d6()
    outcome.defender_total = def_combat + def_mod + dice.roll_2d6()
    outcome.difference = outcome.attacker_total - outcome.defender_total

    if outcome.difference > 0:
        outcome.winner_side = 'attacker'
    elif outcome.difference < 0:
        outcome.winner_side = 'defender'
    else:
        outcome.winner_side = 'tie'

    diff = abs(outcome.difference)
    outcome.assault_result = get_assault_result(diff)

    # All winners make skill -1 (G29)
    winners = attackers if outcome.winner_side == 'attacker' else defenders
    for f in winners:
        result = dice.skill_check(getattr(f, 'skill', 7), -1)
        if not result.success:
            f.fall()
            outcome.messages.append(f"{getattr(f,'name','?')} falls during assault")

    # Skill checks for losers
    info = get_skill_check_info(diff)
    losers = defenders if outcome.winner_side == 'attacker' else attackers
    _apply_skill_checks(losers, info, outcome)

    outcome.messages.append(
        f"Assault: {outcome.attacker_total} vs {outcome.defender_total} "
        f"→ {outcome.assault_result.value}")

    return outcome


def resolve_swoop(swooper: Any, target: Any) -> CombatOutcome:
    """Resolve a swoop attack (Rules G37-G43)."""
    outcome = CombatOutcome(combat_type=CombatType.SWOOP)

    atk_mod, def_mod, _, _, penalties = calculate_combat_modifiers(
        [swooper], [target], CombatType.SWOOP)
    outcome.penalties = penalties

    c1 = getattr(swooper, 'combat', 5) + atk_mod + dice.roll_2d6()
    c2 = getattr(target, 'combat', 5) + def_mod + dice.roll_2d6()

    outcome.attacker_total = c1
    outcome.defender_total = c2
    outcome.difference = c1 - c2

    outcome.winner_side = 'attacker' if outcome.difference > 0 else (
        'defender' if outcome.difference < 0 else 'tie')

    diff = abs(outcome.difference)
    outcome.brawl_result = get_brawl_result(diff)

    # Swooper automatically falls (G37, G53)
    swooper.fall()
    outcome.messages.append(f"{getattr(swooper,'name','?')} swoops and falls!")

    # Swooper does NOT make toughness check (G43)
    # Loser: toughness -1 penalty (G43)
    info = get_skill_check_info(diff)
    info['toughness_mod'] = info.get('toughness_mod', 0) - 1
    _apply_skill_checks([target], info, outcome)

    # vs biker: Decisive+ = auto cycle chart (G41)
    if getattr(target, 'is_biker', False):
        if diff >= 6:  # Decisive+
            chart_result = dice.roll_cycle_chart()
            outcome.messages.append(f"Biker auto cycle chart: {chart_result.details}")

    outcome.messages.append(
        f"Swoop: {getattr(swooper,'name','?')} {c1} vs "
        f"{getattr(target,'name','?')} {c2}")

    return outcome


def _pair_man_to_man(
    winners: List[Any], losers: List[Any], outcome: CombatOutcome
) -> None:
    """Pair figures for man-to-man (Rule G21)."""
    pairs = min(len(winners), len(losers))
    for i in range(pairs):
        w, l = winners[i], losers[i]
        w.start_man_to_man(l)
        l.start_man_to_man(w)
        outcome.man_to_man_pairs.append((w, l))
        outcome.messages.append(
            f"Man-to-man: {getattr(w,'name','?')} vs {getattr(l,'name','?')}")


def check_combat_penalties(outcome: CombatOutcome) -> List[Tuple[Any, int, str]]:
    """Check for penalty infractions from combat (Rules B3, B6, B7, B10)."""
    results = []
    penalty_map = {
        'attack_fallen': (3, 'Attacking fallen figure'),
        'skater_attacks_biker': (3, 'Skater/catcher attacking biker'),
        'biker_attacks': (3, 'Biker attacking'),
        'ball_as_weapon': (3, 'Using ball as weapon'),
    }
    for fig, infraction in outcome.penalties:
        if infraction in penalty_map:
            minutes, desc = penalty_map[infraction]
            results.append((fig, minutes, desc))
    return results
