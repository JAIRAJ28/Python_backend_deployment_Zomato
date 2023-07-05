from flask import Flask, jsonify, request
import pickle

app = Flask(__name__)

MENU_FILE = 'menu_data.pickle'
ORDER_FILE = 'order_data.pickle'

menu = {}
order = {}


def load_menu_data():
    try:
        with open(MENU_FILE, 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        return {}


def save_menu_data(menu_data):
    with open(MENU_FILE, 'wb') as f:
        pickle.dump(menu_data, f)


def load_order_data():
    try:
        with open(ORDER_FILE, 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        return {}


def save_order_data(order_data):
    with open(ORDER_FILE, 'wb') as f:
        pickle.dump(order_data, f)


# Load menu and order data at startup
menu = load_menu_data()
order = load_order_data()


@app.route('/')
def home():
    return jsonify({'menu': menu, 'order': order})


@app.route("/menu", methods=["POST"])
def add_menu():
    data = request.json
    menu[str(data['id'])] = data
    save_menu_data(menu)
    return jsonify({"message": "Item has been added", "dish": data}), 200


@app.route('/menu/<dish_id>', methods=['DELETE'])
def remove_dish(dish_id):
    id = str(dish_id)
    if id in menu:
        del menu[id]
        save_menu_data(menu)
        return jsonify({'message': 'Dish removed successfully'}), 200
    else:
        return jsonify({'message': 'Dish not found'}), 404


@app.route("/menu/<dish_id>", methods=["PUT"])
def update(dish_id):
    id = str(dish_id)
    if id in menu:
        dish = menu[id]
        dish['available'] = not dish.get('available', False)
        save_menu_data(menu)
        return jsonify({'message': 'Availability updated successfully', 'dish': dish}), 200
    else:
        return jsonify({'message': 'Dish not found'}), 404


@app.route('/order', methods=['POST', 'PUT'])
def handle_order():
    if request.method == 'POST':
        data = request.json
        customer_name = data.get('customer_name')
        dish_ids = data.get('dish_ids')

        order_items = []
        for dish_id in dish_ids:
            if str(dish_id) in menu:
                dish = menu[str(dish_id)]
                if dish.get('available'):
                    order_items.append(dish)
                else:
                    return jsonify({'message': f"Dish with ID {dish_id} is not available"}), 400
            else:
                return jsonify({'message': f"Dish with ID {dish_id} does not exist"}), 400

        order_id = len(order) + 1
        order_data = {
            'order_id': order_id,
            'customer_name': customer_name,
            'items': order_items,
            'status': 'received'
        }
        order[str(order_id)] = order_data
        save_order_data(order)
        return jsonify({'message': 'Order placed successfully', 'order': order_data}), 200
    elif request.method == 'PUT':
        data = request.json
        order_id = data.get('order_id')
        status = data.get('status')

        if str(order_id) in order:
            if status in ['preparing', 'ready for pickup', 'delivered']:
                order[str(order_id)]['status'] = status
                save_order_data(order)
                return jsonify({'message': 'Order status updated successfully', 'order': order[str(order_id)]}), 200
            else:
                return jsonify({'message': 'Invalid status'}), 400
        else:
            return jsonify({'message': 'Order not found'}), 404


@app.route('/order/<int:order_id>', methods=['PUT'])
def update_order_status(order_id):
    order_id = str(order_id)
    if order_id in order:
        data = request.json
        status = data.get('status')
        if status in ['received', 'preparing', 'ready for pickup', 'delivered']:
            order[order_id]['status'] = status
            save_order_data(order)
            return jsonify({'message': 'Order status updated successfully', 'order': order[order_id]}), 200
        else:
            return jsonify({'message': 'Invalid status'}), 400
    else:
        return jsonify({'message': 'Order not found'}), 404



@app.route('/order/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    order_id = str(order_id)
    if order_id in order:
        if order[order_id]['status'] == 'delivered':
            del order[order_id]
            save_order_data(order)
            return jsonify({'message': 'Order deleted successfully'}), 200
        else:
            return jsonify({'message': 'Only delivered orders can be deleted'}), 400
    else:
        return jsonify({'message': 'Order not found'}), 404


@app.route('/order', methods=['GET'])
def get_order():
    return jsonify({'order': order})


@app.route('/exit', methods=['GET'])
def exit_app():
    save_menu_data(menu)
    save_order_data(order)
    return 'Exiting the application...'


if __name__ == '__main__':
    app.run(debug=True)
