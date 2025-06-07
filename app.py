import streamlit as st
import datetime
import qrcode
from io import BytesIO
from PIL import Image

# Инициализация при запуске
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

if 'user_holdings' not in st.session_state:
    st.session_state.user_holdings = {
        "AAPL": 2.5,
        "GOOGL": 1.8,
        "TSLA": 3.0,
        "AMZN": 4.2,
    }

# Текущие цены акций
stock_prices = {
    "AAPL": 180.00,
    "GOOGL": 135.50,
    "TSLA": 220.20,
    "AMZN": 127.80,
}

st.set_page_config(page_title="SmartStockPay", page_icon="💸")
st.title("SmartStockPay 💸")
st.subheader("Pay with your stocks — instantly and smartly.")

# Показываем портфель
st.markdown("### 📊 Your Portfolio")
for stock, shares in st.session_state.user_holdings.items():
    price = stock_prices[stock]
    total_value = round(shares * price, 2)
    st.write(f"**{stock}** — {shares} shares x ${price} = **${total_value}**")

st.markdown("---")

# Ввод суммы
amount_due = st.number_input("💰 Enter amount to pay ($):", min_value=1.0)

# Выбор способа
payment_type = st.radio("How would you like to pay?", ["AI selects best stock", "I choose stock and amount"])

if payment_type == "AI selects best stock":
    # AI выбирает
    best_stock = max(stock_prices, key=lambda k: stock_prices[k] if st.session_state.user_holdings[k] > 0 else 0)
    price = stock_prices[best_stock]
    max_available = st.session_state.user_holdings[best_stock] * price

    if max_available >= amount_due:
        shares_needed = round(amount_due / price, 4)
        st.write(f"🤖 AI selected **{best_stock}**.")
        st.write(f"Sell **{shares_needed} shares** at ${price} = ${amount_due}")
        confirm = st.button("Pay with AI-selected stock")

        if confirm:
            st.session_state.user_holdings[best_stock] -= shares_needed
            transaction = {
                "stock": best_stock,
                "shares": shares_needed,
                "value": amount_due,
                "date": str(datetime.datetime.now())[:19],
                "type": "AI"
            }
            st.session_state.transactions.append(transaction)
            st.success("✅ Payment successful!")
            st.balloons()

    else:
        st.error(f"Not enough {best_stock} stock to cover ${amount_due}. You have only ${max_available:.2f}")

else:
    # Пользователь сам выбирает
    stock = st.selectbox("Choose stock to use:", list(st.session_state.user_holdings.keys()))
    owned_shares = st.session_state.user_holdings[stock]
    price = stock_prices[stock]
    max_value = round(owned_shares * price, 2)

    st.write(f"🪙 You have {owned_shares} shares of {stock} (${price} each) = ${max_value}")

    shares_to_use = st.number_input("How many shares to sell:", min_value=0.0, max_value=owned_shares, step=0.01)
    value_used = round(shares_to_use * price, 2)
    remaining = round(amount_due - value_used, 2)

    if shares_to_use > 0:
        st.write(f"💳 This will cover **${value_used}** of the ${amount_due}")

    if st.button("Confirm Payment"):
        st.session_state.user_holdings[stock] -= shares_to_use
        transaction = {
            "stock": stock,
            "shares": shares_to_use,
            "value": value_used,
            "date": str(datetime.datetime.now())[:19],
            "type": "Manual"
        }
        st.session_state.transactions.append(transaction)
        st.success("✅ Payment successful!")
        st.balloons()

        # Генерируем QR-код как чек
        qr = qrcode.make(f"{shares_to_use} shares of {stock} = ${value_used} on {transaction['date']}")
        buffer = BytesIO()
        qr.save(buffer)
        st.image(Image.open(buffer), caption="🧾 Payment Receipt QR Code")

# История транзакций
st.markdown("---")
st.markdown("### 🧾 Transaction History")
if st.session_state.transactions:
    for t in st.session_state.transactions[::-1]:
        st.write(f"📅 {t['date']} — {t['shares']} shares of {t['stock']} used = ${t['value']} ({t['type']})")
else:
    st.info("No transactions yet.")
