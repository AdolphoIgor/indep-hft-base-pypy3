from datetime import datetime, timedelta


class Momentum:
    _mm_lst = []
    _dt_start = None

    def get_momentum(self, lst_tt: list, minutes=5, skip_minutes=5, buy_threshold=0.80, sell_threshold=0.20):

        if not self._mm_lst:
            self._dt_start = datetime.strptime(lst_tt[0][1], "%Y-%m-%d %H:%M:%S.%f")
            self._dt_start = self._dt_start + timedelta(minutes=skip_minutes)

        self._mm_lst.extend(lst_tt)

        tt_dtt = datetime.strptime(lst_tt[-1][1], "%Y-%m-%d %H:%M:%S.%f")
        tt_dtt = tt_dtt - timedelta(minutes=minutes)

        lst_rem = list(
            filter(lambda x: (datetime.strptime(x[1], "%Y-%m-%d %H:%M:%S.%f") <= tt_dtt) or
                             (datetime.strptime(x[1], "%Y-%m-%d %H:%M:%S.%f") <= self._dt_start), self._mm_lst))

        for rem in lst_rem:
            self._mm_lst.remove(rem)

        if not self._mm_lst:
            return None

        mm_max = 0.0
        mm_med = 0.0
        mm_min = 0.0
        mm_vfn = 0.0
        mm_qtd = 0

        for mm in self._mm_lst:
            mm_max = mm[2] if mm[2] > mm_max else mm_max
            mm_min = mm[2] if mm_min == 0.0 or mm[2] <= mm_min else mm_min
            mm_qtd += mm[3]
            mm_vfn += mm[2] * mm[3]
            mm_med = round(mm_vfn / mm_qtd, 2)

        max_min = round(mm_max - mm_min, 2)
        med_min = round(mm_med - mm_min, 2)
        b_buy, b_sell = False, False
        if max_min > 0 and med_min > 0:
            med_max_min = round(med_min / max_min, 2)
            b_buy = med_max_min >= buy_threshold
            b_sell = med_max_min <= sell_threshold

        return [mm_max, mm_med, mm_min, b_buy, b_sell]
