import mysql.connector
import os
import time
import json
from android.storage import primary_external_storage_path
from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from random import randint
from kivy.animation import Animation
from kivy.clock import Clock
from kivy import platform


from android.permissions import request_permissions, Permission
request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

mydb = mysql.connector.connect(host='b6gxr4yhrz9angmy26rx-mysql.services.clever-cloud.com', user='u0h3y0vbt41kr38n', password='Fkkt8pUT9yIAniNMZAD1', database='b6gxr4yhrz9angmy26rx')
conn = mydb.cursor()


class AllScreens(ScreenManager):

    def change_screen(self, screen):
        self.current = screen



class HomeScreen(Screen):

    def how_to_play(self):
        show_how_to_play = MDDialog(title="How To Play", md_bg_color=(
            1, 1, 1, 1), text="Getting three in a row is the aim of a game of Tic-Tac-Toe. A three by three gaming board is used during play. X always goes first before O, and if nobody gets three it's referred to as a cat game")
        show_how_to_play.open()



class WelcomeScreen(Screen):

    def add_user(self, username_field, username):
        if len(username) < 6 and len(username) > 1:
            try:
                os.mkdir(f'{primary_external_storage_path()}/tictactoe')
                file = open(
                    f'{primary_external_storage_path()}/tictactoe/info.txt', 'w', encoding='UTF-8')
                file.write(username)
                file.close()
            except FileExistsError:
                file = open(
                    f'{primary_external_storage_path()}/tictactoe/info.txt', 'w', encoding='UTF-8')
                file.write(username)
                file.close()
            self.parent.change_screen('homescreen')



class GamePrepScreen(Screen):
    def to_home_screen(self):
        AllScreens.current = 'homescreen'



