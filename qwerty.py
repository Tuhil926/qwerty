#!/bin/python3
import pygame
import pyperclip
import time
from Crypto.Cipher import AES
import hashlib
import os

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
QWERTY_FILENAME = "qwerty.txt"
MAGIC = "qwertyuiopasdfghjklzxcvbnm"
deleted_entries = []


def collide_rect(rect, pos):
    return pos[0] > rect[0] and pos[0] < rect[0] + rect[2] and pos[1] > rect[1] and pos[1] < rect[1] + rect[3]


current_page = "pwd"


def encrypt(text: str, pwd: str):
    salt = os.urandom(AES.block_size)
    key = hashlib.sha256(salt + pwd.encode('utf-8')).digest()
    iv = os.urandom(AES.block_size)
    cipher = AES.new(key, AES.MODE_CFB, iv=iv)
    return salt + iv + cipher.encrypt(text.encode('utf-8'))


def decrypt(data: bytes, pwd: str):
    salt = data[:AES.block_size]
    key = hashlib.sha256(salt + pwd.encode('utf-8')).digest()
    iv = data[AES.block_size:2 * AES.block_size]
    ciphertext = data[2 * AES.block_size:]
    decrypt_cipher = AES.new(key, AES.MODE_CFB, iv=iv)
    return decrypt_cipher.decrypt(ciphertext).decode('utf-8')


actual_pwd = ""


def goto_main_page():
    global current_page, pwd_page, main_page, actual_pwd
    pwd = pwd_page.input.text
    enc_file = open(QWERTY_FILENAME, 'rb')
    data = enc_file.read()
    enc_file.close()
    try:
        decrypted = decrypt(data, pwd)
    except:
        pwd_page.input.text = ""
        pwd_page.entered_wrong_pwd = True
        return
    lines = decrypted.split('\n')
    if lines[0] != MAGIC:
        pwd_page.input.text = ""
        pwd_page.entered_wrong_pwd = True
        return
    actual_pwd = pwd
    entries = []
    for i in range(1, len(lines), 2):
        if i + 1 >= len(lines):
            break
        entries.append((lines[i], lines[i + 1]))
    main_page.entry_list = EntryList((10, main_page.entry_list_default_y_offset),
                                     SCREEN_WIDTH - 20,
                                     entries,
                                     default_y_offset=main_page.entry_list_default_y_offset,
                                     focus_on_searchbar=main_page.focus_on_searchbar,
                                     unfocus_on_searchbar=main_page.unfocus_on_searchbar)
    main_page.searchbar = TextInput((10, 10),
                                    SCREEN_WIDTH - 20,
                                    50,
                                    alt_text="search",
                                    onEnter=None,
                                    onInput=main_page.entry_list.set_filter_text,
                                    only_edit_mode=True,
                                    clear_on_escape=True)

    current_page = "main"


def focus_input_2():
    global change_pwd_page
    change_pwd_page.input1.is_focused = False
    change_pwd_page.input1.editing = False
    change_pwd_page.input2.is_focused = True


def change_password():
    global change_pwd_page, current_page, actual_pwd
    pwd1 = change_pwd_page.input1.text
    pwd2 = change_pwd_page.input2.text
    if pwd1 != pwd2:
        change_pwd_page.pwd_mismatched = True
        return
    if pwd1 == "":
        return
    actual_pwd = pwd1
    change_pwd_page.input1.text = ""
    change_pwd_page.input2.text = ""
    change_pwd_page.input1.is_focused = True
    change_pwd_page.input2.is_focused = False
    current_page = "main"


def goto_change_pwd_page():
    global current_page
    current_page = "change_pwd"


def goto_main_page_without_pwd():
    global current_page, change_pwd_page
    current_page = "main"
    change_pwd_page.input1.text = ""
    change_pwd_page.input2.text = ""
    change_pwd_page.input1.is_focused = True
    change_pwd_page.input2.is_focused = False


def save_data():
    global main_page, actual_pwd
    if actual_pwd == "":
        return
    text = MAGIC + '\n' + main_page.entry_list.get_text()
    enc_data = encrypt(text, actual_pwd)
    with open(QWERTY_FILENAME, 'wb') as qwerty_file:
        qwerty_file.write(enc_data)


def goto_pwd():
    global current_page
    current_page = "pwd"


try:
    file = open(QWERTY_FILENAME, "r")
    file.close()
except FileNotFoundError:
    qwertfile = open(QWERTY_FILENAME, "wb")
    init_data = MAGIC + '\n' + 'it\n' + 'works\n'
    pwd = "qwerty"
    qwertfile.write(encrypt(init_data, pwd))
    qwertfile.close()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("qwerty")
pygame.display.set_icon(pygame.image.load("qwerty.png"))

font = pygame.font.Font("PixelOperator8.ttf", 16)


