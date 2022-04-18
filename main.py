import os
from time import sleep

from play_in_browser_utils import WORDLE_URL, answer_word, build_result_text, to_print_str
from playwright.sync_api import Playwright, sync_playwright
from slack import post_to_slack
from wordle import PILOT_ANSWERS, Wordle


def get_wordle_res(page, ans: str, ans_idx: int):
    ans_res = answer_word(page, ans, ans_idx)
    print(ans_res)
    return ans_res


def close_playwright(context, browser):
    context.close()
    browser.close()


def run(playwright: Playwright, headless: bool, eu: bool = False) -> None:
    post_url = os.environ["SLACK_POST_CHANNEL_URL"]

    browser = playwright.chromium.launch(headless=headless)
    context = browser.new_context()
    page = context.new_page()
    page.goto(WORDLE_URL)
    if eu:
        try:
            page.click("#pz-gdpr-btn-accept")
            page.wait_for_timeout(1000)
        except:
            print("not find #pz-gdpr-btn-accept")
    page.click("game-modal path")

    w = Wordle("")
    print("Wordle Class ready")
    print("Try PILOT_ANSWERS", PILOT_ANSWERS)
    for idx, ans in enumerate(PILOT_ANSWERS):
        w.ans_res_list.append(get_wordle_res(page, ans, idx + 1))
    new_df = w.target_df
    mes_list = []
    for ans, res in w.ans_res_list:
        mes_list.append(to_print_str(ans, res))
        new_df = w.filter_df_from_response(new_df, ans, res)

    print("Filter answer...")
    idx = 4
    while True:
        next_ans = w.extract_next_ans(new_df, ans)
        ans, res = answer_word(page, next_ans, idx)
        w.ans_res_list.append((ans, res))
        if new_df.shape[0] < 10:
            print(idx, ans, res, new_df.shape, new_df.word.values)
            mes_list.append(to_print_str(idx, ans, res, new_df.shape, new_df.word.values))

        else:
            print(idx, ans, res, new_df.shape)
            mes_list.append(to_print_str(idx, ans, res, new_df.shape))

        if w.ans_res_list[-1][1] == w.CORRECT_RESPONSE:
            page.click("text=Share")
            result_text = build_result_text(mes_list)
            word_mean = w.target_df.get(w.target_df.word == next_ans)["mean"].values[0]
            if "c4" in w.target_df.columns:
                c4 = w.target_df.get(w.target_df.word == next_ans)["c4"].values[0]
            else:
                c4 = None
            print(f"WIN!! Correct: {next_ans}: {word_mean}〈{c4}〉")
            mes_list.append(to_print_str(f"WIN!! Correct: {next_ans}: {word_mean}〈{c4}〉"))

            if post_url:
                post_to_slack(result_text + "\n".join([""] + mes_list), post_url)
            close_playwright(context, browser)
            break

        if w.ans_res_list[-1][1] == [None, None, None, None, None] or idx > 9:
            print("nanka dame")
            mes_list.append(to_print_str("nanka dame"))

            if post_url:
                post_to_slack("\n".join(mes_list), post_url)
            close_playwright(context, browser)
            break

        new_df = w.filter_df_from_response(new_df, ans, res)
        idx += 1
        sleep(1)

    close_playwright(context, browser)


def main(headless: bool, eu: bool = False):
    print(headless, eu, type(headless), type(eu))
    with sync_playwright() as playwright:
        run(playwright, headless=headless, eu=eu)


if __name__ == "__main__":
    from dotenv import load_dotenv
    from fire import Fire

    load_dotenv()
    Fire()
