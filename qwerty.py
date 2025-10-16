#!/bin/python3
import pyperclip
import pygame
import time
from crypto_ops import *
from qwerty_oauth import *
from enum import Enum

create_qwertyfile_if_not_exists()

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

deleted_entries = []


def collide_rect(rect, pos):
    return pos[0] > rect[0] and pos[0] < rect[0] + rect[2] and pos[1] > rect[1] and pos[1] < rect[1] + rect[3]


current_page = "pwd"
actual_pwd = ""


# Returns non-zero number on error (wrong password)
def decrypt_and_goto_main_page() -> int:
    global current_page, pwd_page, main_page, actual_pwd
    pwd = pwd_page.input.text
    entries = try_decrypt(pwd)
    if not entries:
        return 1
    actual_pwd = pwd
    main_page.__init__(entries)
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
                 alt_text="",
                 onEnter=None,
                 onInput=None,
                 text_hidden_level=TextHideLevel.FULLY_VISIBLE,
                 on_navigation=None,
                 only_edit_mode=False,
                 clear_on_escape=False):
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
        self.default_text = font.render("<lotta text>", False, (200, 200, 200))
        self.alt_text = alt_text
        self.alt_text_rendered = font.render(alt_text, False, (120, 120, 120))
        self.onEnter = onEnter
        self.onInput = onInput
        self.color = (20, 20, 20)
        self.is_cursor_visible = True
        self.cursor_blink_timer = 0
        self.cursor_blink_time = 0.3

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.pos[0], self.pos[1], self.width, self.height))
        if (
                self.text_hidden_level == TextHideLevel.FULLY_HIDDEN
                or (self.text_hidden_level == TextHideLevel.HIDDEN_UNLESS_FOCUSED and not self.is_focused)
                or (self.text_hidden_level == TextHideLevel.HIDDEN_UNLESS_EDITING and not self.editing)
                ):
            text = font.render("*" * len(self.text), False, (255, 255, 255))
        else:
            text = font.render(self.text, False, (255, 255, 255))
        if text.get_width() <= self.width or self.editing:
            if self.text != "":
                screen.blit(text, (self.pos[0] + self.width / 2 - text.get_width() / 2, self.pos[1] + self.height / 2 - text.get_height() / 2))
            elif not self.editing or self.only_edit_mode:
                screen.blit(self.alt_text_rendered, (self.pos[0] + self.width / 2 - self.alt_text_rendered.get_width() / 2,
                                                     self.pos[1] + self.height / 2 - self.alt_text_rendered.get_height() / 2))
            if self.editing and self.is_cursor_visible and (not self.only_edit_mode or not self.text == ""):
                pygame.draw.rect(
                    screen, (255, 255, 255),
                    (self.pos[0] + self.width / 2 + text.get_width() / 2, self.pos[1] + self.height / 2 - text.get_height() / 2, 10, text.get_height()))
        else:
            screen.blit(self.default_text,
                        (self.pos[0] + self.width / 2 - self.default_text.get_width() / 2, self.pos[1] + self.height / 2 - self.default_text.get_height() / 2))

    def update_dims(self, pos, width, height):
        self.pos = pos
        self.width = width
        self.height = height

    def update(self, keys, mouseState, delta=0.0, events=[]):
        mouse_pos = mouseState[0]
        # mouse_pressed = mouseState[1]
        if self.is_focused and self.only_edit_mode:
            self.editing = True
        elif not self.is_focused:
            self.editing = False
        # i = -1 
        # to_pop = -1
        for event in events:
            # i += 1
            if event.type == pygame.KEYDOWN:
                if self.is_focused:
                    if self.editing:
                        if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE or (keys[pygame.K_LCTRL] and event.key == pygame.K_w):
                            if keys[pygame.K_LCTRL]:
                                while len(self.text) and self.text[-1] != " ":
                                    self.text = self.text[:-1]
                            if len(self.text):
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
                            self.on_navigation(-1)
                        if self.onInput:
                            self.onInput(self.text)
                    elif event.key == pygame.K_c and keys[pygame.K_LCTRL] and self.text != "":
                        pyperclip.copy(self.text)
                        if self.on_navigation:
                            self.on_navigation(-1)
                    elif event.key == pygame.K_v and keys[pygame.K_LCTRL]:
                        self.text = pyperclip.paste()
                        if self.on_navigation:
                            self.on_navigation(-1)
                    elif event.key == pygame.K_RETURN:
                        self.editing = True
                        if self.on_navigation:
                            self.on_navigation(-1)
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
                if collide_rect((self.pos[0], self.pos[1], self.width, self.height), event.pos):
                    if self.is_focused:
                        self.editing = True
                    else:
                        self.is_focused = True
                    if self.on_navigation:
                        self.on_navigation(-1)
                    event.pos = (1000000000, 1000000000)
                    # to_pop = i
                else:
                    self.is_focused = False
                    self.editing = False
        # Remove an event if it leads to a click
        # if to_pop != -1:
        #     events.pop(to_pop)

        if self.is_focused:
            self.color = (50, 50, 50)
        elif collide_rect((self.pos[0], self.pos[1], self.width, self.height), mouse_pos):
            self.color = (30, 30, 30)
        else:
            self.color = (20, 20, 20)

        self.cursor_blink_timer += delta
        if self.cursor_blink_timer > self.cursor_blink_time:
            self.cursor_blink_timer = 0
            self.is_cursor_visible = not self.is_cursor_visible


