import base64
import functions_framework
from google.cloud import secretmanager_v1beta1 as secretmanager

def get_github_token():
    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version(request={"name": "projects/352350778257/secrets/GITHUB_API/versions/1"})
    return response.payload.data.decode("UTF-8")

@functions_framework.cloud_event
def trigger_pipeline(cloud_event):
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

    # Декодувати дані повідомлення з Pub/Sub
    data = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
    print("Received Pub/Sub message:", data)

    # Викликати функцію trigger_pipeline для обробки повідомлення
    trigger_pipeline(cloud_event)

    return 'OK'
