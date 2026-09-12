import os


def clean_file(file_path):
    dct_output = {}
    with open(file_path, mode='r', encoding="UTF-8", newline='\n') as file:
        lst_lines = file.readlines()
        lst_lines.sort()

        # Linhas duplicadas
        last_line = ""
        lst_output = []
        for line in lst_lines:
            if last_line == line:
                continue

            last_line = line
            lst_output.append(line)

        lst_lines.clear()
        for line in lst_output:
            lst_val = line.replace("nan", "-1").split("|")
            symbol = eval(lst_val[2])[0]

            lst_sbl = dct_output.get(symbol, [])
            if not lst_sbl:
                dct_output[symbol] = lst_sbl

            lst_sbl.append(line)

    for sbl, lst in dct_output.items():
        # Ppayloads duplicados
        last_payload = ""
        lst_output = []
        for line in lst:
            payload = line.replace("nan", "-1").split("|")
            if last_payload == payload[2]:
                continue

            if payload[1] in ["new_trade_callback", "change_cotation_callback"]:
                lst_dt = str(eval(payload[2])[1]).split(" ")
                dt = lst_dt[0].split("/")
                payload[0] = f"{dt[-1]}-{dt[1]}-{dt[0]} {lst_dt[1]}000"

            last_payload = payload[2]
            lst_output.append("|".join(payload))

        dct_output[sbl] = lst_output

    lst_file_path = file_path.split("/")
    lst_name_ext = lst_file_path[-1].split(".")
    for sbl, lst in dct_output.items():
        file_out_name = file_path.replace(f"{lst_file_path[-1]}",
                                          f"{lst_name_ext[0]}/{lst_name_ext[0]}_{sbl}_{lst_name_ext[-1]}")
        os.makedirs(os.path.dirname(file_out_name), exist_ok=True)
        file = open(file_out_name, mode="w", encoding="UTF-8", newline='\n')
        lst.sort()
        file.writelines(lst)
        file.flush()
        file.close()


lst_files = [
    "/home/adolpho/Devel/indep/indep-hft-base-pypy3/logs/profit_logs/20230302.log",
    "/home/adolpho/Devel/indep/indep-hft-base-pypy3/logs/profit_logs/20230303.log",
    "/home/adolpho/Devel/indep/indep-hft-base-pypy3/logs/profit_logs/20230307.log",
    "/home/adolpho/Devel/indep/indep-hft-base-pypy3/logs/profit_logs/20230308.log",
    "/home/adolpho/Devel/indep/indep-hft-base-pypy3/logs/profit_logs/20230309.log",
    "/home/adolpho/Devel/indep/indep-hft-base-pypy3/logs/profit_logs/20230310.log",
    "/home/adolpho/Devel/indep/indep-hft-base-pypy3/logs/profit_logs/20230313.log",
    "/home/adolpho/Devel/indep/indep-hft-base-pypy3/logs/profit_logs/20230314.log",
    "/home/adolpho/Devel/indep/indep-hft-base-pypy3/logs/profit_logs/20230316.log"
]

for fl in lst_files:
    clean_file(fl)
