import axios from 'axios';


const api = axios.create({
    baseURL: process.env.REACT_APP_API_URL//apiUrl'http://192.168.0.163:8082/'process.env.BACKEND_API_URL
    // baseURL: 'http://backend:8082/'
    // baseURL: 'http://localhost:8082/'
})

export default api;