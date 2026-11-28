import time, random, requests

SERVER_URL = "http://127.0.0.1:5000"
print("=== SIMULATEUR ESP32 ORION-ROVER (Ctrl+C pour arreter) ===")

step = 0
try:
    while True:
        step += 1
        front_dist = round(85.0 - (step % 15) * 5.0, 1)
        left_dist  = round(60.0 + random.uniform(-3, 3), 1)
        right_dist = round(65.0 + random.uniform(-3, 3), 1)
        ir = {"s1": 1, "s2": 1, "s3": 0, "s4": 1, "s5": 1}

        payload = {
            "ultrasonic": {"front": front_dist, "left": left_dist, "right": right_dist},
            "infrared": ir
        }
        requests.post(f"{SERVER_URL}/api/sensors", json=payload, timeout=2)
        r_nav = requests.post(f"{SERVER_URL}/api/navigation/decision", json=payload, timeout=2).json()
        dec = r_nav.get("decision", {})
        print(f"[Tick {step:02d}] Avant={front_dist:4.1f}cm -> {dec.get('decision')} (Vitesse={dec.get('speed')})")
        time.sleep(1.0)
except KeyboardInterrupt:
    print("\nSimulation arretee.")
