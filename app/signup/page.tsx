"use client";

import { useEffect, useState } from "react";
import { registerAgency } from "../../lib/signupService";
import { useRouter } from "next/navigation";

export default function SignupPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    email: "",
    password: "",
    name: "",
    phone: "",
    address: "",
    plan: "standard",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  // const storedAgencyId = localStorage.getItem("agencyId");

  const handleSignup = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const data = await registerAgency(form);
      console.log("Agency Registered:", data);
      // localStorage.setItem("agencyId", data.agencyId);

      // const storedAgencyId = localStorage.getItem("agencyId");
      // if (storedAgencyId) {
      //   router.push("/");
      // }
      router.push("/login");
    } catch (err) {
      setError(err.message || "Signup failed");
      console.error("Signup Error:", err);
    } finally {
      setLoading(false);
    }
  };

  // useEffect(() => {
  //   if (storedAgencyId) {
  //     router.push("/");
  //   }
  // }, [storedAgencyId]);

  return (
    <div className="min-h-screen flex items-center justify-center ">
      <div className="bg-white p-8 w-full max-w-md">
        <h2 className="text-2xl font-bold text-center text-gray-800">
          Sign Up
        </h2>
        <p className="text-center text-gray-500 mb-6">
          Create your agency account
        </p>

        <form onSubmit={handleSignup} className="space-y-4">
          <input
            name="name"
            type="text"
            placeholder="Agency Name"
            onChange={handleChange}
            required
            className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
          <input
            name="email"
            type="email"
            placeholder="Email"
            onChange={handleChange}
            required
            className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
          <input
            name="password"
            type="password"
            placeholder="Password"
            onChange={handleChange}
            required
            className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
          <input
            name="phone"
            type="tel"
            placeholder="Phone Number"
            onChange={handleChange}
            required
            className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
          <input
            name="address"
            type="text"
            placeholder="Address"
            onChange={handleChange}
            required
            className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
          <select
            name="plan"
            onChange={handleChange}
            value={form.plan}
            className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            <option value="standard">Standard</option>
            <option value="premium">Premium</option>
          </select>

          <button
            type="submit"
            disabled={loading}
            className="w-full p-3 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 transition disabled:bg-gray-400"
          >
            {loading ? "Creating Agency..." : "Register Agency"}
          </button>

          {error && <p className="text-red-500 text-center">{error}</p>}
        </form>

        <p className="text-center text-gray-600 mt-4">
          Already have an account?{" "}
          <a href="/login" className="text-blue-500 hover:underline">
            Log in
          </a>
        </p>
      </div>
    </div>
  );
}
