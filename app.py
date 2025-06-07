import streamlit as st
import yfinance as yf
import datetime

st.set_page_config(page_title="SmartStockPay", page_icon="💸")
st.title("SmartStockPay - Pay with Stocks 💸")

# --- Инициализация портфеля пользователя (пример) ---
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {
        "AAPL": 10,      # количество акций Apple
        "MSFT": 5,       # Microsoft
        "TSLA": 8,       # Tesla
        "AMZN": 3,       # Amazon
    }

if "transactions" not in st.session_state:
    st.session_state.transactions = []

# --- Получаем актуальные цены акций ---
def get_stock_prices(tickers):
    data = yf.download(tickers, period="1d", progress=False)
    prices = {}
    for ticker in tickers:
        try:
            prices[ticker] = data['Close'][-1]
        except Exception:
            prices[ticker] = None
    return prices

tickers = list(st.session_state.portfolio.keys())
prices = get_stock_prices(tickers)

# --- Отображение портфеля с актуальными ценами ---
st.header("Your Portfolio")
total_value = 0
for stock, shares in st.session_state.portfolio.items():
    price = prices.get(stock)
    if price:
        value = shares * price
        total_value += value
        st.write(f"{stock}: {shares} shares × ${price:.2f} = **${value:.2f}**")
    else:
        st.write(f"{stock}: {shares} shares × Price unavailable")

st.write(f"**Total portfolio value: ${total_value:.2f}**")
st.markdown("---")

# --- Ввод суммы для оплаты ---
amount_due = st.number_input("Enter the amount to pay ($):", min_value=0.01, step=0.01, format="%.2f")

# --- Выбор режима оплаты ---
mode = st.radio("Choose payment mode:", ["AI selects stocks", "I select stocks"])

# --- Оплата AI ---
if mode == "AI selects stocks":
    st.subheader("AI Payment Mode")
    remaining = amount_due
    payment = {}

    # Сортируем акции по цене за акцию по убыванию
    sorted_stocks = sorted(prices.items(), key=lambda x: x[1] if x[1] else 0, reverse=True)

    for stock, price in sorted_stocks:
        if price is None:
            continue
        shares_available = st.session_state.portfolio.get(stock, 0)
        max_value = shares_available * price
        if max_value <= 0:
            continue
        if max_value >= remaining:
            shares_needed = remaining / price
            payment[stock] = shares_needed
            remaining = 0
            break
        else:
            payment[stock] = shares_available
            remaining -= max_value

    if remaining > 0:
        st.error(f"Not enough stocks to cover ${amount_due:.2f}. Short by ${remaining:.2f}.")
    else:
        st.write("AI suggests selling:")
        for stock, shares in payment.items():
            st.write(f"- {shares:.4f} shares of {stock} (${prices[stock]:.2f} each)")

        if st.button("Pay with AI-selected stocks"):
            # Обновляем портфель и добавляем транзакцию
            for stock, shares in payment.items():
                st.session_state.portfolio[stock] -= shares
            st.session_state.transactions.append({
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": "AI",
                "details": payment,
                "amount": amount_due
            })
            st.success("Payment successful! 🎉")
            st.balloons()

# --- Ручной режим оплаты ---
else:
    st.subheader("Manual Payment Mode")
    remaining_due = amount_due
    user_payment = {}
    for stock, shares_available in st.session_state.portfolio.items():
        price = prices.get(stock)
        if price is None:
            st.write(f"{stock}: price unavailable")
            continue

        max_value = shares_available * price
        st.write(f"{stock}: {shares_available} shares available (${max_value:.2f})")
        max_spend = min(max_value, remaining_due)
        spend = st.number_input(f"How much $ to spend from {stock} (max ${max_spend:.2f}):",
                                min_value=0.0, max_value=max_spend, step=0.01, format="%.2f", key=stock)

        if spend > 0:
            shares_to_sell = spend / price
            user_payment[stock] = shares_to_sell
            remaining_due -= spend
            remaining_due = round(remaining_due, 2)

    if remaining_due > 0:
        st.warning(f"⚠️ You still need to cover ${remaining_due:.2f}. Please adjust payments.")
    else:
        if st.button("Confirm Payment"):
            # Проверяем хватает ли акций
            valid = True
            for stock, shares in user_payment.items():
                if shares > st.session_state.portfolio.get(stock, 0):
                    st.error(f"Not enough shares of {stock}.")
                    valid = False
            if valid:
                for stock, shares in user_payment.items():
                    st.session_state.portfolio[stock] -= shares
                st.session_state.transactions.append({
                    "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "type": "Manual",
                    "details": user_payment,
                    "amount": amount_due
                })
                st.success("Payment successful! 🎉")
                st.balloons()

# --- История транзакций ---
st.markdown("---")
st.header("Transaction History")
if st.session_state.transactions:
    for tx in reversed(st.session_state.transactions):
        tx_details = ", ".join([f"{shares:.4f} shares {stock}" for stock, shares in tx["details"].items()])
        st.write(f"{tx['date']} — {tx['type']} payment — ${tx['amount']:.2f} using {tx_details}")
else:
    st.write("No transactions yet.")
