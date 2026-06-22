import cv2
import requests
import numpy as np
from pyzbar.pyzbar import decode
import time

# =========================
# ESP32-CAM IMAGE URL
# =========================

CAM_URL = "http://192.168.0.179/capture"

# =========================
# FLASK BACKEND
# =========================

BACKEND_URL = (
    "https://smart-parking-backend-4dum.onrender.com/validate_qr"
)

# =========================
# ESP32 DEVKIT GATE API
# =========================

ENTRY_GATE_URL = "http://192.168.0.198/openEntry"

# =========================
# SCAN CONTROL
# =========================

last_scanned = ""
last_scan_time = 0

print("\nSMART QR SYSTEM STARTED")

while True:

    try:

        # =====================
        # GET CAMERA FRAME
        # =====================

        response = requests.get(
            CAM_URL,
            timeout=5
        )

        img_array = np.array(
            bytearray(response.content),
            dtype=np.uint8
        )

        frame = cv2.imdecode(
            img_array,
            cv2.IMREAD_COLOR
        )

        if frame is None:

            print("Failed to decode image")
            continue

        # =====================
        # QR DETECTION
        # =====================

        qr_codes = decode(frame)

        for qr in qr_codes:

            booking_id = qr.data.decode("utf-8")

            current_time = time.time()

            # =====================
            # PREVENT RAPID REPEAT
            # =====================

            if (
                booking_id == last_scanned
                and current_time - last_scan_time < 5
            ):
                continue

            last_scanned = booking_id
            last_scan_time = current_time

            print("\nQR DETECTED:")
            print(booking_id)

            # =====================
            # VALIDATE WITH BACKEND
            # =====================

            try:

                backend_response = requests.post(
                    BACKEND_URL,
                    json={
                        "booking_id": booking_id
                    },
                    timeout=10
                )

                data = backend_response.json()

                print("\nBACKEND RESPONSE:")
                print(data)

                # =====================
                # VALID QR
                # =====================

                if data.get("success"):

                    print("\nVALID QR")
                    print("OPENING ENTRY GATE")

                    print("\nSending gate request...")

                    try:

                        gate_response = requests.get(
                            ENTRY_GATE_URL,
                            timeout=5
                        )

                        print(
                            "Status Code:",
                            gate_response.status_code
                        )

                        print(
                            "Response:",
                            gate_response.text
                        )

                    except Exception as gate_error:

                        print(
                            "Gate Error:",
                            gate_error
                        )

                else:

                    print("\nINVALID QR")

                    print(
                        data.get(
                            "message",
                            "Unknown Error"
                        )
                    )

            except Exception as backend_error:

                print(
                    "\nBACKEND ERROR:",
                    backend_error
                )

            # =====================
            # DRAW QR BOX
            # =====================

            points = qr.polygon

            if len(points) == 4:

                for i in range(4):

                    pt1 = (
                        points[i].x,
                        points[i].y
                    )

                    pt2 = (
                        points[(i + 1) % 4].x,
                        points[(i + 1) % 4].y
                    )

                    cv2.line(
                        frame,
                        pt1,
                        pt2,
                        (0, 255, 0),
                        3
                    )

            x = qr.rect.left
            y = qr.rect.top

            cv2.putText(
                frame,
                booking_id,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

        # =====================
        # SHOW CAMERA
        # =====================

        cv2.imshow(
            "SMART PARKING QR SYSTEM",
            frame
        )

        # ESC KEY TO EXIT

        if cv2.waitKey(1) == 27:
            break

    except Exception as e:

        print("\nERROR:", e)

cv2.destroyAllWindows()