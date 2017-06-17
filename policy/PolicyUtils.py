import googlemaps
import responses

def getDistanceMatrix(origins, destinations):
    '''
    Method for get distance based on google map api
    :param origins: list of origin location or address
    :type origins: list
    :param destinations: list of destination location or address
    :type destinations: list
    :returns: distances (list)
    '''

    key = 'AIzaSyA7_93ScVnH3suiHO-PoPlg8w2gF9ycH_4'
    client = googlemaps.Client(key)

    responses.add(responses.GET, 
                  'https://maps.googleapis.com/maps/distancematrix/json',
                  body='{"status":"OK", "rows":[]}',
                  status=200,
                  content_type='application/json')

    matrix = client.distance_matrix(origins, destinations)

    return matrix
