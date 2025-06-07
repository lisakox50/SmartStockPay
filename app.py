import streamlit as st
import datetime

# Инициализация
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

if 'user_holdings' not in st.session_state:
    st.session_state.user_holdings = {
        "AAPL": 2.5,
        "GOOGL": 1.8,
        "TSLA": 3.0,
        "AMZN": 4.2,
    }

stock_prices = {
    "AAPL": 180.00,
    "GOOGL": 135.50,
    "TSLA": 220.20,
    "AMZN": 127.80,
}

st.set_page_config(page_title="SmartStockPay", page_icon="💸")
st.title("SmartStockPay 💸")
st.markdown("## Use your stocks to pay instantly and smartly")

# Показываем портфель
st.markdown("### 📈 Your Portfolio")
total_portfolio_value = 0
for stock, shares in st.session_state.user_holdings.items():
    price = stock_prices[stock]
    value = shares * price
    total_portfolio_value += value
    st.write(f"**{stock}**: {shares:.4f} shares × ${price} = **${value:.2f}**")

st.markdown(f"**Total portfolio value: ${total_portfolio_value:.2f}**")
st.markdown("---")

# Сумма к оплате
amount_due = st.number_input("Enter amount to pay ($):", min_value=1.0, step=0.01)

# Оплата несколькими акциями
st.markdown("### Select stocks to pay with (partial payments allowed)")

payment_stocks = {}
remaining_due = amount_due

for stock, shares in st.session_state.user_holdings.items():
    price = stock_prices[stock]
    max_value = shares * price

    st.write(f"{stock}: {shares:.4f} shares available (${max_value:.2f})")

    max_spend = min(max_value, remaining_due)
    if max_spend > 0:
        spend = st.number_input(f"How much $ to spend from {stock} (max ${max_spend:.2f}):", 
                                min_value=0.0, max_value=max_spend, step=0.01, key=stock)
        if spend > 0:
            shares_to_sell = spend / price
            payment_stocks[stock] = (shares_to_sell, spend)
            remaining_due -= spend
            remaining_due = round(remaining_due, 2)

if remaining_due > 0:
    st.warning(f"⚠️ You still need to cover ${remaining_due:.2f}. Please adjust payments.")
else:
    if st.button("Confirm Payment"):
        # Проверяем, что у пользователя хватает акций
        enough_shares = True
        for stock, (shares_to_sell, spend) in payment_stocks.items():
            if shares_to_sell > st.session_state.user_holdings[stock]:
                enough_shares = False
                st.error(f"Not enough shares of {stock} to cover ${spend:.2f}")
        if enough_shares:
            # Списываем акции
            for stock, (shares_to_sell, spend) in payment_stocks.items():
                st.session_state.user_holdings[stock] -= shares_to_sell
                st.session_state.transactions.append({
                    "stock": stock,
                    "shares": shares_to_sell,
                    "value": spend,
                    "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })
            st.success("✅ Payment successful! All stocks updated.")
            st.balloons()

st.markdown("---")
st.markdown("### 🧾 Transaction History")
if st.session_state.transactions:
    for tx in reversed(st.session_state.transactions):
        st.write(f"{tx['date']}: Sold {tx['shares']:.4f} shares of {tx['stock']} for ${tx['value']:.2f}")
else:
    st.write("No transactions yet.")
