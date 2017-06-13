class Policy(object):
	'''
	Interface class for a policy. Responsible for selecting the next system action and handling the learning of the policy.

	To create your own reward model derive from this class.
	'''
	def __init__(self):
		"""
		Constructor for policy.
		:return:
		"""
		
		self.lastSystemAction = None
		self.prevbelief = None

		self.startwithhello = False
	
	def act_on(self, beliefstate):
		'''
		Main policy method: mapping of belief state to system action.
		
		This method is automatically invoked by the agent at each turn after tracking the belief state.

		May initially return 'hello()' as hardcoded action. Keeps track of last system action and last belief state.

		:param beliefstate: the belief state to act on
		:type beliefstate: dict
		:returns: the next system action
		'''
		if self.lastSystemAction is None and self.startwithhello:
			systemAct = 'hello()'
		else:
			systemAct = self.nextAction(beliefstate)
		self.lastSystemAction = systemAct
		self.prevbelief = beliefstate
		return systemAct

###################################################################################
# interface methods
###################################################################################

	def nextAction(self, beliefstate):
		'''
		Interface method for selecting the next system action. Should be overriden by sub-class.
		
		This method is automatically executed by :meth:`act_on thus at each turn.
		:param beliefstate: the state the policy acts on
		:type beliefstate: dict
		:returns: the next system action
		'''
		pass
