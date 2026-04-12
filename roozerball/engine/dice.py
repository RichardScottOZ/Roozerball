"""Dice rolling mechanics for Roozerball.

Covers all random resolution: basic dice, skill/toughness/combat checks,
injury dice (D6-D10), ball physics, cycle chart, referees.
"""
from __future__ import annotations

import random
from typing import NamedTuple, Optional, List

from roozerball.engine.constants import InjuryFace

# ---------------------------------------------------------------------------
# Basic dice
# ---------------------------------------------------------------------------

def roll_d6() -> int:
    return random.randint(1, 6)

def roll_2d6() -> int:
    return random.randint(1, 6) + random.randint(1, 6)

def roll_3d6() -> int:
    return random.randint(1, 6) + random.randint(1, 6) + random.randint(1, 6)

def roll_d12() -> int:
    return random.randint(1, 12)

# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

class CheckResult(NamedTuple):
    success: bool
    roll: int
    target: int

def skill_check(skill_value: int, modifier: int = 0) -> CheckResult:
    """Roll 2d6 <= skill + modifier (Rule D3)."""
    target = skill_value + modifier
    roll = roll_2d6()
    return CheckResult(roll <= target, roll, target)

def toughness_check(toughness_value: int, modifier: int = 0) -> CheckResult:
    """Roll 2d6 <= toughness + modifier (Rule D5)."""
    target = toughness_value + modifier
    roll = roll_2d6()
    return CheckResult(roll <= target, roll, target)

def combat_roll(combat_value: int, modifier: int = 0) -> int:
    """Roll 2d6 + combat + modifier (Rule D4/G2)."""
    return roll_2d6() + combat_value + modifier

def referee_check(modifier: int = 0) -> CheckResult:
    """Roll 2d6 <= 8 + modifier to spot infraction (Rule B14)."""
    target = 8 + modifier
    roll = roll_2d6()
    return CheckResult(roll <= target, roll, target)

# ---------------------------------------------------------------------------
# Injury dice (Rules D6-D10)
# ---------------------------------------------------------------------------

INJURY_FACES = list(InjuryFace)

class InjuryResult(NamedTuple):
    injury_type: str        # 'none','shaken','badly_shaken','injured','unconscious','dead'
    duration: int           # minutes (0 if N/A)
    body_part: Optional[str]
    details: str

def _roll_injury_face() -> InjuryFace:
    return random.choice(INJURY_FACES)

def roll_injury_dice(fatality: bool = False, bdd: bool = False) -> InjuryResult:
    """Roll injury dice per Rules D6-D10.

    Two base dice; if bdd=True add third die.
    Check all pairs for matches.
    """
    dice: List[InjuryFace] = [_roll_injury_face(), _roll_injury_face()]
    if bdd:
        dice.append(_roll_injury_face())

    # Check all pairs for combinations
    pairs = []
    for i in range(len(dice)):
        for j in range(i + 1, len(dice)):
            if dice[i] == dice[j]:
                pairs.append(dice[i])
            elif {dice[i], dice[j]} & {InjuryFace.BODY}:
                pairs.append(('body_combo', dice[i], dice[j]))

    # Find the worst result from all pairs
    best: Optional[InjuryResult] = None

    for i in range(len(dice)):
        for j in range(i + 1, len(dice)):
            a, b = dice[i], dice[j]
            result = _evaluate_pair(a, b, fatality)
            if result and (best is None or _severity(result) > _severity(best)):
                best = result

    if best is None:
        return InjuryResult('none', 0, None, f"Dice: {[d.value for d in dice]} — no combination")

    return InjuryResult(best.injury_type, best.duration, best.body_part,
                        f"Dice: {[d.value for d in dice]} — {best.details}")


