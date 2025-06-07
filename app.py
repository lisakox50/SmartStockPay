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
    return sum(shares * prices.get(stock, 0) for stock, shares in portfolio.items())

def clean_portfolio(portfolio):
    to_delete = [stock for stock, shares in portfolio.items() if shares <= 0]
    for stock in to_delete:
        del portfolio[stock]

def show_success_checkmark():
    st.markdown(
        """
        <style>
        .checkmark-screen {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background-color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            user-select: none;
        }
        .checkmark {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            border: 12px solid #4BB543;
            position: relative;
        }
        .checkmark:after {
            content: '';
            position: absolute;
            left: 40px;
            top: 65px;
            width: 35px;
            height: 70px;
            border-right: 12px solid #4BB543;
            border-bottom: 12px solid #4BB543;
            transform: rotate(45deg);
            transform-origin: left top;
        }
        </style>
        <div class="checkmark-screen">
            <div class="checkmark"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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

payment_mode = st.radio("Select payment mode:", ["AI selects stocks", "I select stocks"])

payment_done = False

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

def pay_manually(amount, portfolio, prices):
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
            # Validate shares
            for stock, spend in user_payment.items():
                price = prices[stock]
                shares_needed = spend / price if price else 0
                if shares_needed > portfolio.get(stock, 0):
                    st.error(f"Not enough shares of {stock} to cover ${spend:.2f}.")
                    return None
            # Deduct shares and record transactions
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
            st.success("Manual payment successful!")
            return True
    return None

if st.button("Pay"):
    if amount_due > total_value:
        st.error("Insufficient portfolio value to cover payment.")
    else:
        if payment_mode == "AI selects stocks":
            payment, remaining = pay_with_ai(amount_due, st.session_state.portfolio, prices)
            if payment is None:
                st.error(f"Cannot cover the amount with your stocks. ${remaining:.2f} short.")
            else:
                for stock, shares_used in payment.items():
                    st.session_state.portfolio[stock] -= shares_used
                    st.session_state.transactions.append({
                        "Stock": stock,
                        "Shares": shares_used,
                        "Amount": shares_used * prices[stock],
                        "Mode": "AI"
                    })
                clean_portfolio(st.session_state.portfolio)
                payment_done = True
        else:
            result = pay_manually(amount_due, st.session_state.portfolio, prices)
            if result:
                payment_done = True

if payment_done:
    show_success_checkmark()
    time.sleep(3)
    st.experimental_rerun()

st.markdown("### Transaction History")
if st.session_state.transactions:
    tx_df = pd.DataFrame(st.session_state.transactions)
    st.table(tx_df)
else:
    st.write("No transactions yet.")
