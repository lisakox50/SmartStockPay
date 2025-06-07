import streamlit as st
import random

st.set_page_config(page_title="SmartStockPay", page_icon="💸")

st.title("💸 SmartStockPay")
st.subheader("Pay with your stocks — instantly.")

st.markdown("Choose how you want to pay for your purchase using your stock portfolio.")

# -------------------------------
# Sample stocks in portfolio
user_stocks = {
    "AAPL": 5,     # 5 Apple shares
    "TSLA": 3,     # 3 Tesla shares
    "GOOGL": 2,    # 2 Google shares
    "AMZN": 1,     # 1 Amazon share
}

# Simulate current stock prices (in $)
stock_prices = {
    "AAPL": random.uniform(170, 200),
    "TSLA": random.uniform(220, 260),
    "GOOGL": random.uniform(130, 150),
    "AMZN": random.uniform(3000, 3300)
}

# -------------------------------
st.write("### 🛒 Enter Purchase Amount")

purchase_amount = st.number_input("Amount to pay ($)", min_value=1.0, step=1.0)

payment_mode = st.radio("How do you want to pay?", ["Let AI choose best combination", "Choose stocks manually"])

def convert_to_stocks(amount):
    selected = {}
    remaining = amount

    # Sort stocks by value descending
    sorted_stocks = sorted(stock_prices.items(), key=lambda x: x[1], reverse=True)

    for symbol, price in sorted_stocks:
        shares_owned = user_stocks.get(symbol, 0)
        shares_to_use = min(remaining // price, shares_owned)

        if shares_to_use >= 1:
            selected[symbol] = int(shares_to_use)
            remaining -= shares_to_use * price

        if remaining <= 0:
            break

    return selected, remaining

# -------------------------------
if purchase_amount > 0:
    if payment_mode == "Let AI choose best combination":
        selected_stocks, leftover = convert_to_stocks(purchase_amount)

        if leftover > 5:
            st.error("❌ Not enough stock value to cover this amount.")
        else:
            st.success("✅ Payment Approved!")
            st.write("**Used Stocks:**")
            for s, q in selected_stocks.items():
                st.write(f"- {q} × {s} @ ${stock_prices[s]:.2f}")

            if leftover > 0:
                st.write(f"Remaining unpaid amount (covered by cash): ${leftover:.2f}")

    else:
        st.write("### 🧾 Choose stocks manually:")
        manual_selection = {}
        total_value = 0

        for symbol, qty in user_stocks.items():
            use = st.slider(f"{symbol} (${stock_prices[symbol]:.2f}) — you own {qty}", 0, qty, 0)
            manual_selection[symbol] = use
            total_value += use * stock_prices[symbol]

        st.write(f"Total selected: ${total_value:.2f}")

        if total_value >= purchase_amount:
            st.success("✅ Payment Approved!")
            st.write("**Used Stocks:**")
            for s, q in manual_selection.items():
                if q > 0:
                    st.write(f"- {q} × {s} @ ${stock_prices[s]:.2f}")
