from flask import Blueprint

admin_api = Blueprint("admin_api", __name__)


@admin_api.route("/")
def main():
    return "Hello admin!"
