import json
import random

# 전남테크노파크 GPS 좌표
latitude = 34.9481
longitude = 127.4866

# 등급표 기준 중심값 (이미지 기준)
base_config = {
    "Device1": {  # Excellent 중간
        "RSSI": -33,    # (-65~0) 중간
        "RSRP": -40,    # (-80~0) 중간
        "SINR": 60,     # (20~100) 중간
        "RSRQ": -5      # (-10~0) 중간
    },
    "Device2": {  # Good 하단
        "RSSI": -74,    # (-75~-65) 하단
        "RSRP": -89,    # (-90~-80) 하단
        "SINR": 13.5,   # (13~20) 하단
        "RSRQ": -14.9   # (-15~-10) 하단
    },
    "Device3": {  # Fair-Good 임계점
        "RSSI": -75,    # (-85~-75) 임계점
        "RSRP": -90,    # (-110~-90) 임계점
        "SINR": 13,     # (0~13) 임계점
        "RSRQ": -15     # (-20~-15) 임계점
    }
}

fluctuation = 2.5  # ±2.5 출렁임
inversion_prob = 0.12  # 12% 확률로 역전

def generate_signal_data(base):
    return {
        "RSSI": round(base["RSSI"] + random.uniform(-fluctuation, fluctuation), 2),
        "RSRP": round(base["RSRP"] + random.uniform(-fluctuation, fluctuation), 2),
        "SINR": round(base["SINR"] + random.uniform(-fluctuation, fluctuation), 2),
        "RSRQ": round(base["RSRQ"] + random.uniform(-fluctuation, fluctuation), 2),
        "lat": latitude,
        "lng": longitude
    }

def create_dataset():
    devices = ["Device1", "Device2", "Device3"]
    carriers = ["KT", "SKT", "U+"]
    dataset = {device: {carrier: [] for carrier in carriers} for device in devices}

    for i in range(60):  # 10분간 10초 간격(60개)
        # 기본 신호 생성
        signals = {dev: generate_signal_data(base_config[dev]) for dev in devices}

        # 간헐적 역전현상
        if random.random() < inversion_prob:
            swap_type = random.choice(["1-2", "2-3", "1-3"])
            if swap_type == "1-2":
                signals["Device1"], signals["Device2"] = signals["Device2"], signals["Device1"]
            elif swap_type == "2-3":
                signals["Device2"], signals["Device3"] = signals["Device3"], signals["Device2"]
            else:
                signals["Device1"], signals["Device3"] = signals["Device3"], signals["Device1"]

        # 각 디바이스-캐리어 1:1 매칭만 데이터 저장
        dataset["Device1"]["KT"].append(signals["Device1"])
        dataset["Device2"]["SKT"].append(signals["Device2"])
        dataset["Device3"]["U+"].append(signals["Device3"])

    return dataset

with open("lte_signal_data_jntp_by_grade.json", "w", encoding="utf-8") as f:
    json.dump(create_dataset(), f, indent=2, ensure_ascii=False)

print("등급표 기준에 맞는 LTE 신호 데이터 생성 완료!")
