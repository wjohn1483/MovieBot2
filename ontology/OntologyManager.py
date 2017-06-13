import numpy as np

from ontology import DataBaseSQLite

class Ontology(object):
    '''Utilities for ontology queries
    '''
    def __init__(self):
        self._set_db()    # sets self.db

    def _set_db(self):
        """Sets self.db to instance of choosen Data base accessing class.

        .. note:: It is currently hardcoded to use the sqlite method. But this can be config based - data base classes share interface
        so only need to change class here, nothing else in code will need adjusting.
        """
        db_fname = "./ontology/ontologies/movie.db"
        try:
            self.db = DataBaseSQLite.DataBase_SQLite(dbfile=db_fname)
        except IOError:
            print(IOError)
        return

class OntologyManager(object):
    def __init__(self):
        self._bootup()

    def _bootup(self):
        self.ontologyManager = Ontology()

    #--------------------------------------------------------------------------
    # Wrappers access to ontologies/database methods and info.
    #--------------------------------------------------------------------------
    def get_all_slots(self):
        return self.ontologyManager.db.get_all_slots()

    def values_by_slot(self, slot):
        return self.ontologyManager.db.values_by_slot(slot=slot)

    def entity_by_features(self, key, constraints):
        return self.ontologyManager.db.entity_by_features(key=key, constraints=constraints)
