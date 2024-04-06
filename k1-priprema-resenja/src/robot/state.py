from abc import *
from board import Board
import math


class State(object):
    """
    Apstraktna klasa koja opisuje stanje pretrage.
    """

    @abstractmethod
    def __init__(self, board: Board, parent=None, position=None, goal_position=None, action=None):
        """
        :param board: Board - tabla
        :param parent: State - roditeljsko stanje
        :param position: (int x, int y) - pozicija stanja
        :param goal_position: (int x, int y) - pozicija krajnjeg stanja
        :return:
        """
        self.board = board  # Reference na stanje table koje se vidi na ekranu. Ovo se ne menja
        self.parent = parent  # roditeljsko stanje
        self.action = action # akcija koja je dovela do trenutnog stanja


        if self.parent is None:  # ako nema roditeljsko stanje, onda je ovo inicijalno stanje
            # pronaladji elemente sa table
            self.position = board.find_position(self.get_agent_code())  # pronadji pocetnu poziciju
            self.goal_position = board.find_position(self.get_agent_goal_code())  # pronadji krajnju poziciju
            self.checkpoints = tuple(board.find_all_positions(self.get_checkpoint_code()))
            self.teleports = tuple(board.find_all_positions(self.get_teleport_code()))
            self.teleport = False
            self.fire = board.find_position(self.get_fire_code())
        else:  # ako ima roditeljsko stanje, samo sacuvaj vrednosti parametara
            self.position = position
            self.goal_position = goal_position
            self.checkpoints = self.parent.checkpoints
            self.teleports = self.parent.teleports
            self.teleport = self.parent.teleport
            self.fire = self.parent.fire

        self.depth = parent.depth + 1 if parent is not None else 1  # povecaj dubinu/nivo pretrage

    def get_next_states(self):
        new_positions = self.get_legal_positions()  # dobavi moguce (legalne) sledece pozicije iz trenutne pozicije
        next_states = []
        # napravi listu mogucih sledecih stanja na osnovu mogucih sledecih pozicija
        for new_position, action in new_positions:
            next_state = self.__class__(self.board, self, new_position, self.goal_position, action)
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

    def get_fire_code(self):
        return 'f'

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

    def __init__(self, board: Board, parent: State=None, position: tuple=None, goal_position: tuple=None, action: tuple=None):
        super().__init__(board, parent, position, goal_position, action)
        # posle pozivanja super konstruktora, mogu se dodavati "custom" stvari vezani za stanje
        if parent is None: 
            self.cost = 0
            self.has_right_checkpoint = False
            self.has_left_checkpoint = False
            self.right_checkpoint = max(self.checkpoints, key=lambda x: x[1])
            self.left_checkpoint = min(self.checkpoints, key=lambda x: x[1])
        else: 
            self.right_checkpoint = self.parent.right_checkpoint
            self.left_checkpoint = self.parent.left_checkpoint
            self.has_right_checkpoint = self.parent.has_right_checkpoint
            self.has_left_checkpoint = self.parent.has_left_checkpoint

            action_cost = 1 if self.parent.action == self.action else 3
            self.cost = self.parent.cost + action_cost

        if self.position == self.right_checkpoint:
            self.has_right_checkpoint = True

        if self.position == self.left_checkpoint:
            self.has_left_checkpoint = True
        

    def get_legal_positions(self):

        # ako je pokupio levu kutiju, a desnu nije stanje je nevalidno
        # sprecavamo ga da nastavi pretragu
        if self.has_left_checkpoint and not self.has_right_checkpoint:
            return []
        
        actions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        # akcije sahovskoh konja
        knight_actions = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)]

        if self.has_right_checkpoint and not self.has_left_checkpoint:
            actions = knight_actions

        row, col = self.position 
        new_positions = []
        for d_row, d_col in actions: 
            new_row = row + d_row
            new_col = col + d_col 

            if not self.board.is_out_of_bounds(new_row, new_col) and not self.board.hits_wall(new_row, new_col):
                new_positions.append(((new_row, new_col), (d_row, d_col)))
        return new_positions

    def is_final_state(self):
        return self.position == self.goal_position and self.has_left_checkpoint and self.has_right_checkpoint

    def unique_hash(self):
        return str(self.position) + str(self.has_left_checkpoint) + str(self.has_right_checkpoint)
    
    def get_cost_estimate(self):
        h = 0
        if not self.has_right_checkpoint:
            h += self.adjusted_distance(self.position, self.right_checkpoint)
            h += self.knight_distance(self.right_checkpoint, self.left_checkpoint)
            h += self.manhattan_distance(self.left_checkpoint, self.goal_position) + 2 # nisu poravnati pa je potreban barem jedan okret
        elif not self.has_left_checkpoint:
            h += self.knight_distance(self.position, self.left_checkpoint)
            h += self.manhattan_distance(self.left_checkpoint, self.goal_position) + 2 # nisu poravnati pa je potreban barem jedan okret
        else:
            h += self.adjusted_distance(self.position, self.goal_position)

        return h
        
    def get_current_cost(self):
        return self.cost
    
    def knight_distance(self, pointA, pointB):
        return self.manhattan_distance(pointA, pointB)/3
    
    def adjusted_distance(self, pointA, pointB):
        distance = self.manhattan_distance(pointA, pointB)
        # heuristika 1 - ako nisu poravnati po nekoj osi, potreban je barem jedna promena pravca
        # if pointA[0] != pointB[0] and pointA[1] != pointB[1]: 
        #     distance += 2
        # heuristika 2 - ako bi nastavljanjem u istom pravcu robot udario u zid, mora promeniti pravac barem jednom
        if self.action != None: # ako bi nastavljanjem 
            momentum_row, momentum_col = self.position
            momentum_row += self.action[0]
            momentum_col += self.action[1]
            if not self.board.is_out_of_bounds(momentum_row, momentum_col) and self.board.hits_wall(momentum_row, momentum_col):
                distance += 2
        return distance
    
    def manhattan_distance(self, pointA, pointB):
        return abs(pointA[0] - pointB[0]) + abs(pointA[1] - pointB[1])
    
    def euclidian_distance(self, pointA, pointB):
        return math.sqrt((pointA[0] - pointB[0])**2 + (pointA[1] - pointB[1])**2)
    
    def diagonal_distance(self, pointA, pointB):
        return max([abs(pointA[0] - pointB[0]), abs(pointA[1] - pointB[1])])


    # dodajemo da lakse debagujemo
    def __repr__(self):
        return f'RobotState(pos={self.position}, depth={self.depth})'