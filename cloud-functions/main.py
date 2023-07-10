import requests
from google.cloud import pubsub_v1
from google.cloud import secretmanager_v1beta1 as secretmanager

def get_github_token():
    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version(request={"name": "projects/352350778257/secrets/GITHUB_API/versions/1"})
    return response.payload.data.decode("UTF-8")

def trigger_pipeline(event, context):
    # Отримати токен GitHub з GCP Secret Manager
    token = get_github_token()

    # Викликати GitHub API для виклику repository_dispatch події
    headers = {
        "Accept": "application/vnd.github.everest-preview+json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "event_type": "token_changed",
        "client_payload": {
            "token": token
        }
    }
    response = requests.post(
        "https://api.github.com/repos/vitalibit/flux-gitops/dispatches",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 204:
        print("Pipeline triggered successfully!")
    else:
        print(f"Failed to trigger pipeline. Status code: {response.status_code}, Message: {response.text}")

def subscribe_to_pubsub_topic():
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path("k8s-k3s-386218", "token-changed-sub")

    def callback(message):
        # Викликати Cloud Function при отриманні повідомлення від Pub/Sub
        trigger_pipeline(None, None)
        message.ack()

    subscriber.subscribe(subscription_path, callback=callback)

subscribe_to_pubsub_topic()
