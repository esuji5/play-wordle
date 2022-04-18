import io
from datetime import datetime
from time import sleep
from typing import List

from PIL import Image
from PIL.PngImagePlugin import PngImageFile
from wordle import ABSENT_VAL, CORRECT_VAL, PRESENT_VAL

WORDLE_URL = "https://www.nytimes.com/games/wordle/index.html"
SCREENSHOT_DIR = "./screenshot"

LETTER_PUSH_DICT = {
    "q": 'button[data-key="q"]',
    "w": 'button[data-key="w"]',
    "e": 'button[data-key="e"]',
    "r": 'button[data-key="r"]',
    "t": 'button[data-key="t"]',
    "y": 'button[data-key="y"]',
    "u": 'button[data-key="u"]',
    "i": 'button[data-key="i"]',
    "o": 'button[data-key="o"]',
    "p": 'button[data-key="p"]',
    "a": 'button[data-key="a"]',
    "s": 'button[data-key="s"]',
    "d": 'button[data-key="d"]',
    "f": 'button[data-key="f"]',
    "g": 'button[data-key="g"]',
    "h": 'button[data-key="h"]',
    "j": 'button[data-key="j"]',
    "k": 'button[data-key="k"]',
    "l": 'button[data-key="l"]',
    "z": 'button[data-key="z"]',
    "x": 'button[data-key="x"]',
    "c": 'button[data-key="c"]',
    "v": 'button[data-key="v"]',
    "b": 'button[data-key="b"]',
    "n": 'button[data-key="n"]',
    "m": 'button[data-key="m"]',
    "bs": "div:nth-child(3) button:nth-child(9)",
}

ABSENT_PIXEL = (120, 124, 126, 255)
PRESENT_PIXEL = (201, 180, 88, 255)
CORRECT_PIXEL = (106, 170, 100, 255)


def to_print_str(*args):
    return " ".join([str(i) for i in args])


def parse_result_text(mes_list):
    res_str_list = [mes.split("[")[1].split("]")[0] for mes in mes_list]
    return [res.replace("0", "⬜️").replace("1", "🟨").replace("2", "🟩").replace(", ", "") for res in res_str_list]


def get_wordle_num():
    """epock: 245, 20220219"""
    epock_num, epock_date = 245, datetime(2022, 2, 19)
    return epock_num + (datetime.now() - epock_date).days


def build_result_text(mes_list):
    res_list = parse_result_text(mes_list)
    wordle_num = get_wordle_num()
    result_text = f"Wordle {wordle_num} {len(mes_list)}/6"
    for res in res_list:
        result_text = result_text + "\n" + res
    return result_text


def check_pixel_to_res(pixel):
    pad = 5
    if ABSENT_PIXEL[0] - pad < pixel[0] < ABSENT_PIXEL[0] + pad:
        return ABSENT_VAL
    if PRESENT_PIXEL[0] - pad < pixel[0] < PRESENT_PIXEL[0] + pad:
        return PRESENT_VAL
    if CORRECT_PIXEL[0] - pad < pixel[0] < CORRECT_PIXEL[0] + pad:
        return CORRECT_VAL


def input_word(page, word):
    for w in word:
        page.click(LETTER_PUSH_DICT[w])
        sleep(0.05)


def get_res_from_image(image: PngImageFile) -> List:
    height_pad = image.height // 6
    width_pad = image.width // 5
    xy_list = [(i * width_pad + width_pad // 2, height_pad) for i in range(5)]
    pixel_list = [image.getpixel(xy) for xy in xy_list]
    # print(xy_list, pixel_list)
    return [check_pixel_to_res(pixel) for pixel in pixel_list]


def answer_word(page, ans: str, ans_idx: int):
    input_word(page, ans)
    page.click("text=enter")
    page.wait_for_timeout(3000)

    screenshot_bytes = page.locator(f"#board >> game-row:nth-child({ans_idx})").screenshot(
        # path=os.path.join(SCREENSHOT_DIR, f"./screenshot_{ans_idx}.png")
    )
    image = Image.open(io.BytesIO(screenshot_bytes))
    res = get_res_from_image(image)
    return ans, res
