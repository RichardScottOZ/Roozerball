"""Tier 4 UI — glass-morphism panels, gradient buttons, enhanced styling.

Re-exports all Tier 3 UI components but overrides drawing helpers,
panel backgrounds, and button rendering for a more polished realistic look.

Tier 4 enhancements:
  * Glass-morphism panel backgrounds with translucent blur effect
  * Gradient buttons with highlight edge
  * Brighter section header typography
  * Subtle top-glow border on panels and dialogs
"""
from __future__ import annotations

import random as _rng
from typing import Any, Callable, Dict, List, Optional, Tuple

import pygame

from roozerball.engine.constants import FigureStatus, TeamSide
from roozerball.engine.team import Team
from roozerball.gui_tier4.constants import (
    BUTTON_ACTIVE,
    BUTTON_BORDER,
    BUTTON_COLOR,
    BUTTON_CORNER_RADIUS,
    BUTTON_GRADIENT_BOTTOM,
    BUTTON_GRADIENT_TOP,
    BUTTON_HEIGHT,
    BUTTON_HOVER,
    BUTTON_PADDING,
    BUTTON_TEXT,
    DIALOG_BG,
    DIALOG_BORDER,
    DIALOG_CORNER_RADIUS,
    DIALOG_GLASS_ALPHA,
    DIALOG_OVERLAY_ALPHA,
    FONT_SIZE_BODY,
    FONT_SIZE_HEADER,
    FONT_SIZE_LABEL,
    FONT_SIZE_SMALL,
    FONT_SIZE_TITLE,
    MAX_ACTION_TEXT_LENGTH,
    MAX_COMBAT_LINES,
    MAX_DICE_LOG,
    MAX_LOG_DISPLAY,
    MAX_LOG_ENTRY_LENGTH,
    MODE_CVC,
    MODE_HVC,
    PANEL_BG,
    PANEL_BG_LIGHT,
    PANEL_BORDER,
    PANEL_BORDER_GLOW,
    PANEL_CORNER_RADIUS,
    PANEL_GLASS_ALPHA,
    PANEL_GLASS_BORDER_ALPHA,
    PANEL_PADDING,
    PANEL_SECTION_GAP,
    PANEL_WIDTH,
    PANEL_X,
    TEXT_ACCENT,
    TEXT_DANGER,
    TEXT_HIGHLIGHT,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_SUCCESS,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)

COMBAT_KEYWORDS = ("Brawl:", "Assault:", "Swoop:")

# ---------------------------------------------------------------------------
# Dice log (module-level)
# ---------------------------------------------------------------------------
_dice_log: List[str] = []


def log_dice(label: str, result: Any) -> None:
    _dice_log.append(f"{label}: {result}")
    if len(_dice_log) > MAX_DICE_LOG:
        _dice_log.pop(0)


def clear_dice_log() -> None:
    _dice_log.clear()


# ---------------------------------------------------------------------------
# Font helpers
# ---------------------------------------------------------------------------
_font_cache: Dict[Tuple[str, int, bool], pygame.font.Font] = {}


def _font(size: int, bold: bool = False) -> pygame.font.Font:
    key = ("arial", size, bold)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.SysFont(
            "arial,helvetica,sans-serif", size, bold=bold,
        )
    return _font_cache[key]


def _mono(size: int) -> pygame.font.Font:
    key = ("mono", size, False)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.SysFont(
            "couriernew,courier,monospace", size,
        )
    return _font_cache[key]


# ---------------------------------------------------------------------------
# Drawing helpers — Tier 4 glass-morphism style
# ---------------------------------------------------------------------------


def _draw_rounded_rect(
    surface: pygame.Surface,
    color: Tuple[int, ...],
    rect: pygame.Rect,
    radius: int = 6,
    border: int = 0,
) -> None:
    """Draw a rounded rectangle with optional glass-morphism effect."""
    if len(color) == 4:
        tmp = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(tmp, color, (0, 0, rect.width, rect.height), border, radius)
        surface.blit(tmp, rect.topleft)
    else:
        pygame.draw.rect(surface, color, rect, border, radius)


def _draw_glass_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    radius: int = PANEL_CORNER_RADIUS,
) -> None:
    """Draw a frosted-glass panel with translucent background and glow border."""
    # Main background
    _draw_rounded_rect(
        surface, (*PANEL_BG, PANEL_GLASS_ALPHA), rect, radius,
    )
    # Top glow border (bright line at top edge)
    glow_rect = pygame.Rect(rect.x + 2, rect.y, rect.width - 4, 1)
    _draw_rounded_rect(
        surface, (*PANEL_BORDER_GLOW, PANEL_GLASS_BORDER_ALPHA), glow_rect, 0,
    )
    # Outer border
    _draw_rounded_rect(
        surface, PANEL_BORDER, rect, radius, 1,
    )


