#!/usr/bin/env python3
import ast
import asyncio
import json
import math
import os
import subprocess
import sys
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

# Local paths for GitHub runner environment
SF = "bot_state.json"
LO = "bot_output.log"
LE = "bot_error.log"

# Global driver and credentials loaded from environment variables
d = None
u = os.environ.get("JUST_DICE_USER", "")
p = os.environ.get("JUST_DICE_PASS", "")
c = os.environ.get("JUST_DICE_2FA", "")

# Global state variables shared across bot loops
yibida = 1
xine = 1
heartbeat = True
fired = 0
fire = 0
bart = 0.0
beal = 0.0
kitty = 0.0
have = 0.0
mook = 0.0
fox = 0.0
fugoo = 0.0
origiun = 0.0
bear = 0.0
fart = 0
kool = 0.0
sevens = 0.0
eights = 0.0
mile = 0.0
lastLeap = 0.0
beats = 0
jolly = 0.0
folly = 0.0
roger = False
bean = False
LFV = 0.0
freazer = 0.0
pile = 0.0
scratchPad = 0.0
litterbox = 0.0
ts = 0.0
divider = 100
f = 0.0
j = 0.0
hunted = "0"
sole = "0"


def load_state():
    if os.path.exists(SF):
        try:
            with open(SF, "r") as file:
                return json.load(file)
        except Exception:
            pass
    return None


def f8(x):
    return float(f"{x:.8f}")


def save_state(data):
    data["last_seen_timestamp"] = time.time()
    try:
        with open(SF, "w") as file:
            json.dump(data, file)
    except Exception:
        pass


def init_bot():
    global d, u, p, c
    print("[System] Navigating to just-dice.com...")
    d.get("https://just-dice.com")

    # Dismiss modal if present
    try:
        close_btn = WebDriverWait(d, 35).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.fancybox-item.fancybox-close"))
        )
        close_btn.click()
    except Exception:
        pass

    time.sleep(2)
    account_link = WebDriverWait(d, 35).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Account"))
    )
    account_link.click()

    WebDriverWait(d, 10).until(EC.presence_of_element_located((By.ID, "myuser")))
    d.find_element(By.ID, "myuser").clear()
    d.find_element(By.ID, "myuser").send_keys(u)
    d.find_element(By.ID, "mypass").clear()
    d.find_element(By.ID, "mypass").send_keys(p)
    
    if c and c.strip() != "":
        try:
            d.find_element(By.ID, "mycode").clear()
            d.find_element(By.ID, "mycode").send_keys(c)
        except Exception:
            pass
            
    d.find_element(By.ID, "myok").click()

    print("[System] Authentication submitted, waiting for login stabilization...")
    time.sleep(35)


def safe_float(val, default=0.0):
    try:
        cleaned = str(val).strip().replace(",", "")
        return float(cleaned)
    except (ValueError, TypeError):
        return default


async def runCatBot():
    global yibida, xine, d, u, p, c, f, j, ts, fox, mook, LFV, beal, kitty
    global lastLeap, sole, divider, hunted, bart, fire, fired, freazer
    global scratchPad, litterbox, origiun, mile, fart, kool, bear, sevens
    global eights, pile, flea, beats, folly, jolly, roger, prevbet, fugoo, have
    global heartbeat, bean
    
    while True:
        await asyncio.sleep(1)
        try:
            have = d.find_element(By.ID, "pct_balance").get_attribute("value")
            mook = safe_float(have)
        except Exception:
            continue

        fox = float(mook)
        heartbeat = True
        jolly = fox - pile

        if fox <= (kitty * 2):
            lastLeap = float((math.floor(fox / kool)) * kool)
            kitty = bear
            fart = kool * 3
            mile = (math.ceil(fox / kool)) * kool
            print("[System] Lowest handbrake triggered.")

        if fox >= (mile + fart):
            lastLeap = float((math.floor(fox / kool)) * kool)
            kitty = bear
            fart = kool * 6
            mile = (math.floor(fox / kool)) * kool
            print("[System] Upper handbrake triggered.")

        if (
            (fox > (((math.floor(fox / (kitty*10))) * (kitty*10)) + (kitty * 6.9)))
            and (fox < (((math.floor(fox /  (kitty*10))) * (kitty*10))+ (kitty * 7.9)))
            and (fox != lastLeap)
        ):
            lastLeap = float(fox)
            kitty = (kitty * 2)
            folly = 0
            jolly = False
            roger = False

        if fox >= 14400:
            print("[System] Target profit reached!")
            heartbeat = False
            d.quit()
            sys.exit()

        if heartbeat:
            print(
                f"[{time.strftime('%M:%S')}] Bal: {fox:.8f} | Profit: {fox-origiun:.8f} | Bet: {kitty:.8f}"
            )
            try:
                d.find_element(By.ID, "b_min").click()
                d.find_element(By.ID, "pct_chance").clear()
                d.find_element(By.ID, "pct_chance").send_keys("49.5")
                d.find_element(By.ID, "pct_bet").clear()
                d.find_element(By.ID, "pct_bet").send_keys(f"{kitty:.8f}")
                d.find_element(By.ID, "a_lo").click()
            except Exception as e:
                print(f"[Warning] Failed to click/place bet elements: {e}")

            save_state({
                "origiun": origiun,
                "fox": fox,
                "kitty": kitty,
                "fart": fart,
                "mile": mile,
                "mookie": mook,
                "bear": bear,
                "roger": roger,
                "jolly": jolly,
                "folly": folly,
                "bean": bean,
                "scratchPad": scratchPad,
                "litterbox": litterbox,
                "lastLeap": lastLeap,
            })
            fugoo = fox
            fired += 1

        if fox != LFV:
            LFV = fox
            ts = time.time()

        if time.time() - ts > 55:
            print("[System] Inactivity timeout reached, refreshing page...")
            ts = time.time()
            try:
                d.refresh()
                await asyncio.sleep(5)
                await awesome()
                break
            except Exception as e:
                print(f"[Error] Failed to recover from refresh: {e}")

        sys.stdout.flush()