class Button:

    def __init__(self, pos, width, height, text="", onClick=None):
        self.pos = pos
        self.width = width
        self.height = height
        self.text = text
        self.onClick = onClick
        self.prev_mouse_state = True
        self.color = (100, 100, 100)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.pos[0], self.pos[1], self.width, self.height))
        if self.text != "":
            text = font.render(self.text, False, (255, 255, 255))
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
                self.color = (120, 120, 120)
            else:
                self.color = (100, 100, 100)
        else:
            self.color = (70, 70, 70)
        self.prev_mouse_state = mouse_pressed


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
        self.num_visible_entries = 0
        for entry in self.entry_list:
            # only render an entry if nothing is being searched, or the search matches the entry.
            entry.visible = (self.filter_text == "") or (self.filter_text.lower() in entry.key_inp.text.lower())
            self.num_visible_entries += entry.visible

            entry.update(keys, mouseState, delta, events)
            if entry.key_inp.is_focused:
                self.curr_focused = i
            elif entry.val_inp.is_focused:
                self.curr_focused = i + 1
            i += 2

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

    def __init__(self, entries=[]):
        self.entry_list_default_y_offset = 70 # The default, and maximum y value of the entry list
        self.entry_list = EntryList((10, self.entry_list_default_y_offset), SCREEN_WIDTH - 20, entries, default_y_offset=self.entry_list_default_y_offset, focus_on_searchbar=self.focus_on_searchbar, unfocus_on_searchbar=self.unfocus_on_searchbar)
        self.searchbar = TextInput((10, 10), SCREEN_WIDTH - 20, 50, alt_text="search", onInput=self.entry_list.set_filter_text, only_edit_mode=True, clear_on_escape=True)

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

    def __init__(self):
        self.input_width = 600
        self.input_height = 50
        self.entered_wrong_pwd = False
        self.wrong_pwd_message = font.render("wrong password", False, (200, 200, 200))
        self.input = TextInput((SCREEN_WIDTH / 2 - self.input_width / 2, SCREEN_HEIGHT / 2 - self.input_height / 2),
                               self.input_width,
                               self.input_height,
                               alt_text="enter pwd",
                               onEnter=self.on_password_entered,
                               only_edit_mode=True,
                               text_hidden_level=TextHideLevel.FULLY_HIDDEN)
        self.input.is_focused = True

    def on_password_entered(self):
        if decrypt_and_goto_main_page():
            self.input.text = ""
            self.entered_wrong_pwd = True

    def draw(self, screen):
        self.input.draw(screen)
        if self.entered_wrong_pwd:
            screen.blit(self.wrong_pwd_message,
                        (SCREEN_WIDTH / 2 - self.wrong_pwd_message.get_width() / 2, SCREEN_HEIGHT / 3 - self.wrong_pwd_message.get_height() / 2))

    def update(self, keys, mouseState, delta=0.0, events=[]):
        self.input.update(keys, mouseState, delta, events)


class ChangePasswordPage:

    def __init__(self):
        self.input_width = 600
        self.input_height = 50
        self.pwd_mismatched = False
        self.pwd_not_match_msg = font.render("passwords don't match", False, (200, 200, 200))
        self.input1 = TextInput((SCREEN_WIDTH / 2 - self.input_width / 2, SCREEN_HEIGHT / 2 - 1.5 * self.input_height),
                                self.input_width,
                                self.input_height,
                                alt_text="enter pwd",
                                onEnter=focus_input_2,
                                text_hidden_level=TextHideLevel.FULLY_HIDDEN)
        self.input2 = TextInput((SCREEN_WIDTH / 2 - self.input_width / 2, SCREEN_HEIGHT / 2 + 0.5 * self.input_height),
                                self.input_width,
                                self.input_height,
                                alt_text="re-enter pwd",
                                text_hidden_level=TextHideLevel.FULLY_HIDDEN)
        self.input1.is_focused = True # Set first input to be in focus by default
        self.change_button = Button((SCREEN_WIDTH / 2 - 200, 3 * SCREEN_HEIGHT / 4 - 25), 400, 50, text="Change password", onClick=self.on_change_password)
        self.cancel_button = Button((SCREEN_WIDTH / 2 - 200, 3 * SCREEN_HEIGHT / 4 + 50), 400, 50, text="Cancel", onClick=self.on_cancel)

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
                        (SCREEN_WIDTH / 2 - self.pwd_not_match_msg.get_width() / 2, SCREEN_HEIGHT / 4 - self.pwd_not_match_msg.get_height() / 2))

    def update(self, keys, mouseState, delta=0.0, events=[]):
        self.input1.update(keys, mouseState, delta, events)
        self.input2.update(keys, mouseState, delta, events)
        self.change_button.update(mouseState)
        self.cancel_button.update(mouseState)


main_page = MainPage()
pwd_page = PasswordPage()
change_pwd_page = ChangePasswordPage()

backing_up_to_drive_text = font.render("Backing up to drive..", False, (255, 255, 255))

running = True
prev_time = time.time_ns()
while running:
    events = pygame.event.get()
    early_break = False
    for event in events:
        if event.type == pygame.QUIT:
            running = False
            screen.blit(backing_up_to_drive_text,
                        (SCREEN_WIDTH / 2 - backing_up_to_drive_text.get_width() / 2, SCREEN_HEIGHT / 2 - backing_up_to_drive_text.get_height() / 2))
            pygame.display.update()
            save_data()
            pyperclip.copy("")
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

    pygame.display.update()
    screen.fill((0, 0, 0))
    time.sleep(1 / 256)
