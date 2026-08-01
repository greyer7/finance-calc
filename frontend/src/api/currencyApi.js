import apiClient from './authApi'

export const getRates = (base = 'USD') =>
  apiClient.get('/currency/rates', { params: { base } })

export const convertCurrency = (amount, fromCurrency, toCurrency) =>
  apiClient.get('/currency/convert', {
    params: { amount, from_currency: fromCurrency, to_currency: toCurrency },
  })