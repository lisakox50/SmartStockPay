import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="SmartStockPay", page_icon="💼")
st.title("SmartStockPay - Pay with Stocks")

# --- Initialize user portfolio ---
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {
        "AAPL": 10,
        "MSFT": 5,
        "TSLA": 8,
        "AMZN": 3,
    }

# --- Initialize transaction history ---
if "transactions" not in st.session_state:
    st.session_state.transactions = []

# --- Fake prices for demo ---
prices = {
    "AAPL": 170.25,
    "MSFT": 305.40,
    "TSLA": 680.10,
    "AMZN": 140.50,
}

def get_portfolio_value(portfolio, prices):
    total = 0
    for stock, shares in portfolio.items():
        price = prices.get(stock, 0)
        total += shares * price
    return total

def clean_portfolio(portfolio):
    to_del = [stock for stock, shares in portfolio.items() if shares <= 0]
    for stock in to_del:
        del portfolio[stock]

st.header("Your Portfolio")

data = []
for stock, shares in st.session_state.portfolio.items():
    price = prices.get(stock, 0)
    value = shares * price
    data.append([stock, f"{shares:.4f}", f"${price:.2f}", f"${value:.2f}"])

df = pd.DataFrame(data, columns=["Stock", "Shares", "Price per Share", "Total Value"])
st.table(df)

total_value = get_portfolio_value(st.session_state.portfolio, prices)
st.markdown(f"**Total Portfolio Value: ${total_value:.2f}**")

st.markdown("---")

amount_due = st.number_input("Enter amount to pay (USD):", min_value=0.01, step=0.01, format="%.2f")

mode = st.radio("Select payment mode:", ["AI selects stocks", "I select stocks"])

def pay_with_ai(amount, portfolio, prices):
    remaining = amount
    payment = {}
    sorted_stocks = sorted(prices.items(), key=lambda x: x[1], reverse=True)

    for stock, price in sorted_stocks:
        shares_available = portfolio.get(stock, 0)
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
        return None, remaining
    return payment, 0

def manual_payment(amount, portfolio, prices):
    st.subheader("Manual Payment Mode")
    remaining_due = amount
    user_payment = {}

    for stock, shares_available in portfolio.items():
        price = prices.get(stock)
        if price is None:
            st.write(f"{stock}: price unavailable")
            continue

        max_value = shares_available * price
        st.write(f"{stock}: {shares_available:.4f} shares available (${max_value:.2f})")
        max_spend = min(max_value, remaining_due)

        spend = st.number_input(
            f"Amount to pay from {stock} (max ${max_spend:.2f}):",
            min_value=0.0,
            max_value=max_spend,
            step=0.01,
            format="%.2f",
            key=f"manual_{stock}"
        )

        user_payment[stock] = spend
        remaining_due -= spend

    if remaining_due > 0:
        st.warning(f"You still need to cover ${remaining_due:.2f}. Please adjust the amounts.")
        return None
    else:
        if st.button("Confirm manual payment"):
            for stock, spend in user_payment.items():
                price = prices[stock]
                shares_needed = spend / price if price else 0
                if shares_needed > portfolio.get(stock, 0):
                    st.error(f"Not enough shares of {stock} to cover ${spend:.2f}.")
                    return None

            for stock, spend in user_payment.items():
                shares_to_deduct = spend / prices[stock]
                portfolio[stock] -= shares_to_deduct
                st.session_state.transactions.append({
                    "Stock": stock,
                    "Shares": shares_to_deduct,
                    "Amount": spend,
                    "Mode": "Manual"
                })

            clean_portfolio(portfolio)
            show_transaction_message()
            return user_payment

    return None

def show_transaction_message():
    # White text on transparent background, centered, displayed for 1 second
    st.markdown(
        """
        <div style="
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 32px;
            color: black;
            background-color: rgba(255, 255, 255, 0.8);
            padding: 20px 40px;
            border-radius: 15px;
            z-index: 9999;
            text-align: center;
            ">
            Transaction successful!
        </div>
        """,
        unsafe_allow_html=True
    )
    time.sleep(1)
    # After sleep Streamlit reruns and message disappears

if amount_due > 0:
    if mode == "AI selects stocks":
        if st.button("Pay with AI"):
            payment, remaining = pay_with_ai(amount_due, st.session_state.portfolio, prices)
            if payment is None:
                st.error(f"Insufficient shares to cover the amount. Short by ${remaining:.2f}.")
            else:
                for stock, shares_to_deduct in payment.items():
                    st.session_state.portfolio[stock] -= shares_to_deduct
                    st.session_state.transactions.append({
                        "Stock": stock,
                        "Shares": shares_to_deduct,
                        "Amount": shares_to_deduct * prices[stock],
                        "Mode": "AI"
                    })
                clean_portfolio(st.session_state.portfolio)
                show_transaction_message()

    else:
        manual_payment(amount_due, st.session_state.portfolio, prices)

st.markdown("---")

st.header("Transaction History")
if st.session_state.transactions:
    tx_data = []
    for tx in st.session_state.transactions:
        tx_data.append([
            tx["Stock"],
            f"{tx['Shares']:.4f}",
            f"${tx['Amount']:.2f}",
            tx["Mode"]
        ])
    tx_df = pd.DataFrame(tx_data, columns=["Stock", "Shares Used", "Amount Paid", "Payment Mode"])
    st.table(tx_df)
else:
    st.write("No transactions yet.")
