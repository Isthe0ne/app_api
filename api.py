from flask import Flask, request, jsonify, send_from_directory, redirect
import datetime
import json

app = Flask(__name__)

data_file = 'tracking_data.json'

tracking_data = {}
mail_campaign_open = "mail_campaign_open"
mail_campaign_click = "mail_campaign_click"


@app.route('/track/open', methods=['GET'])
def track_open():
    is_user_exist = False

    data = request.args
    tracking_id = data['tracking_id']
    campaign_id = data['campaign_id']
    group_id = data['group_id']
    user_id = data['user_id']
    end_date = str(data['end_date'])
    admin_id = data['admin_id']
    timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    event = 'open'
    if timestamp <= end_date:
        try:
            with open(data_file) as sd:
                stored_data = json.load(sd)

            if len(stored_data) != 0:

                if mail_campaign_open not in stored_data:
                        stored_data[mail_campaign_open] = {'data': []}
                else:
                    for i in stored_data[mail_campaign_open]['data']:
                        # Check if the user exist
                        if i['user_id'] == user_id :
                            is_user_exist = True
                            print("user exist")
                            break

                # Closing file
                sd.close()

                if not is_user_exist:
                    print("user not exist")
                    

                    stored_data[mail_campaign_open]['data'].append({'user_id': user_id, 'campaign_id': campaign_id, 'group_id': group_id, 'event': event, 'timestamp': timestamp, 'admin_id': admin_id})

            elif mail_campaign_open not in stored_data:
                print("Key not exist")
                stored_data[mail_campaign_open] = {'data': []}
                stored_data[mail_campaign_open]['data'].append({'user_id': user_id, 'campaign_id': campaign_id, 'group_id': group_id, 'event': event, 'timestamp': timestamp, 'admin_id': admin_id})

            with open(data_file, 'w') as f:
                json.dump(stored_data, f)


        except json.JSONDecodeError:
            if mail_campaign_open not in tracking_data:
                tracking_data[mail_campaign_open] = {'data': []}
                tracking_data[mail_campaign_open]['data'].append({'user_id': user_id, 'campaign_id': campaign_id, 'group_id': group_id, 'event': event, 'timestamp': timestamp, 'admin_id': admin_id})

            with open(data_file, 'w') as f:
                json.dump(tracking_data, f)

    return redirect(url_for('serve_logo'))


@app.route('/track/click', methods=['GET'])
def track_click():
    is_user_exist = False

    data = request.args
    tracking_id = data['tracking_id']
    campaign_id = data['campaign_id']
    group_id = data['group_id']
    user_id = data['user_id']
    end_date = str(data['end_date'])
    admin_id = data['admin_id']
    timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    event = 'click'

    if timestamp <= end_date:
        try:
            with open(data_file) as sd:
                stored_data = json.load(sd)

            if len(stored_data) != 0:

                if mail_campaign_click not in stored_data:
                        stored_data[mail_campaign_click] = {'data': []}
                else:
                    for i in stored_data[mail_campaign_click]['data']:
                        # Check if the user exist
                        if i['user_id'] == user_id :
                            is_user_exist = True
                            print("user exist")
                            break

                # Closing file
                sd.close()

                if not is_user_exist:
                    print("user not exist")
                    

                    stored_data[mail_campaign_click]['data'].append({'user_id': user_id, 'campaign_id': campaign_id, 'group_id': group_id, 'event': event, 'timestamp': timestamp, 'admin_id': admin_id})

            elif mail_campaign_click not in stored_data:
                print("Key not exist")
                stored_data[mail_campaign_click] = {'data': []}
                stored_data[mail_campaign_click]['data'].append({'user_id': user_id, 'campaign_id': campaign_id, 'group_id': group_id, 'event': event, 'timestamp': timestamp, 'admin_id': admin_id})

            with open(data_file, 'w') as f:
                json.dump(stored_data, f)


        except json.JSONDecodeError:
            if mail_campaign_click not in tracking_data:
                tracking_data[mail_campaign_click] = {'data': []}
                tracking_data[mail_campaign_click]['data'].append({'user_id': user_id, 'campaign_id': campaign_id, 'group_id': group_id, 'event': event, 'timestamp': timestamp, 'admin_id': admin_id})

            with open(data_file, 'w') as f:
                json.dump(tracking_data, f)

    return '', 204


@app.route('/get_tracking_data/<campaign_id>', methods=['GET', 'POST'])
def get_tracking_data(campaign_id):
    clicked_users = []
    opened_users = []

    campaign_id = str(campaign_id)

    with open(data_file) as td:
        stored_data = json.load(td)



    for campaign in stored_data:
        if campaign == 'mail_campaign_click':
            for user in stored_data['mail_campaign_click']['data']:
                if user['campaign_id'] == campaign_id:
                    clicked_users.append(user)

        elif campaign == 'mail_campaign_open':
            for user in stored_data['mail_campaign_open']['data']:
                if user['campaign_id'] == campaign_id:
                    opened_users.append(user)

    td.close()

    if len(clicked_users) != 0 or len(opened_users) != 0:
        return jsonify({'clicked_users': clicked_users},{'opened_users': opened_users})
    else:
        return '', 404 


@app.route('/logo.jpg')
def serve_logo():

    is_user_exist = False

    data = request.args
    tracking_id = data['tracking_id']
    campaign_id = data['campaign_id']
    group_id = data['group_id']
    user_id = data['user_id']
    end_date = str(data['end_date'])
    admin_id = data['admin_id']
    timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    event = 'open'
    if timestamp <= end_date:
        try:
            with open(data_file) as sd:
                stored_data = json.load(sd)

            if len(stored_data) != 0:

                if mail_campaign_open not in stored_data:
                        stored_data[mail_campaign_open] = {'data': []}
                else:
                    for i in stored_data[mail_campaign_open]['data']:
                        # Check if the user exist
                        if i['user_id'] == user_id :
                            is_user_exist = True
                            print("user exist")
                            break

                # Closing file
                sd.close()

                if not is_user_exist:
                    print("user not exist")
                    

                    stored_data[mail_campaign_open]['data'].append({'user_id': user_id, 'campaign_id': campaign_id, 'group_id': group_id, 'event': event, 'timestamp': timestamp, 'admin_id': admin_id})

            elif mail_campaign_open not in stored_data:
                print("Key not exist")
                stored_data[mail_campaign_open] = {'data': []}
                stored_data[mail_campaign_open]['data'].append({'user_id': user_id, 'campaign_id': campaign_id, 'group_id': group_id, 'event': event, 'timestamp': timestamp, 'admin_id': admin_id})

            with open(data_file, 'w') as f:
                json.dump(stored_data, f)


        except json.JSONDecodeError:
            if mail_campaign_open not in tracking_data:
                tracking_data[mail_campaign_open] = {'data': []}
                tracking_data[mail_campaign_open]['data'].append({'user_id': user_id, 'campaign_id': campaign_id, 'group_id': group_id, 'event': event, 'timestamp': timestamp, 'admin_id': admin_id})

            with open(data_file, 'w') as f:
                json.dump(tracking_data, f)

    return send_from_directory(app.root_path, 'logo.jpg')

if __name__ == '__main__':
   app.run(debug=True, port=5050)