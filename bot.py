#!/usr/bin/env python3
import json
import math
import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

STATE_FILE = ".bot_state.json"

startingPocketChange = 0.0
tinyPeanutSize = 0.0
backupPeanut = 0.0
tenPeanuts = 0.0
walletStash = 0.0
previousWalletState = 0.0
currentWagerAmount = 0.0
previousWagerAmount = 0.0
checkpointJuice = 0.0
wobbleFactor = 1.0
safetyCheckpoint = 0.0


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Error] Failed to load state file: {e}", flush=True)
    return None


def save_state():
    bot_state = {
        "walletStash": round(float(walletStash), 8),
        "startingPocketChange": round(float(startingPocketChange), 8),
        "tinyPeanutSize": round(float(tinyPeanutSize), 8),
        "backupPeanut": round(float(backupPeanut), 8),
        "tenPeanuts": round(float(tenPeanuts), 8),
        "previousWalletState": round(float(previousWalletState), 8),
        "currentWagerAmount": round(float(currentWagerAmount), 8),
        "previousWagerAmount": round(float(previousWagerAmount), 8),
        "checkpointJuice": round(float(checkpointJuice), 8),
        "wobbleFactor": wobbleFactor,
        "safetyCheckpoint": round(float(safetyCheckpoint), 8),
        "last_seen_timestamp": time.time(),
    }
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(bot_state, f)
    except Exception as e:
        print(f"[Error] Failed to save state file: {e}", flush=True)


def calculate_next_progression_step(incoming_wager):
    global walletStash, currentWagerAmount, wobbleFactor, checkpointJuice, safetyCheckpoint

    base_wager = round(float(incoming_wager), 8)
    walletStash = round(float(walletStash), 8)
    checkpointJuice = round(float(checkpointJuice), 8)
    safetyCheckpoint = round(float(safetyCheckpoint), 8)

    if walletStash >= round(safetyCheckpoint + ((tinyPeanutSize * 10) * wobbleFactor), 8):
        currentWagerAmount = round(float(tinyPeanutSize), 8)
        wobbleFactor = 1.0
        checkpointJuice = round(float((math.floor(walletStash / (tinyPeanutSize * 10))) * (tinyPeanutSize * 10)), 8)
        safetyCheckpoint = round(float((math.floor(walletStash / (tinyPeanutSize * 10))) * (tinyPeanutSize * 10)), 8)
        return currentWagerAmount
    
    if base_wager > backupPeanut:
        if walletStash > round(checkpointJuice + (base_wager * 5.0), 8):
            currentWagerAmount = round(float(base_wager * 2.0), 8)
            checkpointJuice = round(float(walletStash), 8)
        elif walletStash < round(checkpointJuice - (base_wager * 5.0), 8):
            currentWagerAmount = round(float(base_wager * 2.0), 8)
            wobbleFactor = 0.0
            checkpointJuice = round(float(walletStash), 8)
        else:
            currentWagerAmount = base_wager
            
    if base_wager <= backupPeanut:
        if walletStash > round(checkpointJuice + round(base_wager * 7.0, 8), 8):
            currentWagerAmount = round(float(base_wager * 2.0), 8)
            checkpointJuice = round(float(walletStash), 8)
        elif walletStash < round(checkpointJuice - round(base_wager * 3.0, 8), 8):
            currentWagerAmount = round(float(base_wager * 2.0), 8)
            checkpointJuice = round(float(walletStash), 8)
        else:
            currentWagerAmount = base_wager

    return round(float(currentWagerAmount), 8)


def log_bet_info(bet_amount, current_balance, current_profit):
    print(f"Bet: {bet_amount:.8f} | Balance: {current_balance:.8f} | Profit: {current_profit:+.8f}", flush=True)


