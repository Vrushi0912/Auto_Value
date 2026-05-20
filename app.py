from website import create_app 

app = create_app() 

@app.template_filter('format_price') 
def format_price(price_str): 
    try: 
        price = float(price_str.replace(',', '')) 
        if price >= 100000: 
            return "{:.2f} Lakh".format(price / 100000) 
        else: 
            return "{:,.0f}".format(price) 
    except ValueError: 
        return price_str  # Return the original string if it cannot be converted to float 

if __name__ == "__main__": 
    app.run(debug=True, port=8700) 
