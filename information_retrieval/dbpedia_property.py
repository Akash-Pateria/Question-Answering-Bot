from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://dbpedia.org/sparql")

def get_property_name(uri):
    property_list = []
    query = ""
    q1 = """SELECT DISTINCT ?property {
  {"""
    q2 = """?property ?o}
  UNION
  { ?s ?property"""
    q3 = """}
}"""

    query = q1+" <"+uri+"> "+q2+" <"+uri+"> "+q3
    #print "\nQUERY : \n",query

    # retrieving property names
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    for result in results["results"]["bindings"]:
        property_list.append(result["property"]["value"])


    return property_list
