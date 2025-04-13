from flask import Flask, request, Request

import gemini_interface

app = Flask(__name__)


def get_code(received_request: Request) -> str:
    data = received_request.get_json()
    if not data or "code" not in data:
        return ""
    return data["code"]

def get_additional_info(received_request: Request) -> str:
    data = received_request.get_json()
    if not data or "additional_info" not in data:
        return ""
    return data["additional_info"]

@app.route("/test")
def test():
    return "hello!"

@app.route("/explain-code", methods=["POST"])
def explain_code():
    code = get_code(received_request=request)
    additional_info = get_additional_info(received_request=request)
    if len(code) == 0:
        return 'Please provide code to explain', 400
    return gemini_interface.handle_code_explanation(code=code, additional_info=additional_info)

