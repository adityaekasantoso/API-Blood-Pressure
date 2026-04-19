import serial
import pyautogui
import time


PORT = "COM5"
BAUDRATE = 9600


def start_rfid_keyboard():
    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)
        print(f"[RFID] Connected {PORT} @ {BAUDRATE}")

        time.sleep(2)  # kasih waktu pindah ke app (notepad / browser)

        while True:
            if ser.in_waiting:
                data = ser.readline().decode(errors="ignore").strip()

                if data:
                    print("[RFID]", data)

                    # 🔥 AUTO TYPE KEYBOARD
                    pyautogui.typewrite(data)
                    pyautogui.press("enter")

    except Exception as e:
        print("[RFID ERROR]", e)


if __name__ == "__main__":
    start_rfid_keyboard()