#!/usr/bin/env python3
"""
Documentation

See also https://www.python-boilerplate.com/flask
"""
import os

from flask import Flask, jsonify, render_template
from src.search import Search
from urllib.parse import unquote

# from flask_cors import CORS


def create_app(config=None):
    app = Flask(__name__, template_folder='template')
    Searcher = Search('./src/inverted/term_tfidf.txt')
    # See http://flask.pocoo.org/docs/latest/config/
    app.config.update(dict(DEBUG=True))
    app.config['JSON_SORT_KEYS'] = False
    app.config.update(config or {})

    # Setup cors headers to allow all domains
    # https://flask-cors.readthedocs.io/en/latest/
    # CORS(app)

    # Definition of the routes. Put them into their own file. See also
    # Flask Blueprints: http://flask.pocoo.org/docs/latest/blueprints
    @app.route("/")
    def index():
        return render_template('index.html')

    @app.route("/api/search/<query>/<total_docs>")
    def search_query(query, total_docs):
        docs = Searcher.search_query(unquote(query))

        returned_docs = []
        total_docs = int(total_docs)

        returned_docs.append({'process_time': docs['process_time']})
        for key in docs:
            if key == 'process_time':
                continue
            if total_docs > 0:
                total_docs -= 1
                returned_docs.append(Searcher.get_article(key))
            else:
                break
        return jsonify(returned_docs)

    @app.route("/api/document/<doc_name>")
    def get_document(doc_name):
        return doc_name

    return app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app = create_app()
    app.run(host="0.0.0.0", port=port)
