from policy import Policy
from ontology import OntologyManager

MAX_SHOWING = 10

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

        if intent[:6] == 'inform':
            results = self.ontology_manager.entity_by_features('*', state)
            movie_showing = [{k: result[k] for k in ('movie_name', 'theater_name', 'showing_time')} for result in results]
            if len(results) > MAX_SHOWING:
                if state['movie_name'] == '':
                    sys_act['act_type'] = 'request_movie_name'
                elif state['theater_name'] == '':
                    sys_act['act_type'] = 'request_theater_name'
                elif state['showing_time'] == '':
                    sys_act['act_type'] = 'request_showing_time'

            elif len(results) > 1:
                 sys_act['act_type'] = 'inform_movie_showing'
                 sys_act['slot_value'] = movie_showing

            elif len(results) == 1:
                sys_act['act_type'] = 'confirm'
                sys_act['slot_value'] = movie_showing

        elif intent[:7] == 'request':
            results = self.ontology_manager.entity_by_features(intent[8:], state)
            sys_act['act_type'] = 'inform_{}'.format(intent[8:])
            sys_act['slot_value'] = results

        elif intent == 'booking':
            sys_act['act_type'] = 'booking'

        elif intent == 'closing_failure':
            sys_act['act_type'] = 'reset'

        return sys_act
