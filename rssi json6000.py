import json
import random
import datetime
import math

# 이동 경로 (시작점, 종료점)
start_lat, start_lng = 34.9481, 127.4866
end_lat, end_lng = 34.9500, 127.5300  # 예시: 북동쪽으로 약 250m 이동

# 등급표 기준 중심값
base_config = {
    "Device1": {  # Excellent 중심
        "RSSI": -60,
        "RSRP": -80,
        "SINR": 20,
        "RSRQ": -4
    },
    "Device2": {  # Good 중심
        "RSSI": -70,
        "RSRP": -93,
        "SINR": 11,
        "RSRQ": -7
    },
    "Device3": {  # Fair 중심
        "RSSI": -80,
        "RSRP": -107,
        "SINR": 8.5,
        "RSRQ": -10.5
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

def create_wobbly_path(start_lat, start_lng, end_lat, end_lng, n_points, wobble=0.0002):
    """구불구불한 경로 생성"""
    path = []
    for i in range(n_points):
        ratio = i / (n_points - 1)
        # 기본 선형 보간
        base_lat = interpolate(start_lat, end_lat, ratio)
        base_lng = interpolate(start_lng, end_lng, ratio)
        # 랜덤성 추가 (wobble: 진폭)
        lat = base_lat + random.uniform(-wobble, wobble)
        lng = base_lng + random.uniform(-wobble, wobble)
        path.append((lat, lng))
    return path

def create_dataset():
    devices = ["Device1", "Device2", "Device3"]
    carriers = ["KT", "SKT", "U+"]
    dataset = {device: {carrier: [] for carrier in carriers} for device in devices}

    # 구불구불한 경로 생성
    path = create_wobbly_path(start_lat, start_lng, end_lat, end_lng, num_points, wobble=0.0002)

    for i in range(num_points):
        lat, lng = path[i]
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
