import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../utils/axios";

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
  });

  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      await api.post("/auth/register", form);
      navigate("/");
    } catch (error) {
      console.log(error);

      alert(
        error.response?.data?.detail || error.message || "Registration Failed",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center h-screen bg-gray-100">
      <div className="bg-white p-8 rounded-xl shadow-xl w-96">
        <h2 className="text-3xl font-bold mb-6 text-center">Register</h2>

        <form onSubmit={handleSubmit}>
          <input
            className="border p-3 rounded w-full mb-4"
            placeholder="Username"
            name="username"
            onChange={handleChange}
          />

          <input
            className="border p-3 rounded w-full mb-4"
            placeholder="Email"
            name="email"
            onChange={handleChange}
          />

          <input
            type="password"
            className="border p-3 rounded w-full mb-6"
            placeholder="Password"
            name="password"
            onChange={handleChange}
          />

          <button className="bg-green-600 text-white w-full p-3 rounded hover:bg-green-700">
            {loading ? "Registering..." : "Register"}
          </button>
        </form>

        <p className="text-center mt-4">
          Already have an account?
          <Link to="/" className="text-blue-600 ml-2">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
}
