import streamlit as st
import pandas as pd

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
    # Удаляем акции с 0 и меньше акций
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
    # Используем акции с самой высокой ценой, чтобы покрыть сумму
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
            for stock, spend in user_payment.items():
                price = prices[stock]
                shares_needed = spend / price if price else 0
                if shares_needed > portfolio.get(stock, 0):
                    st.error(f"Not enough shares of {stock} to cover ${spend:.2f}.")
                    return None

            for stock, spend in user_payment.items():
                shares_to_deduct = spend / prices[stock]
                portfolio[stock] -= shares_to_deduct
                # Добавляем в историю
                st.session_state.transactions.append({
                    "Stock": stock,
                    "Shares": shares_to_deduct,
                    "Amount": spend,
                    "Mode": "Manual"
                })

            clean_portfolio(portfolio)
            st.success("Manual payment successful!")
            return user_payment

    return None

def show_success_checkmark():
    # Показываем белую галочку на весь экран
    checkmark_style = """
    <style>
    .checkmark-screen {
        position: fixed;
        top:0; left:0; width: 100vw; height: 100vh;
        background-color: white;
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    }
    .checkmark {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        border: 10px solid #4BB543;
        position: relative;
    }
    .checkmark:after {
        content: '';
        position: absolute;
        left: 40px;
        top: 70px;
        width: 35px;
        height: 70px;
        border-right: 10px solid #4BB543;
        border-bottom: 10px solid #4BB543;
        transform: rotate(45deg);
        transform-origin: left top;
    }
    </style>
    <div class="checkmark-screen">
      <div class="checkmark"></div>
    </div>
    """
    st.markdown(checkmark_style, unsafe_allow_html=True)

payment_done = False

if mode == "AI selects stocks":
    st.subheader("AI Payment Mode")
    payment, shortage = pay_with_ai(amount_due, st.session_state.portfolio, prices)
    if payment is None:
        st.error(f"Insufficient stocks to cover the payment. Short by ${shortage:.2f}")
    else:
        st.write("AI suggests selling:")
        for stock, shares in payment.items():
            st.write(f"- {shares:.4f} shares of {stock} at ${prices[stock]:.2f} per share")
        if st.button("Confirm AI payment"):
            for stock, shares in payment.items():
                st.session_state.portfolio[stock] -= shares
                st.session_state.transactions.append({
                    "Stock": stock,
                    "Shares": shares,
                    "Amount": shares * prices[stock],
                    "Mode": "AI"
                })
            clean_portfolio(st.session_state.portfolio)
            st.success("AI payment successful!")
            payment_done = True

elif mode == "I select stocks":
    manual_payment = pay_manually(amount_due, st.session_state.portfolio, prices)
    if manual_payment is not None:
        payment_done = True

st.markdown("---")

# --- Show transaction history ---
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
    tx_df = pd.DataFrame(tx_data, columns=["Stock", "Shares Sold", "Amount (USD)", "Payment Mode"])
    st.table(tx_df)
else:
    st.write("No transactions yet.")

# --- Show white checkmark fullscreen on payment success ---
if payment_done:
    show_success_checkmark()
