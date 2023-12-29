from flask import Flask,send_file, request, jsonify

from elasticsearch import Elasticsearch

es = Elasticsearch(
    [{'host': 'localhost', 'port': 9200, 'scheme': 'http'}],
    http_auth=('emad2', 'emadmassri'))

index_name = "news_index"

app = Flask(__name__)
@app.route("/")
def main():
    return send_file('index.html')

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('query')
    if len(query) < 3:
        return jsonify(suggestions=[])
    
    search_body = {
        "query": {
            "bool": {
                "should": [
                    {
                        "fuzzy": {
                            "Title": {
                                "value": query.lower(),
                                "fuzziness": "AUTO",
                                "prefix_length": 0,
                                "max_expansions": 10
                            }
                        }
                    },
                    {
                        "match_phrase": {
                            "Title": {
                                "query": query
                            }
                        }
                    },
                    {
                        "wildcard": {
                            "Title": {
                                "value": f"*{query.lower()}*"
                            }
                        }
                    },
                ],
                "minimum_should_match": 1
            }
        }
    }


    results = es.search(index=index_name, body=search_body)
    suggestions = [hit['_source']['Title'] for hit in results['hits']['hits']]
    
    return jsonify(suggestions=suggestions)




if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=8000)