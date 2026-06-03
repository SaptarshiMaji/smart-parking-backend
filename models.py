from database import db
from datetime import datetime

# ================= USERS =================

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    uuid = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    phone = db.Column(
        db.String(15),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

# ================= VEHICLES =================

class Vehicle(db.Model):

    __tablename__ = 'vehicles'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    vehicle_number = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    vehicle_type = db.Column(
        db.String(20)
    )

# ================= PARKING SLOTS =================

class ParkingSlot(db.Model):

    __tablename__ = 'parking_slots'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    parking_name = db.Column(
        db.String(200),
        nullable=False
    )

    slot_number = db.Column(
        db.String(20),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default='available'
    )

# ================= BOOKINGS =================

class Booking(db.Model):

    __tablename__ = 'bookings'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    booking_uuid = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    user_email = db.Column(
        db.String(120)
    )

    parking_name = db.Column(
        db.String(200)
    )

    slot_number = db.Column(
        db.String(20)
    )

    vehicle_number = db.Column(
        db.String(20)
    )

    booking_date = db.Column(
        db.String(50)
    )

    entry_time = db.Column(
        db.String(50)
    )

    exit_time = db.Column(
        db.String(50)
    )

    amount = db.Column(
        db.Float
    )

    qr_data = db.Column(
        db.String(200),
        unique=True
    )

    status = db.Column(
        db.String(20),
        default='active'
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

# ================= PARKING LOGS =================

class ParkingLog(db.Model):

    __tablename__ = 'parking_logs'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    booking_id = db.Column(
        db.Integer
    )

    entry_time = db.Column(
        db.DateTime
    )

    exit_time = db.Column(
        db.DateTime
    )

# ================= ADMINS =================

class Admin(db.Model):

    __tablename__ = 'admins'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True
    )

    password = db.Column(
        db.String(200)
    )