class GameScreen(Screen):
    player_name, player_score, opp_score, board, cell0, cell1, cell2, cell3, cell4, cell5, cell6, cell7, cell8 = ObjectProperty(None), ObjectProperty(None), ObjectProperty(None), ObjectProperty(
        None), ObjectProperty(None), ObjectProperty(None), ObjectProperty(None), ObjectProperty(None), ObjectProperty(None), ObjectProperty(None), ObjectProperty(None), ObjectProperty(None), ObjectProperty(None)

    player = ''
    opp = ''
    next_turn = ''
    opp_pick = []
    player_pick = []
    possible = [["0", "1", "2"], ["0", "3", "6"], ["0", "4", "8"], ["1", "4", "7"], [
        "2", "4", "6"], ["2", "5", "8"], ["3", "4", "5"], ["6", "7", "8"], ]
    pause_game_dialog = None

    def pause_game(self):
        self.pause_game_dialog = MDDialog(md_bg_color=(1, 1, 1, 1), buttons=[
            MDRaisedButton(text="CONTINUE", md_bg_color=(
                0, 0.5, 0, 1), on_press=lambda x: self.continue_game(), size_hint=(None, None)),
            MDRaisedButton(text="QUIT", md_bg_color=(
                0.5, 0, 0, 1), on_press=lambda x: self.quit_game(), size_hint=(None, None))
        ])
        self.pause_game_dialog.open()

    def quit_game(self):
        if self.pause_game_dialog:
            self.pause_game_dialog.dismiss(force=True)
            cells_list = [self.cell0, self.cell1, self.cell2, self.cell3,
                          self.cell4, self.cell5, self.cell6, self.cell7, self.cell8]
            for i in cells_list:
                i.text = ''
                i.md_bg_color = (0, 0, 0, 1)
                i.size_hint = (None, None)
                anim = Animation(
                    size=(self.board.width/3, self.board.height/3))
                anim.start(i)
            self.player_score.text = '0'
            self.opp_score.text = '0'
            self.opp_pick = []
            self.player_pick = []
            try:
                self.parent.change_screen('homescreen')
            except Exception as e:
                AllScreens().change_screen('homescreen')

    def continue_game(self):
        if self.pause_game_dialog:
            self.pause_game_dialog.dismiss(force=True)

    def comp_choice(self):
        return randint(0, 8)

    def arrange_game(self, dt):
        cells_list = [self.cell0, self.cell1, self.cell2, self.cell3,
                      self.cell4, self.cell5, self.cell6, self.cell7, self.cell8]

        def clear_frame(dt):
            for i in cells_list:
                i.text = ''
                i.md_bg_color = (0, 0, 0, 1)
                i.size_hint = (None, None)
                anim = Animation(
                    size=(self.board.width/3, self.board.height/3))
                anim.start(i)
                self.opp_pick = []
                self.player_pick = []

        if self.player_score.text == "5":
            SoundLoader.load('bigwin.wav').play()
            Clock.schedule_once(clear_frame, 3)
            self.player_score.text = '0'
            self.opp_score.text = '0'
        elif self.opp_score.text == '5':
            SoundLoader.load('biglose.wav').play()
            Clock.schedule_once(clear_frame, 3)
            self.player_score.text = '0'
            self.opp_score.text = '0'
        else:
            Clock.schedule_once(clear_frame, 1)

    def comp_play_game(self):
        picked_cells = self.player_pick + self.opp_pick

        if len(picked_cells) < 9:
            cells_list = [self.cell0, self.cell1, self.cell2, self.cell3,
                          self.cell4, self.cell5, self.cell6, self.cell7, self.cell8]
            opp_choice = str(self.comp_choice())
            while opp_choice in picked_cells:
                opp_choice = str(self.comp_choice())
            self.opp_pick.append(opp_choice)

            comp_picked_cell = cells_list[int(opp_choice)]
            comp_picked_cell.text = self.opp
            comp_picked_cell.size_hint = (None, None)
            anim = Animation(
                size=(self.board.width/3, self.board.height/3), duration=0.2)
            anim.start(comp_picked_cell)
            self.next_turn = self.player

    def player_play_game(self, cell, position):
        if self.next_turn == self.player and position not in self.opp_pick and position not in self.player_pick:
            self.player_pick.append(position)
            cells_list = [self.cell0, self.cell1, self.cell2, self.cell3,
                          self.cell4, self.cell5, self.cell6, self.cell7, self.cell8]
            for i in range(len(self.possible)):
                if all(items in self.player_pick for items in self.possible[i]):
                    for k in self.possible[i]:
                        cells_list[int(k)].md_bg_color = (0, 0.3, 0, 1)
                    self.player_score.text = str(int(self.player_score.text)+1)
                    self.player_pick = ["0", "1", "2",
                                        "3", "4", "5", "6", "7", "8"]
                    SoundLoader.load('smallwin.wav').play()
                    Clock.schedule_once(self.arrange_game, 2)
                    break

            cell.text = self.player
            cell.size_hint = (None, None)
            anim = Animation(size=(self.board.width/3, self.board.height/3))
            anim.start(cell)

            # Computer choice after self choice
            self.comp_play_game()

            # checking for win
            for i in range(len(self.possible)):
                if all(items in self.opp_pick for items in self.possible[i]):
                    for k in self.possible[i]:
                        cells_list[int(k)].md_bg_color = (0, 0.3, 0, 1)
                    self.opp_score.text = str(int(self.opp_score.text) + 1)
                    self.player_pick = ["0", "1", "2",
                                        "3", "4", "5", "6", "7", "8"]
                    SoundLoader.load('smalllose.wav').play()
                    Clock.schedule_once(self.arrange_game, 2)
                    break

            if len(self.opp_pick+self.player_pick) == 9:
                Clock.schedule_once(self.arrange_game, 2)

    def choose_letter(self, chosen_letter):
        if 'tictactoe' in os.listdir(primary_external_storage_path()):
            info_file = open(
                f'{primary_external_storage_path()}/tictactoe/info.txt', 'r', encoding='UTF-8')
            self.player_name.text = str(info_file.readlines()[0])
            info_file.close()

        if chosen_letter == 'o':
            self.player = 'o'
            self.opp = 'x'
            picked_cells = self.player_pick + self.opp_pick

            cells_list = [self.cell0, self.cell1, self.cell2, self.cell3,
                          self.cell4, self.cell5, self.cell6, self.cell7, self.cell8]
            opp_choice = str(self.comp_choice())
            while opp_choice in picked_cells:
                opp_choice = str(self.comp_choice())
            self.opp_pick.append(opp_choice)

            comp_picked_cell = cells_list[int(opp_choice)]
            comp_picked_cell.text = self.opp
            comp_picked_cell.size_hint = (
                self.board.size_hint_x/3, self.board.size_hint_y/3)
            self.next_turn = self.player
        else:
            self.player = 'x'
            self.opp = 'o'
            self.next_turn = self.player



