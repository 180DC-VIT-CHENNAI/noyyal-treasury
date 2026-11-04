def to_inr(amount,currency,fx): return amount*(1 if currency=='INR' else fx['usdinr_spot' if currency=='USD' else 'eurinr_spot'])
