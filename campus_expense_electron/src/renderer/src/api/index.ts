import axios from 'axios'

const API_BASE = 'http://127.0.0.1:8000/api'

export interface Expense {
  id: number
  amount: number
  category: string
  description: string
  date: string
  created_at: string
}

export interface Category {
  id: number
  name: string
  icon: string
  is_default: boolean
}

export interface BudgetData {
  monthly_budget: number | null
  spent: number
  remaining: number
  percentage: number
}

export interface CategoryStat {
  category: string
  total: number
}

export interface MonthlyStats {
  year: number
  month: number
  total: number
  categories: CategoryStat[]
}

export interface BackupData {
  version: string
  exported_at?: string
  expenses: Expense[]
  categories: Category[]
  budget: number | null
}

export const api = {
  getExpenses(
    year?: number,
    month?: number,
    filters?: {
      keyword?: string
      category?: string
      date_from?: string
      date_to?: string
      min_amount?: number
      max_amount?: number
    }
  ) {
    return axios.get<Expense[]>(`${API_BASE}/expenses`, {
      params: { year, month, ...filters }
    })
  },

  createExpense(data: { amount: number; category: string; description: string; date: string }) {
    return axios.post<Expense>(`${API_BASE}/expenses`, data)
  },

  updateExpense(
    id: number,
    data: { amount: number; category: string; description: string; date: string }
  ) {
    return axios.put<Expense>(`${API_BASE}/expenses/${id}`, data)
  },

  deleteExpense(id: number) {
    return axios.delete(`${API_BASE}/expenses/${id}`)
  },

  getCategories() {
    return axios.get<Category[]>(`${API_BASE}/categories`)
  },

  createCategory(data: { name: string; icon: string }) {
    return axios.post<Category>(`${API_BASE}/categories`, data)
  },

  deleteCategory(id: number) {
    return axios.delete(`${API_BASE}/categories/${id}`)
  },

  getStatistics(year: number, month: number) {
    return axios.get<MonthlyStats>(`${API_BASE}/statistics/${year}/${month}`)
  },

  getBudget() {
    return axios.get<BudgetData>(`${API_BASE}/budget`)
  },

  setBudget(amount: number) {
    return axios.put(`${API_BASE}/budget`, { amount })
  },

  exportCSV() {
    return axios.get(`${API_BASE}/export`, { responseType: 'blob' })
  },

  getBackup() {
    return axios.get<BackupData>(`${API_BASE}/backup`)
  },

  restoreBackup(payload: unknown) {
    return axios.post<{ message: string }>(`${API_BASE}/restore`, payload)
  }
}
