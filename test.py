import utils
import sys
sys.path.append('./NLU')
from NLU import NLU
from ontology import OntologyManager

if __name__ == '__main__':
  nlu = NLU.NLU()
  OM = OntologyManager.OntologyManager() 
  while(True):
    sentence = input("> ")
    print(nlu.understand(sentence))
    print(utils.error_correction(nlu.understand(sentence), OM))
