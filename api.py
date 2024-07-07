import os
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
import datetime
import json

from script.send_sms import send

app = Flask(__name__)

# Use environment variables for configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Create Group Model
class TrackingDataMail(db.Model):
    __tablename__ = 'tracking_data_mail'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    campaign_id = db.Column(db.Integer, nullable=False)
    group_id = db.Column(db.Integer, nullable=False)
    event_open = db.Column(db.Boolean)
    event_click = db.Column(db.Boolean)
    event_phished = db.Column(db.Boolean)
    timestamp_open = db.Column(db.DateTime)
    timestamp_click = db.Column(db.DateTime)
    timestamp_phished = db.Column(db.DateTime)
    admin_id = db.Column(db.String(255), nullable=False)


class TrackingDataSMS (db.Model):
    __tablename__ = 'tracking_data_sms'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    campaign_id = db.Column(db.Integer, nullable=False)
    group_id = db.Column(db.Integer, nullable=False)
    event_click = db.Column(db.Boolean)
    event_phished = db.Column(db.Boolean)
    timestamp_click = db.Column(db.DateTime)
    timestamp_phished = db.Column(db.DateTime)
    admin_id = db.Column(db.String(255), nullable=False)
    end_date = db.Column(db.DateTime)


#Track for clicks
@app.route('/track/click', methods=['GET'])
def track_click():
    data = request.args

    # Validate input data
    if not all(key in data for key in ['tracking_id', 'campaign_id', 'group_id', 'user_id', 'end_date', 'admin_id']):
        return 'Missing input data', 400

    try:
        campaign_id = int(data['campaign_id'])
        group_id = int(data['group_id'])
        user_id = int(data['user_id'])
    except ValueError:
        return 'Invalid input data', 400

    if campaign_id < 0 or group_id < 0 or user_id < 0:
        return 'Invalid input data', 400

    timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    end_date = str(datetime.datetime.strptime(data['end_date'], "%Y-%m-%d %H:%M:%S"))
    admin_id = data['admin_id']

    if timestamp <= end_date:
        with db.engine.connect() as conn:
            result = conn.execute(text("""
            SELECT * FROM tracking_data_mail
            WHERE user_id = :user_id AND campaign_id = :campaign_id AND group_id = :group_id
            """), {"user_id": user_id, "campaign_id": campaign_id, "group_id": group_id}).fetchone()

            if result is None:
                conn.execute(text("""
                INSERT INTO tracking_data_mail (user_id, campaign_id, group_id, event_click, timestamp_click, admin_id)
                VALUES (:user_id, :campaign_id, :group_id, TRUE, :timestamp, :admin_id)
                """), {"user_id": user_id, "campaign_id": campaign_id, "group_id": group_id, "timestamp": timestamp, "admin_id": admin_id})
            else:

                result = conn.execute(text("""
                SELECT * FROM tracking_data_mail
                WHERE user_id = :user_id AND campaign_id = :campaign_id AND group_id = :group_id AND event_click = TRUE
                """), {"user_id": user_id, "campaign_id": campaign_id, "group_id": group_id}).fetchone()

                if result is None:
                    conn.execute(text("""
                    UPDATE tracking_data_mail
                    SET event_click = TRUE, timestamp_click = :timestamp
                    WHERE user_id = :user_id AND campaign_id = :campaign_id AND group_id = :group_id
                    """), {"timestamp": timestamp, "user_id": user_id, "campaign_id": campaign_id, "group_id": group_id})

                else:
                    print("exist!")   

            conn.commit()

    return '', 204


#Track for opens
@app.route('/logo.jpg')
def serve_logo():
    data = request.args

    # Validate input data
    if not all(key in data for key in ['tracking_id', 'campaign_id', 'group_id', 'user_id', 'end_date', 'admin_id']):
        return 'Missing input data', 400

    try:
        campaign_id = int(data['campaign_id'])
        group_id = int(data['group_id'])
        user_id = int(data['user_id'])
    except ValueError:
        return 'Invalid input data', 400

    if campaign_id < 0 or group_id < 0 or user_id < 0:
        return 'Invalid input data', 400

    timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    end_date = str(datetime.datetime.strptime(data['end_date'], "%Y-%m-%d %H:%M:%S"))
    admin_id = data['admin_id']

    if timestamp <= end_date:
        with db.engine.connect() as conn:
            result = conn.execute(text("""
            SELECT * FROM tracking_data_mail
            WHERE user_id = :user_id AND campaign_id = :campaign_id AND group_id = :group_id
            """), {"user_id": user_id, "campaign_id": campaign_id, "group_id": group_id}).fetchone()

            if result is None:
                conn.execute(text("""
                INSERT INTO tracking_data_mail (user_id, campaign_id, group_id, event_open, timestamp_open, admin_id)
                VALUES (:user_id, :campaign_id, :group_id, TRUE, :timestamp, :admin_id)
                """), {"user_id": user_id, "campaign_id": campaign_id, "group_id": group_id, "timestamp": timestamp, "admin_id": admin_id})
            else:
                result = conn.execute(text("""
                SELECT * FROM tracking_data_mail
                WHERE user_id = :user_id AND campaign_id = :campaign_id AND group_id = :group_id AND event_open = TRUE
                """), {"user_id": user_id, "campaign_id": campaign_id, "group_id": group_id}).fetchone()


                if result is None:
                    conn.execute(text("""
                    UPDATE tracking_data_mail
                    SET event_open = TRUE, timestamp_open = :timestamp
                    WHERE user_id = :user_id AND campaign_id = :campaign_id AND group_id = :group_id
                    """), {"timestamp": timestamp, "user_id": user_id, "campaign_id": campaign_id, "group_id": group_id})

                else:
                    print("exist!")

            conn.commit()

    return send_from_directory(app.root_path, 'logo.jpg')


