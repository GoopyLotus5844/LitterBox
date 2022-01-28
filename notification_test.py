import firebase_admin
from firebase_admin import messaging
from firebase_admin import credentials

cred = credentials.Certificate("litterbox-c0253-firebase-adminsdk-tijh3-bd711f51af.json")
firebase_admin.initialize_app(cred)

def send_to_token():
    # [START send_to_token]
    # This registration token comes from the client FCM SDKs.
    registration_token = 'dMYYNsbiTTKHyu5-LHXIPP:APA91bF99aXhWSlJKe8PFGKI2HhcMKENRMTIDZWoNLsX3OVV64gDZ-qQy9eFWNMDx0jolv4RFJklwT6ozxinq2EEvg8z3qaKRqxm_TMFOmnGWJNbCjeOWv_zTsJnAluKXU5xnQSlBXWz'

    # See documentation on defining a message payload.
    message = messaging.Message(
        notification=messaging.Notification(
            title='first from python',
            body='this was sent from python. cool.',
        ),
        token=registration_token
    )

    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)

send_to_token()