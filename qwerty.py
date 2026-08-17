#!/usr/bin/env python
import json
import pyperclip
import pygame
import time
import math
from crypto_ops import *
from qwerty_oauth import *
from enum import Enum

create_qwertyfile_if_not_exists()

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

ONLY_EDIT_MODE = False

BACKGROUND_COLOR = (0, 0, 0)
DEFAULT_TEXT_COLOR = (255, 255, 255)
SLIGHTLY_DISABLED_TEXT_COLOR = (200, 200, 200)

TEXTINPUT_DEFAULT_BACKGROUND_COLOR = (20, 20, 20)
TEXTINPUT_HOVER_BACKGROUND_COLOR = (30, 30, 30)
TEXTINPUT_FOCUS_BACKGROUND_COLOR = (50, 50, 50)
TEXTINPUT_ALT_TEXT_COLOR = (120, 120, 120)

BUTTON_DEFAULT_BACKGROUND_COLOR = (70, 70, 70)
BUTTON_HOVER_BACKGROUND_COLOR = (100, 100, 100)
BUTTON_FOCUS_BACKGROUND_COLOR = (120, 120, 120)

def get_color_setting(json_object, key, default_value):
    color_setting = json_object[key]
    if isinstance(color_setting, list) and len(color_setting) == 3 and all(isinstance(value, int) for value in color_setting):
        return tuple(color_setting)
    return default_value

try:
    with open("settings.json", "r") as settings_file:
        settings = json.load(settings_file)

    screen_width = settings["screen_width"]
    if isinstance(screen_width, int) and screen_width > 0:
        SCREEN_WIDTH = screen_width

    screen_height = settings["screen_height"]
    if isinstance(screen_height, int) and screen_height > 0:
        SCREEN_height = screen_height

    only_edit_mode = settings["only_edit_mode"]
    if isinstance(only_edit_mode, bool):
        ONLY_EDIT_MODE = only_edit_mode

    BACKGROUND_COLOR = get_color_setting(settings, "background_color", BACKGROUND_COLOR)
    DEFAULT_TEXT_COLOR = get_color_setting(settings, "default_text_color", DEFAULT_TEXT_COLOR)
    SLIGHTLY_DISABLED_TEXT_COLOR = get_color_setting(settings, "slightly_disabled_text_color", SLIGHTLY_DISABLED_TEXT_COLOR)

    TEXTINPUT_DEFAULT_BACKGROUND_COLOR = get_color_setting(settings, "textinput_default_background_color", TEXTINPUT_DEFAULT_BACKGROUND_COLOR)
    TEXTINPUT_HOVER_BACKGROUND_COLOR = get_color_setting(settings, "textinput_hover_background_color", TEXTINPUT_HOVER_BACKGROUND_COLOR)
    TEXTINPUT_FOCUS_BACKGROUND_COLOR = get_color_setting(settings, "textinput_focus_background_color", TEXTINPUT_FOCUS_BACKGROUND_COLOR)
    TEXTINPUT_ALT_TEXT_COLOR = get_color_setting(settings, "textinput_alt_text_color", TEXTINPUT_ALT_TEXT_COLOR)

    BUTTON_DEFAULT_BACKGROUND_COLOR = get_color_setting(settings, "button_default_background_color", BUTTON_DEFAULT_BACKGROUND_COLOR)
    BUTTON_HOVER_BACKGROUND_COLOR = get_color_setting(settings, "button_hover_background_color", BUTTON_HOVER_BACKGROUND_COLOR)
    BUTTON_FOCUS_BACKGROUND_COLOR = get_color_setting(settings, "button_focus_background_color", BUTTON_FOCUS_BACKGROUND_COLOR)
except:
    print("Could not open settings file")

deleted_entries = []


def collide_rect(rect, pos):
    return pos[0] > rect[0] and pos[0] < rect[0] + rect[2] and pos[1] > rect[1] and pos[1] < rect[1] + rect[3]


current_page = "pwd"
actual_pwd = ""


def save_settings():
    with open("settings.json", "w") as settings_file:
        settings = {
            "screen_width": SCREEN_WIDTH,
            "screen_height": SCREEN_HEIGHT,

            "only_edit_mode": ONLY_EDIT_MODE,

            "background_color": BACKGROUND_COLOR,
            "default_text_color": DEFAULT_TEXT_COLOR,
            "slightly_disabled_text_color": SLIGHTLY_DISABLED_TEXT_COLOR,

            "textinput_default_background_color": TEXTINPUT_DEFAULT_BACKGROUND_COLOR,
            "textinput_hover_background_color": TEXTINPUT_HOVER_BACKGROUND_COLOR,
            "textinput_focus_background_color": TEXTINPUT_FOCUS_BACKGROUND_COLOR,
            "textinput_alt_text_color": TEXTINPUT_ALT_TEXT_COLOR,

            "button_default_background_color": BUTTON_DEFAULT_BACKGROUND_COLOR,
            "button_hover_background_color": BUTTON_HOVER_BACKGROUND_COLOR,
            "button_focus_background_color": BUTTON_FOCUS_BACKGROUND_COLOR,
        }
        json.dump(settings, settings_file, indent=4)


# Returns non-zero number on error (wrong password)
def decrypt_and_goto_main_page() -> int:
    global current_page, pwd_page, main_page, actual_pwd
    pwd = pwd_page.input.text
    entries = try_decrypt(pwd)
    if not entries:
        return 1
    actual_pwd = pwd
    main_page.__init__([0, 60], SCREEN_WIDTH, SCREEN_HEIGHT - 60, entries)
    current_page = "main"
    return 0


def focus_input_2():
    global change_pwd_page
    change_pwd_page.input1.is_focused = False
    change_pwd_page.input1.editing = False
    change_pwd_page.input2.is_focused = True


def change_password(new_password):
    global actual_pwd
    actual_pwd = new_password


def goto_change_pwd_page():
    global current_page
    current_page = "change_pwd"

def goto_settings_page():
    global current_page
    current_page = "settings"

def goto_main_page():
    global current_page
    current_page = "main"


def save_data():
    global main_page, actual_pwd, start_hash, end_hash
    if actual_pwd == "":
        return
    text = main_page.entry_list.get_text()
    if save_entries(text, actual_pwd) or not os.path.exists("token.pickle"):
        try:
            drive_service = authenticate()
            upload_file(drive_service, QWERTY_FILENAME, QWERTY_FILENAME)
        except:
            print("Could not backup to drive!")


