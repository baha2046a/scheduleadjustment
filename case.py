from datetime import time, timedelta, datetime, date
from typing import Optional

client_not_available_time = {
    "伊藤": [
    ],
    "若杉": [
    ],
    "福永": [
    ],
    "里館": [
        [time(10, 0), time(11, 10)],
        [time(12, 20), time(15, 30)]
    ],
    "吉田": [
        [time(10, 0), time(11, 10)],
        [time(12, 20), time(15, 30)]
    ]
}

require_time = {
    "伊藤": time(0, 30),
    "若杉": time(0, 50),
    "福永": time(0, 50),
    "里館": time(0, 40),
    "吉田": time(0, 55)
}

move_time = {
    "伊藤": time(0, 5),
    "若杉": time(0, 10),
    "福永": time(0, 5),
    "里館": time(0, 7),
    "吉田": time(0, 5)
}

today_work_time = [
    [time(10, 5), time(13, 0)],
    [time(14, 0), time(17, 0)]
]


def add_time(f: time, dt: time):
    td = timedelta(hours=int(dt.hour), minutes=int(dt.minute))
    result = datetime.combine(date.today(), f) + td
    return result.time()


def sub_time(f: time, dt: time):
    td = timedelta(hours=int(dt.hour), minutes=int(dt.minute))
    result = datetime.combine(date.today(), f) - td
    return result.time()


def to_min(in_time: time) -> int:
    return (int(in_time.hour) * 60) + int(in_time.minute)


def get_require_time(name):
    result = add_time(require_time[name], move_time[name])
    # print(name, result)
    return result


def simplify_client_time(client) -> dict:
    modified_client = {}
    for m, t in client.items():
        modified_t = []

        for idx, rang in enumerate(t):
            if idx > 0:
                if add_time(t[idx - 1][1], get_require_time(m)) > rang[0]:
                    modified_t[-1][1] = rang[1]
                else:
                    modified_t.append(t[idx])
            else:
                modified_t.append(t[idx])
        modified_client[m] = modified_t
    return modified_client


def client_today_empty_time(client, today_empty) -> dict:
    modified_client = {}
    for m, t in client.items():
        modified_t = []
        for rang in today_empty:
            if len(t) < 1 or rang[0] > t[-1][1] or rang[1] < t[0][0]:
                modified_t.append(rang)
            else:
                for c_idx, c_rang in enumerate(t):
                    if rang[1] >= c_rang[0] > rang[0] or rang[1] >= c_rang[1] > rang[0]:
                        if c_rang[0] > rang[0]:
                            if not (modified_t and modified_t[-1][1] == c_rang[0]):
                                modified_t.append([rang[0], c_rang[0]])
                        if c_rang[1] < rang[1]:
                            to = rang[1]
                            if len(t) > (c_idx + 1):
                                to = min(to, t[c_idx + 1][0])
                            modified_t.append([c_rang[1], to])

        modified_client[m] = modified_t
    return modified_client


def client_today_ready_time(client) -> dict:
    modified_client = {}
    for m, t in client.items():
        modified_t = []
        for c_rang in t:
            if add_time(c_rang[0], get_require_time(m)) > c_rang[1]:
                continue
            last_enter = sub_time(c_rang[1], get_require_time(m))
            modified_t.append([c_rang[0], last_enter])
        modified_client[m] = modified_t
    return modified_client


def can_fit_waiting_time(client, start_time, waiting_time) -> Optional[str]:
    for m, t in client.items():
        if to_min(get_require_time(m)) > waiting_time:
            continue
        print("F", m, waiting_time)
        for c_t in t:
            if c_t[1] >= start_time >= c_t[0]:
                return m
    return None


def try_arrange(client: dict, today_empty: list):
    result, no_match = try_arrange_run(client, today_empty, [])

    if no_match:
        no_match_count = len(no_match)
        for wait in range(20, 50, 10):
            while True:
                try_result, try_no_match = try_arrange_run(client, today_empty, no_match, wait)
                if len(try_no_match) < no_match_count:
                    no_match_count = len(try_no_match)
                    no_match = try_no_match
                    result = try_result
                    if not no_match:
                        break
                else:
                    break

            if not no_match:
                break

    return result, no_match


def try_arrange_run(client: dict, today_empty: list, first_client: list, waiting_ok: int = 0):
    print("try_arrange_run", first_client, waiting_ok)
    client = client.copy()
    today_empty = today_empty.copy()
    result = []
    try_start = today_empty.pop(0).copy()
    while client:
        min_diff = 1000
        target = None
        start_time = None
        waiting_time = None

        for m, t in client.items():
            for c_rang in t:
                # print(try_start[0], c_rang[0], c_rang[1])
                if c_rang[1] >= try_start[0] >= c_rang[0] or c_rang[0] > try_start[0]:
                    if c_rang[0] > try_start[1]:
                        continue
                    if c_rang[0] > try_start[0]:
                        diff = sub_time(c_rang[0], try_start[0])
                        diff = timedelta(hours=int(diff.hour), minutes=int(diff.minute)).total_seconds()
                        diff = int(diff // 60)
                    else:
                        diff = 0

                    # print(waiting_ok)
                    if m in first_client:
                        if diff <= waiting_ok:
                            diff = -1

                    # print(try_start, m, diff)
                    if diff < min_diff:
                        target = m
                        start_time = max(c_rang[0], try_start[0])
                        waiting_time = to_min(sub_time(start_time, try_start[0]))
                        min_diff = diff

        if target is not None:
            print(target,  try_start[0], start_time, waiting_time)
            if waiting_time > 10:
                try_fit = can_fit_waiting_time(client, try_start[0], waiting_time)
                if try_fit:
                    fit_end_time = add_time(try_start[0], get_require_time(try_fit))
                    client.pop(try_fit)
                    result.append([try_fit, try_start[0], fit_end_time])

            end_time = add_time(start_time, get_require_time(target))
            client.pop(target)
            result.append([target, start_time, end_time])
            try_start[0] = end_time
        else:
            print("None")
            if len(today_empty) < 1:
                break
            try_start = today_empty.pop(0).copy()
    return result, list(client.keys())


if __name__ == '__main__':
    s_client = simplify_client_time(client_not_available_time)

    print()
    print("今日の診察時間")
    print(today_work_time)

    e_client = client_today_empty_time(s_client, today_work_time)

    print()
    print("診察時間内、患者空いている時間")
    for m, t in e_client.items():
        print(m)
        print(t)

    print()
    print("必要診察＋移動時間")
    for m, t in e_client.items():
        print(m, get_require_time(m))

    f_client = client_today_ready_time(e_client)

    print()
    print("患者を診察の開始出来る時間")
    for m, t in f_client.items():
        print(m)
        print(t)

    arg, no_arg = try_arrange(f_client, today_work_time)

    print()
    print("スケジュール試作")

    for i in arg:
        print(i)

    print()
    print("スケジュール試作(移動時間除く)")

    for i in arg:
        i[1] = add_time(i[1], move_time[i[0]])
        print(f"移動{move_time[i[0]]}", i, sub_time(i[2], i[1]))

    if no_arg:
        print("対応出来ない")
        print(no_arg)
