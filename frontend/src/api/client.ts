import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

client.interceptors.response.use(
  (res) => res,
  (err) => {
    const detail = err.response?.data?.detail
    return Promise.reject(new Error(detail ?? err.message))
  }
)

export default client
