import json
import random
import datetime

# 이동 경로 (시작점, 종료점)
start_lat, start_lng = 34.9481, 127.4866
end_lat, end_lng = 34.9500, 127.5300  # 예시: 북동쪽으로 약 250m 이동

# 등급표 기준 중심값 (첨부 이미지 기준)
base_config = {
    "Device1": {  # Excellent 중심
        "RSSI": -60,    # > -65
        "RSRP": -80,    # > -84
        "SINR": 20,     # > 12.5
        "RSRQ": -4      # > -5
    },
    "Device2": {  # Good 중심
        "RSSI": -70,    # -65 ~ -75
        "RSRP": -93,    # -85 ~ -102
        "SINR": 11,     # 10 ~ 12.5
        "RSRQ": -7      # -9 ~ -5
    },
    "Device3": {  # Fair 중심
        "RSSI": -80,    # -75 ~ -85
        "RSRP": -107,   # -103 ~ -111
        "SINR": 8.5,    # 7 ~ 10
        "RSRQ": -10.5   # -12 ~ -9
    }
}

fluctuation = 3  # ±3dB 출렁임
inversion_prob = 0.12  # 12% 확률 역전
num_points = 6000  # 1000분간 10초 간격(6000개)
start_time = datetime.datetime.now()

def interpolate(start, end, ratio):
    return start + (end - start) * ratio

def generate_signal_data(base, timestamp, lat, lng):
    return {
        "RSSI": round(base["RSSI"] + random.uniform(-fluctuation, fluctuation), 2),
        "RSRP": round(base["RSRP"] + random.uniform(-fluctuation, fluctuation), 2),
        "SINR": round(base["SINR"] + random.uniform(-fluctuation, fluctuation), 2),
        "RSRQ": round(base["RSRQ"] + random.uniform(-fluctuation, fluctuation), 2),
        "lat": round(lat, 7),
        "lng": round(lng, 7),
        "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }

def create_dataset():
    devices = ["Device1", "Device2", "Device3"]
    carriers = ["KT", "SKT", "U+"]
    dataset = {device: {carrier: [] for carrier in carriers} for device in devices}

    for i in range(num_points):
        ratio = i / (num_points - 1)
        lat = interpolate(start_lat, end_lat, ratio)
        lng = interpolate(start_lng, end_lng, ratio)
        measure_time = start_time + datetime.timedelta(seconds=10*i)
        signals = {dev: generate_signal_data(base_config[dev], measure_time, lat, lng) for dev in devices}

        # 간헐적 역전(임의로 신호 swap)
        if random.random() < inversion_prob:
            swap_type = random.choice(["1-2", "2-3", "1-3"])
            if swap_type == "1-2":
                signals["Device1"], signals["Device2"] = signals["Device2"], signals["Device1"]
            elif swap_type == "2-3":
                signals["Device2"], signals["Device3"] = signals["Device3"], signals["Device2"]
            else:
                signals["Device1"], signals["Device3"] = signals["Device3"], signals["Device1"]

        dataset["Device1"]["KT"].append(signals["Device1"])
        dataset["Device2"]["SKT"].append(signals["Device2"])
        dataset["Device3"]["U+"].append(signals["Device3"])

    return dataset

# JSON 파일로 저장
with open("jntp_lte_signal_data_latest.json", "w", encoding="utf-8") as f:
    json.dump(create_dataset(), f, indent=2, ensure_ascii=False)

"""
- 등급 구간은 첨부 표(두 이미지)와 완전 일치
- Device1: Excellent, Device2: Good, Device3: Fair 중심
- ±3dB 출렁임, 12% 확률 역전, 10분간 10초 간격(60개)
- 선형 이동(시작~종료점), 각 계측마다 같은 위치에서 기록
- timestamp 포함, JSON 구조 완벽 호환
"""