def goto_pwd():
    global current_page
    current_page = "pwd"


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("qwerty")
pygame.display.set_icon(pygame.image.load("qwerty.png"))

font = pygame.font.Font("PixelOperator8.ttf", 16)


class TextHideLevel(Enum):
    FULLY_VISIBLE = 0
    HIDDEN_UNLESS_FOCUSED = 1
    HIDDEN_UNLESS_EDITING = 2
    FULLY_HIDDEN = 3


class TextInput:

    def __init__(self,
                 pos,
                 width,
                 height,
                 text="",
                 alt_text="", # text to display when input is empty
                 onEnter=None,
                 onInput=None,
                 text_hidden_level=TextHideLevel.FULLY_VISIBLE,
                 on_navigation=None, # callback function to call when a navigation event is triggered
                 only_edit_mode=False, # makes it only either be focused or in edit mode
                 clear_on_escape=False,
                 has_copy_button=True):
        self.text = text
        self.pos = pos
        self.width = width
        self.height = height
        self.is_focused = False
        self.editing = False
        self.text_hidden_level = text_hidden_level
        self.only_edit_mode = only_edit_mode
        self.on_navigation = on_navigation
        self.clear_on_escape = clear_on_escape
        self.default_text = font.render("<lotta text>", False, SLIGHTLY_DISABLED_TEXT_COLOR)
        self.alt_text = alt_text
        self.alt_text_rendered = font.render(alt_text, False, TEXTINPUT_ALT_TEXT_COLOR)
        self.onEnter = onEnter
        self.onInput = onInput
        self.color = TEXTINPUT_DEFAULT_BACKGROUND_COLOR
        self.is_cursor_visible = True
        self.cursor_blink_timer = 0
        self.cursor_blink_time = 0.3

        self.backspace_held_timer = None
        self.backspace_hold_threshold = 0.5
        self.quick_backspace_interval = 0.05
        self.quick_backspace_timer = 0
        self.copy_button = CopyButton([0, 0], 0, 0, self.copy_value)
        self.has_copy_button = has_copy_button

    def copy_value(self):
        pyperclip.copy(self.text)

    def draw(self, screen):
        # bounding box
        pygame.draw.rect(screen, self.color, (self.pos[0], self.pos[1], self.width, self.height))

        # render stars when text should be hidden, otherwise the text
        if (
                self.text_hidden_level == TextHideLevel.FULLY_HIDDEN
                or (self.text_hidden_level == TextHideLevel.HIDDEN_UNLESS_FOCUSED and not self.is_focused)
                or (self.text_hidden_level == TextHideLevel.HIDDEN_UNLESS_EDITING and not self.editing)
                ):
            text = font.render("*" * len(self.text), False, DEFAULT_TEXT_COLOR)
        else:
            text = font.render(self.text, False, DEFAULT_TEXT_COLOR)

        # If the text fits on the screen or it's in edit mode
        if text.get_width() <= self.width or self.editing:
            # If there's text, render it
            if self.text != "":
                screen.blit(text, (self.pos[0] + self.width / 2 - text.get_width() / 2, self.pos[1] + self.height / 2 - text.get_height() / 2))
            # Otherwise render alt text if we're not editing, or if it's in edit only mode
            # (because otherwise alt text will not show in the initial password field since it's focuesd by default)
            elif not self.editing or self.only_edit_mode:
                screen.blit(self.alt_text_rendered, (self.pos[0] + self.width / 2 - self.alt_text_rendered.get_width() / 2,
                                                     self.pos[1] + self.height / 2 - self.alt_text_rendered.get_height() / 2))

            # Always render the cursor if it's in edit mode
            if self.editing and self.is_cursor_visible:
                pygame.draw.rect(
                    screen, DEFAULT_TEXT_COLOR,
                    (self.pos[0] + self.width / 2 + text.get_width() / 2, self.pos[1] + self.height / 2 - text.get_height() / 2, 10, text.get_height()))
        # If the text doesn't fit, render <lotta text>
        else:
            screen.blit(self.default_text,
                        (self.pos[0] + self.width / 2 - self.default_text.get_width() / 2, self.pos[1] + self.height / 2 - self.default_text.get_height() / 2))
        if self.has_copy_button:
            self.copy_button.draw(screen)

    def update_dims(self, pos, width, height):
        self.pos = pos
        self.width = width
        self.height = height
        self.copy_button.update_dims([self.pos[0] + self.width - self.height + 4, self.pos[1] + 4], self.height - 8, self.height - 8)

    def update(self, keys, mouseState, delta=0.0, events=[]):
        if self.has_copy_button:
            self.copy_button.update(mouseState)
        mouse_pos = mouseState[0]
        # mouse_pressed = mouseState[1]
        if self.is_focused and self.only_edit_mode:
            self.editing = True
        elif not self.is_focused:
            self.editing = False

        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.is_focused:
                    if self.editing:
                        if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE or (keys[pygame.K_LCTRL] and event.key == pygame.K_w):
                            if keys[pygame.K_LCTRL]:
                                while len(self.text) and self.text[-1] != " ":
                                    self.text = self.text[:-1]
                            if len(self.text):
                                self.backspace_held_timer = 0
                                self.text = self.text[:-1]
                        elif event.key == pygame.K_ESCAPE or (event.key == pygame.K_c and keys[pygame.K_LCTRL]):
                            self.editing = False
                            if self.only_edit_mode:
                                self.is_focused = False
                                if self.clear_on_escape:
                                    self.text = ""
                        elif event.key == pygame.K_v and keys[pygame.K_LCTRL]:
                            self.text += pyperclip.paste()
                        elif event.key == pygame.K_RETURN:
                            self.editing = False
                            if self.onEnter:
                                self.onEnter()
                        else:
                            self.text += event.unicode
                        if self.on_navigation:
                            self.on_navigation(-1) # creating a dummy navigation event so it gets scrolled to if it's off screen
                        if self.onInput:
                            self.onInput(self.text)
                    elif event.key == pygame.K_c and keys[pygame.K_LCTRL] and self.text != "":
                        pyperclip.copy(self.text)
                        if self.on_navigation:
                            self.on_navigation(-1) # creating a dummy navigation event so it gets scrolled to if it's off screen
                    elif event.key == pygame.K_v and keys[pygame.K_LCTRL]:
                        self.text = pyperclip.paste()
                        if self.on_navigation:
                            self.on_navigation(-1) # creating a dummy navigation event so it gets scrolled to if it's off screen
                    elif event.key == pygame.K_RETURN:
                        self.editing = True
                        if self.on_navigation:
                            self.on_navigation(-1) # creating a dummy navigation event so it gets scrolled to if it's off screen
                    elif event.key == pygame.K_UP or event.key == pygame.K_k:
                        if self.on_navigation:
                            self.on_navigation(0)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_h or event.key == pygame.K_b:
                        if self.on_navigation:
                            self.on_navigation(1)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_j:
                        if self.on_navigation:
                            self.on_navigation(2)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_l or event.key == pygame.K_TAB or event.key == pygame.K_e:
                        if self.on_navigation:
                            self.on_navigation(3)
                    elif event.key == pygame.K_d and keys[pygame.K_LCTRL]:
                        if self.on_navigation:
                            self.on_navigation(4)
                    elif event.key == pygame.K_u and keys[pygame.K_LCTRL]:
                        if self.on_navigation:
                            self.on_navigation(5)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if collide_rect((self.pos[0], self.pos[1], self.width - (self.height - 4)*self.has_copy_button, self.height), event.pos):
                    if self.is_focused:
                        self.editing = True
                    else:
                        self.is_focused = True
                        # If there is no text, go straight into edit mode. Also if normal mode is disabled
                        if self.text == "" or ONLY_EDIT_MODE:
                            self.editing = True
                    if self.on_navigation:
                        self.on_navigation(-1) # creating a dummy navigation event so it gets scrolled to if it's off screen
                    event.pos = (1000000000, 1000000000) # invalid position so only one thing can be clicked on at a time
                else:
                    self.is_focused = False
                    self.editing = False
        mouse_over = collide_rect((self.pos[0], self.pos[1], self.width, self.height), mouse_pos)
        if self.is_focused:
            self.color = TEXTINPUT_FOCUS_BACKGROUND_COLOR
        elif mouse_over:
            self.color = TEXTINPUT_HOVER_BACKGROUND_COLOR
        else:
            self.color = TEXTINPUT_DEFAULT_BACKGROUND_COLOR

        if self.has_copy_button:
            if mouse_over:
                self.copy_button.visible = True
            else:
                self.copy_button.visible = False


        self.cursor_blink_timer += delta
        if self.cursor_blink_timer > self.cursor_blink_time:
            self.cursor_blink_timer = 0
            self.is_cursor_visible = not self.is_cursor_visible

        if self.backspace_held_timer is not None:
            if keys[pygame.K_BACKSPACE]:
                self.backspace_held_timer += delta
                if self.backspace_held_timer > self.backspace_hold_threshold:
                    self.quick_backspace_timer += delta
                    if self.quick_backspace_timer > self.quick_backspace_interval:
                        self.quick_backspace_timer -= self.quick_backspace_interval
                        if len(self.text):
                            self.text = self.text[:-1]
            else:
                self.backspace_held_timer = None
                self.quick_backspace_timer = 0


