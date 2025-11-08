import { useState } from 'react'
import './App.css'
import DeleteParticipantsDemo from "./DeleteParticipantsDemo";

function App() {
  const [count, setCount] = useState(0)

  const apiBase = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";

  return (
    <>
      <DeleteParticipantsDemo
        adminCode="u1"
        apiBase={apiBase}
        roomId="r1"
      />
    </>
  )
}

export default App