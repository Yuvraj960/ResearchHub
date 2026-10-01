import { io } from 'socket.io-client'

// In dev: connect to same origin — Vite proxies /socket.io → Flask backend.
// In prod: set VITE_SOCKET_URL to the backend URL.
const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || window.location.origin

let socket = null

export function connectSocket(userId) {
  if (socket?.connected) {
    // Already connected — just (re)join the user room
    socket.emit('join_user_room', { user_id: userId })
    return socket
  }

  socket = io(SOCKET_URL, {
    // Allow polling→WebSocket upgrade (don't force WebSocket-only)
    transports: ['polling', 'websocket'],
    path: '/socket.io',
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 2000,
  })

  socket.on('connect', () => {
    console.log('[Socket] Connected:', socket.id)
    socket.emit('join_user_room', { user_id: userId })
  })

  socket.on('disconnect', (reason) => {
    console.log('[Socket] Disconnected:', reason)
  })

  socket.on('connect_error', (err) => {
    console.warn('[Socket] Connection error:', err.message)
  })

  return socket
}

export function disconnectSocket() {
  if (socket) {
    socket.disconnect()
    socket = null
  }
}

export function getSocket() {
  return socket
}
