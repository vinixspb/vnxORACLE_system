# 🏛 vnxSYSTEMS: Server Infrastructure & Command Center

**Environment:** VDS (Ubuntu/Debian)
**Root Path:** `/opt/`

## 🕹 Command Center Configuration
Ниже приведена актуальная конфигурация `.bashrc` для управления всеми системами через терминал.

### 📋 .bashrc Content (Do not change without review)

```bash
# =========================================================
# 🏛 vnxSYSTEMS: COMMAND CENTER (ROOT)
# =========================================================

# --- 1. vnxMATRIX (VPN Core) ---
alias matrix-cd='cd /opt/vnxMATRIX_system_bot'
alias matrix-restart='systemctl restart vnxMATRIX_system_bot && journalctl -u vnxMATRIX_system_bot -f'
alias matrix-logs='journalctl -u vnxMATRIX_system_bot -f'
alias matrix-stop='systemctl stop vnxMATRIX_system_bot'
alias matrix-start='systemctl start vnxMATRIX_system_bot'

# --- 2. vnxORACLE (AI Core) ---
alias oracle-cd='cd /opt/vnxORACLE_system'
alias oracle-restart='systemctl restart vnx-oracle && journalctl -u vnx-oracle -f'
alias oracle-logs='journalctl -u vnx-oracle -f'
alias oracle-stop='systemctl stop vnx-oracle'
alias oracle-start='systemctl start vnx-oracle'

# --- 3. KegPro System ---
alias keg-cd='cd /opt/KegPro_system'
alias keg-restart='systemctl restart keg_pro && journalctl -u keg_pro -f'
alias keg-logs='journalctl -u keg_pro -f'
alias keg-stop='systemctl stop keg_pro'
alias keg-start='systemctl start keg_pro'  # <--- ДОБАВЛЕНО

# --- 4. SHOROHI System ---
alias shorohi-cd='cd /opt/SHOROHI_system'
alias shorohi-restart='systemctl restart shorohi && journalctl -u shorohi -f'
alias shorohi-logs='journalctl -u shorohi -f'
alias shorohi-stop='systemctl stop shorohi'
alias shorohi-start='systemctl start shorohi' # <--- ДОБАВЛЕНО

# --- 5. vnxChooseApple ---
alias apple-cd='cd /opt/vnxChooseApple_bot'
alias apple-restart='systemctl restart vnx-apple-shop && journalctl -u vnx-apple-shop -f'
alias apple-logs='journalctl -u vnx-apple-shop -f'
alias apple-stop='systemctl stop vnx-apple-shop'
alias apple-start='systemctl start vnx-apple-shop' # <--- ДОБАВЛЕНО

# =========================================================
# 📟 STATUS DASHBOARD
# =========================================================
echo -e "\n\033[1;36m👋 ARCHITECT TERMINAL ONLINE\033[0m"
echo "📂 PWD: $(pwd)"
echo "---------------------------------------------------"
printf "%-15s | %-10s | %s\n" "SYSTEM" "STATUS" "COMMANDS"
echo "---------------------------------------------------"
printf "%-15s | %-10s | %s\n" "🕶 vnxMATRIX" "$(systemctl is-active vnxMATRIX_system_bot)" "matrix-restart"
printf "%-15s | %-10s | %s\n" "👁 vnxORACLE" "$(systemctl is-active vnx-oracle)" "oracle-restart"
printf "%-15s | %-10s | %s\n" "🍺 KegPro" "$(systemctl is-active keg_pro)" "keg-restart"
printf "%-15s | %-10s | %s\n" "👻 SHOROHI" "$(systemctl is-active shorohi)" "shorohi-restart"
printf "%-15s | %-10s | %s\n" "🍏 AppleShop" "$(systemctl is-active vnx-apple-shop)" "apple-restart"
echo "---------------------------------------------------"
echo " "
