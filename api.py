from flask import Flask, request, jsonify, send_from_directory, redirect
from sqlalchemy import create_engine, text
import os
import datetime
import json

app = Flask(__name__)

SSL_CA = './etc/secrets/singlestore_bundle.pem'


USERNAME = os.environ.get('USERNAME')
PASSWORD = os.environ.get('PASSWORD')
HOST = os.environ.get('HOST')
PORT = os.environ.get('PORT')
DB = os.environ.get('DB')


# Connect to the SingleStore database
engine = create_engine(f'mysql+mysqldb://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB}?ssl_ca={SSL_CA}')
# Create the connection
conn = engine.connect()


data_file = 'tracking_data.json'

tracking_data = {}
mail_campaign_open = "mail_campaign_open"
mail_campaign_click = "mail_campaign_click"



@app.route('/track/click', methods=['GET'])
def track_click():
    data = request.args

    # Validate input data
    if not all(key in data for key in ['tracking_id', 'campaign_id', 'group_id', 'user_id', 'end_date', 'admin_id']):
        return 'Missing input data', 400

    tracking_id = data['tracking_id']
    campaign_id = data['campaign_id']
    group_id = data['group_id']
    user_id = data['user_id']
    end_date = str(data['end_date'])
    admin_id = data['admin_id']

    # Validate input data types
    try:
        campaign_id = int(campaign_id)
        group_id = int(group_id)
        user_id = int(user_id)
    except ValueError:
        return 'Invalid input data', 400

    # Validate input data ranges
    if campaign_id < 0 or group_id < 0 or user_id < 0:
        return 'Invalid input data', 400

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if timestamp <= end_date:
        # Check if the user already exists in the table
        with engine.connect() as conn:
            result = conn.execute(text("""
            SELECT * FROM tracking_data_mail
            WHERE user_id = :user_id AND campaign_id = :campaign_id AND group_id = :group_id
            """), {"user_id": user_id, "campaign_id": campaign_id, "group_id": group_id}).fetchone()

            if result is None:
                # Insert the data into the table
                conn.execute(text("""
                INSERT INTO tracking_data_mail (user_id, campaign_id, group_id, event_click, timestamp_click, admin_id)
                VALUES (:user_id, :campaign_id, :group_id, TRUE, :timestamp, :admin_id)
                """), {"user_id": user_id, "campaign_id": campaign_id, "group_id": group_id, "timestamp": timestamp, "admin_id": admin_id})
            else:
                # Check if the user clicked event already set to TRUE
                result = conn.execute(text("""
                SELECT * FROM tracking_data_mail
                WHERE user_id = :user_id AND campaign_id = :campaign_id AND group_id = :group_id AND event_click = TRUE
                """), {"user_id": user_id, "campaign_id": campaign_id, "group_id": group_id}).fetchone()

                if result is None:
                    # Update the data in the table
                    conn.execute(text("""
                    UPDATE tracking_data_mail
                    SET event_click = TRUE, timestamp_click = :timestamp
                    WHERE user_id = :user_id AND campaign_id = :campaign_id AND group_id = :group_id
                    """), {"user_id": user_id, "campaign_id": campaign_id, "group_id": group_id, "timestamp": timestamp})
                else:
                    print("exist!")

            conn.commit()

    return '', 204


@app.route('/logo.jpg')
def serve_logo():
    data = request.args

    # Validate input data
    if not all(key in data for key in ['tracking_id', 'campaign_id', 'group_id', 'user_id', 'end_date', 'admin_id']):
        return 'Missing input data', 400

    tracking_id = data['tracking_id']
    campaign_id = data['campaign_id']
    group_id = data['group_id']
    user_id = data['user_id']
    end_date = str(data['end_date'])
    admin_id = data['admin_id']

    # Validate input data types
    try:
        campaign_id = int(campaign_id)
        group_id = int(group_id)
        user_id = int(user_id)
    except ValueError:
        return 'Invalid input data', 400

    # Validate input data ranges
    if campaign_id < 0 or group_id < 0 or user_id < 0:
        return 'Invalid input data', 400

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if timestamp <= end_date:
        # Check if the user already exists in the table
        with engine.connect() as conn:
            result = conn.execute(text("""
            SELECT * FROM tracking_data_mail
            WHERE user_id = :user_id AND campaign_id = :campaign_id AND group_id = :group_id
            """), {"user_id": user_id, "campaign_id": campaign_id, "group_id": group_id}).fetchone()

            if result is None:
                # Insert the data into the table
                conn.execute(text("""
                INSERT INTO tracking_data_mail (user_id, campaign_id, group_id, event_open, timestamp_open, admin_id)
                VALUES (:user_id, :campaign_id, :group_id, TRUE, :timestamp, :admin_id)
                """), {"user_id": user_id, "campaign_id": campaign_id, "group_id": group_id, "timestamp": timestamp, "admin_id": admin_id})
            else:
                # Check if the user opened event already set to TRUE
                result = conn.execute(text("""
                SELECT * FROM tracking_data_mail
                WHERE user_id = :user_id AND campaign_id = :campaign_id AND group_id = :group_id AND event_open = TRUE
                """), {"user_id": user_id, "campaign_id": campaign_id, "group_id": group_id}).fetchone()

                if result is None:
                    # Update the data in the table
                    conn.execute(text("""
                    UPDATE tracking_data_mail
                    SET event_open = TRUE, timestamp_open = :timestamp
                    WHERE user_id = :user_id AND campaign_id = :campaign_id AND group_id = :group_id
                    """), {"user_id": user_id, "campaign_id": campaign_id, "group_id": group_id, "timestamp": timestamp})
                else:
                    print("exist!")

            conn.commit()
    return send_from_directory(app.root_path, 'logo.jpg')


@app.route('/get_tracking_data/<campaign_id>', methods=['GET', 'POST'])
def get_tracking_data(campaign_id):

    clicked_users = []
    opened_users = []
    all_users = []

    campaign_id = str(campaign_id)

    with engine.connect() as conn:
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
            

    if len(clicked_users) != 0 or len(opened_users) != 0 or len(all_users) != 0:
        return jsonify({'clicked_users': clicked_users, 'opened_users': opened_users, 'all_users' : all_users})
    else:
        return '', 404




if __name__ == '__main__':
   app.run(debug=True, port=5050)