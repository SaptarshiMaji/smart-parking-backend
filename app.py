from config import DATABASE_URI

print("\nDATABASE URI:")
print(DATABASE_URI)
print()

from flask import Flask, request, jsonify
from flask_cors import CORS

from datetime import datetime
import uuid

from database import db
from config import DATABASE_URI

from models import (
    User,
    Booking,
    ParkingSlot
)

app = Flask(__name__)

CORS(app)

# =========================
# DATABASE CONFIG
# =========================

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# =========================
# CREATE TABLES
# =========================

with app.app_context():

    db.create_all()

# =========================
# AUTO RELEASE EXPIRED SLOTS
# =========================

def auto_release_slots():

    bookings = Booking.query.filter_by(

        status="active"

    ).all()

    current_time = datetime.now()

    for booking in bookings:

        try:

            exit_datetime = datetime.strptime(

                f"{booking.booking_date} {booking.exit_time}",

                "%d/%m/%Y %H:%M"
            )

            if current_time >= exit_datetime:

                slot = ParkingSlot.query.filter_by(

                    slot_number=booking.slot_number

                ).first()

                if slot:

                    slot.status = "available"

                booking.status = "completed"

        except Exception as e:

            print("Auto release error:", e)

    db.session.commit()

# =========================
# HOME ROUTE
# =========================

@app.route("/")

def home():

    return jsonify({

        "message":
            "Smart Parking Backend Running"
    })

# =========================
# REGISTER API
# =========================

@app.route("/register", methods=["POST"])

def register():

    data = request.json

    existing_email = User.query.filter_by(

        email=data.get("email")

    ).first()

    if existing_email:

        return jsonify({

            "success": False,

            "message":
                "Email already exists"
        })

    existing_phone = User.query.filter_by(

        phone=data.get("phone")

    ).first()

    if existing_phone:

        return jsonify({

            "success": False,

            "message":
                "Phone already exists"
        })

    new_user = User(

        uuid=str(uuid.uuid4()),

        name=data.get("name"),

        email=data.get("email"),

        phone=data.get("phone"),

        password=data.get("password")
    )

    db.session.add(new_user)

    db.session.commit()

    return jsonify({

        "success": True,

        "message":
            "Registration Successful"
    })

# =========================
# LOGIN API
# =========================

@app.route("/login", methods=["POST"])

def login():

    data = request.json

    user = User.query.filter_by(

        email=data.get("email"),

        password=data.get("password")

    ).first()

    if user:

        return jsonify({

            "success": True,

            "message":
                "Login Successful",

            "user": {

                "id": user.id,

                "name": user.name,

                "email": user.email,

                "phone": user.phone
            }
        })

    return jsonify({

        "success": False,

        "message":
            "Invalid Email or Password"
    })

# =========================
# FORGOT PASSWORD
# =========================

@app.route(
    "/forgot_password",
    methods=["POST"]
)
def forgot_password():

    data = request.json

    email = data.get(
        "email"
    )

    new_password = data.get(
        "new_password"
    )

    user = User.query.filter_by(
        email=email
    ).first()

    if not user:

        return jsonify({

            "success": False,

            "message":
                "Email not registered"
        })

    user.password = new_password

    db.session.commit()

    return jsonify({

        "success": True,

        "message":
            "Password updated successfully"
    })

# =========================
# GET ALL PARKING SLOTS
# =========================

@app.route("/parking_slots", methods=["GET"])

def get_parking_slots():

    auto_release_slots()

    slots = ParkingSlot.query.all()

    slot_list = []

    for slot in slots:

        slot_list.append({

            "slot_number":
                slot.slot_number,

            "parking_name":
                slot.parking_name,

            "status":
                slot.status
        })

    return jsonify({

        "success": True,

        "slots": slot_list
    })

# =========================
# GET SLOTS BY PARKING
# =========================

@app.route(
    "/parking_slots/<parking_name>",
    methods=["GET"]
)
def get_slots_by_parking(
    parking_name
):

    auto_release_slots()

    slots = ParkingSlot.query.filter_by(

        parking_name=parking_name

    ).all()

    slot_list = []

    for slot in slots:

        slot_list.append({

            "slot_number":
                slot.slot_number,

            "status":
                slot.status
        })

    return jsonify({

        "success": True,

        "slots": slot_list
    })

# =========================
# CREATE INITIAL SLOTS
# =========================

@app.route("/create_slots")

