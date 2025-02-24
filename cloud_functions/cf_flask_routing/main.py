from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/user/<string:id>', methods=['GET', 'DELETE'])
def delete_user(id):
    data = request.get_json()
    headers = dict(request.headers)

    response = {
        "user_id": id,
        "data": data,
        "headers": headers,
        "message": "DELETE request: A specific user delete url triggered"
    }
    return jsonify(response)

@app.route('/user/<string:id>', methods=['GET', 'POST'])
def update_user(id):
    data = request.get_json()
    headers = dict(request.headers)

    response = {
        "user_id": id,
        "data": data,
        "headers": headers,
        "message": "POST request: A specific user update url triggered"
    }
    return jsonify(response)

@app.route('/', methods=['GET','POST'])
def main():
    data = request.get_json()
    headers = dict(request.headers)

    response = {
        "data": data,
        "headers": headers,
        "message": "POST request: The main host url triggered"
    }
    return jsonify(response)

#Set my_function as an entry function
def my_function(request):
    """
    Handles incoming requests and dispatches them to the internal Flask app.

    Args:
        request: The Cloud Function request object.

    Returns:
        The response from the internal Flask app.
    """
    with app.test_request_context(
        path=request.path, method=request.method, 
        headers={k: v for k, v in request.headers.items()}, 
        data=request.data
    ):
        return app.full_dispatch_request()