class OnlineGamePrepScreen(Screen):
    def __init__(self, **kwargs):
        super(OnlineGamePrepScreen, self).__init__(**kwargs)
        self.conn_dialog = None
        self.conn_option = None
        self.player = None

    def connect_opp(self, code, textfield, status_label):
        # checking length of code to be valid
        if code != '' and len(code) > 3 and self.conn_option == None:
            # ensuring the table name is valid for mysql
            try:
                code = int(code)
                code = 'ttt'+str(code)
                self.code = code
            except Exception as e:
                self.code = code

            if 'tictactoe' in os.listdir(primary_external_storage_path()):
                info_file = open(
                    f'{primary_external_storage_path()}/tictactoe/info.txt', 'r', encoding='UTF-8')
                player_name = str(info_file.readlines()[0])
                info_file.close()
            else:
                player_name = 'BOSS'

            # try and except below checks if there is a connection
            try:
                conn.execute(
                    f'INSERT INTO `connections` (`match_code`, `status`, `player1id`, `player1letter`) VALUES ("{code}", "ready", "{player_name}", "X")')
                mydb.commit()
                self.player = 'X'
                textfield.text = ''

                def opp_wait(dt):
                    conn.execute(
                        f'SELECT `status`, `player2id` FROM connections WHERE "{code}" = match_code')
                    details = conn.fetchall()
                    if self.conn_option != None:
                        if details[0][0] == 'connected':
                            status_label.text = 'connecting...'
                            Clock.unschedule(opp_wait)
                            status_label.text = ''
                            textfield.text = ''
                            self.conn_option = None
                            self.parent.ids.onlinegamescreen.start_game(
                                code, self.player, details[0][1])
                            self.parent.change_screen('onlinegamescreen')
                    else:
                        status_label.text = ''
                        Clock.unschedule(opp_wait)
                    mydb.commit()
                status_label.text = 'Waiting for opponent....'
                self.conn_option = "Used"
                Clock.schedule_interval(opp_wait, 0.1)

            except Exception as e:
                conn.execute(
                    f'SELECT status FROM connections WHERE "{code}" = match_code')
                details = conn.fetchall()
                if details[0][0] == 'ready':
                    self.player = 'O'
                    conn.execute(
                        f'UPDATE connections SET `status` = "connected", `player2id` = "{player_name}", `player2letter` = "O" WHERE match_code = "{code}"')
                    mydb.commit()
                    textfield.text = ''
                    status_label.text = ''
                    conn.execute(
                        f'SELECT `player1id` from connections WHERE match_code = "{code}"')
                    opp_name = (conn.fetchall())[0][0]
                    mydb.commit()

                    # changing screent
                    self.parent.ids.onlinegamescreen.start_game(
                        code, self.player, opp_name)
                    self.parent.change_screen('onlinegamescreen')
                else:
                    # display that another person is using the code
                    textfield.text = ''
                    self.avail_code_check()
                    self.conn_option = None

    def to_home_screen(self):
        if self.conn_option == None:
            self.parent.change_screen('homescreen')
        else:
            self.conn_option = None
            conn.execute(
                f'DELETE FROM `connections` WHERE `match_code` = "{self.code}"')
            mydb.commit()
            self.code = None
            self.parent.change_screen('homescreen')

    def avail_code_check(self):
        if not self.conn_dialog:
            self.conn_dialog = MDDialog(
                title='Connection Error', text='Sorry, this code is being used at the moment, please try another code')
        self.conn_dialog.open()



