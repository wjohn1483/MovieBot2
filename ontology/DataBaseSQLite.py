import sqlite3
#from utils import Settings

class DataBase_SQLite:
    def __init__(self, dbfile):
        self._loaddb(dbfile)
        self.domain = "Movie_Showing"
        self.from_all_tables = '''from {}
            join Movies, Theaters
            on Movie_Showing.movie_name=Movies.movie_name
            and Movie_Showing.theater_name=Theaters.theater_name
            '''.format(self.domain)
        self.no_constraints_sql_query = '''select *
            from {}'''.format(self.domain)
        self.limit = 10 # number of randomly returned entities

    def _loaddb(self, dbfile):
        '''Sets self.de
        '''
        try:
            self.db_connection = sqlite3.connect(dbfile)
            self.db_connection.row_factory = self._dict_factory # for getting entities back as python dict's
            self.cursor = self.db_connection.cursor()
        except Exception as e:
            print(e)

    def _dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def get_all_slots(self):
        '''Retrieves all slots

        :returns: (list) all slots
        '''
        try:
            sql_query = 'select * ' + self.from_all_tables
            cursor = self.cursor.execute(sql_query)
            results = list(set(map(lambda x: x[0], cursor.description)))
        except Exception as e:
            print(e)

        return results        

    def values_by_slot(self, slot):
        '''Retrieves from database all entities matching the given slot.

        :param slot: slot name. String
        :returns: (list) all entities matching the given slot.
        '''
        try:
            if slot=='movie_name' or slot=='theater_name':
                sql_query = 'select distinct {} '.format(self.domain+'.'+slot) + self.from_all_tables
            else:
                sql_query = 'select distinct {} '.format(slot) + self.from_all_tables
            results = [row[slot] for row in self.cursor.execute(sql_query)]
        except Exception as e:
            print(e)

        return results

    def entity_by_features(self, constraints):
        '''Retrieves from database all entities matching the given constraints.

        :param constraints: features. Dict {slot:value, ...}
        :returns: (list) all entities (each dict) matching the given features.
        '''
        
        # 1. Format constraints into sql_query
        # NO safety checking - constraints should be a dict
        # Also no checking of values regarding none: if const.val == [None, '**NONE**']: --> ERROR
        doRand = False
    
        if len(constraints):
            bits = []
            values = []
            for slot,value in constraints.items():
                if value != 'dontcare':
                    bits.append(slot + '= ?')
                    values.append(value)

            # 2. Finalise and Execute sql_query
            try:
                if len(bits):
                    sql_query = '''select *
                    from {}
                    where '''.format(self.domain)
                    sql_query += ' and '.join(bits)
                    self.cursor.execute(sql_query, tuple(values))
                else:
                    sql_query = self.no_constraints_sql_query
                    self.cursor.execute(sql_query)
                    doRand = True
            except Exception as e:
                print(e)        # hold to debug here
        
        else:
            # NO CONSTRAINTS --> get all entities in database?
            #TODO check when this occurs ... is it better to return a single, random entity? --> returning random 10

            # 2. Finalise and Execute sql_query
            sql_query = self._no_constraints_sql_query
            self.cursor.execute(sql_query)
            doRand = True

        results = self.cursor.fetchall()    # can return directly
        if doRand:
            #Settings.random.shuffle(results)
            if len(results) > self.limit:
                results = results[self.limit:]
        return results
        