def _evaluate_pair(a: InjuryFace, b: InjuryFace, fatality: bool) -> Optional[InjuryResult]:
    """Evaluate a single pair of injury dice."""
    limbs = {InjuryFace.LEFT_ARM, InjuryFace.RIGHT_ARM,
             InjuryFace.LEFT_LEG, InjuryFace.RIGHT_LEG}

    if a == b:
        # Doubles
        if a == InjuryFace.BODY:
            if fatality:
                return InjuryResult('dead', 0, 'body', 'Double body — fatality')
            return InjuryResult('badly_shaken', random.randint(4, 6), 'body',
                                'Double body — badly shaken')
        if a == InjuryFace.HEAD:
            if fatality:
                return InjuryResult('dead', 0, 'head', 'Double head — fatality')
            return InjuryResult('unconscious', 0, 'head', 'Double head — unconscious')
        if a in limbs:
            dur = random.randint(4, 6)
            if fatality:
                return InjuryResult('injured', 0, a.value, f'Double {a.value} — broken')
            return InjuryResult('injured', dur, a.value,
                                f'Double {a.value} — injured + shaken {dur} min')
    else:
        # Body + something
        has_body = (a == InjuryFace.BODY or b == InjuryFace.BODY)
        if has_body:
            other = b if a == InjuryFace.BODY else a
            if fatality:
                dur = random.randint(4, 6)
                return InjuryResult('badly_shaken', dur, other.value,
                                    f'Body + {other.value} — badly shaken {dur} min')
            dur = random.randint(1, 3)
            return InjuryResult('shaken', dur, other.value,
                                f'Body + {other.value} — shaken {dur} min')
    return None


_SEVERITY_ORDER = {'none': 0, 'shaken': 1, 'badly_shaken': 2,
                   'injured': 3, 'unconscious': 4, 'dead': 5}

def _severity(r: InjuryResult) -> int:
    return _SEVERITY_ORDER.get(r.injury_type, 0)

# ---------------------------------------------------------------------------
# Ball dice
# ---------------------------------------------------------------------------

def roll_ball_speed() -> int:
    """3d6 + 12 for initial ball speed (Rule C13)."""
    return roll_3d6() + 12

def roll_ball_bounce() -> int:
    """3d6 for speed loss on bobble (Rule C17)."""
    return roll_3d6()

def roll_direction() -> int:
    """Random sector index 0-11 for ball bounce direction."""
    return random.randint(0, 11)

class MissedShotResult(NamedTuple):
    dead_ball: bool
    bounce_direction: Optional[str]   # 'left' or 'right' or None

def roll_missed_shot() -> MissedShotResult:
    """50% dead, 25% left, 25% right (Rule F8)."""
    r = random.randint(1, 4)
    if r <= 2:
        return MissedShotResult(True, None)
    if r == 3:
        return MissedShotResult(False, 'left')
    return MissedShotResult(False, 'right')

def roll_shaken_duration(badly: bool = False) -> int:
    """1-3 for shaken, 4-6 for badly shaken."""
    if badly:
        return random.randint(4, 6)
    return random.randint(1, 3)

# ---------------------------------------------------------------------------
# Cycle Chart (Rule E19)
# ---------------------------------------------------------------------------

class CycleChartResult(NamedTuple):
    result: str
    thrown: bool
    thrown_distance: int
    injury_fatality: bool
    bdd: bool
    details: str

def roll_cycle_chart(modifier: int = 0) -> CycleChartResult:
    """2d6 + modifier on the Cycle Chart (Rule E19)."""
    roll = roll_2d6() + modifier
    if roll <= 3:
        return CycleChartResult('ok', False, 0, False, False, f'Roll {roll}: OK')
    if roll <= 5:
        return CycleChartResult('near_miss', False, 0, False, False,
                                f'Roll {roll}: Near Miss — skill check')
    if roll <= 7:
        return CycleChartResult('skid', False, 0, False, False,
                                f'Roll {roll}: Skid — skill check -1')
    if roll <= 9:
        return CycleChartResult('thrown', True, 1, False, False,
                                f'Roll {roll}: Thrown — biker thrown, cycle stays')
    if roll <= 11:
        return CycleChartResult('bad_wreck', True, random.randint(1, 2), True, False,
                                f'Roll {roll}: Bad Wreck — thrown 1-2 sq, injury dice')
    if roll == 12:
        return CycleChartResult('major_wreck', True, random.randint(2, 3), True, False,
                                f'Roll {roll}: Major Wreck — thrown 2-3 sq, fatal injury')
    # 13+
    return CycleChartResult('major_wreck', True, random.randint(3, 4), True, True,
                            f'Roll {roll}: Major Wreck — thrown 3+ sq, fatal + BDD')

def roll_explosion(severity: str) -> bool:
    """Roll d6 for explosion chance (Rule E20)."""
    r = roll_d6()
    if severity == 'major_wreck':
        return r >= 3      # explodes on 3-6
    if severity == 'bad_wreck':
        return r >= 5      # explodes on 5-6
    return False
