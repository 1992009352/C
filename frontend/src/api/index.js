import request from './request'

export const authApi = {
  login: (data) => request.post('/auth/login', data),
  register: (data) => request.post('/auth/register', data),
  getMe: () => request.get('/auth/me'),
  updateMe: (data) => request.put('/auth/me', data),
  changePassword: (data) => request.post('/auth/change-password', data),
}

export const dashboardApi = {
  getStats: () => request.get('/dashboard/stats'),
  getFinanceTrend: (year) => request.get('/dashboard/finance-trend', { params: { year } }),
}

export const financeApi = {
  getCategories: () => request.get('/finance/categories'),
  createCategory: (data) => request.post('/finance/categories', data),
  deleteCategory: (id) => request.delete(`/finance/categories/${id}`),
  getTransactions: (params) => request.get('/finance/transactions', { params }),
  createTransaction: (data) => request.post('/finance/transactions', data),
  updateTransaction: (id, data) => request.put(`/finance/transactions/${id}`, data),
  deleteTransaction: (id) => request.delete(`/finance/transactions/${id}`),
  getSummary: (params) => request.get('/finance/summary', { params }),
  getBudgets: () => request.get('/finance/budgets'),
  createBudget: (data) => request.post('/finance/budgets', data),
}

export const healthApi = {
  getRecords: (params) => request.get('/health/records', { params }),
  createRecord: (data) => request.post('/health/records', data),
  deleteRecord: (id) => request.delete(`/health/records/${id}`),
  getExercises: (params) => request.get('/health/exercises', { params }),
  createExercise: (data) => request.post('/health/exercises', data),
  deleteExercise: (id) => request.delete(`/health/exercises/${id}`),
  getSleepRecords: (params) => request.get('/health/sleep', { params }),
  createSleepRecord: (data) => request.post('/health/sleep', data),
}

export const todoApi = {
  getCategories: () => request.get('/todos/categories'),
  createCategory: (data) => request.post('/todos/categories', data),
  getTodos: (params) => request.get('/todos', { params }),
  createTodo: (data) => request.post('/todos', data),
  updateTodo: (id, data) => request.put(`/todos/${id}`, data),
  deleteTodo: (id) => request.delete(`/todos/${id}`),
}

export const noteApi = {
  getCategories: () => request.get('/notes/categories'),
  createCategory: (data) => request.post('/notes/categories', data),
  getNotes: (params) => request.get('/notes', { params }),
  createNote: (data) => request.post('/notes', data),
  updateNote: (id, data) => request.put(`/notes/${id}`, data),
  deleteNote: (id) => request.delete(`/notes/${id}`),
}

export const habitApi = {
  getHabits: (params) => request.get('/habits', { params }),
  createHabit: (data) => request.post('/habits', data),
  updateHabit: (id, data) => request.put(`/habits/${id}`, data),
  deleteHabit: (id) => request.delete(`/habits/${id}`),
  getRecords: (params) => request.get('/habits/records', { params }),
  createRecord: (data) => request.post('/habits/records', data),
  getCheckinCalendar: (params) => request.get('/habits/checkin-calendar', { params }),
}

export const dietApi = {
  getFoods: (params) => request.get('/diet/foods', { params }),
  createFood: (data) => request.post('/diet/foods', data),
  getRecords: (params) => request.get('/diet/records', { params }),
  createRecord: (data) => request.post('/diet/records', data),
  deleteRecord: (id) => request.delete(`/diet/records/${id}`),
  getDailySummary: (params) => request.get('/diet/daily-summary', { params }),
}

export const readingApi = {
  getBooks: (params) => request.get('/reading/books', { params }),
  createBook: (data) => request.post('/reading/books', data),
  updateBook: (id, data) => request.put(`/reading/books/${id}`, data),
  deleteBook: (id) => request.delete(`/reading/books/${id}`),
  getRecords: (params) => request.get('/reading/records', { params }),
  createRecord: (data) => request.post('/reading/records', data),
}

export const experienceApi = {
  getExperiences: (params) => request.get('/experiences', { params }),
  createExperience: (data) => request.post('/experiences', data),
  updateExperience: (id, data) => request.put(`/experiences/${id}`, data),
  deleteExperience: (id) => request.delete(`/experiences/${id}`),
}

export const contactApi = {
  getGroups: () => request.get('/contacts/groups'),
  createGroup: (data) => request.post('/contacts/groups', data),
  getContacts: (params) => request.get('/contacts', { params }),
  createContact: (data) => request.post('/contacts', data),
  updateContact: (id, data) => request.put(`/contacts/${id}`, data),
  deleteContact: (id) => request.delete(`/contacts/${id}`),
}

export const passwordApi = {
  getGroups: () => request.get('/passwords/groups'),
  createGroup: (data) => request.post('/passwords/groups', data),
  getPasswords: (params) => request.get('/passwords', { params }),
  createPassword: (data) => request.post('/passwords', data),
  updatePassword: (id, data) => request.put(`/passwords/${id}`, data),
  deletePassword: (id) => request.delete(`/passwords/${id}`),
}

export const goalApi = {
  getGoals: (params) => request.get('/goals', { params }),
  createGoal: (data) => request.post('/goals', data),
  updateGoal: (id, data) => request.put(`/goals/${id}`, data),
  deleteGoal: (id) => request.delete(`/goals/${id}`),
  getProgress: (params) => request.get('/goals/progress', { params }),
  createProgress: (data) => request.post('/goals/progress', data),
}
