import streamlit as st
import datetime
import qrcode
from io import BytesIO
from PIL import Image

# Инициализация состояния
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
st.subheader("Pay with your stocks — instantly and smartly.")

# Портфель пользователя
st.markdown("### 📊 Your Portfolio")
for stock, shares in st.session_state.user_holdings.items():
    price = stock_prices[stock]
    total_value = round(shares * price, 2)
    st.write(f"**{stock}** — {shares} shares x ${price} = **${total_value}**")

st.markdown("---")

# Ввод суммы к оплате
amount_due = st.number_input("💰 Enter amount to pay ($):", min_value=1.0)

# Выбор способа оплаты
payment_type = st.radio("How would you like to pay?", ["AI selects best stock", "I choose stock and amount"])

if payment_type == "AI selects best stock":
    # AI выбирает акцию с максимальной стоимостью для оплаты
    best_stock = max(
        [s for s in stock_prices if st.session_state.user_holdings.get(s, 0) > 0],
        key=lambda k: stock_prices[k]
    )
    price = stock_prices[best_stock]
    max_available = st.session_state.user_holdings[best_stock] * price

    if max_available >= amount_due:
        shares_needed = round(amount_due / price, 4)
        st.write(f"🤖 AI selected **{best_stock}**.")
        st.write(f"Sell **{shares_needed} shares** at ${price} = ${amount_due}")

        if st.button("Pay with AI-selected stock"):
            st.session_state.user_holdings[best_stock] -= shares_needed
            transaction = {
                "stock": best_stock,
                "shares": shares_needed,
                "value": amount_due,
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": "AI"
            }
            st.session_state.transactions.append(transaction)
            st.success("✅ Payment successful!")
            st.balloons()

            # Генерация QR-кода
            qr = qrcode.make(f"Paid {shares_needed} shares of {best_stock} = ${amount_due} on {transaction['date']}")
            buffer = BytesIO()
            qr.save(buffer)
            st.image(Image.open(buffer), caption="🧾 Payment Receipt QR Code")

    else:
        st.error(f"Not enough {best_stock} stock to cover ${amount_due}. You have only ${max_available:.2f}")

else:
    # Пользователь сам выбирает акцию и количество
    stock = st.selectbox("Choose stock to use:", list(st.session_state.user_holdings.keys()))
    owned_shares = st.session_state.user_holdings[stock]
    price = stock_prices[stock]
    max_value = round(owned_shares * price, 2)

    st.write(f"🪙 You have {owned_shares} shares of {stock} (${price} each) = ${max_value}")

    shares_to_use = st.number_input(
        "How many shares to sell:",
        min_value=0.0,
        max_value=owned_shares,
        step=0.01,
        format="%.2f"
    )

    value_used = round(shares_to_use * price, 2)
    remaining = round(amount_due - value_used, 2)

    if shares_to_use > 0:
        st.write(f"💳 This will cover **${value_used}** of the ${amount_due}")

    if st.button("Confirm Payment"):
        if shares_to_use <= owned_shares and shares_to_use > 0:
            st.session_state.user_holdings[stock] -= shares_to_use
            transaction = {
                "stock": stock,
                "shares": shares_to_use,
                "value": value_used,
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": "Manual"
            }
            st.session_state.transactions.append(transaction)
            st.success("✅ Payment successful!")
            st.balloons()

            # Генерация QR-кода
            qr = qrcode.make(f"Paid {shares_to_use} shares of {stock} = ${value_used} on {transaction['date']}")
            buffer = BytesIO()
            qr.save(buffer)
            st.image(Image.open(buffer), caption="🧾 Payment Receipt QR Code")
        else:
            st.error("❌ Invalid number of shares")

st.markdown("---")
st.markdown("### 🧾 Transaction History")

if st.session_state.transactions:
    for tx in reversed(st.session_state.transactions):
        st.write(f"{tx['date']}: {tx['type']} payment of {tx['shares']:.4f} shares of {tx['stock']} for ${tx['value']:.2f}")
else:
    st.write("No transactions yet.")
