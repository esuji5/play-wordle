from collections import Counter
from itertools import combinations
from typing import Any, List

import pandas as pd
from make_five_letters_data import CSV_PATH
from pandas import DataFrame

ABSENT_VAL, PRESENT_VAL, CORRECT_VAL = 0, 1, 2
# ABSENT_VAL, PRESENT_VAL, CORRECT_VAL = '⬜️', '🟨', '🟩'
# ABSENT_VAL, PRESENT_VAL, CORRECT_VAL = '⬜️', '🚼', '✅'
PILOT_ANSWERS = ["stern", "lynch", "audio"]


class Wordle:
    ABSENT_VAL, PRESENT_VAL, CORRECT_VAL = ABSENT_VAL, PRESENT_VAL, CORRECT_VAL
    CORRECT_RESPONSE = [CORRECT_VAL, CORRECT_VAL, CORRECT_VAL, CORRECT_VAL, CORRECT_VAL]

    def __init__(self, key: str, target_df: Any = None, debug: bool = False, disp: bool = False) -> None:
        self.key: str = key
        self.ans_res_list: List = []
        self.dff_list: List[DataFrame] = []
        if target_df:
            self.target_df = target_df
        else:
            self.target_df = pd.read_csv(CSV_PATH)
        self.debug = debug
        self.disp = disp

    @classmethod
    def get_include_target_df(cls, df, targets: str) -> DataFrame:
        for let in targets:
            df = df[df.word.apply(lambda x: x.find(let) != -1)].copy()
        return df

    @classmethod
    def get_not_include_target_df(cls, df, targets: str) -> DataFrame:
        for let in targets:
            df = df[df.word.apply(lambda x: x.find(let) == -1)].copy()
        return df

    @classmethod
    def get_absent_df(cls, df, let: str) -> DataFrame:
        return df[df.word.apply(lambda x: x.find(let) == -1)].copy()

    @classmethod
    def get_present_df(cls, df, let: str, idx: int) -> DataFrame:
        return df[df.word.apply(lambda x: x.find(let) != -1 and x.find(let) != idx)].copy()

    @classmethod
    def get_correct_df(cls, df, let: str, idx: int) -> DataFrame:
        return df[df.word.apply(lambda x: x[idx] == let)].copy()

    def get_frec_letters(self, df):
        all_words = "".join(df.word.values)
        frec_words = sorted(Counter(all_words.lower()).items(), key=lambda x: x[1], reverse=True)
        return [wf[0] for wf in frec_words]

    def get_frec_letters_df(self, df, frec_letters, word_index=3) -> DataFrame:
        letters_combinations = list(combinations(frec_letters, word_index))
        df_list = []
        for combi in letters_combinations:
            try:
                df_list.append(self.get_include_target_df(df, "".join(combi)))
            except AttributeError:
                pass
        if df_list:
            return pd.concat(df_list)
        else:
            return df

    def filter_df_from_response(self, df, ans: str, res: List) -> DataFrame:
        new_df = df.copy()
        for idx, av in enumerate(zip(ans, res)):
            ans_let, val = av
            if val == self.ABSENT_VAL:
                new_df = self.get_absent_df(new_df, ans_let)
            if val == self.PRESENT_VAL:
                new_df = self.get_present_df(new_df, ans_let, idx)
            if val == self.CORRECT_VAL:
                new_df = self.get_correct_df(new_df, ans_let, idx)
            if self.debug:
                if new_df.shape[0] < 10:
                    print(idx, ans_let, val, new_df.shape, new_df.word.values)
                else:
                    print(idx, ans_let, val, new_df.shape)
            if new_df.shape[0] == 1:
                break

        return new_df

    def select_next_ans(self, df, ans: str) -> str:
        dfex = df[df.word != ans].copy()
        dff = dfex.query("level == 2").copy()
        if dff.shape[0]:
            return dff.values[0][1]
        dff = dfex.query("level == 1").copy()
        if dff.shape[0]:
            return dff.values[0][1]
        dff = dfex.query("boin_num == 0").copy()
        if dff.shape[0]:
            return dff.values[0][1]

        for sn in range(5):
            for bn in range(5):
                dff = dfex.query("boin_num == @bn & same_num==@sn").copy()
                if dff.shape[0]:
                    return dff.values[0][1]
        return dfex.values[0][1]

    def get_nice_filter_df(self, new_df, frec_letters):
        dff = self.get_frec_letters_df(new_df, frec_letters[:5], 5)
        if dff.shape[0]:
            return dff
        dff = self.get_frec_letters_df(new_df, frec_letters[:6], 5)
        if dff.shape[0]:
            return dff
        dff = self.get_frec_letters_df(new_df, frec_letters[:7], 5)
        if dff.shape[0]:
            return dff
        dff = self.get_frec_letters_df(new_df, frec_letters[:5], 4)
        if dff.shape[0]:
            return dff
        dff = self.get_frec_letters_df(new_df, frec_letters[:6], 4)
        if dff.shape[0]:
            return dff
        dff = self.get_frec_letters_df(new_df, frec_letters[:7], 4)
        if dff.shape[0]:
            return dff

    def extract_next_ans(self, new_df, ans):
        if new_df.shape[0] == 1:
            next_ans = new_df.values[0][1]
        else:
            frec_letters = self.get_frec_letters(new_df)
            dff = self.get_nice_filter_df(new_df, frec_letters)
            next_ans = self.select_next_ans(dff, ans)
        return next_ans

    def answer_wordle(self, ans, res, target_df):
        new_df = self.filter_df_from_response(target_df, ans, res)
        self.new_df = new_df
        next_ans = self.extract_next_ans(new_df, ans)
        self.pre_df = new_df
        return next_ans, new_df

    def solve_wordle(self, next_ans, target_df, start_idx=1, disp=True, debug=False):
        self.disp = disp
        self.debug = debug
        if not target_df[target_df.word == self.key].shape[0]:
            raise Exception(f"{self.key} is not in target df")
        idx = start_idx
        while True:
            res = self.get_wordle_response(next_ans)
            if disp:
                if res:
                    print(f'try num: {idx} {next_ans}: {"".join(res)}')
                else:
                    print("dame", idx, next_ans, res)

            if res == self.CORRECT_RESPONSE:
                if disp:
                    print(f"WIN!! Correct: {next_ans}")
                self.solve_take = idx
                break
            next_ans, target_df = self.answer_wordle(next_ans, res, target_df)
            self.dff_list.append(target_df)
            idx += 1

    def solve_wordle_opt(self, target_df, pilot_answers: List = PILOT_ANSWERS, disp=True, debug=False):
        self.disp = disp
        self.debug = debug
        ans1, ans2, ans3 = pilot_answers
        wres = self.get_wordle_response(ans1)
        ndf = self.filter_df_from_response(self.target_df, ans1, wres)
        wres2 = self.get_wordle_response(ans2)
        ndf2 = self.filter_df_from_response(ndf, ans2, wres2)
        wres3 = self.get_wordle_response(ans3)
        ndf3 = self.filter_df_from_response(ndf2, ans3, wres3)
        self.solve_wordle(ndf3.word.values[0], ndf3, start_idx=4)

    def get_let_response(self, ans, ans_let, idx):
        if ans_let not in self.key:
            return self.ABSENT_VAL
        if ans_let in self.key:
            if self.key[idx] == ans[idx]:
                return self.CORRECT_VAL
            else:
                return self.PRESENT_VAL

    def get_wordle_response(self, ans):
        if len(self.key) != len(ans):
            raise Exception("not match length")
        return [self.get_let_response(ans, ans_let, idx) for idx, ans_let in enumerate(ans)]