class TextInput:

    def __init__(self,
                 pos,
                 width,
                 height,
                 text="",
                 alt_text="",
                 onEnter=None,
                 onInput=None,
                 hidden=False,
                 hidden_unless_focused=False,
                 on_navigation=None,
                 only_edit_mode=False,
                 clear_on_escape=False):
        self.text = text
        self.pos = pos
        self.width = width
        self.height = height
        self.is_focused = False
        self.editing = False
        self.hidden = hidden
        self.hidden_unless_focused = hidden_unless_focused
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
        if self.hidden or (self.hidden_unless_focused and not self.is_focused):
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
        for event in events:
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
                else:
                    self.is_focused = False
                    self.editing = False

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

    def __init__(self, pos, width, height, key="", val="", on_navigation=None):
        self.pos = pos
        self.width = width
        self.height = height
        self.deleted = False
        self.on_navigation = on_navigation
        kv_width = self.width - self.height
        self.key_inp = TextInput(self.pos, kv_width / 2 - 3, self.height, text=key, alt_text="key", on_navigation=self.on_navigation)
        self.val_inp = TextInput((self.pos[0] + kv_width / 2 + 3, self.pos[1]),
                                 kv_width / 2 - 3,
                                 self.height,
                                 text=val,
                                 alt_text="value",
                                 hidden_unless_focused=True,
                                 on_navigation=self.on_navigation)
        self.del_button = Button((self.pos[0] + kv_width + 6, self.pos[1]), self.height - 6, self.height, onClick=self.delete_self, text="X")

    def draw(self, screen):
        self.key_inp.draw(screen)
        self.val_inp.draw(screen)
        self.del_button.draw(screen)

    def update_dims(self, pos, width, height, index=0):
        self.pos = pos
        self.width = width
        self.height = height
        self.index = index
        kv_width = self.width - self.height
        self.key_inp.update_dims(self.pos, kv_width / 2 - 3, self.height)
        self.val_inp.update_dims((self.pos[0] + kv_width / 2 + 3, self.pos[1]), kv_width / 2 - 3, self.height)
        self.del_button.update_dims((self.pos[0] + kv_width + 6, self.pos[1]), self.height - 6, self.height)

    def delete_self(self):
        self.deleted = True
        deleted_entries.append((self.key_inp.text, self.val_inp.text))

    def update(self, keys, mouseState, delta=0.0, events=[]):
        self.key_inp.update(keys, mouseState, delta=delta, events=events)
        self.val_inp.update(keys, mouseState, delta=delta, events=events)
        self.del_button.update(mouseState)


class EntryList:

    def __init__(self, pos, width, entries=[], default_y_offset=10, focus_on_searchbar=None, unfocus_on_searchbar=None):
        self.pos = [pos[0], pos[1]]
        self.y_val = pos[1]
        self.default_y_offset = default_y_offset
        self.width = width
        self.entry_height = 50
        self.spacing = 60
        self.curr_focused = -1
        self.filter_text = ""
        self.focus_on_searchbar = focus_on_searchbar
        self.unfocus_on_searchbar = unfocus_on_searchbar
        self.entry_list = [
            Entry((self.pos[0], self.pos[1] + i * self.spacing), self.width, 50, key=entries[i][0], val=entries[i][1], on_navigation=self.navigate_enqueue)
            for i in range(len(entries))
        ]
        self.add_button = Button((self.pos[0], self.pos[1] + self.spacing * len(self.entry_list)), self.width, 50, "+", onClick=self.add_entry)
        self.navigate_queue = [
            0,
        ]

    def set_filter_text(self, text):
        self.filter_text = text

    def draw(self, screen):
        for entry in self.entry_list:
            if (self.filter_text == "") or (self.filter_text in entry.key_inp.text):
                entry.draw(screen)
        self.add_button.draw(screen)

    def update_dims(self, pos, width):
        self.pos = pos
        self.width = width
        for i in range(len(self.entry_list)):
            self.entry_list[i].update_dims((self.pos[0], self.pos[1] + i * self.spacing), self.width, self.entry_height, index=i)
        self.add_button.update_dims((self.pos[0], self.pos[1] + self.spacing * len(self.entry_list)), self.width, self.entry_height)

    def update(self, keys, mouseState, delta=0.0, events=[]):
        for i in range(len(self.entry_list)):
            if self.entry_list[i].deleted:
                self.delete_entry(i)
                break
        self.curr_focused = -1
        i = 0
        for entry in self.entry_list:
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
        if abs(self.pos[1] - self.y_val) > 0.01:
            self.pos[1] += 10 * (self.y_val - self.pos[1]) * delta
            self.update_dims(self.pos, self.width)

    def navigate_enqueue(self, dir):
        self.navigate_queue.append(dir)

    def navigate(self, dir):
        if self.curr_focused == -1:
            if len(self.entry_list):
                if dir == 6:
                    self.entry_list[-1].key_inp.is_focused = True
                    if self.unfocus_on_searchbar:
                        self.unfocus_on_searchbar()
                elif dir == 7:
                    if self.focus_on_searchbar:
                        self.focus_on_searchbar()
                else:
                    self.entry_list[0].key_inp.is_focused = True
                    if self.unfocus_on_searchbar:
                        self.unfocus_on_searchbar()
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
            if self.focus_on_searchbar:
                self.focus_on_searchbar()

        if focused_ind == len(self.entry_list) - 1:
            self.y_val = min(SCREEN_HEIGHT - self.spacing - (focused_ind + 1) * self.spacing, self.default_y_offset)
            self.update_dims(self.pos, self.width)
        if self.y_val + (focused_ind + 1) * self.spacing > SCREEN_HEIGHT:
            self.y_val -= self.y_val + (focused_ind + 1) * self.spacing - SCREEN_HEIGHT
            self.update_dims(self.pos, self.width)
        if self.y_val + focused_ind * self.spacing < self.default_y_offset:
            self.y_val = self.default_y_offset - focused_ind * self.spacing
            self.update_dims(self.pos, self.width)

    def add_entry(self, entry=("", "")):
        self.entry_list.append(Entry((0, 0), 0, 0, key=entry[0], val=entry[1], on_navigation=self.navigate_enqueue))
        self.update_dims(self.pos, self.width)

    def delete_entry(self, i):
        self.entry_list.pop(i)
        self.update_dims(self.pos, self.width)

    def get_text(self):
        text = ""
        for entry in self.entry_list:
            key = entry.key_inp.text
            val = entry.val_inp.text
            if key or val:
                text += key + '\n'
                text += val + '\n'
        return text


