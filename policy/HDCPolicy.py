from policy import Policy
from ontology import OntologyManager
import random

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
        state, intent, unfinished_intent, last_sys_act = belief

        # if there is unfinished intent, do it first
        if intent[:6] == 'inform' and unfinished_intent != '':
            intent = unfinished_intent
            unfinished_intent = '' 

        # inform type intent
        if intent[:6] == 'inform':
            sys_act, unfinished_intent = self._getInform(state, intent, unfinished_intent)

        # request type intent
        elif intent[:7] == 'request':
            sys_act, unfinished_intent = self._getRequest(state, intent, unfinished_intent)


        elif intent == 'dontcare':
            slot = '{}_{}'.format(last_sys_act.split('_')[1:])
            results = self.ontology_manager.entity_by_features(slot, state)
            state[slot] = random.sample(results, 1)[0]
            sys_act, unfinished_intent = self.getInform(state, intent, unfinished_intent)

        elif intent == 'greeting':
            sys_act['act_type'] = 'greeting'

        return (sys_act, unfinished_intent)

    def _getInform(self, state, intent, unfinished_intent):
        sys_act={}
        
        results = self.ontology_manager.entity_by_features('*', state)
        movie_showing = [{k: result[k] for k in ('movie_name', 'theater_name', 'showing_time')} for result in results]

        # too many results => request for more information
        if len(results) > MAX_RESULTS:
            if state['theater_name'] == '':
                slot = 'theater_name'
            elif state['movie_name'] == '':
                slot = 'movie_name'
            elif state['showing_time'] == '':
                slot = 'showing_time'
            sys_act['act_type'] = 'request_{}'.format(slot)
            results = self.ontology_manager.entity_by_features(slot, state)
            if len(results) > MAX_RESULTS:
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
            error_slot = {}
            for slot in state:
                results = self.ontology_manager.entity_by_features('*', {slot: state[slot]})
                if len(results) == 0:
                    error_slot[slot] = state[slot]
            if error_slot != {}:
                sys_act['act_type'] = 'confuse'
                sys_act['slot_value'] = [error_slot]
            else:
                sys_act['act_type'] = 'no_result'
        
        return (sys_act, unfinished_intent)

    def _getRequest(self, state, intent, unfinished_intent):
        sys_act={}
        
        results = self.ontology_manager.entity_by_features(intent[8:], state)
        # no results or remove error slots
        if len(results) == 0:
            error_slot = {}
            for slot in state:
                results = self.ontology_manager.entity_by_features('*', {slot: state[slot]})
                if len(results) == 0:
                    error_slot[slot] = state[slot]
            if error_slot != {}:
                sys_act['act_type'] = 'confuse'
                sys_act['slot_value'] = [error_slot]
            else:
                sys_act['act_type'] = 'no_result'

        # movie, theater, time could be multiple results
        elif intent[8:] == 'movie_name' or intent[8:] == 'theater_name' or intent[8:] == 'showing_time':
            sys_act['act_type'] = 'inform_{}'.format(intent[8:])
            if len(results) > MAX_RESULTS:
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
                if state['theater_name'] == '':
                    slot = 'theater_name'
                elif state['movie_name'] == '':
                    slot = 'movie_name'
                elif state['showing_time'] == '':
                    slot = 'showing_time'
            else:
                slot = '{}_name'.format(intent.split('_')[1])
            sys_act['act_type'] = 'request_{}'.format(slot)
            results = self.ontology_manager.entity_by_features(slot, state)
            if len(results) > MAX_RESULTS:
                sys_act['slot_value'] = random.sample(results, MAX_RESULTS)
            else:
                sys_act['slot_value'] = results[:MAX_RESULTS]                
            unfinished_intent = intent

        return (sys_act, unfinished_intent)