class OnlineGameScreen(Screen):


    def __init__(self, **kwargs):
        super(OnlineGameScreen, self).__init__(**kwargs)
        onl_board, onl_cell0, onl_cell1, onl_cell2, onl_cell3, onl_cell4, onl_cell5, onl_cell6, onl_cell7, onl_cell8 = ObjectProperty(None), ObjectProperty(None), ObjectProperty(
            None), ObjectProperty(None), ObjectProperty(None), ObjectProperty(None), ObjectProperty(None), ObjectProperty(None), ObjectProperty(None), ObjectProperty(None),
        self.player = None
        self.opp = None
        online_opp_name, online_opp_score, online_player_score, online_player_name = ObjectProperty(None),  ObjectProperty(None), ObjectProperty(None), ObjectProperty(None)
        online_timer = ObjectProperty(None)
        self.game_code = None
        self.game_status = 'start'
        self.player_turn = None
        self.turns = 0
        self.player_inp = []
        self.opp_inp = []
        self.possible = [["0", "1", "2"], ["0", "3", "6"], ["0", "4", "8"], ["1", "4", "7"], [
            "2", "4", "6"], ["2", "5", "8"], ["3", "4", "5"], ["6", "7", "8"], ]
        self.winstatusdialog = None
        self.game_time = 7
        self.pause_game_dialog = None
        self.game_paused_time = 0
        self.game_pause_condition = False
        self.player_pauses = 0
        self.game_forfeit = False


    def start_game(self, match_code, player, opp_name):
        onl_cells_list = [self.onl_cell0, self.onl_cell1, self.onl_cell2, self.onl_cell3,
                          self.onl_cell4, self.onl_cell5, self.onl_cell6, self.onl_cell7, self.onl_cell8]

        self.player = player
        self.game_code = match_code
        # updating names
        if 'tictactoe' in os.listdir(primary_external_storage_path()):
            info_file = open(
                f'{primary_external_storage_path()}/tictactoe/info.txt', 'r', encoding='UTF-8')
            self.online_player_name.text = str(info_file.readlines()[0])
            info_file.close()
        else:
            player_name = 'YOU'

        self.online_opp_name.text = opp_name
        # names updating finished

        # Starting game on first person
        if self.player == 'X':
            self.opp = 'O'
            self.player_turn = self.player
            conn.execute(f"CREATE TABLE {match_code} (`p1_game_pause_condition` LONGTEXT NULL, `p2_game_pause_condition` LONGTEXT NULL, `p1_pauses` INT NOT NULL DEFAULT '3',   `p2_pauses` INT NOT NULL DEFAULT '3',  `p1inp` LONGTEXT NULL,  `p2inp` LONGTEXT NULL, `p1active` INT NOT NULL DEFAULT '3' ,  `p2active` INT NOT NULL DEFAULT '3' )")
            mydb.commit()
        else:
            self.opp = 'X'
            self.player_turn = self.opp

        for i in onl_cells_list:
            i.size_hint = (self.onl_board.size_hint_x/3,
                           self.onl_board.size_hint_y/3)
        self.game_continue()


    def game_continue(self):
        all_cells = [self.onl_cell0, self.onl_cell1, self.onl_cell2, self.onl_cell3,
                     self.onl_cell4, self.onl_cell5, self.onl_cell6, self.onl_cell7, self.onl_cell8]

        if self.game_status == 'start':
            self.game_status == 'started'
            if self.player == 'X':
                self.player_turn = self.player

                def start_check_oppo_inp(dt):

                    conn.execute(f"SELECT `p1_game_pause_condition`, `p2_game_pause_condition` FROM {self.game_code}")
                    playerpauses = conn.fetchall()
                    mydb.commit()
                    if playerpauses:
                        if playerpauses[0][0] == "Wait" and playerpauses[0][1] == "Wait":
                            self.game_pause_condition = True
                        elif playerpauses[0][0]  == '' and playerpauses[0][1] == '':
                            self.game_pause_condition = False
                            try:
                                self.pause_game_dialog.dismiss(force=True)
                            except AttributeError:
                                pass
                        elif (playerpauses[0][0] == '' and playerpauses[0][1] == 'Wait') or (playerpauses[0][0] == 'Wait' and playerpauses[0][1] == ''):
                            conn.execute(f"INSERT INTO {self.game_code} (`p1_game_pause_condition`, `p2_game_pause_condition`) VALUES ('Wait', 'Wait')")
                            self.game_pause_condition = True
                        elif playerpauses[0][0] == 'Ready' and playerpauses[0][1] == 'Ready':
                            conn.execute(f"UPDATE {self.game_code} SET `p1_game_pause_condition` = (''), `p2_game_pause_condition` = ('')")
                        elif playerpauses[0][1] == 'Forfeit':
                            self.game_forfeit = True
                            Clock.unschedule(start_check_oppo_inp)
                            self.opponent_forfeit()
                            return None


                    if self.game_pause_condition == True:
                        if self.pause_game_dialog == None:

                            def forfeit_game():
                                self.game_forfeit = True
                                Clock.unschedule(start_check_oppo_inp)
                                self.pause_game()
                                self.forfeit_game()


                            self.pause_game_dialog = MDDialog(md_bg_color=(1, 1, 1, 1), buttons=[
                                MDRaisedButton(text="CONTINUE", md_bg_color=(0, 0.5, 0, 1), on_press=lambda x: self.continue_paused_game(), size_hint=(None, None)),
                                MDRaisedButton(text="QUIT", md_bg_color=(0.5, 0, 0, 1), on_press=lambda x: forfeit_game(), size_hint=(None, None))
                            ])
                            def noneDialog():
                                self.pause_game_dialog = None
                            self.pause_game_dialog.bind(on_dismiss=lambda x: noneDialog())
                            self.pause_game_dialog.open()
                        return None

                    self.game_time -= 0.1
                    self.online_timer.text = str(int(self.game_time)) + 's '

                    if self.game_time <= 0:
                        if self.player_turn == self.player:
                            self.player_turn = self.opp
                        else:
                            self.player_turn = self.player
                        self.game_time = 7

                    if self.game_status == 'end':
                        Clock.unschedule(start_check_oppo_inp)
                    else:
                        conn.execute(f"SELECT `p2inp` FROM {self.game_code}")
                        p2inp_list = conn.fetchall()
                        mydb.commit()

                        if len(p2inp_list) > 0:
                            if len(p2inp_list[0][0]) > 0:
                                p2inp = json.loads(p2inp_list[0][0])
                                if len(p2inp) > len(self.opp_inp) and self.player_turn != None:
                                    all_cells[int(p2inp[-1])].text = self.opp
                                    self.player_turn = self.player
                                    self.game_time = 7
                                    self.opp_inp = p2inp
                                    self.check_win()

                Clock.schedule_interval(start_check_oppo_inp, 0.1)
            elif self.player == 'O':
                def start_check_oppx_inp(dt):

                    conn.execute(f"SELECT `p1_game_pause_condition`, `p2_game_pause_condition` FROM {self.game_code}")
                    playerpauses = conn.fetchall()
                    mydb.commit()
                    if playerpauses:
                        if playerpauses[0][0] == "Wait" and playerpauses[0][1] == "Wait":
                            self.game_pause_condition = True
                        elif playerpauses[0][0]  == '' and playerpauses[0][1] == '':
                            self.game_pause_condition = False
                            try:
                                self.pause_game_dialog.dismiss(force=True)
                            except AttributeError:
                                pass
                        elif (playerpauses[0][0] == '' and playerpauses[0][1] == 'Wait') or (playerpauses[0][0] == 'Wait' and playerpauses[0][1] == ''):
                            conn.execute(f"INSERT INTO {self.game_code} (`p1_game_pause_condition`, `p2_game_pause_condition`) VALUES ('Wait', 'Wait')")
                            self.game_pause_condition = True
                        elif playerpauses[0][0] == 'Ready' and playerpauses[0][0] == 'Ready':
                            conn.execute(f"UPDATE {self.game_code} SET `p1_game_pause_condition` = (''), `p2_game_pause_condition` = ('')")
                        elif playerpauses[0][0] == 'Forfeit':
                            self.game_forfeit == True
                            Clock.unschedule(start_check_oppx_inp)
                            self.opponent_forfeit()
                            return None

                    if self.game_pause_condition == True:
                        if self.pause_game_dialog == None:

                            def forfeit_game():
                                self.game_forfeit = True
                                Clock.unschedule(start_check_oppx_inp)
                                self.pause_game()
                                self.forfeit_game()


                            self.pause_game_dialog = MDDialog(md_bg_color=(1, 1, 1, 1), buttons=[
                                MDRaisedButton(text="CONTINUE", md_bg_color=(0, 0.5, 0, 1), on_press=lambda x: self.continue_paused_game(), size_hint=(None, None)),
                                MDRaisedButton(text="QUIT", md_bg_color=(0.5, 0, 0, 1), on_press=lambda x: forfeit_game(), size_hint=(None, None))
                            ])
                            def noneDialog():
                                self.pause_game_dialog = None
                            self.pause_game_dialog.bind(on_dismiss=lambda x: noneDialog())
                            self.pause_game_dialog.open()
                        return None

                    
                    self.game_time -= 0.1
                    self.online_timer.text = str(int(self.game_time)) + 's '

                    if self.game_time <= 0:
                        if self.player_turn == self.player:
                            self.player_turn = self.opp
                        else:
                            self.player_turn = self.player
                        self.game_time = 7

                    if self.game_status == 'end':
                        Clock.unschedule(start_check_oppx_inp)
                    else:
                        try:
                            conn.execute(f"SELECT `p1inp` FROM {self.game_code}")
                        except Exception as e:
                            print(e)
                        p1inp_list = conn.fetchall()
                        mydb.commit()

                        if len(p1inp_list) > 0:
                            if len(p1inp_list[0][0]) > 0:
                                p1inp = json.loads(p1inp_list[0][0])
                                if len(p1inp) > len(self.opp_inp) and self.player_turn != None:
                                    all_cells[int(p1inp[-1])].text = self.opp
                                    self.player_turn = self.player
                                    self.game_time = 7
                                    self.opp_inp = p1inp
                                    self.check_win()
                        
                Clock.schedule_interval(start_check_oppx_inp, 0.1)


    def pause_game(self):

        if self.player_pauses <= 3 and self.game_forfeit == False:
            self.player_pauses += 1
            if self.player == 'X':
                conn.execute(f"SELECT `p1_game_pause_condition`, `p2_game_pause_condition` FROM {self.game_code}")
                if not (conn.fetchall()):
                    mydb.commit()
                    conn.execute(f"INSERT INTO {self.game_code} (`p1_game_pause_condition`) VALUES ('Wait')")
                else:
                    mydb.commit()
                    conn.execute(f"UPDATE {self.game_code} SET `p1_game_pause_condition` = ('Wait')")
            else:
                conn.execute(f"SELECT `p2_game_pause_condition`, `p1_game_pause_condition` FROM {self.game_code}")
                if not (conn.fetchall()):
                    mydb.commit()
                    conn.execute(f"INSERT INTO {self.game_code} (`p2_game_pause_condition`) VALUES ('Wait')")
                else:
                    mydb.commit()
                    conn.execute(f"UPDATE {self.game_code} SET `p2_game_pause_condition` = ('Wait')")

            self.game_paused_time = 0
            def game_paused_timer(dt):
                if self.game_forfeit == True:
                    print('okay')
                    try:
                        Clock.unschedule(game_paused_timer)
                    except Exception as e:
                        print(e)
                    return None

                self.game_paused_time += 0.1
                if self.game_paused_time >= 7 and self.game_pause_condition == True and self.game_forfeit == False:
                    try:
                        conn.execute(f"UPDATE {self.game_code} SET `p1_game_pause_condition` = (''), `p2_game_pause_condition` = ('')")
                    except BaseException as e:
                        print(e) 
                    self.game_paused_time = 0
            Clock.schedule_interval(game_paused_timer, 0.1)


    def forfeit_game(self):
        if self.player == 'X':
            conn.execute(f"UPDATE {self.game_code} SET `p1_game_pause_condition` = 'Forfeit'")
            mydb.commit()
            try:
                self.pause_game_dialog.dismiss(force=True)
            except AttributeError:
                pass
            self.change_to_game_prepscreen()
        else:
            conn.execute(f"UPDATE {self.game_code} SET `p2_game_pause_condition` = 'Forfeit'")
            mydb.commit()
            try:
                self.pause_game_dialog.dismiss(force=True)
            except AttributeError:
                pass
            self.change_to_game_prepscreen()


    def opponent_forfeit(self):
        self.pause_game()
        conn.execute(f"DROP TABLE {self.game_code}")
        mydb.commit()
        conn.execute(f"DELETE FROM `connections` WHERE `match_code` = '{self.game_code}'")
        mydb.commit()
        self.pause_game_dialog.dismiss(force=True)
        self.winstatusdialog = MDDialog(title='Fortunately,', text='Your opponent has forfeited the match')
        self.winstatusdialog.open()
        self.winstatusdialog.bind(on_dismiss = lambda x: self.change_to_game_prepscreen())
        mydb.commit()


    def continue_paused_game(self):

        if self.player == 'X':
            conn.execute(f"UPDATE {self.game_code} SET `p1_game_pause_condition` = ('Ready')")
        else:
            conn.execute(f"UPDATE {self.game_code} SET `p2_game_pause_condition` = ('Ready')")
   

    def game_cell_clicked(self, cell_clicked):
        all_cells = [self.onl_cell0, self.onl_cell1, self.onl_cell2, self.onl_cell3,
                     self.onl_cell4, self.onl_cell5, self.onl_cell6, self.onl_cell7, self.onl_cell8]
        if self.player_turn == self.player and self.game_status != "end":
            if cell_clicked not in self.opp_inp and cell_clicked not in self.player_inp:
                all_cells[int(cell_clicked)].text = self.player

                if self.player == 'X':
                    if len(self.player_inp) > 0 or self.turns > 0:
                        self.player_inp.append(cell_clicked)
                        player_inp_list = json.dumps(self.player_inp)
                        conn.execute(
                            f"UPDATE {self.game_code}  SET `p1inp` = ('{player_inp_list}')")
                        mydb.commit()
                        self.player_turn = self.opp
                        self.game_time = 7
                        self.check_win()

                    else:
                        self.player_inp.append(cell_clicked)
                        player_inp_list = json.dumps(self.player_inp)
                        conn.execute(
                            f"INSERT INTO {self.game_code} (`p1inp`, `p2inp`) VALUES('{player_inp_list}', '')")
                        mydb.commit()
                        self.player_turn = self.opp
                        self.game_time = 7
                        self.check_win()
                else:
                    self.player_inp.append(cell_clicked)
                    player_inp_list = json.dumps(self.player_inp)
                    conn.execute(
                        f"UPDATE {self.game_code}  SET `p2inp` = ('{player_inp_list}')")
                    mydb.commit()
                    self.player_turn = self.opp
                    self.game_time = 7
                    self.check_win()
        elif self.game_status == 'end':
            self.change_to_game_prepscreen()


    def change_to_game_prepscreen(self):
        # Preparing to change screen to online game prep screen
        self.player = None
        self.opp = None
        self.game_code = None
        self.game_status = 'start'
        self.player_turn = None
        self.turns = 0
        self.player_inp = []
        self.opp_inp = []
        self.possible = [["0", "1", "2"], ["0", "3", "6"], ["0", "4", "8"], ["1", "4", "7"], ["2", "4", "6"], ["2", "5", "8"], ["3", "4", "5"], ["6", "7", "8"], ]
        self.winstatusdialog = None
        self.game_time = 7
        self.pause_game_dialog = None
        self.game_paused_time = 0
        self.game_pause_condition = False
        self.player_pauses = 0
        self.game_forfeit = False
        self.opp_pauses = 0
        self.online_timer.text = "7s  "
        self.online_opp_name.text, self.online_opp_score.text, self.online_player_score.text, self.online_player_name.text = 'YOU', '0', '0', 'OPP'

        all_cells = [self.onl_cell0, self.onl_cell1, self.onl_cell2, self.onl_cell3, self.onl_cell4, self.onl_cell5, self.onl_cell6, self.onl_cell7, self.onl_cell8]
        for i in all_cells:
            i.md_bg_color = (0, 0, 0, 1)
            i.text = ''

        # Changing screen to online game prep screen
        self.parent.change_screen('onlinegameprepscreen')


    def check_win(self):
        # All game rows and columns
        all_cells = [self.onl_cell0, self.onl_cell1, self.onl_cell2, self.onl_cell3,
                     self.onl_cell4, self.onl_cell5, self.onl_cell6, self.onl_cell7, self.onl_cell8]

        # CLEAR CELLS FUNCTION
        # Clears all cells
        def clear_cells(dt):
            self.player_turn = None
            self.player_inp = []
            self.opp_inp = []
            try:
                conn.execute(
                    f"UPDATE {self.game_code} SET `p1inp` = '[]', `p2inp` = '[]'")
            except:
                pass
            for i in all_cells:
                i.md_bg_color = (0, 0, 0, 1)
                i.text = ''
            if self.player == 'X':
                self.player_turn = self.player
            else:
                self.player_turn = self.opp
            self.game_time = 7
            self.turns += 1
            
            
            # If statement output the win status of user depending on scores
            if self.turns == 3:
                self.game_status = 'end'
                if self.player == 'X':
                    conn.execute(f"""DROP TABLE {self.game_code};""")
                    mydb.commit()
                    conn.execute(
                        f"""DELETE FROM `connections` WHERE `match_code` = '{self.game_code}';""")
                    mydb.commit()

                if int(self.online_player_score.text) > int(self.online_opp_score.text):
                    # USER WINS GAME
                    SoundLoader.load('bigwin.wav').play()
                    if not self.winstatusdialog:
                        self.winstatusdialog = MDDialog(title='Congratulations', text='You\'ve won this match, you must be proud of yourself')
                        self.winstatusdialog.open()
                        self.winstatusdialog.bind(on_dismiss = lambda x: self.change_to_game_prepscreen)
                
                elif int(self.online_player_score.text) < int(self.online_opp_score.text):
                    # Lose Game
                    SoundLoader.load('biglose.wav').play()
                    if not self.winstatusdialog:
                        self.winstatusdialog = MDDialog(title='Good Try', text='You lose! \n Come back stronger next time')
                        self.winstatusdialog.open()
                        self.winstatusdialog.bind(on_dismiss = lambda x: self.change_to_game_prepscreen)
                else:
                    # Draw game
                    SoundLoader.load('biglose.wav').play()
                    if not self.winstatusdialog:
                        self.winstatusdialog = MDDialog(title='Nice Try', text='You drawed ' + self.online_player_name.text + '. You can do better next time')
                        self.winstatusdialog.open()
                        self.winstatusdialog.bind(on_dismiss = lambda x: self.change_to_game_prepscreen)

        for i in self.possible:
            if all(items in self.player_inp for items in i):
                for k in i:
                    all_cells[int(k)].md_bg_color = (0, 0.3, 0, 1)
                SoundLoader.load('smallwin.wav').play()
                self.online_player_score.text = str(
                    int(self.online_player_score.text) + 1)
                Clock.schedule_once(clear_cells, 3)
                break

            elif all(items in self.opp_inp for items in i):
                for k in i:
                    all_cells[int(k)].md_bg_color = (0.3, 0, 0, 1)
                SoundLoader.load('smalllose.wav').play()
                self.online_opp_score.text = str(
                    int(self.online_opp_score.text) + 1)
                Clock.schedule_once(clear_cells, 3)
                break

        if len(self.player_inp)+len(self.opp_inp) == len(all_cells) and self.game_status != 'end':
            Clock.schedule_once(clear_cells, 3)



class TicApp(MDApp):

    def build(self):
        screen = Builder.load_file('tictac.kv')
        if 'tictactoe' not in os.listdir(primary_external_storage_path()):
            screen.ids.scr_mgr.current = 'welcomescreen'
        return screen



if __name__ == '__main__':
    TicApp().run()
