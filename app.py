import streamlit as st

# Пример текущих цен акций
stock_prices = {
    "AAPL": 180.00,
    "GOOGL": 135.50,
    "TSLA": 220.20,
    "AMZN": 127.80,
}

st.set_page_config(page_title="SmartStockPay", page_icon="💸")
st.title("SmartStockPay 💸")
st.subheader("Turn your stock into real-world payments.")

# Пользователь вводит общую сумму оплаты
amount = st.number_input("Enter the total amount you want to spend ($):", min_value=1.0)

# Выбор способа оплаты
option = st.radio("How do you want to pay?", ["AI selects best stock", "I choose stock and amount"])

if option == "AI selects best stock":
    best_stock = max(stock_prices, key=stock_prices.get)
    stock_price = stock_prices[best_stock]
    shares_needed = round(amount / stock_price, 4)

    st.write(f"Smart AI selected **{best_stock}** for payment.")
    st.write(f"Current price: ${stock_price}")
    st.write(f"You need to sell **{shares_needed} shares** of {best_stock}.")

else:
    stock = st.selectbox("Choose the stock you want to use:", list(stock_prices.keys()))
    stock_price = stock_prices[stock]

    part_in_stock = st.number_input(
        f"How much of the ${amount} you want to pay using {stock}? ($)", 
        min_value=0.0, 
        max_value=amount, 
        step=0.01
    )
    part_in_card = round(amount - part_in_stock, 2)
    shares_to_sell = round(part_in_stock / stock_price, 4)

    st.write(f"Stock price of {stock}: ${stock_price}")
    st.write(f"You will use **{shares_to_sell} shares** of {stock} worth ${part_in_stock}")
    st.write(f"The remaining **${part_in_card}** can be paid by card or other method.")

# Кнопка оплаты
if st.button("Pay now"):
    st.success("✅ Payment completed successfully!")
    st.balloons()