def create_slots():

    ParkingSlot.query.delete()

    parkings = [

        "B-Zone Smart Parking",

        "Junction Mall Parking",

        "Benachity Parking Hub"
    ]

    for parking in parkings:

        for i in range(1, 9):

            db.session.add(

                ParkingSlot(

                    slot_number=f"S{i}",

                    parking_name=parking,

                    status="available"
                )
            )

    db.session.commit()

    return jsonify({

        "success": True,

        "message":
            "Slots Created Successfully"
    })

# =========================
# DEBUG SLOTS
# =========================

@app.route("/debug_slots")

def debug_slots():

    slots = ParkingSlot.query.all()

    data = []

    for slot in slots:

        data.append({

            "slot":
                slot.slot_number,

            "parking":
                slot.parking_name,

            "status":
                slot.status
        })

    return jsonify(data)
# =========================
# CREATE BOOKING
# =========================

@app.route("/parking_summary", methods=["GET"])
def parking_summary():

    result = []

    parking_names = db.session.query(
        ParkingSlot.parking_name
    ).distinct().all()

    for (name,) in parking_names:

        total = ParkingSlot.query.filter_by(
            parking_name=name
        ).count()

        available = ParkingSlot.query.filter_by(
            parking_name=name,
            status="available"
        ).count()

        result.append({

            "parking_name": name,

            "available": available,

            "total": total
        })

    return jsonify({
        "success": True,
        "data": result
    })


@app.route("/create_booking", methods=["POST"])

def create_booking():

    auto_release_slots()

    data = request.json

    user_email = data.get("user_email")

    active_booking = Booking.query.filter(

        Booking.user_email == user_email,

        Booking.status == "active"

    ).first()

    if active_booking:

        return jsonify({

            "success": False,

            "message":
                "You already have an active booking"
        }), 400

    slot = ParkingSlot.query.filter_by(

        slot_number=data.get("slot"),
        parking_name=data.get("parking_name")

    ).first()

    if not slot:

        return jsonify({

            "success": False,

            "message":
                "Invalid slot"
        }), 400

    if slot.status == "occupied":

        return jsonify({

            "success": False,

            "message":
                "Slot already occupied"
        }), 400

    booking_id = \
        f"BOOK-{uuid.uuid4().hex[:8].upper()}"

    slot.status = "occupied"

    new_booking = Booking(

        booking_uuid=booking_id,

        user_email=user_email,

        parking_name=data.get("parking_name"),

        slot_number=data.get("slot"),

        vehicle_number=data.get("vehicle_number"),

        booking_date=data.get("booking_date"),

        entry_time=data.get("entry_time"),

        exit_time=data.get("exit_time"),

        amount=data.get("amount"),

        qr_data=booking_id,

        status="active"
    )

    db.session.add(new_booking)

    db.session.commit()

    return jsonify({

        "success": True,

        "booking_id": booking_id,

        "message":
            "Booking Created Successfully"
    })

# =========================
# GET BOOKINGS
# =========================

@app.route("/bookings/<email>", methods=["GET"])
def get_bookings(email):

    auto_release_slots()

    bookings = Booking.query.filter_by(
        user_email=email
    ).all()

    status_priority = {
        "active": 0,
        "cancelled": 1,
        "completed": 2
    }

    bookings.sort(
        key=lambda booking: (
            status_priority.get(
                booking.status,
                99
            ),
            -booking.id
        )
    )

    booking_list = []

    for booking in bookings:

        booking_list.append({

            "booking_id":
                booking.booking_uuid,

            "parking_name":
                booking.parking_name,

            "slot":
                booking.slot_number,

            "vehicle_number":
                booking.vehicle_number,

            "booking_date":
                booking.booking_date,

            "entry_time":
                booking.entry_time,

            "exit_time":
                booking.exit_time,

            "amount":
                booking.amount,

            "status":
                booking.status
        })

    return jsonify({

        "success": True,

        "bookings": booking_list
    })
# =========================
# GET ACTIVE BOOKING
# =========================

@app.route("/active_booking/<email>")
def get_active_booking(email):

    booking = Booking.query.filter_by(
        user_email=email,
        status="active"
    ).order_by(
        Booking.id.desc()
    ).first()

    if not booking:

        return jsonify({

            "success": False,

            "message": "No active booking"
        })

    return jsonify({

        "success": True,

        "booking": {

            "booking_id":
                booking.booking_uuid,

            "parking_name":
                booking.parking_name,

            "slot":
                booking.slot_number,

            "vehicle_number":
                booking.vehicle_number,

            "booking_date":
                booking.booking_date,

            "entry_time":
                booking.entry_time,

            "exit_time":
                booking.exit_time
        }
    })

