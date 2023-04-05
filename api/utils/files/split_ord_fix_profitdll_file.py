import os


def proc(file_path):
    dct_output = {}
    with open(file_path, mode='r', encoding="UTF-8", newline='\n') as file:
        lst_lines = file.readlines()
        lst_lines.sort()

        last_line = ""
        lst_output = []
        for line in lst_lines:
            if last_line == line:
                continue

            lst_output.append(line)
            last_line = line

        lst_lines.clear()
        for line in lst_output:
            lst_val = line.replace("nan", "-1").split("|")
            symbol = eval(lst_val[2])[0]

            lst_sbl = dct_output.get(symbol, [])
            if not lst_sbl:
                dct_output[symbol] = lst_sbl

            lst_sbl.append(line)

    lst_file_path = file_path.split("/")
    lst_name_ext = lst_file_path[-1].split(".")
    for sbl, lst in dct_output.items():
        file_out_name = file_path.replace(f"{lst_file_path[-1]}",
                                          f"{lst_name_ext[0]}/{lst_name_ext[0]}_{sbl}_{lst_name_ext[-1]}")
        os.makedirs(os.path.dirname(file_out_name), exist_ok=True)
        file = open(file_out_name, mode="w", encoding="UTF-8", newline='\n')
        file.writelines(lst)
        file.flush()
        file.close()


proc("/home/adolpho/Devel/indep/indep-hft-base-pypy3/logs/profit_logs/20230307.log")
proc("/home/adolpho/Devel/indep/indep-hft-base-pypy3/logs/profit_logs/20230309.log")
proc("/home/adolpho/Devel/indep/indep-hft-base-pypy3/logs/profit_logs/20230310.log")
proc("/home/adolpho/Devel/indep/indep-hft-base-pypy3/logs/profit_logs/20230314.log")
proc("/home/adolpho/Devel/indep/indep-hft-base-pypy3/logs/profit_logs/20230316.log")
