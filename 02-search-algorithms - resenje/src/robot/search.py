from __future__ import print_function

from collections import deque
from abc import *


class Search(object):
    """
    Apstraktna klasa za pretragu.
    """

    def __init__(self, board):
        self.board = board

    def search(self, initial_state):
        """
        Implementirana pretraga.

        :param initial_state: Inicijalno stanje. Tip: implementacija apstraktne klase State.
        :return: path, processed_list, states_list
        """
        # inicijalizacija pretrage
        initial_state = initial_state(self.board)  # pocetno stanje
        states_list = deque([initial_state])  # deque - "brza" lista u Python-u
        states_set = {initial_state.unique_hash()}  # set - za brzu pretragu stanja

        processed_list = deque([])  # deque procesiranih stanja
        processed_set = set()  # set procesiranih stanja

        # pretraga
        while len(states_list) > 0:  # dok ima stanja za obradu
            curr_state = self.select_state(states_list)  # preuzmi sledece stanje za obradu
            states_set.remove(curr_state.unique_hash())  # izbaci stanja iz seta stanja

            processed_list.append(curr_state)  # ubaci stanje u listu procesiranih stanja
            processed_set.add(curr_state.unique_hash())  # ubaci stanje u set procesiranih stanja

            if curr_state.is_final_state():  # ako je krajnje stanje
                # rekonsturisi putanju
                return Search.reconstruct_path(curr_state), processed_list, states_list

            # ako nije krajnje stanje
            # izgenerisi sledeca moguca stanja
            new_states = curr_state.get_next_states()
            # iz liste sledecih mogucih stanja izbaci ona koja su vec u listi i koja su vec procesirana
            new_states = [new_state for new_state in new_states if
                          new_state.unique_hash() not in processed_set and
                          new_state.unique_hash() not in states_set]
            # dodaj sledeca moguca stanja na kraj liste stanja
            states_list.extend(new_states)
            # dodaj sledeca moguca stanja u set stanja
            states_set.update([new_state.unique_hash() for new_state in new_states])
        return None, processed_list, states_list

    @staticmethod
    def reconstruct_path(final_state):
        path = []
        while final_state is not None:
            path.append(final_state.position)
            final_state = final_state.parent
        return reversed(path)

    @abstractmethod
    def select_state(self, states):
        """
        Apstraktna metoda koja, na osnovu liste svih mogucih sledecih stanja,
        bira sledece stanje za obradu.
        *** STRATEGIJA PRETRAGE SE IMPLEMENTIRA OVERRIDE-ovanjem OVE METODE ***

        :param states: lista svih mogucih sledecih stanja
        :return: odabrano sledece stanje za obradu
        """
        pass


class BreadthFirstSearch(Search):
    def select_state(self, states):
        return states.popleft()


class DepthFirstSearch(Search):
    def select_state(self, states: list):
        # TODO 1 - Implementirati pretragu prvi u dubinu (DFS)
        return states.pop()


class MaxDepthException(Exception):
    def __init__(self):
        self.message = 'Nema vise stanja za obradu. Stigli smo do maksimalne definisane dubine.'
        super().__init__(self.message)        

class IterativeDepthFirstSearch(Search):
    def __init__(self, board):
        super().__init__(board)
        self.max_depth = 1
    
    def search(self, initial_state):
        ''' Override-ujemo podrazumevanu pretragu.
        Pretragu pokrećemo iznova svaki put sa novom maksimalnom dubinom povećanom za 1 
        (rekurzivno se poziva).'''
        try:
            return super().search(initial_state)
        # u slučaju da smo stigli do maksimalne dubine i nismo pronašli rešenje, povećavamo dubinu pretrage i pokrećemo pretragu iznova
        except MaxDepthException:
            self.max_depth += 1
            return self.search(initial_state)
    
    def select_state(self, states):
        # pretražujemo sva stanja do određene dubine
        # sva stanja koja su preduboka samo izbacujemo iz liste stanja
        while states:
            state = states.pop() # isto kao i DFS
            if state.depth <= self.max_depth:
                return state

        # Ako nismo uspeli da nadjemo sledeće stanje u okviru definisane dubine `max_depth`, to znači da nema više stanja za obradu. 
        # Kada se desi greška, znači da smo stigli do maksimalne dubine, a nismo pronašli rešenje.
        raise MaxDepthException()



class UniformCostSearch(Search):
    def select_state(self, states):
        min_cost = float('inf')
        min_cost_state = None
        for state in states:
            g = state.get_current_cost()
            if g < min_cost:
                min_cost = g
                min_cost_state = state

        states.remove(min_cost_state)
        return min_cost_state


class GreedySearch(Search):
    def select_state(self, states):
        # TODO 4 - Implementirati pohlepnu pretragu (GS).
        min_cost = float('inf')
        min_cost_state = None
        for state in states:
            h = state.get_cost_estimate()
            if h < min_cost:
                min_cost = h
                min_cost_state = state

        states.remove(min_cost_state)
        return min_cost_state


class AStarSearch(Search):
    def select_state(self, states):
        # TODO 5 - Implementirati A*
        min_cost = float('inf')
        min_cost_state = None
        for state in states:
            h = state.get_cost_estimate()
            g = state.get_current_cost()
            f = g + h
            if f < min_cost:
                min_cost = f
                min_cost_state = state
        
        states.remove(min_cost_state)
        return min_cost_state

# napomena: traženje stanja sa najmanjim ključem može i kraće da se napiše koristeći min(states, key=) sintaksu.