class MainPage:

    def __init__(self, entries=[]):
        self.entry_list_default_y_offset = 70
        self.entry_list = EntryList((10, self.entry_list_default_y_offset), SCREEN_WIDTH - 20, entries, default_y_offset=self.entry_list_default_y_offset)
        self.searchbar = TextInput((0, 0), 0, 0)

    def draw(self, screen):
        self.entry_list.draw(screen)
        self.searchbar.draw(screen)

    def update(self, keys, mouseState, delta=0.0, events=[]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if keys[pygame.K_LCTRL] and event.key == pygame.K_z and len(deleted_entries):
                    entry = deleted_entries.pop()
                    self.entry_list.add_entry(entry=entry)
                if keys[pygame.K_LCTRL] and event.key == pygame.K_p:
                    goto_change_pwd_page()
                if keys[pygame.K_LCTRL] and event.key == pygame.K_a:
                    self.entry_list.add_entry()
                    self.entry_list.navigate_enqueue(6)
                if self.entry_list.curr_focused == -1 and event.key == pygame.K_TAB and len(self.entry_list.entry_list):
                    self.entry_list.navigate_enqueue(0)
            if event.type == pygame.MOUSEWHEEL:
                if (len(self.entry_list.entry_list) + 2) * self.entry_list.spacing > SCREEN_HEIGHT:
                    self.entry_list.y_val += event.y * 10000 * delta
                    if self.entry_list.y_val > self.entry_list_default_y_offset:
                        self.entry_list.y_val = self.entry_list_default_y_offset
                    if self.entry_list.y_val < -(len(self.entry_list.entry_list)-2) * self.entry_list.spacing:
                        self.entry_list.y_val = -(len(self.entry_list.entry_list)-2) * self.entry_list.spacing
                else:
                    self.entry_list.y_val = self.entry_list_default_y_offset
                self.entry_list.update_dims(self.entry_list.pos, self.entry_list.width)

        self.entry_list.update(keys, mouseState, delta, events)
        self.searchbar.update(keys, mouseState, delta, events)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if keys[pygame.K_LCTRL] and event.key == pygame.K_SLASH:
                    self.entry_list.navigate_enqueue(7)

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
                               onEnter=goto_main_page,
                               only_edit_mode=True,
                               hidden=True)
        self.input.is_focused = True

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
                                hidden=True)
        self.input2 = TextInput((SCREEN_WIDTH / 2 - self.input_width / 2, SCREEN_HEIGHT / 2 + 0.5 * self.input_height),
                                self.input_width,
                                self.input_height,
                                alt_text="re-enter pwd",
                                hidden=True)
        self.input1.is_focused = True
        self.change_button = Button((SCREEN_WIDTH / 2 - 200, 3 * SCREEN_HEIGHT / 4 - 25), 400, 50, text="Change password", onClick=change_password)
        self.cancel_button = Button((SCREEN_WIDTH / 2 - 200, 3 * SCREEN_HEIGHT / 4 + 50), 400, 50, text="Cancel", onClick=goto_main_page_without_pwd)

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

running = True
prev_time = time.time_ns()
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
            save_data()

    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()[0]
    mouseState = (mouse_pos, mouse_pressed)

    curr_time = time.time_ns()
    delta = (curr_time - prev_time) / 1e9
    prev_time = curr_time
    if current_page == "pwd":
        pwd_page.update(keys, mouseState, delta, events)
        pwd_page.draw(screen)
    elif current_page == "main":
        main_page.update(keys, mouseState, delta, events)
        main_page.draw(screen)
    elif current_page == "change_pwd":
        change_pwd_page.update(keys, mouseState, delta, events)
        change_pwd_page.draw(screen)

    pygame.display.update()
    screen.fill((0, 0, 0))
    time.sleep(1 / 256)
