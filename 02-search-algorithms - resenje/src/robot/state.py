from abc import *
from board import Board


class State(object):
    """
    Apstraktna klasa koja opisuje stanje pretrage.
    """

    @abstractmethod
    def __init__(self, board: Board, parent=None, position=None, goal_position=None,  checkpoints=None, teleports=None, teleport=False):
        """
        :param board: Board - tabla
        :param parent: State - roditeljsko stanje
        :param position: (int x, int y) - pozicija stanja
        :param goal_position: (int x, int y) - pozicija krajnjeg stanja
        :return:
        """
        self.board = board
        self.parent = parent  # roditeljsko stanje

        if checkpoints == None:
            self.checkpoints = tuple(
                board.find_all_positions(self.get_checkpoint_code()))
        else:
            self.checkpoints = checkpoints

        self.teleport = teleport
        if teleports == None:
            self.teleports = tuple(
                board.find_all_positions(self.get_teleport_code()))
        else:
            self.teleports = teleports

        if self.parent is None:  # ako nema roditeljsko stanje, onda je ovo inicijalno stanje
            self.position = board.find_position(
                self.get_agent_code())  # pronadji pocetnu poziciju
            self.goal_position = board.find_position(
                self.get_agent_goal_code())  # pronadji krajnju poziciju
        else:  # ako ima roditeljsko stanje, samo sacuvaj vrednosti parametara
            self.position = position
            self.goal_position = goal_position
        # povecaj dubinu/nivo pretrage
        self.depth = parent.depth + 1 if parent is not None else 1

    def get_next_states(self):
        new_positions = self.get_legal_positions()  # dobavi moguce (legalne) sledece pozicije iz trenutne pozicije
        next_states = []
        # napravi listu mogucih sledecih stanja na osnovu mogucih sledecih pozicija
        for new_position in new_positions:
            next_state = self.__class__(self.board, self, new_position, self.goal_position)
            next_states.append(next_state)
        return next_states


    def get_agent_code(self):
        return 'r'

    def get_agent_goal_code(self):
        return 'g'
    
    def get_checkpoint_code(self):
        return 'b'
    
    def get_teleport_code(self):
        return 'y'

    @abstractmethod
    def get_legal_positions(self):
        """
        Apstraktna metoda koja treba da vrati moguce (legalne) sledece pozicije na osnovu trenutne pozicije.
        :return: list
        """
        pass

    @abstractmethod
    def is_final_state(self):
        """
        Apstraktna metoda koja treba da vrati da li je treuntno stanje zapravo zavrsno stanje.
        :return: bool
        """
        pass

    @abstractmethod
    def unique_hash(self):
        """
        Apstraktna metoda koja treba da vrati string koji je JEDINSTVEN za ovo stanje
        (u odnosu na ostala stanja).
        :return: str
        """
        pass
    
    @abstractmethod
    def get_cost_estimate(self):
        """
        Apstraktna metoda koja treba da vrati procenu cene
        (vrednost heuristicke funkcije - h(n)) za ovo stanje.
        Koristi se za vodjene pretrage.
        :return: float
        """
        pass
    
    @abstractmethod
    def get_current_cost(self):
        """
        Apstraktna metoda koja treba da vrati stvarnu dosadašnju trenutnu cenu za ovo stanje, odnosno g(n)
        Koristi se za vodjene pretrage.
        :return: float
        """
        pass


class RobotState(State):

    def __init__(self, board: Board, parent: State=None, position: tuple=None, goal_position: tuple=None):
        super(self.__class__, self).__init__(board, parent, position,
                                             goal_position, checkpoints, teleports, teleport)
        # posle pozivanja super konstruktora, mogu se dodavati "custom" stvari vezani za stanje
        self.cost = 0
        if self.parent:
            self.cost += self.parent.cost + 1
        # TODO 5: prosiriti stanje sa informacijom da li je robot pokupio kutiju
        # TODO 6: prosiriti stanje sa informacijom o preostalim kutijama
        if self.position in self.checkpoints:
            self.checkpoints = tuple(
                [c for c in self.checkpoints if c != self.position])
        # TODO 7: prosiriti stanje sa informacijom o teleportovanju
        if self.teleport:
            self.teleports = tuple(
                [t for t in self.teleports if t != self.position])
            self.teleport = False
        elif self.position in self.teleports:
            self.teleports = tuple(
                [t for t in self.teleports if t != self.position])
            next_position = self.teleports[0]
            self.teleport = True

    def get_legal_positions(self):
        # moguci smerovi kretanja robota (desno, levo, dole, gore)
        actions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        row, col = self.position  # trenutno pozicija
        new_positions = []
        for d_row, d_col in actions:  # za sve moguce smerove
            new_row = row + d_row  # nova pozicija po redu
            new_col = col + d_col  # nova pozicija po koloni
            # ako nova pozicija nije van table i ako nije zid ('w'), ubaci u listu legalnih pozicija
            if not self.board.is_out_of_bounds(new_row, new_col) and not self.board.hits_wall(new_row, new_col):
                new_positions.append((new_row, new_col))
        return new_positions

    def is_final_state(self):
        return self.position == self.goal_position

    def unique_hash(self):
        return str(self.position)
    
    def get_cost_estimate(self):
        # TODO 4 - Implementirati heuristiku 
        # kao heuristiku u ovom primeru koristimo 'Manhatten' distancu
        pos = self.position
        goal = self.goal_position
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
    
    def get_current_cost(self):
        # TODO 3 - Implementirati cenu
        return self.cost

    # dodajemo da lakse debagujemo
    def __repr__(self):
        return f'RobotState(pos={self.position}, depth={self.depth})'