import streamlit as st
import datetime

st.set_page_config(page_title="SmartStockPay", page_icon="💸")
st.title("SmartStockPay - Pay with Stocks 💸")

# --- Инициализация портфеля пользователя ---
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {
        "AAPL": 10,
        "MSFT": 5,
        "TSLA": 8,
        "AMZN": 3,
    }

if "transactions" not in st.session_state:
    st.session_state.transactions = []

# --- Фиктивные цены для теста (замени на реальный API) ---
prices = {
    "AAPL": 170.25,
    "MSFT": 305.40,
    "TSLA": 680.10,
    "AMZN": 140.50,
}

# --- Функция подсчёта стоимости портфеля ---
def get_portfolio_value(portfolio, prices):
    total = 0
    for stock, shares in portfolio.items():
        price = prices.get(stock)
        if price:
            total += shares * price
    return total

# --- Отображаем портфель ---
st.header("Your Portfolio")
total_value = get_portfolio_value(st.session_state.portfolio, prices)
for stock, shares in st.session_state.portfolio.items():
    price = prices.get(stock)
    value = shares * price if price else 0
    st.write(f"{stock}: {shares:.4f} shares × ${price:.2f} = **${value:.2f}**")

st.write(f"**Total Portfolio Value: ${total_value:.2f}**")
st.markdown("---")

# --- Ввод суммы к оплате ---
amount_due = st.number_input("Enter amount to pay ($):", min_value=0.01, step=0.01, format="%.2f")

# --- Выбор способа оплаты ---
mode = st.radio("Choose payment mode:", ["AI selects stocks", "I select stocks"])

def pay_with_ai(amount, portfolio, prices):
    remaining = amount
    payment = {}
    # Сортируем акции по убыванию цены, чтобы тратить дорогие акции в первую очередь
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
        return None, remaining  # Не хватает средств
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
    else:
        if st.button("Confirm manual payment"):
            # Проверка на достаточность акций
            for stock, spend in user_payment.items():
                price = prices[stock]
                shares_needed = spend / price if price else 0
                if shares_needed > portfolio.get(stock, 0):
                    st.error(f"Not enough shares of {stock} to cover ${spend:.2f}.")
                    return None

            # Вычитаем акции из портфеля
            for stock, spend in user_payment.items():
                shares_to_deduct = spend / prices[stock]
                portfolio[stock] -= shares_to_deduct

            st.success("Manual payment successful! 🎉")
            return user_payment

    return None

# --- Логика оплаты ---
if mode == "AI selects stocks":
    st.subheader("AI Payment Mode")
    payment, shortage = pay_with_ai(amount_due, st.session_state.portfolio, prices)
    if payment is None:
        st.error(f"Not enough stocks to cover the payment. Short by ${shortage:.2f}")
    else:
        st.write("AI suggests selling:")
        for stock, shares in payment.items():
            st.write(f"- {shares:.4f} shares of {stock} at ${prices[stock]:.2f} each")

        if st.button("Pay with AI-selected stocks"):
            # Вычитаем акции из портфеля
            for stock, shares in payment.items():
                st.session_state.portfolio[stock] -= shares
            # Записываем транзакцию
            st.session_state.transactions.append({
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": "AI",
                "details": payment,
                "amount": amount_due
            })
            st.success("Payment successful! 🎉")
            st.balloons()

else:
    payment_result = pay_manually(amount_due, st.session_state.portfolio, prices)
    if payment_result:
        st.session_state.transactions.append({
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "Manual",
            "details": payment_result,
            "amount": amount_due
        })

# --- История транзакций ---
if st.session_state.transactions:
    st.markdown("---")
    st.header("Payment History")
    for tx in reversed(st.session_state.transactions):
        st.write(f"**{tx['date']} — {tx['type']} payment — ${tx['amount']:.2f}**")
        for stock, val in tx['details'].items():
            if tx['type'] == "AI":
                st.write(f"- {val:.4f} shares of {stock}")
            else:
                st.write(f"- ${val:.2f} from {stock}")
