import apiClient from './authApi'

export const calculateLoanAnnuity = (data) =>
  apiClient.post('/calculate/loan/annuity', data)

export const calculateLoanDifferentiated = (data) =>
  apiClient.post('/calculate/loan/differentiated', data)

export const calculateDeposit = (data) =>
  apiClient.post('/calculate/deposit', data)

export const calculateInflation = (data) =>
  apiClient.post('/calculate/inflation', data)

export const getCalculationHistory = (params = {}) =>
  apiClient.get('/calculate/history', { params })

export const deleteCalculation = (id) =>
  apiClient.delete(`/calculate/history/${id}`)