def _draw_glass_button(
    surface: pygame.Surface,
    rect: pygame.Rect,
    text: str,
    hovered: bool = False,
    pressed: bool = False,
) -> None:
    """Draw a gradient button with glass-morphism style."""
    if pressed:
        color = BUTTON_ACTIVE
    elif hovered:
        color = BUTTON_HOVER
    else:
        color = BUTTON_COLOR

    # Gradient fill (top lighter, bottom darker)
    grad_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    top_color = BUTTON_GRADIENT_TOP if not (hovered or pressed) else color
    bot_color = BUTTON_GRADIENT_BOTTOM if not (hovered or pressed) else color
    for row in range(rect.height):
        t = row / max(1, rect.height - 1)
        r = int(top_color[0] + (bot_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bot_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bot_color[2] - top_color[2]) * t)
        pygame.draw.line(grad_surf, (r, g, b, 240), (0, row), (rect.width - 1, row))

    # Clip to rounded rect
    mask_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(
        mask_surf, (255, 255, 255, 255),
        (0, 0, rect.width, rect.height), 0, BUTTON_CORNER_RADIUS,
    )
    grad_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surface.blit(grad_surf, rect.topleft)

    # Border
    _draw_rounded_rect(
        surface, BUTTON_BORDER, rect, BUTTON_CORNER_RADIUS, 1,
    )
    # Top highlight
    pygame.draw.line(
        surface, (*PANEL_BORDER_GLOW, 50),
        (rect.x + 3, rect.y + 1), (rect.x + rect.width - 3, rect.y + 1),
    )

    font = _font(FONT_SIZE_BODY)
    txt = font.render(text, True, BUTTON_TEXT)
    surface.blit(
        txt,
        (rect.centerx - txt.get_width() // 2,
         rect.centery - txt.get_height() // 2),
    )


# ---------------------------------------------------------------------------
# Button
# ---------------------------------------------------------------------------


class Button:
    """Tier 4 themed button with gradient fill and glow border."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        callback: Optional[Callable[[], None]] = None,
    ) -> None:
        self.rect = rect
        self.text = text
        self.callback = callback
        self.hovered = False
        self.pressed = False
        self.visible = True

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        _draw_glass_button(
            surface, self.rect, self.text, self.hovered, self.pressed,
        )

    def handle_motion(self, pos: Tuple[int, int]) -> None:
        self.hovered = self.rect.collidepoint(pos)
        if not self.hovered:
            self.pressed = False

    def handle_click(self, pos: Tuple[int, int]) -> bool:
        if self.visible and self.rect.collidepoint(pos):
            self.pressed = True
            if self.callback:
                self.callback()
            return True
        return False

    def handle_release(self) -> None:
        self.pressed = False


# ---------------------------------------------------------------------------
# Text input box
# ---------------------------------------------------------------------------


class TextInput:
    """Minimal text input field with glass-morphism styling."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str = "",
        placeholder: str = "",
    ) -> None:
        self.rect = rect
        self.text = text
        self.placeholder = placeholder
        self.focused = False
        self.cursor_visible = True
        self._cursor_timer = 0

    def draw(self, surface: pygame.Surface) -> None:
        bg = (*PANEL_BG_LIGHT, 220) if self.focused else (*PANEL_BG, 200)
        _draw_rounded_rect(surface, bg, self.rect, 5)
        border = PANEL_BORDER_GLOW if self.focused else PANEL_BORDER
        _draw_rounded_rect(surface, border, self.rect, 5, 1)
        font = _font(FONT_SIZE_BODY)
        display = self.text if self.text else self.placeholder
        color = TEXT_PRIMARY if self.text else TEXT_SECONDARY
        txt = font.render(display, True, color)
        surface.blit(
            txt,
            (self.rect.x + 6, self.rect.centery - txt.get_height() // 2),
        )
        if self.focused and self.cursor_visible:
            cx = self.rect.x + 6 + font.size(self.text)[0]
            pygame.draw.line(
                surface, TEXT_PRIMARY,
                (cx, self.rect.y + 4), (cx, self.rect.bottom - 4), 1,
            )

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.focused = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.focused:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_TAB:
                pass
            elif event.unicode and len(self.text) < 25:
                self.text += event.unicode

    def update(self, dt_ms: float = 16) -> None:
        self._cursor_timer += dt_ms
        if self._cursor_timer > 530:
            self._cursor_timer = 0
            self.cursor_visible = not self.cursor_visible


# ---------------------------------------------------------------------------
# Side panel — glass-morphism panels with tier 4 styling
# ---------------------------------------------------------------------------


class SidePanel:
    """Right-side information panels with glass-morphism backgrounds."""

    def __init__(self) -> None:
        self._scroll_y = 0

    def draw(
        self,
        surface: pygame.Surface,
        game: Any,
        selected_figure: Optional[Any],
        mode: str,
    ) -> None:
        x = PANEL_X
        y = 55
        w = PANEL_WIDTH

        snapshot = game.snapshot()

        y = self._section_scoreboard(surface, x, y, w, snapshot)
        y = self._section_phase(surface, x, y, w, snapshot)
        y = self._section_selected(surface, x, y, w, selected_figure, game)
        y = self._section_penalty_box(surface, x, y, w, game)
        y = self._section_combat(surface, x, y, w, game)
        y = self._section_dice(surface, x, y, w)
        y = self._section_log(surface, x, y, w, game)

    def _draw_section(
        self,
        surface: pygame.Surface,
        x: int, y: int, w: int, h: int,
        title: str,
    ) -> int:
        """Draw a glass-morphism section background and return inner y."""
        rect = pygame.Rect(x, y, w, h)
        _draw_glass_panel(surface, rect)
        font = _font(FONT_SIZE_TITLE, bold=True)
        title_surf = font.render(title, True, TEXT_ACCENT)
        surface.blit(title_surf, (x + PANEL_PADDING, y + 4))
        return y + 20

    def _section_scoreboard(
        self, surface: pygame.Surface, x: int, y: int, w: int, snapshot: Dict,
    ) -> int:
        h = 72
        iy = self._draw_section(surface, x, y, w, h, "Scoreboard")
        font = _font(FONT_SIZE_BODY)
        scores = snapshot["scores"]
        for name, score in scores.items():
            txt = font.render(f"{name}: {score}", True, TEXT_PRIMARY)
            surface.blit(txt, (x + PANEL_PADDING, iy))
            iy += 15
        txt = font.render(
            f"Period {snapshot['period']}  Turn {snapshot['turn']}  "
            f"{snapshot['time_remaining']}:00",
            True, TEXT_SECONDARY,
        )
        surface.blit(txt, (x + PANEL_PADDING, iy))
        return y + h + PANEL_SECTION_GAP

    def _section_phase(
        self, surface: pygame.Surface, x: int, y: int, w: int, snapshot: Dict,
    ) -> int:
        h = 40
        iy = self._draw_section(surface, x, y, w, h, "Phase")
        font = _font(FONT_SIZE_BODY)
        phase_txt = snapshot.get("phase", "—")
        init_txt = f"Initiative: Sector {snapshot.get('initiative_sector', '?')}"
        txt = font.render(f"{phase_txt}   {init_txt}", True, TEXT_HIGHLIGHT)
        surface.blit(txt, (x + PANEL_PADDING, iy))
        return y + h + PANEL_SECTION_GAP

    def _section_selected(
        self,
        surface: pygame.Surface,
        x: int, y: int, w: int,
        figure: Optional[Any],
        game: Any,
    ) -> int:
        if figure is None:
            h = 28
            iy = self._draw_section(surface, x, y, w, h, "Selected Figure")
            font = _font(FONT_SIZE_SMALL)
            txt = font.render("Click a figure to select", True, TEXT_SECONDARY)
            surface.blit(txt, (x + PANEL_PADDING, iy))
            return y + h + PANEL_SECTION_GAP

        h = 110
        iy = self._draw_section(surface, x, y, w, h, "Selected Figure")
        font = _font(FONT_SIZE_BODY)

        name = getattr(figure, "name", "?")
        ftype = figure.figure_type.value.title()
        status = figure.status.value
        txt = font.render(f"{name} ({ftype})", True, TEXT_PRIMARY)
        surface.blit(txt, (x + PANEL_PADDING, iy))
        iy += 15
        txt = font.render(f"Status: {status}", True, TEXT_SECONDARY)
        surface.blit(txt, (x + PANEL_PADDING, iy))
        iy += 15
        stats = (
            f"SPD {figure.speed}  SKL {figure.skill}  "
            f"COM {figure.combat}  TGH {figure.toughness}"
        )
        txt = font.render(stats, True, TEXT_PRIMARY)
        surface.blit(txt, (x + PANEL_PADDING, iy))
        iy += 15

        sq = game.board.find_square_of_figure(figure)
        if sq is not None:
            loc = f"Sector {sq.sector_index}  {sq.ring.value}  Pos {sq.position}"
            txt = font.render(loc, True, TEXT_SECONDARY)
            surface.blit(txt, (x + PANEL_PADDING, iy))
            iy += 15

        # Tow info
        if getattr(figure, "is_towed", False):
            biker = getattr(figure, "towed_by", None)
            if biker:
                txt = font.render(f"Towed by {biker.name}", True, TEXT_SUCCESS)
                surface.blit(txt, (x + PANEL_PADDING, iy))
                iy += 15

        # Ball indicator
        if figure.has_ball:
            txt = font.render("CARRYING BALL", True, TEXT_ACCENT)
            surface.blit(txt, (x + PANEL_PADDING, iy))

        return y + h + PANEL_SECTION_GAP

    def _section_penalty_box(
        self, surface: pygame.Surface, x: int, y: int, w: int, game: Any,
    ) -> int:
        penalized: List[str] = []
        for fig in game.all_figures():
            if getattr(fig, "penalty_timer", 0) > 0:
                penalized.append(
                    f"{fig.name} ({fig.penalty_timer}min)"
                )

        h = max(28, 20 + len(penalized) * 14)
        iy = self._draw_section(surface, x, y, w, h, "Penalty Box")
        font = _font(FONT_SIZE_SMALL)
        if not penalized:
            txt = font.render("Empty", True, TEXT_SECONDARY)
            surface.blit(txt, (x + PANEL_PADDING, iy))
        else:
            for entry in penalized[:6]:
                txt = font.render(entry, True, TEXT_DANGER)
                surface.blit(txt, (x + PANEL_PADDING, iy))
                iy += 14
        return y + h + PANEL_SECTION_GAP

    def _section_combat(
        self, surface: pygame.Surface, x: int, y: int, w: int, game: Any,
    ) -> int:
        combat_lines: List[str] = []
        for msg in reversed(game.log):
            if any(kw in msg for kw in COMBAT_KEYWORDS):
                combat_lines.append(msg[:MAX_LOG_ENTRY_LENGTH])
                if len(combat_lines) >= MAX_COMBAT_LINES:
                    break

        h = max(28, 20 + len(combat_lines) * 14)
        iy = self._draw_section(surface, x, y, w, h, "Combat Log")
        font = _font(FONT_SIZE_SMALL)
        if not combat_lines:
            txt = font.render("No combat yet", True, TEXT_SECONDARY)
            surface.blit(txt, (x + PANEL_PADDING, iy))
        else:
            for line in combat_lines:
                txt = font.render(line, True, TEXT_PRIMARY)
                surface.blit(txt, (x + PANEL_PADDING, iy))
                iy += 14
        return y + h + PANEL_SECTION_GAP

    def _section_dice(
        self, surface: pygame.Surface, x: int, y: int, w: int,
    ) -> int:
        recent = _dice_log[-6:] if _dice_log else []
        h = max(28, 20 + len(recent) * 13)
        iy = self._draw_section(surface, x, y, w, h, "Dice Rolls")
        font = _mono(FONT_SIZE_SMALL)
        if not recent:
            txt = font.render("No rolls yet", True, TEXT_SECONDARY)
            surface.blit(txt, (x + PANEL_PADDING, iy))
        else:
            for entry in recent:
                txt = font.render(entry[:MAX_LOG_ENTRY_LENGTH], True, TEXT_PRIMARY)
                surface.blit(txt, (x + PANEL_PADDING, iy))
                iy += 13
        return y + h + PANEL_SECTION_GAP

    def _section_log(
        self, surface: pygame.Surface, x: int, y: int, w: int, game: Any,
    ) -> int:
        entries = game.log[-MAX_LOG_DISPLAY:] if game.log else []
        recent = entries[-8:]
        h = max(28, 20 + len(recent) * 13)
        iy = self._draw_section(surface, x, y, w, h, "Replay Log")
        font = _font(FONT_SIZE_SMALL)
        if not recent:
            txt = font.render("No events yet", True, TEXT_SECONDARY)
            surface.blit(txt, (x + PANEL_PADDING, iy))
        else:
            for entry in recent:
                truncated = entry[:MAX_LOG_ENTRY_LENGTH]
                txt = font.render(truncated, True, TEXT_SECONDARY)
                surface.blit(txt, (x + PANEL_PADDING, iy))
                iy += 13
        return y + h + PANEL_SECTION_GAP


# ---------------------------------------------------------------------------
# Control bar
# ---------------------------------------------------------------------------


class ControlBar:
    """Top control bar with glass-morphism buttons."""

    def __init__(self) -> None:
        self.buttons: List[Button] = []
        self._mode_label = ""
        self._interaction_label = ""

    def build(self, actions: Dict[str, Callable]) -> None:
        self.buttons.clear()
        x = 10
        for label, callback in actions.items():
            w = max(80, _font(FONT_SIZE_BODY).size(label)[0] + 18)
            self.buttons.append(
                Button(pygame.Rect(x, 12, w, BUTTON_HEIGHT), label, callback)
            )
            x += w + BUTTON_PADDING

    def update_state(self, game: Any, mode: str) -> None:
        self._mode_label = mode

    def set_interaction(self, text: str) -> None:
        self._interaction_label = text

    def draw(self, surface: pygame.Surface) -> None:
        # Top bar background — glass-morphism strip
        bar_rect = pygame.Rect(0, 0, WINDOW_WIDTH, 50)
        bar_surf = pygame.Surface((WINDOW_WIDTH, 50), pygame.SRCALPHA)
        bar_surf.fill((*PANEL_BG, PANEL_GLASS_ALPHA))
        surface.blit(bar_surf, (0, 0))
        # Bottom glow line
        pygame.draw.line(
            surface, (*PANEL_BORDER_GLOW, 40),
            (0, 49), (WINDOW_WIDTH, 49),
        )

        for btn in self.buttons:
            btn.draw(surface)

        # Mode label
        right_x = self.buttons[-1].rect.right + 16 if self.buttons else 200
        font = _font(FONT_SIZE_LABEL)
        mode_surf = font.render(self._mode_label, True, TEXT_SECONDARY)
        surface.blit(mode_surf, (right_x, 20))

        # Interaction label
        if self._interaction_label:
            ilabel = font.render(
                self._interaction_label[:MAX_ACTION_TEXT_LENGTH],
                True, TEXT_HIGHLIGHT,
            )
            surface.blit(ilabel, (right_x, 35))

    def handle_motion(self, pos: Tuple[int, int]) -> None:
        for btn in self.buttons:
            btn.handle_motion(pos)

    def handle_click(self, pos: Tuple[int, int]) -> None:
        for btn in self.buttons:
            btn.handle_click(pos)


# ---------------------------------------------------------------------------
# Dialog system
# ---------------------------------------------------------------------------


class DialogBase:
    """Base class for modal dialogs with glass-morphism backdrop."""

    def __init__(self, width: int = 500, height: int = 400) -> None:
        self.width = width
        self.height = height
        self.done = False
        self.buttons: List[Button] = []
        cx = WINDOW_WIDTH // 2 - width // 2
        cy = WINDOW_HEIGHT // 2 - height // 2
        self.rect = pygame.Rect(cx, cy, width, height)

    def draw(self, surface: pygame.Surface) -> None:
        # Overlay
        overlay = pygame.Surface(
            (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA,
        )
        overlay.fill((0, 0, 0, DIALOG_OVERLAY_ALPHA))
        surface.blit(overlay, (0, 0))

        # Dialog box — glass-morphism
        dlg_surf = pygame.Surface(
            (self.width, self.height), pygame.SRCALPHA,
        )
        dlg_surf.fill((*DIALOG_BG, DIALOG_GLASS_ALPHA))
        surface.blit(dlg_surf, self.rect.topleft)

        # Top glow
        pygame.draw.line(
            surface, (*PANEL_BORDER_GLOW, 70),
            (self.rect.x + 3, self.rect.y + 1),
            (self.rect.right - 3, self.rect.y + 1),
        )
        # Border
        pygame.draw.rect(
            surface, DIALOG_BORDER, self.rect, 1, DIALOG_CORNER_RADIUS,
        )

        self._draw_content(surface)
        for btn in self.buttons:
            btn.draw(surface)

    def _draw_content(self, surface: pygame.Surface) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            for btn in self.buttons:
                btn.handle_motion(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                btn.handle_click(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            for btn in self.buttons:
                btn.handle_release()


class NewMatchDialog(DialogBase):
    """Mode selection and team names dialog."""

    def __init__(self) -> None:
        super().__init__(420, 340)
        self.result_mode: Optional[str] = None
        self.result_home_name = "Home"
        self.result_visitor_name = "Visitor"
        self.wants_team_gen: Tuple[bool, bool] = (False, False)
        self._gen_home = False
        self._gen_vis = False

        self._mode = MODE_CVC
        self._home_input = TextInput(
            pygame.Rect(self.rect.x + 120, self.rect.y + 100, 250, 28), "Home",
        )
        self._visitor_input = TextInput(
            pygame.Rect(self.rect.x + 120, self.rect.y + 140, 250, 28), "Visitor",
        )

        # Mode toggle buttons
        self._cvc_btn = Button(
            pygame.Rect(self.rect.x + 30, self.rect.y + 55, 170, 28),
            "Computer vs Computer",
            lambda: self._set_mode(MODE_CVC),
        )
        self._hvc_btn = Button(
            pygame.Rect(self.rect.x + 210, self.rect.y + 55, 170, 28),
            "Human vs Computer",
            lambda: self._set_mode(MODE_HVC),
        )

        # Gen checkboxes (simple toggle buttons)
        self._gen_home_btn = Button(
            pygame.Rect(self.rect.x + 30, self.rect.y + 190, 170, 28),
            "Generate Home",
            self._toggle_gen_home,
        )
        self._gen_vis_btn = Button(
            pygame.Rect(self.rect.x + 210, self.rect.y + 190, 170, 28),
            "Generate Visitor",
            self._toggle_gen_vis,
        )

        self.buttons = [
            self._cvc_btn,
            self._hvc_btn,
            self._gen_home_btn,
            self._gen_vis_btn,
            Button(
                pygame.Rect(
                    self.rect.x + self.width // 2 - 60,
                    self.rect.y + self.height - 50,
                    120, 34,
                ),
                "Start Match",
                self._start,
            ),
        ]

    def _set_mode(self, m: str) -> None:
        self._mode = m

    def _toggle_gen_home(self) -> None:
        self._gen_home = not self._gen_home

    def _toggle_gen_vis(self) -> None:
        self._gen_vis = not self._gen_vis

    def _start(self) -> None:
        self.result_mode = self._mode
        self.result_home_name = self._home_input.text or "Home"
        self.result_visitor_name = self._visitor_input.text or "Visitor"
        self.wants_team_gen = (self._gen_home, self._gen_vis)
        self.done = True

    def _draw_content(self, surface: pygame.Surface) -> None:
        font = _font(FONT_SIZE_HEADER, bold=True)
        title = font.render("New Match", True, TEXT_ACCENT)
        surface.blit(title, (self.rect.x + 20, self.rect.y + 14))

        font = _font(FONT_SIZE_BODY)
        # Mode indicator
        mode_color = TEXT_HIGHLIGHT if self._mode == MODE_CVC else TEXT_SECONDARY
        txt = font.render(f"Mode: {self._mode}", True, mode_color)
        surface.blit(txt, (self.rect.x + 30, self.rect.y + 88))

        # Labels
        txt = font.render("Home:", True, TEXT_PRIMARY)
        surface.blit(txt, (self.rect.x + 30, self.rect.y + 106))
        txt = font.render("Visitor:", True, TEXT_PRIMARY)
        surface.blit(txt, (self.rect.x + 30, self.rect.y + 146))

        self._home_input.draw(surface)
        self._visitor_input.draw(surface)

        # Gen state indicators
        if self._gen_home:
            pygame.draw.circle(
                surface, TEXT_SUCCESS,
                (self.rect.x + 20, self.rect.y + 204), 5,
            )
        if self._gen_vis:
            pygame.draw.circle(
                surface, TEXT_SUCCESS,
                (self.rect.x + 200, self.rect.y + 204), 5,
            )

    def handle_event(self, event: pygame.event.Event) -> None:
        super().handle_event(event)
        self._home_input.handle_event(event)
        self._visitor_input.handle_event(event)


class TeamGenDialog(DialogBase):
    """Team generation preview dialog."""

    def __init__(self, side: TeamSide, name: str) -> None:
        super().__init__(550, 480)
        self.side = side
        self.team_name = name
        self.result_team: Optional[Team] = None
        self._team = Team(name)
        self._team.generate_roster()

        self.buttons = [
            Button(
                pygame.Rect(self.rect.x + 30, self.rect.y + self.height - 50, 120, 34),
                "Roll Team",
                self._reroll,
            ),
            Button(
                pygame.Rect(
                    self.rect.x + self.width - 150,
                    self.rect.y + self.height - 50,
                    120, 34,
                ),
                "Accept",
                self._accept,
            ),
        ]

    def _reroll(self) -> None:
        self._team = Team(self.team_name)
        self._team.generate_roster()

    def _accept(self) -> None:
        self.result_team = self._team
        self.done = True

    def _draw_content(self, surface: pygame.Surface) -> None:
        font_h = _font(FONT_SIZE_HEADER, bold=True)
        title = font_h.render(f"Team: {self.team_name}", True, TEXT_ACCENT)
        surface.blit(title, (self.rect.x + 20, self.rect.y + 14))

        font = _font(FONT_SIZE_SMALL)
        y = self.rect.y + 42
        headers = "Name                Type      SPD SKL COM TGH"
        txt = font.render(headers, True, TEXT_HIGHLIGHT)
        surface.blit(txt, (self.rect.x + 16, y))
        y += 16

        for fig in self._team.roster[:20]:
            ftype = fig.figure_type.value[:7].ljust(9)
            line = (
                f"{fig.name[:20]:<20s} {ftype} "
                f"{fig.speed:>3d} {fig.skill:>3d} {fig.combat:>3d} {fig.toughness:>3d}"
            )
            txt = font.render(line, True, TEXT_PRIMARY)
            surface.blit(txt, (self.rect.x + 16, y))
            y += 14


class CombatTargetDialog(DialogBase):
    """Choose which opponent to attack."""

    def __init__(self, attacker: Any, opponents: List[Any]) -> None:
        super().__init__(400, 60 + len(opponents) * 36 + 20)
        self.attacker = attacker
        self.opponents = opponents
        self.result: Optional[Any] = None

        for i, opp in enumerate(opponents):
            lbl = f"{opp.name} (COM {opp.combat})"
            btn = Button(
                pygame.Rect(
                    self.rect.x + 30,
                    self.rect.y + 50 + i * 36,
                    340, 30,
                ),
                lbl,
                lambda o=opp: self._pick(o),
            )
            self.buttons.append(btn)

    def _pick(self, opp: Any) -> None:
        self.result = opp
        self.done = True

    def _draw_content(self, surface: pygame.Surface) -> None:
        font = _font(FONT_SIZE_HEADER, bold=True)
        title = font.render(
            f"Target for {self.attacker.name}?", True, TEXT_ACCENT,
        )
        surface.blit(title, (self.rect.x + 20, self.rect.y + 14))


class EscalateDialog(DialogBase):
    """Marginal brawl escalation prompt."""

    def __init__(self, figure: Any, opponent: Any) -> None:
        super().__init__(380, 160)
        self.figure = figure
        self.opponent = opponent
        self.result: bool = False
        self.buttons = [
            Button(
                pygame.Rect(self.rect.x + 40, self.rect.y + 110, 130, 34),
                "Escalate",
                self._yes,
            ),
            Button(
                pygame.Rect(self.rect.x + 200, self.rect.y + 110, 130, 34),
                "Decline",
                self._no,
            ),
        ]

    def _yes(self) -> None:
        self.result = True
        self.done = True

    def _no(self) -> None:
        self.result = False
        self.done = True

    def _draw_content(self, surface: pygame.Surface) -> None:
        font = _font(FONT_SIZE_HEADER, bold=True)
        title = font.render("Escalate to Man-to-Man?", True, TEXT_ACCENT)
        surface.blit(title, (self.rect.x + 20, self.rect.y + 14))
        font = _font(FONT_SIZE_BODY)
        txt = font.render(
            f"{self.figure.name} vs {self.opponent.name}",
            True, TEXT_PRIMARY,
        )
        surface.blit(txt, (self.rect.x + 20, self.rect.y + 50))
        txt = font.render(
            "Marginal result — escalate to man-to-man combat?",
            True, TEXT_SECONDARY,
        )
        surface.blit(txt, (self.rect.x + 20, self.rect.y + 72))


class TowBarDialog(DialogBase):
    """Tow bar attachment selection."""

    def __init__(self, biker: Any, candidates: List[Any]) -> None:
        super().__init__(420, 60 + len(candidates) * 34 + 60)
        self.biker = biker
        self.candidates = candidates
        self.result: Optional[List[Any]] = None
        self._selected: List[bool] = [False] * len(candidates)

        for i, cand in enumerate(candidates):
            lbl = f"{cand.name} (SPD {cand.speed})"
            self.buttons.append(
                Button(
                    pygame.Rect(
                        self.rect.x + 30,
                        self.rect.y + 50 + i * 34,
                        340, 28,
                    ),
                    lbl,
                    lambda idx=i: self._toggle(idx),
                ),
            )
        self.buttons.append(
            Button(
                pygame.Rect(
                    self.rect.x + self.width // 2 - 60,
                    self.rect.y + self.height - 50,
                    120, 34,
                ),
                "Confirm",
                self._confirm,
            ),
        )

    def _toggle(self, idx: int) -> None:
        self._selected[idx] = not self._selected[idx]

    def _confirm(self) -> None:
        self.result = [
            c for c, s in zip(self.candidates, self._selected) if s
        ]
        self.done = True

    def _draw_content(self, surface: pygame.Surface) -> None:
        font = _font(FONT_SIZE_HEADER, bold=True)
        title = font.render(
            f"Tow Bar: {self.biker.name}", True, TEXT_ACCENT,
        )
        surface.blit(title, (self.rect.x + 20, self.rect.y + 14))

        for i, selected in enumerate(self._selected):
            if selected:
                pygame.draw.circle(
                    surface, TEXT_SUCCESS,
                    (self.rect.x + 18, self.rect.y + 64 + i * 34),
                    5,
                )


class ScoringDialog(DialogBase):
    """Scoring attempt decision."""

    def __init__(self, shooter: Any, modifiers: List[Tuple[str, int]]) -> None:
        super().__init__(400, 200 + len(modifiers) * 16)
        self.shooter = shooter
        self.modifiers = modifiers
        self.result: bool = False

        self.buttons = [
            Button(
                pygame.Rect(self.rect.x + 40, self.rect.y + self.height - 50, 130, 34),
                "Shoot!",
                self._shoot,
            ),
            Button(
                pygame.Rect(self.rect.x + 200, self.rect.y + self.height - 50, 130, 34),
                "Pass",
                self._skip,
            ),
        ]

    def _shoot(self) -> None:
        self.result = True
        self.done = True

    def _skip(self) -> None:
        self.result = False
        self.done = True

    def _draw_content(self, surface: pygame.Surface) -> None:
        font = _font(FONT_SIZE_HEADER, bold=True)
        title = font.render("Scoring Attempt", True, TEXT_ACCENT)
        surface.blit(title, (self.rect.x + 20, self.rect.y + 14))

        font = _font(FONT_SIZE_BODY)
        txt = font.render(
            f"Shooter: {self.shooter.name} (SKL {self.shooter.skill})",
            True, TEXT_PRIMARY,
        )
        surface.blit(txt, (self.rect.x + 20, self.rect.y + 45))

        y = self.rect.y + 70
        total = 0
        for desc, val in self.modifiers:
            sign = f"+{val}" if val >= 0 else str(val)
            txt = font.render(f"  {desc}: {sign}", True, TEXT_SECONDARY)
            surface.blit(txt, (self.rect.x + 20, y))
            y += 16
            total += val

        sign = f"+{total}" if total >= 0 else str(total)
        txt = font.render(f"Total modifier: {sign}", True, TEXT_HIGHLIGHT)
        surface.blit(txt, (self.rect.x + 20, y + 6))


class PackFormationDialog(DialogBase):
    """Pack formation selection."""

    def __init__(self, packs: List[List[Any]]) -> None:
        super().__init__(450, 60 + len(packs) * 34 + 60)
        self.packs = packs
        self.result: Optional[List[int]] = None
        self._selected: List[bool] = [False] * len(packs)

        for i, pack in enumerate(packs):
            names = ", ".join(f.name for f in pack[:3])
            if len(pack) > 3:
                names += f" +{len(pack) - 3}"
            self.buttons.append(
                Button(
                    pygame.Rect(
                        self.rect.x + 20,
                        self.rect.y + 50 + i * 34,
                        400, 28,
                    ),
                    f"Pack {i + 1}: {names}",
                    lambda idx=i: self._toggle(idx),
                ),
            )
        self.buttons.append(
            Button(
                pygame.Rect(
                    self.rect.x + self.width // 2 - 60,
                    self.rect.y + self.height - 50,
                    120, 34,
                ),
                "Confirm",
                self._confirm,
            ),
        )

    def _toggle(self, idx: int) -> None:
        self._selected[idx] = not self._selected[idx]

    def _confirm(self) -> None:
        self.result = [i for i, s in enumerate(self._selected) if s]
        self.done = True

    def _draw_content(self, surface: pygame.Surface) -> None:
        font = _font(FONT_SIZE_HEADER, bold=True)
        title = font.render("Pack Formation", True, TEXT_ACCENT)
        surface.blit(title, (self.rect.x + 20, self.rect.y + 14))

        for i, selected in enumerate(self._selected):
            if selected:
                pygame.draw.circle(
                    surface, TEXT_SUCCESS,
                    (self.rect.x + 12, self.rect.y + 64 + i * 34),
                    5,
                )


class GameOverDialog(DialogBase):
    """Match result and final scores."""

    def __init__(self, result: str, scores: Dict[str, int]) -> None:
        super().__init__(400, 200)
        self.match_result = result
        self.scores = scores
        self.buttons = [
            Button(
                pygame.Rect(
                    self.rect.x + self.width // 2 - 50,
                    self.rect.y + self.height - 50,
                    100, 34,
                ),
                "OK",
                self._close,
            ),
        ]

    def _close(self) -> None:
        self.done = True

    def _draw_content(self, surface: pygame.Surface) -> None:
        font = _font(FONT_SIZE_HEADER, bold=True)
        title = font.render("GAME OVER", True, TEXT_ACCENT)
        surface.blit(
            title,
            (self.rect.centerx - title.get_width() // 2, self.rect.y + 20),
        )

        font = _font(FONT_SIZE_TITLE, bold=True)
        if self.match_result == "Draw":
            res_text = "DRAW"
        else:
            res_text = f"WINNER: {self.match_result}"
        txt = font.render(res_text, True, TEXT_HIGHLIGHT)
        surface.blit(
            txt,
            (self.rect.centerx - txt.get_width() // 2, self.rect.y + 55),
        )

        font = _font(FONT_SIZE_BODY)
        y = self.rect.y + 90
        for name, score in self.scores.items():
            txt = font.render(f"{name}: {score}", True, TEXT_PRIMARY)
            surface.blit(
                txt,
                (self.rect.centerx - txt.get_width() // 2, y),
            )
            y += 22


class MessageDialog(DialogBase):
    """Simple message box."""

    def __init__(self, title: str, message: str) -> None:
        super().__init__(380, 150)
        self._title = title
        self._message = message
        self.buttons = [
            Button(
                pygame.Rect(
                    self.rect.x + self.width // 2 - 50,
                    self.rect.y + self.height - 50,
                    100, 34,
                ),
                "OK",
                self._close,
            ),
        ]

    def _close(self) -> None:
        self.done = True

    def _draw_content(self, surface: pygame.Surface) -> None:
        font = _font(FONT_SIZE_HEADER, bold=True)
        title = font.render(self._title, True, TEXT_ACCENT)
        surface.blit(title, (self.rect.x + 20, self.rect.y + 14))
        font = _font(FONT_SIZE_BODY)
        txt = font.render(self._message, True, TEXT_PRIMARY)
        surface.blit(txt, (self.rect.x + 20, self.rect.y + 50))