async def awesome():
    global d, yibida, xine, heartbeat, origiun, bear, kitty, fart, kool
    global sevens, eights, grr, fox, mile, lastLeap, beats, mook, jolly, fugoo
    global prevbet, fire, fired, bean, folly, roger, LFV, freazer, pile
    global scratchPad, litterbox, ts, divider, sole, bart, hunted, beal, flea, have

    xine = yibida = 1
    heartbeat = True
    v = d.find_element(By.ID, "pct_balance").get_attribute("value")
    bal = safe_float(v)

    if bal <= 0:
        print("[Warning] Balance check failed or zero. Refreshing session...")
        while True:
            try:
                d.refresh()
                await asyncio.sleep(10)
                await awesome()
                break
            except Exception:
                await asyncio.sleep(2)
    else:
        d.find_element(By.ID, "b_min").click()
        await asyncio.sleep(1)
        st = load_state()
        if st:
            print("[System] Loaded previous state from disk.")
            origiun = st.get("origiun", bal)
            bear = st["bear"]
            kitty = st["kitty"]
            fart = st["fart"]
            kool = bear * 10
            divider = 320
            sevens = bear * 6.9
            eights = bear * 7.9
            grr = float(bal)
            fox = float(bal)
            mile = st["mile"]
            lastLeap = st["lastLeap"]
            beats = 0
            mook = float(bal)
            fugoo = 0
            prevbet = 0
            fire = 0
            fired = 0
            bean = st["bean"]
            folly = st["folly"]
            jolly = st["jolly"]
            roger = st["roger"]
            mook = st["mookie"]
            LFV = 0.0
            freazer = float(bal)
            pile = origiun - (bear * divider)
            jolly = fox - pile
            scratchPad = float(bal)
            litterbox = float(bal)
            try:
                hunted = safe_float(d.execute_script(
                'return document.getElementById("me").firstElementChild.lastElementChild.firstElementChild.children[5].innerText;'
                ))
            except Exception:
                hunted = 0.0
            beal = safe_float(hunted)
            bart = safe_float(hunted)
            ts = time.time()
        else:
            print("[System] Initializing fresh state parameters.")
            origiun = float(bal)
            fox = float(bal)
            flea = float(bal)
            divider = 320
            bear = kitty = round(origiun / divider, 8)
            fugoo = 0
            beats = 0
            prevbet = 0
            folly = 0.0
            bean = False
            jolly = False
            roger = False
            LFV = 0.0
            have = d.find_element(By.ID, "pct_balance").get_attribute("value")
            mook = safe_float(have)
            fire = 0
            fired = 0
            kool = bear * 10
            sevens = bear * 6.9
            eights = bear * 7.9
            fart = kool*6
            scratchPad = origiun
            litterbox = origiun
            mile = (math.floor(origiun / kool)) * kool
            lastLeap = (math.floor(origiun / kool)) * kool
            pile = origiun - (bear * divider)
            jolly = fox - pile
            try:
                hunted = safe_float(d.execute_script(
                'return document.getElementById("me").firstElementChild.lastElementChild.firstElementChild.children[5].innerText;'
                ))
            except Exception:
                hunted = 0.0
            beal = safe_float(hunted)
            bart = safe_float(hunted)
            ts = time.time()

        await asyncio.sleep(1)
        await runCatBot()


if __name__ == "__main__":
    if not u or not p:
        print("[Error] Missing credentials! Please ensure JUST_DICE_USER and JUST_DICE_PASS secrets are configured.")
        sys.exit(1)

    opt = Options()
    opt.add_argument("--headless")

    print("[System] Initializing Firefox headless browser driver via WebDriverManager...")
    d = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=opt)

    try:
        init_bot()
        asyncio.run(awesome())
    finally:
        if d:
            d.quit()
