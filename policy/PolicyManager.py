class PolicyManager(object):
	'''
	The policy manager manages the policies.

	It provides the interface to get the next system action based on the current belief state in :func:`act_on` and to initiate the learning in the policy in :func:`train`.
	'''
	def __init__(self):
		self.prevbelief = None
		self.lastSystemAction = None

		self._load_policy()

	def act_on(self, belief):
		'''
		Main policy method which maps the provided belief to the next system action.

		:param belief: the belief state the policy should act on
		:type belief: dict
		:returns: the next system action
		'''
		self.prevbelief = belief

		systemAct = self.policy.act_on(beliefstate=belief)

		self.lastSystemAction = systemAct
		return systemAct

	def _load_policy(self):
		'''
		Loads and instantiates the respective policy as configured in config file. The new object is added to the internal dictionary.
	
		Default is 'hdc'.

		:returns: the new policy object
		'''

		# get type:
		policy_type = 'hdc'

		if policy_type == 'hdc':
			from policy import HDCPolicy
			self.policy = HDCPolicy.HDCPolicy()
	
		return