class Button:

    def __init__(self, pos, width, height, text="", onClick=None, background_color=BUTTON_DEFAULT_BACKGROUND_COLOR, hover_color=BUTTON_HOVER_BACKGROUND_COLOR, focus_color=BUTTON_FOCUS_BACKGROUND_COLOR, text_color=DEFAULT_TEXT_COLOR):
        self.pos = pos
        self.width = width
        self.height = height
        self.text = text
        self.onClick = onClick
        self.prev_mouse_state = True
        self.color = background_color
        self.background_color = background_color
        self.hover_color = hover_color
        self.focus_color = focus_color
        self.text_color = text_color

    def draw(self, screen):
        # bounding box
        pygame.draw.rect(screen, self.color, (self.pos[0], self.pos[1], self.width, self.height))

        # text
        if self.text != "":
            text = font.render(self.text, False, self.text_color)
            screen.blit(text, (self.pos[0] + self.width / 2 - text.get_width() / 2, self.pos[1] + self.height / 2 - text.get_height() / 2))

    def update_dims(self, pos, width, height):
        self.pos = pos
        self.width = width
        self.height = height

    def update(self, mouseState):
        mouse_pos = mouseState[0]
        mouse_clicked = mouseState[1]
        colliding = collide_rect((self.pos[0], self.pos[1], self.width, self.height), mouse_pos)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and colliding:
                if self.onClick:
                    self.onClick()
        if colliding:
            if mouse_clicked:
                self.color = self.focus_color
            else:
                self.color = self.hover_color
        else:
            self.color = self.background_color
        self.prev_mouse_state = mouse_pressed


