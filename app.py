from config import *
from flask import Flask, jsonify, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder='./static')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_POOL_SIZE'] = SQLALCHEMY_POOL_SIZE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS


@app.route('/')
def hello_world():
    boxes = Box.query.order_by(Box.id).all()

    return render_template('BitBlox.html', boxes=boxes)


# Route to change box color to a specific color
@app.route('/change/<int:box_id>/<string:color>', methods=['POST'])
def change_color(box_id, color):
    box = Box.query.get(box_id)
    data = None

    if box.color_num == 4:
        if color == "yellow":
            box.color_num = 0
        elif color == "blue":
            box.color_num = 1
        elif color == "orange":
            box.color_num = 2
        elif color == "green":
            box.color_num = 3
        data = "You successfully changed the title color!"
    else:
        data = "You cannot send a POST request to an already colored tile. You have to use a PUT request."

    db.session.commit()

    return jsonify({'data': data})


# Route to change color if the square already has a color
@app.route('/change/<int:box_id>/<string:color>', methods=['PUT'])
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
@app.route('/change/<int:box_id>/white', methods=['DELETE'])
def change_white(box_id):
    box = Box.query.get(box_id)
    box.color_num = 4
    db.session.commit()

    return jsonify({'data': box.color_num})


if __name__ == '__main__':
    app.run()


class Box(db.Model):
    # 0 is red 1 is blue 2 is orange 3 is green and 4 is white
    id = db.Column(db.Integer, primary_key=True)
    color_num = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Box('{self.id}')"
