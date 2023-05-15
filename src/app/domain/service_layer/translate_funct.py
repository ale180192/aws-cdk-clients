import json
from google.cloud import pubsub_v1
from webhook_validator import WebhookValidator

class SignatureError(Exception):
    pass

class Handler:
    def __init__(self, webhook_public_key):
        self.validator = WebhookValidator(webhook_public_key)
        self.pubsub = pubsub_v1.PublisherClient()

    def handle_webhook(self, data, signature):
        attributes = {}
        if not self.validator.validate_signature(data, signature):
            attributes["SigError"] = "true"
            attributes["SigValue"] = signature
        json_data = json.loads(data)
        if json_data["action"] == "message_create":
            conversation_id = json_data.get("data", {}).get("message", {}).get("conversation_id")
            self.pubsub.publish(
                topic="freshdesk-webhook",
                data=data,
                ordering_key=conversation_id,
                attributes=attributes,
            )
        else:
            conversation_id = (
                json_data.get("data", {}).get("reopen", {}).get("conversation", {}).get("conversation_id") or
                json_data.get("data", {}).get("assignment", {}).get("conversation", {}).get("conversation_id") or
                json_data.get("data", {}).get("resolve", {}).get("conversation", {}).get("conversation_id")
            )
            self.pubsub.publish(
                topic="freshdesk-webhook-events",
                data=data,
                ordering_key=conversation_id,
                attributes=attributes,
            )
        return { "result": "success" }

handler = Handler(b"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqdKxZxkWfisXRDYk0vv++c1qMzulB36DWdiu2XqFSZVSMzPD9SPwhHBzyD8BdH/icJc321FKawaBbJJRtaPSPbjR+ZaeBKdZUwXlaIZo0kMCmWcY8pcuWeyqxADrf+zfon2Wcj4NajsDCjl25n6vU8G1H1BwRDW69sOOqvKsKrtxzbH6U7BBpXMLcELm6E0n1y2b/Woh2dXb+i3flM3rLLePvQkpgomPx1k0U5ZwDF0f1fydBD7zPy3rQrRJSufNXvf2BSs/KTEnzHaM2sYsx8CjiS/MekQ+roW3cyLdPXeE13Xlo9Z6UugploJnXdv7Nl7HVmY+U0/ehXu0ulRLSQIDAQAB\n-----END PUBLIC KEY-----")

app = Flask(__name__)

@app.route("/", methods=["POST"])
def handle_webhook():
    signature = request.headers.get("X-Freshchat-Signature")
    data = request.get_data()
    if signature is None or data is None:
        return Response(
            json.dumps({"error": "Missing required body or header."}),
            status=400,
            mimetype="application/json",
        )
    else:
        try:
            result = handler.handle_webhook(data, signature)
            return Response(
                json.dumps(result),
                status=200,
                mimetype="application/json",
            )
        except SignatureError:
            return Response(
                json.dumps({"error": "Signature mismatch
