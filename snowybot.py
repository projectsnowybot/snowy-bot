import time
import json
import math
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Read credentials safely from GitHub Secrets environment variables
USERNAME = os.environ.get("JUST_DICE_USER", "")
PASSWORD = os.environ.get("JUST_DICE_PASS", "")
CODE_2FA = os.environ.get("JUST_DICE_2FA", "") # Optional: Ignored if left blank

STATE_FILE = "bot_state.json"

startingPocketChange = 0.0
tinyPeanutSize = 0.0
backupPeanut = 0.0
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
        except:
            pass
    return None

def save_state():
    state = {
        "walletStash": round(float(walletStash), 8),
        "startingPocketChange": round(float(startingPocketChange), 8),
        "tinyPeanutSize": round(float(tinyPeanutSize), 8),
        "backupPeanut": round(float(backupPeanut), 8),
        "previousWagerAmount": round(float(previousWagerAmount), 8),
        "checkpointJuice": round(float(checkpointJuice), 8),
        "wobbleFactor": wobbleFactor,
        "safetyCheckpoint": round(float(safetyCheckpoint), 8),
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

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
        safetyCheckpoint = checkpointJuice
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
    else:
        if walletStash > round(checkpointJuice + round(base_wager * 7.0, 8), 8):
            currentWagerAmount = round(float(base_wager * 2.0), 8)
            checkpointJuice = round(float(walletStash), 8)
        elif walletStash < round(checkpointJuice - round(base_wager * 3.0, 8), 8):
            currentWagerAmount = round(float(base_wager * 2.0), 8)
            checkpointJuice = round(float(walletStash), 8)
        else:
            currentWagerAmount = base_wager

    return round(float(currentWagerAmount), 8)

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print("[System] Navigating to just-dice.com...")
    driver.get("https://just-dice.com")
    time.sleep(5)

    try:
        close_btn = driver.find_element(By.CSS_SELECTOR, "a.fancybox-item.fancybox-close")
        close_btn.click()
    except:
        pass

    try:
        user_el = driver.find_element(By.ID, "myuser")
        pass_el = driver.find_element(By.ID, "mypass")
        ok_el = driver.find_element(By.ID, "myok")
        
        print("[System] Submitting credentials...")
        user_el.send_keys(USERNAME)
        pass_el.send_keys(PASSWORD)
        
        # Optional 2FA Check: Only executes if CODE_2FA secret is provided and not empty
        if CODE_2FA and CODE_2FA.strip() != "":
            try:
                code_el = driver.find_element(By.ID, "mycode")
                code_el.send_keys(CODE_2FA.strip())
                print("[System] 2FA code provided and entered.")
            except Exception as e:
                print("[System] 2FA input field not found on page, skipping.")
        else:
            print("[System] No 2FA code provided, skipping 2FA step.")

        ok_el.click()
        time.sleep(5)
    except Exception as e:
        print("[System] Login fields not found or already logged in.")

    bal_elem = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "pct_balance"))
    )
    current_bal = float(bal_elem.get_attribute("value").replace(",", "").strip())
    print(f"[System] Initial Balance Read: {current_bal:.8f}")

    savedState = load_state()
    startingPocketChange = savedState.get("startingPocketChange", current_bal) if savedState else current_bal
    tinyPeanutSize = savedState.get("tinyPeanutSize", round(startingPocketChange / 1440000.0, 8)) if savedState else round(startingPocketChange / 1440000.0, 8)
    backupPeanut = savedState.get("backupPeanut", tinyPeanutSize) if savedState else tinyPeanutSize
    walletStash = savedState.get("walletStash", startingPocketChange) if savedState else startingPocketChange
    previousWalletState = savedState.get("previousWalletState", walletStash) if savedState else walletStash
    currentWagerAmount = savedState.get("currentWagerAmount", backupPeanut) if savedState else backupPeanut
    previousWagerAmount = savedState.get("previousWagerAmount", currentWagerAmount) if savedState else currentWagerAmount
    checkpointJuice = savedState.get("checkpointJuice", walletStash) if savedState else walletStash
    wobbleFactor = savedState.get("wobbleFactor", 1.0) if savedState else 1.0
    safetyCheckpoint = savedState.get("safetyCheckpoint", walletStash) if savedState else walletStash

    last_observed_balance = current_bal
    last_balance_change_time = time.time()
    has_first_bet = False

    print("[System] Starting betting loop...")

    # Run for up to 5 hours per workflow execution
    start_run_time = time.time()
    while time.time() - start_run_time < 18000:
        time.sleep(0.5)
        try:
            bal_val = driver.find_element(By.ID, "pct_balance").get_attribute("value")
            walletStash = round(float(bal_val.replace(",", "").strip()), 8)
        except:
            continue

        current_time = time.time()
        balance_changed = (walletStash == round(last_observed_balance + previousWagerAmount, 8) or walletStash == round(last_observed_balance - previousWagerAmount, 8))

        if walletStash > 0 and balance_changed:
            last_balance_change_time = current_time
            last_observed_balance = walletStash

        # Watchdog stall check (10 seconds)
        if (current_time - last_balance_change_time) >= 10.0 or walletStash <= 0:
            print("[Watchdog] Balance stalled or zero. Refreshing page...")
            driver.refresh()
            time.sleep(5)
            last_balance_change_time = time.time()
            continue

        if balance_changed or not has_first_bet:
            has_first_bet = True
            computed_next_bet = calculate_next_progression_step(previousWagerAmount)

            if walletStash >= 144000:
                print(f"[System] Target reached ({walletStash:.8f}). Halting.")
                if os.path.exists(STATE_FILE):
                    os.remove(STATE_FILE)
                break

            profit = round(walletStash - startingPocketChange, 8)
            print(f"Bet: {computed_next_bet:.8f} | Balance: {walletStash:.8f} | Profit: {profit:+.8f}")

            driver.find_element(By.ID, "b_min").click()
            chance_el = driver.find_element(By.ID, "pct_chance")
            chance_el.clear()
            chance_el.send_keys("49.5")

            bet_el = driver.find_element(By.ID, "pct_bet")
            bet_el.clear()
            bet_el.send_keys(f"{computed_next_bet:.8f}")

            driver.find_element(By.ID, "a_lo").click()

            previousWagerAmount = computed_next_bet
            previousWalletState = walletStash
            save_state()

except Exception as e:
    print("[Error] Bot crashed:", e)
finally:
    driver.quit()
