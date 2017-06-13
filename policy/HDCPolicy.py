from policy import Policy
from ontology import OntologyManager

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
        constraints={}
        state, intent = belief

        # inform type intent
        if intent[:6] == 'inform':
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
                sys_act['slot_value'] = self.ontology_manager.entity_by_features(slot, state)[:MAX_RESULTS]

            # show result for user to select
            elif len(results) > 1:
                 sys_act['act_type'] = 'inform_movie_showing'
                 sys_act['slot_value'] = movie_showing

            # confirm the only result
            elif len(results) == 1:
                sys_act['act_type'] = 'confirm'
                sys_act['slot_value'] = movie_showing

            # no results => remove error slots
            else:
                sys_act['act_type'] = 'confuse'
                error_slot = {}
                for slot in state:
                    results = self.ontology_manager.entity_by_features('*', {slot: state[slot]})
                    if len(results) == 0:
                        error_slot[slot] = state[slot]
                sys_act['slot_value'] = [error_slot]

        # request type intent
        elif intent[:7] == 'request':
            results = self.ontology_manager.entity_by_features(intent[8:], state)

            # no results => remove error slots
            if len(results) == 0:
                sys_act['act_type'] = 'confuse'
                error_slot = {}
                for slot in state:
                    results = self.ontology_manager.entity_by_features('*', {slot: state[slot]})
                    if len(results) == 0:
                        error_slot[slot] = state[slot]
                sys_act['slot_value'] = [error_slot]

            # movie, theater, time could be multiple results
            elif intent[8:] == 'movie_name' or intent[8:] == 'theater_name' or intent[8:] == 'showing_time':
                sys_act['act_type'] = 'inform_{}'.format(intent[8:])
                sys_act['slot_value'] = results[:MAX_RESULTS]

            # only one result => just show it!
            elif len(results) == 1:
                sys_act['act_type'] = 'inform_{}'.format(intent[8:])
                sys_act['slot_value'] = results

            # too many results => request for more information
            else:
                slot = '{}_name'.format(intent.split('_')[1])
                sys_act['act_type'] = 'request_{}'.format(slot)
                sys_act['slot_value'] = self.ontology_manager.entity_by_features(slot, state)[:MAX_RESULTS]

        elif intent == 'booking':
            sys_act['act_type'] = 'booking'

        elif intent == 'closing_failure':
            sys_act['act_type'] = 'reset'

        return sys_act
