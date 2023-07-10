from flask import Flask

app = Flask(__name__)

@app.route('/', methods=['POST'])
def trigger_pipeline():
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
        
    return 'OK'

def get_github_token():
    client = secretmanager.SecretManagerServiceClient()
    response = client.access_secret_version(request={"name": "projects/352350778257/secrets/GITHUB_API/versions/1"})
    return response.payload.data.decode("UTF-8")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