#Get data from DB
@app.route('/get_tracking_data/<campaign_id>', methods=['GET'])
def get_tracking_data(campaign_id):

    campaign_id = str(campaign_id)
    clicked_users = []
    opened_users = []
    phished_users = []
    all_users = []

    with db.engine.connect() as conn:
        result = conn.execute(text("""
        SELECT * FROM tracking_data_mail
        WHERE campaign_id = :campaign_id
        """), {"campaign_id": campaign_id}).fetchall()

        for row in result:
            user = {
                'user_id': row[1],
                'campaign_id': row[2],
                'group_id': row[3],
                'event_click': row[4],
                'event_open': row[5],
                'event_phished': row[6],
                'timestamp_open': row[7],
                'timestamp_click': row[8],
                'timestamp_phished': row[9],
                'admin_id': row[10],
            }

            all_users.append(user)

            if row[4]:
                clicked_users.append(user)
            if row[5]:
                opened_users.append(user)
            if row[6]:
                phished_users.append(user)

    if clicked_users or opened_users or all_users:
        return jsonify({'clicked_users': clicked_users, 'opened_users': opened_users, 'all_users': all_users, 'phished_users': phished_users})
    else:
        return '', 404




@app.route('/send-sms', methods=['POST'])
def send_sms():
    # Receive the JSON data
    data = request.get_json()

    # Extract title and content
    users = data.get('users')

    # Print the received data
    for user in users:
        # Check if user is a dictionary and has the expected keys
        if not isinstance(user, dict) or not all(key in user for key in ['tracking_id', 'user_id', 'group_id', 'campaign_id', 'end_date', 'admin_unique_id', 'msg', 'phone']):
            return jsonify({"error": "Invalid user data"}), 400

    # Print the received data
    for user in users:
        tracking_id = user["tracking_id"]
        user_id = user["user_id"]
        group_id = user["group_id"]
        campaign_id = user["campaign_id"]
        end_date = user["end_date"]
        admin_unique_id = user["admin_unique_id"]
        display_name = user["msg"]["display_name"]
        phone = user["phone"]
        content = user["msg"]["content"]
    
        send(display_name, phone, content)



    # Send a response back to the client
    return jsonify({"message": "Data received successfully"}), 200

@app.route('/store-sms', methods=['GET'])
def store_sms():
    data = request.args

    # Validate input data
    if not all(key in data for key in ['tracking_id', 'campaign_id', 'group_id', 'user_id', 'end_date', 'admin_id']):
        return 'Missing input data', 400

    try:
        campaign_id = int(data['campaign_id'])
        group_id = int(data['group_id'])
        user_id = int(data['user_id'])
    except ValueError:
        return 'Invalid input data', 400

    if campaign_id < 0 or group_id < 0 or user_id < 0:
        return 'Invalid input data', 400

    try:
        end_date = datetime.datetime.strptime(data['end_date'], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return 'Invalid date format', 400
    
    admin_id = data['admin_id']

    with db.engine.connect() as conn:
        result = conn.execute(text("""
        SELECT * FROM tracking_data_sms
        WHERE user_id = :user_id AND campaign_id = :campaign_id AND group_id = :group_id
        """), {"user_id": user_id, "campaign_id": campaign_id, "group_id": group_id}).fetchone()

        if result is not None:
            return 'Data already exists', 409

        result = conn.execute(text("""
        INSERT INTO tracking_data_sms (user_id, campaign_id, group_id, admin_id, end_date)
        VALUES (:user_id, :campaign_id, :group_id, :admin_id, :end_date)
        RETURNING id
        """), {"user_id": user_id, "campaign_id": campaign_id, "group_id": group_id, "admin_id": admin_id, "end_date": end_date})

        new_id = result.fetchone()[0]
        conn.commit()

    return {'id': new_id}, 200




@app.route('/<int:id>', methods=['GET'])
def get_data(id):
    timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    with db.engine.connect() as conn:
        result = conn.execute(text("""
        SELECT * FROM tracking_data_sms WHERE id = :id
        """), {"id": id}).fetchone()

        if result is None:
            return 'Data not found', 404

        conn.execute(text("""
        UPDATE tracking_data_sms
        SET event_click = TRUE, timestamp_click = :timestamp
        WHERE id = :id
        """), {"timestamp": timestamp, "id": id})

        conn.commit()
    return 200


@app.route('/get_tracking_data_sms/<campaign_id>', methods=['GET'])
def get_tracking_data_sms(campaign_id):

    campaign_id = str(campaign_id)
    clicked_users = []
    phished_users = []
    all_users = []

    with db.engine.connect() as conn:
        result = conn.execute(text("""
        SELECT * FROM tracking_data_sms
        WHERE campaign_id = :campaign_id
        """), {"campaign_id": campaign_id}).fetchall()

        for row in result:
            user = {
                'user_id': row[0],
                'campaign_id': row[1],
                'group_id': row[2],
                'event_click': row[3],
                'event_phished': row[4],
                'timestamp_click': row[5],
                'timestamp_phished': row[6],
                'admin_id': row[7],
            }

            all_users.append(user)

            if row[3]:
                clicked_users.append(user)
            if row[4]:
                phished_users.append(user)

    if clicked_users or phished_users or all_users:
        return jsonify({'clicked_users': clicked_users, 'phished_users': phished_users, 'all_users': all_users})
    else:
        return '', 404




if __name__ == '__main__':
    app.run(debug=True, port=5050)
