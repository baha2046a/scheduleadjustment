from datetime import time, timedelta, datetime, date

client_not_available_time = {
    "伊藤": [
        [time(10, 30), time(11, 0)],
        [time(15, 30), time(16, 0)]
    ],
    "若杉": [
        [time(11, 0), time(11, 30)],
        [time(11, 30), time(12, 0)],
        [time(13, 30), time(14, 0)],
        [time(16, 0), time(16, 30)]
    ],
    "福永": [
        [time(11, 0), time(11, 30)]
    ],
    "里館": [
        [time(10, 0), time(10, 30)],
        [time(10, 30), time(11, 0)],
        [time(14, 30), time(15, 0)]
    ],
    "吉田": [
        [time(10, 0), time(10, 30)],
        [time(14, 30), time(15, 0)],
        [time(15, 0), time(15, 30)]
    ]
}

require_time = {
    "伊藤": time(0, 30),
    "若杉": time(0, 10),
    "福永": time(0, 50),
    "里館": time(0, 20),
    "吉田": time(0, 40)
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
    [time(14, 0), time(16, 0)]
]


def add_time(f: time, dt: time):
    td = timedelta(hours=int(dt.hour), minutes=int(dt.minute))
    result = datetime.combine(date.today(), f) + td
    return result.time()


def sub_time(f: time, dt: time):
    td = timedelta(hours=int(dt.hour), minutes=int(dt.minute))
    result = datetime.combine(date.today(), f) - td
    return result.time()


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


def client_with_empty_time(client, today_empty) -> dict:
    modified_client = {}
    for m, t in client.items():
        modified_t = []
        for rang in today_empty:
            if len(t) < 1 or rang[0] > t[-1][1] or rang[1] < t[0][0]:
                modified_t.append(rang)
            else:
                for c_idx, c_rang in enumerate(t):
                    print(m, c_idx, rang)
                    if rang[1] >= c_rang[0] > rang[0]:
                        if c_rang[0] > rang[0]:
                            if not(modified_t and modified_t[-1][1] == c_rang[0]):
                                modified_t.append([rang[0], c_rang[0]])
                        if c_rang[1] < rang[1]:
                            to = rang[1]
                            if len(t) > (c_idx + 1):
                                to = min(to, t[c_idx + 1][0])
                            modified_t.append([c_rang[1], to])
                    elif rang[0] < c_rang[1] <= rang[1]:
                        if c_rang[1] < rang[1]:
                            to = rang[1]
                            if len(t) > (c_idx + 1):
                                to = min(to, t[c_idx + 1][0])
                            modified_t.append([c_rang[1], to])
                        if c_rang[0] > rang[0]:
                            if not(modified_t and modified_t[-1][1] == c_rang[0]):
                                modified_t.append([rang[0], c_rang[0]])

        modified_client[m] = modified_t
    return modified_client


def client_can_fit_time(client):
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


def can_fit(start, end, name, client_ok_time):
    for t in client_ok_time:
        if t[0] >= start:
            if add_time(t[0], get_require_time(name)) <= end:
                return t[0] - start
    return None


def try_arrange(client: dict, today_empty: list):
    result = []
    try_start = today_empty.pop(0)
    while client:
        min_diff = 1000
        target = None
        start_time = None
        for m, t in client.items():
            for c_rang in t:
                print(try_start[0], c_rang[0], c_rang[1])
                if c_rang[1] >= try_start[0] >= c_rang[0] or c_rang[0] > try_start[0]:
                    if c_rang[0] > try_start[0]:
                        diff = sub_time(c_rang[0], try_start[0])
                        diff = timedelta(hours=int(diff.hour), minutes=int(diff.minute)).total_seconds()
                        diff = int(diff // 60)
                    else:
                        diff = 0

                    # print(try_start, m, diff)
                    if diff < min_diff:
                        target = m
                        start_time = max(c_rang[0], try_start[0])
                        min_diff = diff
                        break

        if target is not None:
            print(target)
            end_time = add_time(start_time, get_require_time(target))
            client.pop(target)
            result.append([target, start_time, end_time])
            try_start[0] = end_time
        else:
            print("None")
            if len(today_empty) < 1:
                break
            try_start = today_empty.pop(0)
    print(client)
    return result


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    s_client = simplify_client_time(client_not_available_time)

    print()
    print("今日の診察時間")
    print(today_work_time)

    e_client = client_with_empty_time(s_client, today_work_time)

    print()
    print("診察時間内、患者空いている時間")
    for m, t in e_client.items():
        print(m)
        print(t)

    print()
    print("必要診察＋移動時間")
    for m, t in e_client.items():
        print(m, get_require_time(m))

    f_client = client_can_fit_time(e_client)

    print()
    print("患者を診察の開始出来る時間")
    for m, t in f_client.items():
        print(m)
        print(t)

    arg = try_arrange(f_client, today_work_time)

    print()
    print("スケジュール試作")

    for i in arg:
        print(i)

    print()
    print("スケジュール試作(移動時間除く)")

    for i in arg:
        i[1] = add_time(i[1], move_time[i[0]])
        print(f"移動{move_time[i[0]]}", i, sub_time(i[2], i[1]))

# try_arrange(e_client, today_empty)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