def main():
    global startingPocketChange, tinyPeanutSize, backupPeanut, tenPeanuts
    global walletStash, previousWalletState, currentWagerAmount, previousWagerAmount
    global checkpointJuice, wobbleFactor, safetyCheckpoint

    username = os.environ.get("JUST_DICE_USER", "")
    password = os.environ.get("JUST_DICE_PASS", "")
    code_2fa = os.environ.get("JUST_DICE_2FA", "")

    if not username or not password:
        print("[Error] Missing JUST_DICE_USER or JUST_DICE_PASS environment secrets.", flush=True)
        sys.exit(1)

    opt = Options()
    opt.add_argument("--headless")

    print("[System] Initializing Firefox headless browser driver for GitHub Actions...", flush=True)
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=opt)
    wait = WebDriverWait(driver, 35)

    try:
        print("[System] Navigating to just-dice.com...", flush=True)
        driver.get("https://just-dice.com")
        time.sleep(5)

        # Dismiss modal if present
        try:
            close_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.fancybox-item.fancybox-close")))
            close_btn.click()
        except Exception:
            pass

        # Click Account / Login
        try:
            account_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Account")))
            account_link.click()
        except Exception:
            pass

        time.sleep(2)
        print("[System] Submitting credentials...", flush=True)
        wait.until(EC.presence_of_element_located((By.ID, "myuser")))
        
        u_el = driver.find_element(By.ID, "myuser")
        p_el = driver.find_element(By.ID, "mypass")
        ok_el = driver.find_element(By.ID, "myok")

        u_el.clear()
        u_el.send_keys(username)
        p_el.clear()
        p_el.send_keys(password)

        if code_2fa and code_2fa.strip() != "":
            try:
                c_el = driver.find_element(By.ID, "mycode")
                c_el.clear()
                c_el.send_keys(code_2fa.strip())
            except Exception:
                pass

        ok_el.click()
        print("[System] Login submitted, waiting 10 seconds for stabilization...", flush=True)
        time.sleep(10)

        # Initialize balance and state
        bal_elem = wait.until(EC.presence_of_element_located((By.ID, "pct_balance")))
        current_bal = round(float(bal_elem.get_attribute("value").replace(",", "").strip()), 8)

        savedState = load_state()

        startingPocketChange = round(float(savedState.get("startingPocketChange", current_bal)), 8) if savedState else current_bal
        tinyPeanutSize = round(float(savedState.get("tinyPeanutSize", round(startingPocketChange / 1440000.0, 8))), 8) if savedState else round(startingPocketChange / 1440000.0, 8)
        backupPeanut = round(float(savedState.get("backupPeanut", tinyPeanutSize)), 8) if savedState else tinyPeanutSize
        tenPeanuts = round(float(savedState.get("tenPeanuts", tinyPeanutSize * 10)), 8) if savedState else tinyPeanutSize * 10

        walletStash = round(float(savedState.get("walletStash", startingPocketChange)), 8) if savedState else startingPocketChange
        previousWalletState = round(float(savedState.get("previousWalletState", walletStash)), 8) if savedState else walletStash
        
        currentWagerAmount = round(float(savedState.get("currentWagerAmount", backupPeanut)), 8) if savedState else backupPeanut
        previousWagerAmount = round(float(savedState.get("previousWagerAmount", currentWagerAmount)), 8) if savedState else currentWagerAmount

        default_chk = walletStash
        checkpointJuice = round(float(savedState.get("checkpointJuice", default_chk)), 8) if savedState else round(float(default_chk), 8)
        wobbleFactor = float(savedState.get("wobbleFactor", 1.0)) if savedState else 1.0
        safetyCheckpoint = round(float(savedState.get("safetyCheckpoint", default_chk)), 8) if savedState else round(float(default_chk), 8)

        last_observed_balance = current_bal
        last_balance_change_time = time.time()
        has_placed_first_bet = False
        watchdog_threshold = 10.0

        print(f"[System] Login verified! Balance loaded: {walletStash:.8f} (Baseline: {startingPocketChange:.8f})", flush=True)
        print("[Watchdog] Dynamic 10-second activity & betting stall watchdog is active.", flush=True)

        # Main betting loop for GitHub Actions
        start_run_time = time.time()
        while time.time() - start_run_time < 18000:  # Run up to 5 hours per execution
            time.sleep(0.5)
            try:
                bal_val = driver.find_element(By.ID, "pct_balance").get_attribute("value")
                walletStash = round(float(bal_val.replace(",", "").strip()), 8)
            except Exception:
                continue

            current_time = time.time()
            balance_changed = (walletStash == round((last_observed_balance + previousWagerAmount), 8) or walletStash == round((last_observed_balance - previousWagerAmount), 8))

            if walletStash > 0 and balance_changed:
                last_balance_change_time = current_time
                last_observed_balance = walletStash

            elapsed_stagnation = current_time - last_balance_change_time

            if elapsed_stagnation >= watchdog_threshold or walletStash <= 0:
                print(f"[Watchdog] Balance has stalled, refreshing page...", flush=True)
                driver.refresh()
                time.sleep(5)
                last_balance_change_time = time.time()
                has_placed_first_bet = False
                watchdog_threshold = min(watchdog_threshold + 5.0, 30.0)
                continue

            if walletStash >= round(startingPocketChange * 24, 8):
                profit = round(walletStash - startingPocketChange, 8)
                print(f"\n[Compound Milestone] Target profit reached (+{profit:.8f})!", flush=True)
                if os.path.exists(STATE_FILE):
                    os.remove(STATE_FILE)
                break

            if balance_changed or not has_placed_first_bet:
                has_placed_first_bet = True
                computedNextBet = calculate_next_progression_step(previousWagerAmount)

                if walletStash >= 144000:
                    print(f"[System] TARGET REACHED ({walletStash:.8f}). Halting execution.", flush=True)
                    if os.path.exists(STATE_FILE):
                        os.remove(STATE_FILE)
                    break

                log_bet_info(computedNextBet, walletStash, round(walletStash - startingPocketChange, 8))

                try:
                    driver.find_element(By.ID, "b_min").click()
                    p_chance = driver.find_element(By.ID, "pct_chance")
                    p_chance.clear()
                    p_chance.send_keys("49.5")

                    p_bet = driver.find_element(By.ID, "pct_bet")
                    p_bet.clear()
                    p_bet.send_keys(f"{computedNextBet:.8f}")

                    driver.find_element(By.ID, "a_lo").click()
                except Exception as bet_err:
                    print(f"[Error] Failed to place bet elements: {bet_err}", flush=True)

                previousWagerAmount = computedNextBet
                previousWalletState = walletStash
                watchdog_threshold = 10.0
                save_state()

    except Exception as e:
        print(f"[Error] Bot crashed: {e}", flush=True)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
