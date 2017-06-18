from policy import Policy
from ontology import OntologyManager
import random
from policy import PolicyUtils

MAX_RESULTS = 5

class HDCPolicy(Policy.Policy):
    """
    Handcrafted policy derives from Policy base class. Based on the slots defined in the ontology and fix threshholds, defines a rule-based policy.

    If no info is provided by the user, the system will always ask for the slot information in the same order based on the ontology.
    """
    def __init__(self):
        """
        Handcrafted policy constructor.
        """
        super(HDCPolicy, self).__init__() # inherited from Policy.Policy()
        self.ontology_manager = OntologyManager.OntologyManager()

    def nextAction(self, belief):
        sys_act={}
        state, intent, unfinished_intent, last_sys_act, search_location = belief

        # if there is unfinished intent, do it first
        if intent[:6] == 'inform' and unfinished_intent != '':
            intent = unfinished_intent
            unfinished_intent = ''

        # inform type intent
        if intent[:6] == 'inform':
            sys_act, unfinished_intent = self._getInform(state, intent, unfinished_intent, search_location)

        # request type intent
        elif intent[:7] == 'request':
            sys_act, unfinished_intent = self._getRequest(state, intent, unfinished_intent, search_location)


        elif intent == 'dontcare':
            if last_sys_act == '':
                error_slot = self._detectErrorSlot(state)
                sys_act['type'] = 'confuse'
                sys_act['slot_value'] = [error_slot]
            elif last_sys_act == 'inform_movie_showing':
                results = self.ontology_manager.entity_by_features('*', state)
                state = random.sample(results, 1)[0]
                state['showing_time_end'] = state['showing_time']
                intent = 'inform_showing_time'
            else:
                slot = '{}_{}'.format(last_sys_act.split('_')[1], last_sys_act.split('_')[2])
                results = self.ontology_manager.entity_by_features(slot, state)
                state[slot] = random.sample(results, 1)[0][slot]
            #error_slot = self._detectErrorSlot(state)
            #for slot in error_slot.keys():
            #    state[slot] = ''
                if slot=='showing_time':
                    state['showing_time_end'] = state[slot] + 100
                intent = 'inform_{}'.format(slot)
            sys_act, unfinished_intent = self._getInform(state, intent, unfinished_intent, search_location)

        elif intent == 'greeting':
            sys_act['act_type'] = 'greeting'

        return (sys_act, unfinished_intent)

    def _getInform(self, state, intent, unfinished_intent, search_location):
        sys_act={}

        results = self.ontology_manager.entity_by_features('*', state)
        movie_showing = [{k: result[k] for k in ('movie_name', 'theater_name', 'showing_time')} for result in results]

        # too many results => request for more information
        if len(results) > MAX_RESULTS:
            if state['movie_name'] == '':
                slot = 'movie_name'
            elif state['theater_name'] == '':
                slot = 'theater_name'
            elif state['showing_time'] == '':
                slot = 'showing_time'
            sys_act['act_type'] = 'request_{}'.format(slot)
            results = self.ontology_manager.entity_by_features(slot, state)

            # sort theater name by distance
            if slot == 'theater_name' and search_location != '':
                results = self._sortByDistance(search_location, results)
                sys_act['slot_value'] = results[:MAX_RESULTS]

            elif len(results) > MAX_RESULTS:
                sys_act['slot_value'] = random.sample(results, MAX_RESULTS)
            else:
                sys_act['slot_value'] = results[:MAX_RESULTS]

        # show result for user to select
        elif len(results) > 1:
             sys_act['act_type'] = 'inform_movie_showing'
             sys_act['slot_value'] = movie_showing

        # confirm the only result
        elif len(results) == 1:
            sys_act['act_type'] = 'confirm'
            sys_act['slot_value'] = movie_showing

        # no results or remove error slots
        else:
            error_slot = self._detectErrorSlot(state)
            if error_slot != {}:
                sys_act['act_type'] = 'confuse'
                sys_act['slot_value'] = [error_slot]
            else:
                sys_act['act_type'] = 'no_result'

        return (sys_act, unfinished_intent)

    def _getRequest(self, state, intent, unfinished_intent, search_location):
        sys_act={}

        results = self.ontology_manager.entity_by_features(intent[8:], state)
        # no results or remove error slots
        if len(results) == 0:
            error_slot = self._detectErrorSlot(state)
            if error_slot != {}:
                sys_act['act_type'] = 'confuse'
                sys_act['slot_value'] = [error_slot]
            else:
                sys_act['act_type'] = 'no_result'

        # movie, theater, time could be multiple results
        elif intent[8:] == 'movie_name' or intent[8:] == 'theater_name' or intent[8:] == 'showing_time':
            sys_act['act_type'] = 'inform_{}'.format(intent[8:])
            # sort theater name by distance
            if intent[8:] == 'theater_name' and search_location != '':
                results = self._sortByDistance(search_location, results)
                sys_act['slot_value'] = results[:MAX_RESULTS]

            elif len(results) > MAX_RESULTS:
                sys_act['slot_value'] = random.sample(results, MAX_RESULTS)
            else:
                sys_act['slot_value'] = results[:MAX_RESULTS]

        # only one result => just show it!
        elif len(results) == 1:
            sys_act['act_type'] = 'inform_{}'.format(intent[8:])
            sys_act['slot_value'] = results

        # too many results => request for more information
        else:
            if intent.split('_')[1] == 'showing':
                if state['movie_name'] == '':
                    slot = 'movie_name'
                elif state['theater_name'] == '':
                    slot = 'theater_name'
                elif state['showing_time'] == '':
                    slot = 'showing_time'
            else:
                slot = '{}_name'.format(intent.split('_')[1])
            sys_act['act_type'] = 'request_{}'.format(slot)
            results = self.ontology_manager.entity_by_features(slot, state)
            # sort theater name by distance
            if slot == 'theater_name' and search_location != '':
                results = self._sortByDistance(search_location, results)
                sys_act['slot_value'] = results[:MAX_RESULTS]

            elif len(results) > MAX_RESULTS:
                sys_act['slot_value'] = random.sample(results, MAX_RESULTS)
            else:
                sys_act['slot_value'] = results[:MAX_RESULTS]
            unfinished_intent = intent

        return (sys_act, unfinished_intent)

    def _sortByDistance(self, location, results):
        origins = [location]
        destinations = [x['theater_name'] for x in results]

        matrix = PolicyUtils.getDistanceMatrix(origins, destinations)
        values = [x['distance']['value'] for x in matrix['rows'][0]['elements']]
        texts = [x['distance']['text'] for x in matrix['rows'][0]['elements']]

        destinations = [x for (y, x) in sorted(zip(values, destinations))]
        texts = [x for (y, x) in sorted(zip(values, texts))]

        results = [{'theater_name': x, 'distance': y, 'search_location': location} for (x,y) in zip(destinations, texts)]

        return results

    def _detectErrorSlot(self, state):
        error_slot = {}
        for slot in state:
            results = self.ontology_manager.entity_by_features('*', {slot: state[slot]})
            if len(results) == 0:
                error_slot[slot] = state[slot]

        return error_slot
