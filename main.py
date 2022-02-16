from flask import Flask, jsonify, request

app = Flask(__name__)

def exception_decorator(func):
	def wrapper(*args, **kwargs):
		try:
			return func(*args, **kwargs)
		except Exception as ex:
			print(ex)
			return jsonify(status='ERROR', message=str(ex)), 400
	wrapper.__name__ = func.__name__
	return wrapper

@app.route('/price', methods=['GET'])
@exception_decorator
def price():
    ...


if __name__ == "__main__":
	app.run(port=4040, host='0.0.0.0', debug=True)