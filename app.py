from config import *
from flask import Flask, jsonify, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__, static_folder='./static')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_POOL_SIZE'] = int(SQLALCHEMY_POOL_SIZE)


# Decorator to check for authentication
def api_key_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        key = request.args.get('api_key')
        if key == "thisistheapikey":
            return f(*args, **kwargs)
        else:
            return jsonify({"message": "You are not authenticated, you need an API Key to use this route"})
    return wrap


# Route for the homepage of the game
@app.route('/')
def hello_world():
    boxes = Box.query.order_by(Box.id).all()

    return render_template('BitBlox.html', boxes=boxes)


# Route to return all boxes
@app.route('/boxes')
@api_key_required
def box_index():
    boxes = Box.query.order_by(Box.id).all()
    box_dict = {}
    for box in boxes:
        color = get_color(box.color_num)
        box_dict['box_' + str(box.id)] = {'id': box.id, 'color': color}
    return jsonify(box_dict)


# Route to return a specific box by id
@app.route('/boxes/<int:box_id>')
@api_key_required
def box_show(box_id):
    box = Box.query.get(box_id)
    color = get_color(box.color_num)

    return jsonify({'data': {'id': box.id, 'color': color}})


# Route to change box color to a specific color
@app.route('/change/<int:box_id>/<string:color>', methods=['POST'])
@api_key_required
def change_color(box_id, color):
    box = Box.query.get(box_id)
    data = None

    if box.color_num == 4:
        data = "You successfully changed the title color!"
        if color == "yellow":
            box.color_num = 0
        elif color == "blue":
            box.color_num = 1
        elif color == "orange":
            box.color_num = 2
        elif color == "green":
            box.color_num = 3
        else:
            data = "Color does not exist."
    else:
        data = "You cannot send a POST request to an already colored tile. You have to use a PUT request."

    db.session.commit()

    return jsonify({'data': data})


# Route to change color if the square already has a color
@app.route('/change/<int:box_id>/<string:color>', methods=['PUT'])
@api_key_required
def switch_color(box_id, color):
    box = Box.query.get(box_id)
    data = None

    if box.color_num != 4:
        if color == "yellow":
            box.color_num = 0
        elif color == "blue":
            box.color_num = 1
        elif color == "orange":
            box.color_num = 2
        elif color == "green":
            box.color_num = 3

        data = "You successfully changed the color of the square!"
    else:
        data = "You can't edit a white square. You have to use a POST request to change the color first."
    db.session.commit()

    return jsonify({'data': data})


# Route to change the box color to white
@app.route('/delete/<int:box_id>', methods=['DELETE'])
@api_key_required
def change_white(box_id):
    box = Box.query.get(box_id)
    box.color_num = 4
    db.session.commit()

    return jsonify({'data': "You successfully removed the color from the tile"})


# Function to return a color based on the color id
def get_color(color_id):
    if color_id == 0:
        return "yellow"
    elif color_id == 1:
        return "blue"
    elif color_id == 2:
        return "orange"
    elif color_id == 3:
        return "green"
    elif color_id == 4:
        return "white"


# Function to wipe out the board
def clear():
    boxes = Box.query.all()
    for box in boxes:
        if box.color_num != 4:
            box.color_num = 4

    db.session.commit()

    return


if __name__ == '__main__':
    app.run()


class Box(db.Model):
    # 0 is red 1 is blue 2 is orange 3 is green and 4 is white
    id = db.Column(db.Integer, primary_key=True)
    color_num = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Box('{self.id}')"
