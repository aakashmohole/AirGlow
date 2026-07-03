import { Router, Route } from "react-router-dom";

function App() {
  return (
    <Router>
      <Route path="/" element={<Login />} />

      <Route path="/register" element={<Register />} />

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
    </Router>
  );
}

export default App;
