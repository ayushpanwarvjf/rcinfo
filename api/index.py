from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure JSON encoding to properly display emojis
app.config['JSON_AS_ASCII'] = False

# Define the copyright string
COPYRIGHT_STRING = "@never_delete this source maker"

# Define the desired order of keys in the output
DESIRED_ORDER = [
    "Owner Name", "Father's Name", "Owner Serial No", "Model Name", "Maker Model",
    "Vehicle Class", "Fuel Type", "Fuel Norms", "Registration Date", "Insurance Company",
    "Insurance No", "Insurance Expiry", "Insurance Upto", "Fitness Upto", "Tax Upto",
    "PUC No", "PUC Upto", "Financier Name", "Registered RTO", "Address", "City Name", "Phone"
]

# ------------------- #
# VEHICLE INFO FETCHER#
# ------------------- #
def get_vehicle_details(rc_number: str) -> dict:
    rc = rc_number.strip().upper()
    url = f"https://vahanx.in/rc-search/{rc}"

    headers = {
        "Host": "vahanx.in",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {e}"}
    except Exception as e:
        return {"error": str(e)}

    def get_value(label):
        try:
            div = soup.find("span", string=label).find_parent("div")
            return div.find("p").get_text(strip=True)
        except AttributeError:
            return None

    data = {
        "Owner Name": get_value("Owner Name"),
        "Father's Name": get_value("Father's Name"),
        "Owner Serial No": get_value("Owner Serial No"),
        "Model Name": get_value("Model Name"),
        "Maker Model": get_value("Maker Model"),
        "Vehicle Class": get_value("Vehicle Class"),
        "Fuel Type": get_value("Fuel Type"),
        "Fuel Norms": get_value("Fuel Norms"),
        "Registration Date": get_value("Registration Date"),
        "Insurance Company": get_value("Insurance Company"),
        "Insurance No": get_value("Insurance No"),
        "Insurance Expiry": get_value("Insurance Expiry"),
        "Insurance Upto": get_value("Insurance Upto"),
        "Fitness Upto": get_value("Fitness Upto"),
        "Tax Upto": get_value("Tax Upto"),
        "PUC No": get_value("PUC No"),
        "PUC Upto": get_value("PUC Upto"),
        "Financier Name": get_value("Financier Name"),
        "Registered RTO": get_value("Registered RTO"),
        "Address": get_value("Address"),
        "City Name": get_value("City Name"),
        "Phone": get_value("Phone")
    }
    
    # Remove None values
    data = {k: v for k, v in data.items() if v is not None}
    return data

# ------------------- #
# API ROUTES          #
# ------------------- #

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "🚗 Vehicle Info API by Mohd Kaif is running!",
        "developer": COPYRIGHT_STRING,
        "usage": "GET /vh?rc=YOUR_RC_NUMBER",
        "example": "https://your-domain.vercel.app/vh?rc=MH01AB1234"
    })

@app.route("/vh", methods=["GET"])
def vh():
    """Main endpoint for vehicle lookup"""
    rc_number = request.args.get("rc")
    if not rc_number:
        return jsonify({
            "error": "Please provide ?rc= parameter",
            "copyright": COPYRIGHT_STRING,
            "example": "/vh?rc=MH01AB1234"
        }), 400

    details = get_vehicle_details(rc_number)
    
    # Check if error occurred
    if "error" in details:
        return jsonify({
            "error": details["error"],
            "copyright": COPYRIGHT_STRING
        }), 500
    
    # Create an ordered dictionary with the desired sequence
    ordered_details = OrderedDict()
    
    # Add keys in the desired order
    for key in DESIRED_ORDER:
        if key in details:
            ordered_details[key] = details[key]
    
    # Add copyright at the end
    ordered_details["copyright"] = COPYRIGHT_STRING
    
    return jsonify(ordered_details)

@app.route("/lookup", methods=["GET"])
def lookup_vehicle():
    """Alternative endpoint (backward compatibility)"""
    return vh()

# Vercel requires this
if __name__ == "__main__":
    app.run()
