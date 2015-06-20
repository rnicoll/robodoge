#!/usr/bin/python3
from flask import Flask, jsonify, request, make_response
from flask.ext.httpauth import HTTPBasicAuth
import psycopg2
import psycopg2.extras
from . import *

app = Flask(__name__)
auth = HTTPBasicAuth()
config = load_configuration('/var/www/robodoge/config.yml')
try:
    merger = Robodoge(config)
except ConfigurationError as err:
    print(err.msg)
    sys.exit(1)

@auth.get_password
def get_password(username):
    if username == 'robodoge':
        return config['http_auth']['password']
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.route('/automerge/api/v1.0/pr/', methods=['GET'])
def get_prs():
    conn = merger.get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""SELECT id,url,state,title,user_login,html_url,assignee_login,milestone_title,base_ref, build_node, s3_arn, test_node
                              FROM pull_request
                              WHERE project='dogecoin/dogecoin' and state!='closed'
                              ORDER BY id ASC""")
            return jsonify({'prs': cursor.fetchall()})
        finally:
            cursor.close()
    finally:
        conn.close()

@app.route('/automerge/api/v1.0/pr/build_ready', methods=['GET'])
def get_buildable_prs():
    conn = merger.get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""SELECT id,url,state,title,user_login,html_url,assignee_login,milestone_title,base_ref, build_node, s3_arn, test_node
                              FROM pull_request
                              WHERE project='dogecoin/dogecoin' and state='open' and assignee_login is null and milestone_title='1.9' and base_ref='1.9-dev' and build_node IS NULL
                              ORDER BY id ASC""")
            return jsonify({'prs': cursor.fetchall()})
        finally:
            cursor.close()
    finally:
        conn.close()

@app.route('/automerge/api/v1.0/pr/<int:pr_id>', methods=['GET'])
@auth.login_required
def get_pr(pr_id):
    conn = merger.get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""SELECT id,url,state,title,user_login,html_url,assignee_login,milestone_title,base_ref, build_node, s3_arn, test_node
                              FROM pull_request
                              WHERE id=%(id)s""", {'id': pr_id})
            return jsonify({'prs': cursor.fetchall()})
        finally:
            cursor.close()
    finally:
        conn.close()

@app.route('/automerge/api/v1.0/pr/<int:pr_id>', methods=['POST'])
@auth.login_required
def update_pr(pr_id):
    conn = merger.get_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute("""SELECT id
                              FROM pull_request
                              WHERE id=%(id)s""", {'id': pr_id})
            if not cursor.fetchone():
                abort(404)
        finally:
            cursor.close()

        if not request.json or not 'operation' in request.json:
            abort(403)

        if request.json['operation'] == 'claim_build':
            return claim_pr(pr_id, request.remote_addr)
        else:
            abort(403)
    finally:
        conn.close()

def claim_pr(pr_id, remote_addr):
    # Verify the PR exists
    # Tell Github we're claiming the PR
    # Update the local database
    # Return a value to let the node know that's okay
    return False