# =========================
# cancel BOOKING
# =========================

@app.route("/cancel_booking", methods=["POST"])
def cancel_booking():

    try:

        data = request.get_json()

        booking_id = data.get("booking_id")

        user_email = data.get("user_email")

        booking = Booking.query.filter_by(

            booking_uuid=booking_id,
            user_email=user_email

        ).first()

        if not booking:

            return jsonify({

                "success": False,

                "message":
                    "Booking not found or unauthorized"

            }), 404

        if booking.status != "active":

            return jsonify({

                "success": False,

                "message":
                    "Only active bookings can be cancelled"

            }), 400

        slot = ParkingSlot.query.filter_by(

            slot_number=booking.slot_number,
            parking_name=booking.parking_name

        ).first()

        if slot:

            slot.status = "available"

        booking.status = "cancelled"

        db.session.commit()

        return jsonify({

            "success": True,

            "message":
                "Booking Cancelled Successfully"

        })

    except Exception as e:

        print("Cancel Booking Error:", e)

        return jsonify({

            "success": False,

            "message":
                str(e)

        }), 500
# =========================
# VALIDATE QR
# =========================

@app.route("/validate_qr", methods=["POST"])

def validate_qr():

    data = request.json

    booking_id = data.get("booking_id")

    booking = Booking.query.filter_by(

        booking_uuid=booking_id

    ).first()

    if not booking:

        return jsonify({

            "success": False,

            "message":
                "Invalid Booking ID"
        })

    if booking.status != "active":

        return jsonify({

            "success": False,

            "message":
                "Booking already used"
        })

    booking.status = "completed"
    slot = ParkingSlot.query.filter_by(
        slot_number=booking.slot_number,
        parking_name=booking.parking_name
    ).first()

    if slot:
        slot.status = "available"
    db.session.commit()

    return jsonify({

        "success": True,

        "message":
            "Valid QR",

        "booking": {

            "slot":
                booking.slot_number,

            "vehicle":
                booking.vehicle_number
        }
    })

# =========================
# GET PROFILE
# =========================

@app.route("/profile/<email>", methods=["GET"])

def get_profile(email):

    user = User.query.filter_by(

        email=email

    ).first()

    if not user:

        return jsonify({

            "success": False,

            "message":
                "User not found"
        })

    bookings = Booking.query.filter_by(

        user_email=email

    ).all()

    total_bookings = len(bookings)

    active_bookings = len([

        b for b in bookings

        if b.status == "active"
    ])

    total_payments = sum([

        b.amount or 0

        for b in bookings
    ])

    booking_history = []

    sorted_bookings = sorted(

        bookings,

        key=lambda x: x.id,

        reverse=True
    )

    for booking in sorted_bookings:

        booking_history.append({

            "parking_name":
                booking.parking_name,

            "slot":
                booking.slot_number,

            "date":
                booking.booking_date,

            "amount":
                booking.amount,

            "status":
                booking.status
        })

    payment_history = []

    for booking in sorted_bookings:

        payment_history.append({

            "amount":
                booking.amount,

            "date":
                booking.booking_date,

            "method":
                "UPI"
        })

    return jsonify({

        "success": True,

        "profile": {

            "name":
                user.name,

            "email":
                user.email,

            "phone":
                user.phone,

            "location":
                "Durgapur, West Bengal",

            "total_bookings":
                total_bookings,

            "active_bookings":
                active_bookings,

            "total_payments":
                total_payments,

            "booking_history":
                booking_history,

            "payment_history":
                payment_history
        }
    })

# =========================
# UPDATE PROFILE
# =========================

@app.route("/update_profile", methods=["POST"])

def update_profile():

    data = request.json

    email = data.get("email")

    user = User.query.filter_by(

        email=email

    ).first()

    if not user:

        return jsonify({

            "success": False,

            "message":
                "User not found"
        })

    user.name = data.get(

        "name",

        user.name
    )

    user.phone = data.get(

        "phone",

        user.phone
    )

    db.session.commit()

    return jsonify({

        "success": True,

        "message":
            "Profile Updated Successfully"
    })

# =========================
# RESET BOOKINGS
# =========================

@app.route("/reset_bookings", methods=["POST"])

def reset_bookings():

    Booking.query.delete()

    slots = ParkingSlot.query.all()

    for slot in slots:

        slot.status = "available"

    db.session.commit()

    return jsonify({

        "success": True,

        "message":
            "All Bookings Reset"
    })

# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True
    )