class CopyButton:
    def __init__(self, pos, width, height, copy_callback):
        self.pos = pos
        self.width = width
        self.height = height
        self.copy_button = Button(self.pos, self.width, self.height, "", copy_callback)
        self.visible = False

    def draw(self, screen):
        if self.visible:
            self.copy_button.draw(screen)
            pygame.draw.rect(screen, (150, 150, 150), (self.pos[0] + (self.width*3)//16, self.pos[1] + (self.height*3)//16, (self.width*7)//16, (self.height*7)//16))
            pygame.draw.rect(screen, (200, 200, 200), (self.pos[0] + (self.width*6)//16, self.pos[1] + (self.height*6)//16, (self.width*7)//16, (self.height*7)//16))

    def update_dims(self, pos, width, height):
        self.pos = pos
        self.width = width
        self.height = height
        self.copy_button.update_dims(self.pos, self.width, self.height)

    def update(self, mouseState):
        self.copy_button.update(mouseState)


class Entry:

    def __init__(self, pos, width, height, key="", val="", on_navigation=None, on_move_clicked=None):
        self.pos = [0, 0]
        self.deleted = False
        self.on_navigation = on_navigation
        self.key_inp = TextInput((0, 0), 0, 0, text=key, alt_text="key", on_navigation=self.on_navigation)
        self.val_inp = TextInput((0, 0),
                                 0,
                                 0,
                                 text=val,
                                 alt_text="value",
                                 text_hidden_level=TextHideLevel.HIDDEN_UNLESS_EDITING,
                                 on_navigation=self.on_navigation)
        self.del_button = Button((0, 0), 0, 0, onClick=self.delete_self, text="X")
        self.move_button= Button((0, 0), 0, 0, onClick=on_move_clicked, text="=")
        self.update_dims(pos, width, height)
        self.visible = True

    def draw(self, screen):
        if self.visible:
            self.key_inp.draw(screen)
            self.val_inp.draw(screen)
            self.del_button.draw(screen)
            self.move_button.draw(screen)

    def update_dims(self, pos, width, height, index=0, interpolation=False, delta=1/256):
        self.pos[0] = pos[0]
        diff = pos[1] - self.pos[1]
        if interpolation and abs(diff) > 0.1:
            ratio = min(30*delta, 0.5)
            self.pos[1] = pos[1]*ratio + self.pos[1]*(1-ratio)
        else:
            self.pos[1] = pos[1]
        self.width = width
        self.height = height
        self.index = index
        kv_width = self.width - 2*self.height
        self.key_inp.update_dims((self.pos[0] + self.height, self.pos[1]), kv_width / 2 - 3, self.height)
        self.val_inp.update_dims((self.pos[0] + self.height + kv_width / 2 + 3, self.pos[1]), kv_width / 2 - 3, self.height)
        self.del_button.update_dims((self.pos[0] + self.height + kv_width + 6, self.pos[1]), self.height - 6, self.height)
        self.move_button.update_dims((self.pos[0], self.pos[1]), self.height - 6, self.height)

    def delete_self(self):
        self.deleted = True
        deleted_entries.append((self.key_inp.text, self.val_inp.text))

    def update(self, keys, mouseState, delta=0.0, events=[]):
        self.key_inp.update(keys, mouseState, delta=delta, events=events)
        self.val_inp.update(keys, mouseState, delta=delta, events=events)
        self.del_button.update(mouseState)
        self.move_button.update(mouseState)


class EntryList:

    def __init__(self, pos, width, entries=[], default_y_offset=10, focus_on_searchbar=None, unfocus_on_searchbar=None):
        self.pos = [pos[0], pos[1]]
        self.y_val = pos[1] # The y value that pos[1] is trying to get to during scroll animation
        self.default_y_offset = default_y_offset
        self.width = width
        self.entry_height = 50 # height of each entry
        self.spacing = 60 # vertical distance between two entries
        self.curr_focused = -1 # twice the index of the currently focused entry, +1 if it is the value input. -1 if none
        self.filter_text = "" # Used for search
        self.focus_on_searchbar = focus_on_searchbar
        self.unfocus_on_searchbar = unfocus_on_searchbar
        self.entry_list = [
            Entry((self.pos[0], self.pos[1] + i * self.spacing), self.width, 50, key=entries[i][0], val=entries[i][1], on_navigation=self.navigate_enqueue, on_move_clicked=self.start_move_entry)
            for i in range(len(entries))
        ]
        self.add_button = Button((self.pos[0], self.pos[1] + self.spacing * len(self.entry_list)), self.width, 50, "+", onClick=self.add_entry)

        # Queue used for navigating among entries.
        self.navigate_queue = [
            0,
        ]

        # State used when dragging and rearranging an entry
        self.moving_entry = None # either an entry or none
        self.moving_index = -1 # index to which entry is trying to move (mouse hovering over this index) or -1 if no entry being moved
        self.start_move = False # Simply used as a signal to trigger the move of an entry, since the move has to be done in the update function.

        self.num_visible_entries = len(self.entry_list)

    def set_filter_text(self, text):
        self.filter_text = text

    def draw(self, screen):
        for entry in self.entry_list:
            entry.draw(screen)
        if self.moving_entry:
            self.moving_entry.draw(screen)
        self.add_button.draw(screen)

    def update_dims(self, pos, width, mouse_pos=(0, 0), interpolation=False, delta=1/256):
        self.pos = pos
        self.width = width
        is_moving = self.moving_index != -1 # whether an entry is being moved

        num_invisible_entries = 0
        for i in range(len(self.entry_list)):
            if not self.entry_list[i].visible:
                num_invisible_entries += 1
            offset = bool(is_moving and (self.moving_index <= i)) # if an entry is being moved, this offset is 1 for all entries with index >= where it is going to be moved to
            self.entry_list[i].update_dims((self.pos[0], self.pos[1] + (i + offset - num_invisible_entries) * self.spacing), self.width, self.entry_height, index=i, interpolation=interpolation, delta=delta)

        # If an entry is being moved, make it's y value follow the mouse
        if self.moving_entry:
            self.moving_entry.update_dims((self.pos[0], mouse_pos[1] - self.entry_height/2), self.width, self.entry_height)

        # add entry button at the end, after all entries
        add_button_y = self.pos[1] + self.spacing * (len(self.entry_list) + is_moving - num_invisible_entries)
        diff = add_button_y - self.add_button.pos[1]
        if interpolation and abs(diff) > 0.1:
            ratio = min(30*delta, 0.5)
            add_button_y = add_button_y*ratio + self.add_button.pos[1]*(1-ratio)
        self.add_button.update_dims((self.pos[0], add_button_y), self.width, self.entry_height)

    def update(self, keys, mouseState, delta=0.0, events=[]):
        for i in range(len(self.entry_list)):
            if self.entry_list[i].deleted:
                self.delete_entry(i)
                break

        # Finding which entry is in focus
        self.curr_focused = -1
        i = 0
        num_visible_entries = 0
        for entry in self.entry_list:
            # only render an entry if nothing is being searched, or the search matches the entry.
            entry.visible = (self.filter_text == "") or (self.filter_text.lower() in entry.key_inp.text.lower())
            num_visible_entries += entry.visible

            entry.update(keys, mouseState, delta, events)
            if entry.key_inp.is_focused:
                self.curr_focused = i
            elif entry.val_inp.is_focused:
                self.curr_focused = i + 1
            i += 2

        self.num_visible_entries = num_visible_entries

        self.add_button.update(mouseState)

        while len(self.navigate_queue):
            dir = self.navigate_queue.pop()
            self.navigate(dir)

        # If sum of heights of all the parts of the main page is greater than the screen height
        if (self.num_visible_entries + 2) * self.spacing > SCREEN_HEIGHT:
            # Scrolling up limit (y_val increased)
            if self.y_val > self.default_y_offset:
                self.y_val = self.default_y_offset
            # Scrolling down limit (y_val decreased)
            if self.y_val < -(len(self.entry_list) - 2) * self.spacing:
                self.y_val = -(len(self.entry_list) - 2) * self.spacing
        else:
            self.y_val = self.default_y_offset

        # Scroll animation
        if abs(self.pos[1] - self.y_val) > 0.01:
            self.pos[1] += 10 * (self.y_val - self.pos[1]) * delta
            self.update_dims(self.pos, self.width)
        else:
            self.update_dims(self.pos, self.width, interpolation=True, delta=delta)

        mouse_pos = mouseState[0]

        # If the move button of an entry was clicked
        if self.start_move:
            self.start_move = False
            move_index = int((mouse_pos[1] - self.pos[1])/self.spacing)
            self.moving_index = move_index
            self.moving_entry = self.entry_list.pop(move_index)
            self.update_dims(self.pos, self.width)

        # If an entry is being moved, and the mouse button was released
        if self.moving_entry and not mouseState[1]:
            move_index = int((mouse_pos[1] - self.pos[1])/self.spacing)
            move_index = min(move_index, len(self.entry_list))
            move_index = max(move_index, 0)
            self.moving_index = -1
            self.entry_list.insert(move_index, self.moving_entry)
            self.moving_entry = None
            self.update_dims(self.pos, self.width)

        # While a moving entry is being dragged
        if self.moving_entry:
            move_index = int((mouse_pos[1] - self.pos[1])/self.spacing)
            move_index = min(move_index, len(self.entry_list))
            move_index = max(move_index, 0)
            self.moving_index = move_index
            self.update_dims(self.pos, self.width, mouse_pos, interpolation=True, delta=delta)

    def navigate_enqueue(self, dir):
        self.navigate_queue.append(dir)

    def navigate(self, dir):
        # Meaning of dir values:
        #-1: Do nothing but scroll to the currently focused element
        # 0: Navigate up
        # 1: Navigate left (If value in focus, go to its key, but if key in focus, go to value of previous)
        # 2: Navigate down
        # 3: Navigate right (If key in focus, go to its value, but if value in focus, go to next key)
        # 4: Go down by 6 entries
        # 5: Go up by 6 entries
        # 6: Go to last entry's key
        # 7: Navigate to search bar
        if self.curr_focused == -1:
            if len(self.entry_list):
                self.curr_focused = 0
                if dir == 6:
                    if self.unfocus_on_searchbar:
                        self.unfocus_on_searchbar()
                elif dir == 7:
                    # self.y_val = self.default_y_offset
                    if self.focus_on_searchbar:
                        self.focus_on_searchbar()
                    # return
                else:
                    self.entry_list[0].key_inp.is_focused = True
                    if self.unfocus_on_searchbar:
                        self.unfocus_on_searchbar()
                    return
            else:
                return
        focused_ind = self.curr_focused // 2
        is_key = not self.curr_focused % 2
        if dir == 0:
            if not focused_ind:
                return
            if is_key:
                self.entry_list[focused_ind].key_inp.is_focused = False
                self.entry_list[focused_ind - 1].key_inp.is_focused = True
            else:
                self.entry_list[focused_ind].val_inp.is_focused = False
                self.entry_list[focused_ind - 1].val_inp.is_focused = True
            focused_ind -= 1
        elif dir == 2:
            if focused_ind == len(self.entry_list) - 1:
                return
            if is_key:
                self.entry_list[focused_ind].key_inp.is_focused = False
                self.entry_list[focused_ind + 1].key_inp.is_focused = True
            else:
                self.entry_list[focused_ind].val_inp.is_focused = False
                self.entry_list[focused_ind + 1].val_inp.is_focused = True
            focused_ind += 1
        elif dir == 1:
            if focused_ind == 0 and is_key:
                return
            if is_key:
                self.entry_list[focused_ind].key_inp.is_focused = False
                self.entry_list[focused_ind - 1].val_inp.is_focused = True
                focused_ind -= 1
            else:
                self.entry_list[focused_ind].val_inp.is_focused = False
                self.entry_list[focused_ind].key_inp.is_focused = True
        elif dir == 3:
            if focused_ind == len(self.entry_list) - 1 and not is_key:
                return
            if is_key:
                self.entry_list[focused_ind].key_inp.is_focused = False
                self.entry_list[focused_ind].val_inp.is_focused = True
            else:
                self.entry_list[focused_ind].val_inp.is_focused = False
                self.entry_list[focused_ind + 1].key_inp.is_focused = True
                focused_ind += 1
        elif dir == 4:
            if not len(self.entry_list):
                return
            new_ind = min(len(self.entry_list) - 1, focused_ind + 6)
            if is_key:
                self.entry_list[focused_ind].key_inp.is_focused = False
                self.entry_list[new_ind].key_inp.is_focused = True
            else:
                self.entry_list[focused_ind].val_inp.is_focused = False
                self.entry_list[new_ind].val_inp.is_focused = True
            focused_ind = new_ind
        elif dir == 5:
            if not len(self.entry_list):
                return
            new_ind = max(0, focused_ind - 6)
            if is_key:
                self.entry_list[focused_ind].key_inp.is_focused = False
                self.entry_list[new_ind].key_inp.is_focused = True
            else:
                self.entry_list[focused_ind].val_inp.is_focused = False
                self.entry_list[new_ind].val_inp.is_focused = True
            focused_ind = new_ind
        elif dir == 6:
            if not len(self.entry_list):
                return
            new_ind = len(self.entry_list) - 1
            if is_key:
                self.entry_list[focused_ind].key_inp.is_focused = False
                self.entry_list[new_ind].key_inp.is_focused = True
            else:
                self.entry_list[focused_ind].val_inp.is_focused = False
                self.entry_list[new_ind].key_inp.is_focused = True
            focused_ind = new_ind
        elif dir == 7:
            self.entry_list[focused_ind].key_inp.is_focused = False
            self.entry_list[focused_ind].val_inp.is_focused = False
            self.y_val = self.default_y_offset
            if self.focus_on_searchbar:
                self.focus_on_searchbar()

        # If navigating to last index, scroll down so you can see it. Useful when a new entry is added.
        if focused_ind == len(self.entry_list) - 1:
            self.y_val = min(SCREEN_HEIGHT - self.spacing - (focused_ind + 1) * self.spacing, self.default_y_offset)
            self.update_dims(self.pos, self.width)
        # If focused index goes off screen below, scroll down to see it
        if self.y_val + (focused_ind + 1) * self.spacing > SCREEN_HEIGHT:
            self.y_val -= self.y_val + (focused_ind + 1) * self.spacing - SCREEN_HEIGHT
            self.update_dims(self.pos, self.width)
        # If focuesd index goes off screen above, scroll up to see it
        if self.y_val + focused_ind * self.spacing < self.default_y_offset:
            self.y_val = self.default_y_offset - focused_ind * self.spacing
            self.update_dims(self.pos, self.width)

    def add_entry(self, entry=("", ""), pos=None):
        new_entry = Entry((0, 0), 0, 0, key=entry[0], val=entry[1], on_navigation=self.navigate_enqueue, on_move_clicked=self.start_move_entry)
        if not pos:
            self.entry_list.append(new_entry)
        else:
            self.entry_list.insert(pos, new_entry)
        self.update_dims(self.pos, self.width)

    def start_move_entry(self):
        if self.num_visible_entries == len(self.entry_list):
            self.start_move = True

    def delete_entry(self, i):
        self.entry_list.pop(i)
        self.update_dims(self.pos, self.width)

    def get_text(self):
        text = ""
        for entry in self.entry_list:
            key = entry.key_inp.text
            val = entry.val_inp.text
            # Discard empty entries
            if key or val:
                text += key + '\n'
                text += val + '\n'
        return text


class MainPage:

    def __init__(self, pos, width, height, entries=[]):
        self.pos = pos
        self.width = width
        self.height = height
        self.entry_list_default_y_offset = self.pos[1] + 70 # The default, and maximum y value of the entry list
        self.entry_list = EntryList((self.pos[0] + 10, self.entry_list_default_y_offset), self.width - 20, entries, default_y_offset=self.entry_list_default_y_offset, focus_on_searchbar=self.focus_on_searchbar, unfocus_on_searchbar=self.unfocus_on_searchbar)
        self.searchbar = TextInput((0, 0), 0, 0, alt_text="search", onInput=self.entry_list.set_filter_text, only_edit_mode=True, clear_on_escape=True, has_copy_button=False)
        self.searchbar.update_dims((self.pos[0] + 10, self.pos[1] + 10), self.width - 20, 50)

    def draw(self, screen):
        self.entry_list.draw(screen)
        self.searchbar.draw(screen)

    def update(self, keys, mouseState, delta=0.0, events=[]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                # If undo shortcut pressed and there is an entry in deleted_entries
                if keys[pygame.K_LCTRL] and event.key == pygame.K_z and len(deleted_entries):
                    entry = deleted_entries.pop()
                    self.entry_list.add_entry(entry=entry)
                # If change password shortcut pressed
                if keys[pygame.K_LCTRL] and event.key == pygame.K_p:
                    goto_change_pwd_page()
                # If settings shortcut pressed
                if keys[pygame.K_LCTRL] and event.key == pygame.K_o:
                    goto_settings_page()
                # If add entry shortcut is pressed
                if keys[pygame.K_LCTRL] and event.key == pygame.K_a:
                    self.entry_list.add_entry()
                    self.entry_list.navigate_enqueue(6) # Navigate to the last entry (new one)
                # If no entry in focus and there is at least one entry, pressing tab will go to the first entry
                if self.entry_list.curr_focused == -1 and event.key == pygame.K_TAB and len(self.entry_list.entry_list):
                    self.entry_list.navigate_enqueue(0)
            if event.type == pygame.MOUSEWHEEL:
                self.entry_list.y_val += event.y * 10000 * delta

        self.searchbar.update(keys, mouseState, delta, events)
        self.entry_list.update(keys, mouseState, delta, events)

        # This is being done after the searchbar update.
        # If done before, search bar will be in focus when updated and a '/' will be typed into it.
        # There's probably a better way to do this but I don't care, this works
        for event in events:
            if event.type == pygame.KEYDOWN:
                if keys[pygame.K_LCTRL] and event.key == pygame.K_SLASH:
                    self.entry_list.navigate_enqueue(7)
                    self.entry_list.y_val = self.entry_list_default_y_offset

    def focus_on_searchbar(self):
        self.searchbar.is_focused = True

    def unfocus_on_searchbar(self):
        self.searchbar.is_focused = False


class PasswordPage:

    def __init__(self, pos, width, height):
        self.pos = pos
        self.width = width
        self.height = height
        self.input_width = 600
        self.input_height = 50
        self.entered_wrong_pwd = False
        self.wrong_pwd_message = font.render("wrong password", False, SLIGHTLY_DISABLED_TEXT_COLOR)
        self.input = TextInput((0, 0),
                               0,
                               0,
                               alt_text="enter pwd",
                               onEnter=self.on_password_entered,
                               only_edit_mode=True,
                               text_hidden_level=TextHideLevel.FULLY_HIDDEN,
                               has_copy_button=False)
        self.input.is_focused = True
        self.input.update_dims((self.pos[0] + self.width / 2 - self.input_width / 2, self.pos[1] + self.height / 2 - self.input_height / 2),
                               self.input_width,
                               self.input_height)

    def on_password_entered(self):
        if decrypt_and_goto_main_page():
            self.input.text = ""
            self.entered_wrong_pwd = True

    def draw(self, screen):
        self.input.draw(screen)
        if self.entered_wrong_pwd:
            screen.blit(self.wrong_pwd_message,
                        (self.pos[0] + self.width / 2 - self.wrong_pwd_message.get_width() / 2, self.pos[1] + self.height / 3 - self.wrong_pwd_message.get_height() / 2))

    def update(self, keys, mouseState, delta=0.0, events=[]):
        self.input.update(keys, mouseState, delta, events)

SECONDS_FOR_ONE_BRUTEFORCE_NUMERATOR = 52
SECONDS_FOR_ONE_BRUTEFORCE_DENOMINATOR = 1000000000

class ChangePasswordPage:

    def __init__(self, pos, width, height):
        self.pos = pos
        self.width = width
        self.height = height
        self.input_width = 600
        self.input_height = 50
        self.pwd_mismatched = False
        self.pwd_not_match_msg = font.render("passwords don't match", False, SLIGHTLY_DISABLED_TEXT_COLOR)
        self.input1 = TextInput((0, 0), 0, 0,
                                alt_text="enter pwd",
                                onEnter=focus_input_2,
                                text_hidden_level=TextHideLevel.FULLY_HIDDEN,
                                only_edit_mode=True,
                                has_copy_button=False)
        self.input2 = TextInput((0, 0), 0, 0,
                                alt_text="re-enter pwd",
                                text_hidden_level=TextHideLevel.FULLY_HIDDEN,
                                only_edit_mode=True,
                                has_copy_button=False)
        self.input1.is_focused = True # Set first input to be in focus by default
        self.change_button = Button((self.pos[0] + self.width / 2 - 200, self.pos[1] + 3 * self.height / 4 - 25), 400, 50, text="Change password", onClick=self.on_change_password)
        self.cancel_button = Button((self.pos[0] + self.width / 2 - 200, self.pos[1] + 3 * self.height / 4 + 50), 400, 50, text="Cancel", onClick=self.on_cancel)

        self.bruteforce_time_message = font.render("Time to bruteforce:", False, SLIGHTLY_DISABLED_TEXT_COLOR)
        self.bruteforce_time = "0 seconds"
        self.bruteforce_time_greenness = 0

        self.input1.update_dims((self.pos[0] + self.width / 2 - self.input_width / 2, self.pos[1] + self.height / 2 - 1.5 * self.input_height),
                                self.input_width,
                                self.input_height)
        self.input2.update_dims((self.pos[0] + self.width / 2 - self.input_width / 2, self.pos[1] + self.height / 2 + 0.5 * self.input_height),
                                self.input_width,
                                self.input_height)

    def reset(self):
        self.input1.text = ""
        self.input2.text = ""
        self.input1.is_focused = True
        self.input2.is_focused = False
        self.pwd_mismatched = False

    def on_change_password(self):
        if self.input1.text!= self.input2.text:
            self.reset()
            self.pwd_mismatched = True
            return
        if self.input1.text == "":
            return
        change_password(self.input1.text)
        self.reset()
        goto_main_page()

    def on_cancel(self):
        self.reset()
        goto_main_page()

    def draw(self, screen):
        self.input1.draw(screen)
        self.input2.draw(screen)
        self.change_button.draw(screen)
        self.cancel_button.draw(screen)
        if self.pwd_mismatched:
            screen.blit(self.pwd_not_match_msg,
                        (self.pos[0] + self.width / 2 - self.pwd_not_match_msg.get_width() / 2, self.pos[1] + self.height / 2 - self.pwd_not_match_msg.get_height() / 2))
        screen.blit(self.bruteforce_time_message,
                    (self.pos[0] + self.width / 2 - self.bruteforce_time_message.get_width() / 2, self.pos[1] + self.height / 4 - self.bruteforce_time_message.get_height() / 2 - 30))
        calculated_bruteforce_time_message = font.render(self.bruteforce_time, False, (255 - self.bruteforce_time_greenness, self.bruteforce_time_greenness, 0))
        screen.blit(calculated_bruteforce_time_message,
                    (self.pos[0] + self.width / 2 - calculated_bruteforce_time_message.get_width() / 2, self.pos[1] + self.height / 4 - calculated_bruteforce_time_message.get_height() / 2 + 30))

    def update(self, keys, mouseState, delta=0.0, events=[]):
        self.input1.update(keys, mouseState, delta, events)
        self.input2.update(keys, mouseState, delta, events)
        self.change_button.update(mouseState)
        self.cancel_button.update(mouseState)

        pwd_text = self.input1.text
        contains_number = False
        contains_lowercase_alpha = False
        contains_uppercase_alpha = False
        contains_special_char = False
        for letter in pwd_text:
            if letter.isnumeric():
                contains_number = True
            elif letter.isalpha():
                if letter.islower():
                    contains_lowercase_alpha = True
                else:
                    contains_uppercase_alpha = True
            else:
                contains_special_char = True
        multiplier_base = 0
        if contains_number:
            multiplier_base += 10
        if contains_lowercase_alpha:
            multiplier_base += 26
        if contains_uppercase_alpha:
            multiplier_base += 26
        if contains_special_char:
            multiplier_base += 32
        total_seconds_to_bruteforce = multiplier_base**len(pwd_text)
        total_seconds_to_bruteforce *= SECONDS_FOR_ONE_BRUTEFORCE_NUMERATOR
        total_seconds_to_bruteforce //= SECONDS_FOR_ONE_BRUTEFORCE_DENOMINATOR
        total_seconds_to_bruteforce //= 10

        self.bruteforce_time = "0 seconds"

        self.bruteforce_time_greenness = int(math.log2(total_seconds_to_bruteforce + 1)*6.7) # +1 to avoid log(0)
        self.bruteforce_time_greenness = min(self.bruteforce_time_greenness, 255)
        self.bruteforce_time_greenness = max(self.bruteforce_time_greenness, 0)

        # seconds
        if total_seconds_to_bruteforce < 60:
            self.bruteforce_time = str(total_seconds_to_bruteforce) + " second"
        else:
            # minutes
            total_seconds_to_bruteforce //= 60
            if total_seconds_to_bruteforce < 60:
                self.bruteforce_time = str(total_seconds_to_bruteforce) + " minute"
            else:
                # hours
                total_seconds_to_bruteforce //= 60
                if total_seconds_to_bruteforce < 24:
                    self.bruteforce_time = str(total_seconds_to_bruteforce) + " hour"
                else:
                    # days
                    total_seconds_to_bruteforce //= 24
                    if total_seconds_to_bruteforce < 30:
                        self.bruteforce_time = str(total_seconds_to_bruteforce) + " day"
                    else:
                        # months
                        total_seconds_to_bruteforce //= 30
                        if total_seconds_to_bruteforce < 12:
                            self.bruteforce_time = str(total_seconds_to_bruteforce) + " month"
                        else:
                            # years
                            total_seconds_to_bruteforce //= 12 # Now I know this assumes a year has 360 days, but this is just an order of magnitude approximation so I don't care
                            self.bruteforce_time = str(total_seconds_to_bruteforce) + " year"
        if total_seconds_to_bruteforce > 1 or total_seconds_to_bruteforce < 1:
            self.bruteforce_time += "s"


def toggle_only_edit_mode():
    global ONLY_EDIT_MODE
    ONLY_EDIT_MODE = not ONLY_EDIT_MODE

def save_and_exit_settings():
    save_settings()
    goto_main_page()


class SettingsPage:
    def __init__(self, pos, width, height):
        self.pos = pos
        self.width = width
        self.height = height
        self.only_edit_mode_state = ONLY_EDIT_MODE
        self.only_edit_mode_toggle_button = Button([self.pos[0] + self.width/2 - 200, self.pos[1] + 100], 400, 50, "Only Edit Mode: " + str(self.only_edit_mode_state), toggle_only_edit_mode)
        self.save_button = Button([self.pos[0] + self.width - 104, self.pos[1] + 4], 100, 50, "Save", save_and_exit_settings)
        self.cancel_button = Button([self.pos[0] + 4, self.pos[1] + 4], 100, 50, "Cancel", goto_main_page)

    def draw(self, screen):
        self.only_edit_mode_toggle_button.draw(screen)
        self.save_button.draw(screen)
        self.cancel_button.draw(screen)

    def update(self, keys, mouseState, delta=0.0, events=[]):
        self.only_edit_mode_toggle_button.update(mouseState)
        self.save_button.update(mouseState)
        self.cancel_button.update(mouseState)
        if self.only_edit_mode_state != ONLY_EDIT_MODE:
            self.only_edit_mode_state = ONLY_EDIT_MODE
            self.only_edit_mode_toggle_button.text = "Only Edit Mode: " + str(self.only_edit_mode_state)


running = True

backing_up_to_drive_text = font.render("Backing up to drive..", False, DEFAULT_TEXT_COLOR)
def save_and_exit():
    global running
    running = False
    screen.blit(backing_up_to_drive_text,
                (SCREEN_WIDTH / 2 - backing_up_to_drive_text.get_width() / 2, SCREEN_HEIGHT / 2 - backing_up_to_drive_text.get_height() / 2))
    pygame.display.update()
    save_data()
    pyperclip.copy("")


class TopBar:
    def __init__(self, pos, width, height):
        self.pos = pos
        self.width = width
        self.height = height
        N = 4
        i1 = 0
        i2 = 1
        i3 = 2
        i4 = 3
        self.goto_main_page_button = Button((i1*SCREEN_WIDTH//N, 0), SCREEN_WIDTH//N, 60, "Passwords", goto_main_page, TEXTINPUT_DEFAULT_BACKGROUND_COLOR)
        self.goto_settings_page_button = Button((i2*SCREEN_WIDTH//N, 0), SCREEN_WIDTH//N, 60, "Settings", goto_settings_page, TEXTINPUT_DEFAULT_BACKGROUND_COLOR)
        self.goto_change_password_page_button = Button((i3*SCREEN_WIDTH//N, 0), SCREEN_WIDTH//N, 60, "Change Pwd", goto_change_pwd_page, TEXTINPUT_DEFAULT_BACKGROUND_COLOR)
        self.exit_button = Button((i4*SCREEN_WIDTH//N, 0), SCREEN_WIDTH//N, 60, "Save and Exit", save_and_exit, TEXTINPUT_DEFAULT_BACKGROUND_COLOR)

    def draw(self, screen):
        self.goto_main_page_button.draw(screen)
        self.goto_settings_page_button.draw(screen)
        self.goto_change_password_page_button.draw(screen)
        self.exit_button.draw(screen)

    def update(self, keys, mouseState, delta=0.0, events=[]):
        self.goto_main_page_button.background_color = TEXTINPUT_DEFAULT_BACKGROUND_COLOR
        self.goto_settings_page_button.background_color = TEXTINPUT_DEFAULT_BACKGROUND_COLOR
        self.goto_change_password_page_button.background_color = TEXTINPUT_DEFAULT_BACKGROUND_COLOR
        self.goto_main_page_button.hover_color = BUTTON_HOVER_BACKGROUND_COLOR
        self.goto_settings_page_button.hover_color = BUTTON_HOVER_BACKGROUND_COLOR
        self.goto_change_password_page_button.hover_color = BUTTON_HOVER_BACKGROUND_COLOR
        self.goto_main_page_button.focus_color = BUTTON_FOCUS_BACKGROUND_COLOR
        self.goto_settings_page_button.focus_color = BUTTON_FOCUS_BACKGROUND_COLOR
        self.goto_change_password_page_button.focus_color = BUTTON_FOCUS_BACKGROUND_COLOR
        if current_page == "main":
            self.goto_main_page_button.background_color = BACKGROUND_COLOR
            self.goto_main_page_button.hover_color = BACKGROUND_COLOR
            self.goto_main_page_button.focus_color = BACKGROUND_COLOR
        elif current_page == "settings":
            self.goto_settings_page_button.background_color = BACKGROUND_COLOR
            self.goto_settings_page_button.hover_color = BACKGROUND_COLOR
            self.goto_settings_page_button.focus_color = BACKGROUND_COLOR
        elif current_page == "change_pwd":
            self.goto_change_password_page_button.background_color = BACKGROUND_COLOR
            self.goto_change_password_page_button.hover_color = BACKGROUND_COLOR
            self.goto_change_password_page_button.focus_color = BACKGROUND_COLOR

        self.goto_main_page_button.update(mouseState)
        self.goto_settings_page_button.update(mouseState)
        self.goto_change_password_page_button.update(mouseState)
        self.exit_button.update(mouseState)


main_page = MainPage([0, 60], SCREEN_WIDTH, SCREEN_HEIGHT - 60)
pwd_page = PasswordPage([0, 0], SCREEN_WIDTH, SCREEN_HEIGHT)
change_pwd_page = ChangePasswordPage([0, 60], SCREEN_WIDTH, SCREEN_HEIGHT - 60)
settings_page = SettingsPage([0, 60], SCREEN_WIDTH, SCREEN_HEIGHT - 60)
top_bar = TopBar([0, 0], 0, 0)

prev_time = time.time_ns()
while running:
    events = pygame.event.get()
    early_break = False
    for event in events:
        if event.type == pygame.QUIT:
            save_and_exit()
            early_break = True
    if early_break:
        break

    # Inputs
    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()[0]
    mouseState = (mouse_pos, mouse_pressed)

    curr_time = time.time_ns()
    delta = (curr_time - prev_time) / 1e9
    prev_time = curr_time

    if current_page != "pwd":
        top_bar.update(keys, mouseState, delta, events)

    # Password page
    if current_page == "pwd":
        pwd_page.update(keys, mouseState, delta, events)
        pwd_page.draw(screen)
    # Main page
    elif current_page == "main":
        main_page.update(keys, mouseState, delta, events)
        main_page.draw(screen)
    # Change password page
    elif current_page == "change_pwd":
        change_pwd_page.update(keys, mouseState, delta, events)
        change_pwd_page.draw(screen)
    # Settings page
    elif current_page == "settings":
        settings_page.update(keys, mouseState, delta, events)
        settings_page.draw(screen)

    if current_page != "pwd":
        top_bar.draw(screen)

    pygame.display.update()
    screen.fill(BACKGROUND_COLOR)
    time.sleep(1 / 256)
