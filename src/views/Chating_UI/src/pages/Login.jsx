// import React, { useState } from "react";

// const Login = ()=>{
//     const [state, setState] = useState("login");
//     const [name, setName] = useState("");
//     const [email, setEmail] = useState("");
//     const [password, setPassword] = useState("");

//     const handleSubmit = async(e)=>{
//         e.preventDefault();
//     }
//     return(

//         <form onSubmit={handleSubmit} className="flex flex-col gap-4 m-auto items-start p-8 py-12 w-80 sm:w-[352px] text-gray-500 rounded-lg shadow-xl border border-gray-200 bg-white">
//             <p className="text-2xl font-medium m-auto">
//                 <span className="text-purple-700">User</span> {state === "login" ? "Login" : "Sign Up"}
//             </p>
//             {state === "register" && (
//                 <div className="w-full">
//                     <p>Name</p>
//                     <input onChange={(e) => setName(e.target.value)} value={name} placeholder="type here" className="border border-gray-200 rounded w-full p-2 mt-1 outline-purple-700" type="text" required />
//                 </div>
//             )}
//             <div className="w-full ">
//                 <p>Email</p>
//                 <input onChange={(e) => setEmail(e.target.value)} value={email} placeholder="type here" className="border border-gray-200 rounded w-full p-2 mt-1 outline-purple-700" type="email" required />
//             </div>
//             <div className="w-full ">
//                 <p>Password</p>
//                 <input onChange={(e) => setPassword(e.target.value)} value={password} placeholder="type here" className="border border-gray-200 rounded w-full p-2 mt-1 outline-purple-700" type="password" required />
//             </div>
//             {state === "register" ? (
//                 <p>
//                     Already have account? <span onClick={() => setState("login")} className="text-purple-700 cursor-pointer">click here</span>
//                 </p>
//             ) : (
//                 <p>
//                     Create an account? <span onClick={() => setState("register")} className="text-purple-700 cursor-pointer">click here</span>
//                 </p>
//             )}
//             <button type="submit" className="bg-purple-700 hover:bg-purple-800 transition-all text-white w-full py-2 rounded-md cursor-pointer">
//                 {state === "register" ? "Create Account" : "Login"}
//             </button>
//         </form>

//     );
// }
// export  default Login


// import React, { useState, useEffect } from "react";
// import { useAppContext } from "../context/AppContext";
// import axios from "axios";
// import { toast } from "react-toastify";

// const Login = () => {
//   const [state, setState] = useState("login");
//   const [name, setName] = useState("");
//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");

//   const { backendUrl, setToken, token, navigate } = useAppContext();

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     try {
//       const endpoint = state === "register" ? "/api/user/register" : "/api/user/login";
//       const payload = state === "register" ? { name, email, password } : { email, password };

//       const { data } = await axios.post(`${backendUrl}${endpoint}`, payload);

//       if (data.success) {
//         setToken(data.token);
//         localStorage.setItem("token", data.token);
//         toast.success(state === "register" ? "Account Created!" : "Welcome Back!");
//       } else {
//         toast.error(data.message);
//       }
//     } catch (error) {
//       toast.error(error.response?.data?.message || "Connection Error");
//     }
//   };

//   return (
//     <form onSubmit={handleSubmit} className="flex flex-col gap-4 m-auto items-start p-8 py-10 w-80 sm:w-[352px] text-gray-500 rounded-3xl shadow-2xl border border-gray-200 dark:border-white/5 bg-white dark:bg-[#1e1e1e] animate-in zoom-in duration-300">
//       <p className="text-2xl font-black m-auto">
//         <span className="text-[#1A9BB3]">User</span> {state === "login" ? "Login" : "Sign Up"}
//       </p>

//       {state === "register" && (
//         <div className="w-full">
//           <p className="text-xs mb-1">Name</p>
//           <input onChange={(e) => setName(e.target.value)} value={name} className="border dark:border-white/10 dark:bg-[#252525] rounded-xl w-full p-2.5 outline-[#1A9BB3]" type="text" required />
//         </div>
//       )}

//       <div className="w-full">
//         <p className="text-xs mb-1">Email</p>
//         <input onChange={(e) => setEmail(e.target.value)} value={email} className="border dark:border-white/10 dark:bg-[#252525] rounded-xl w-full p-2.5 outline-[#1A9BB3]" type="email" required />
//       </div>

//       <div className="w-full">
//         <p className="text-xs mb-1">Password</p>
//         <input onChange={(e) => setPassword(e.target.value)} value={password} className="border dark:border-white/10 dark:bg-[#252525] rounded-xl w-full p-2.5 outline-[#1A9BB3]" type="password" required />
//       </div>

//       <button type="submit" className="bg-[#1A9BB3] hover:opacity-90 text-white w-full py-3 rounded-xl font-bold mt-2 transition-all active:scale-95 shadow-lg">
//         {state === "register" ? "Create Account" : "Login"}
//       </button>

//       <p className="text-xs m-auto">
//         {state === "register" ? "Already have account?" : "New to UniAsk?"} 
//         <span onClick={() => setState(state === 'login' ? 'register' : 'login')} className="text-[#1A9BB3] cursor-pointer font-bold ml-1">Click here</span>
//       </p>
//     </form>
//   );
// }

// export default Login;




import React, { useState } from "react";
import { useAppContext } from "../context/AppContext";
import axios from "axios";
import { toast } from "react-toastify";

const Login = ({ setShowAuthOverlay }) => {
  const [state, setState] = useState("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const { backendUrl, setToken, theme } = useAppContext();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const projectId = 0;
      const endpoint = state === "register" ? `/api/v1/user/register/${projectId}` : `/api/v1/user/login/${projectId}`;
      const payload = state === "register" ? { name, email, password } : { email, password };

      const { data } = await axios.post(`${backendUrl}${endpoint}`, payload);

      if (data.user_id) {
        setToken(data.user_id);
        localStorage.setItem("token", data.user_id);
        toast.success(state === "register" ? "Account Created!" : "Welcome Back!");
        if (setShowAuthOverlay) setShowAuthOverlay(false);
      } else {
        toast.error(data.signal || "Authentication failed");
      }
    } catch (error) {
      toast.error(error.response?.data?.signal || "Connection Error");
    }
  };

  return (
    <form onSubmit={handleSubmit} className={`flex flex-col gap-4 m-auto items-start p-8 py-10 w-80 sm:w-[352px] rounded-3xl shadow-2xl border transition-colors animate-in zoom-in duration-300
      ${theme === 'dark' ? 'bg-[#1e1e1e] border-white/5 text-gray-400' : 'bg-white border-gray-200 text-gray-600'}`}>
      <p className={`text-2xl font-black m-auto ${theme === 'dark' ? 'text-white' : 'text-gray-800'}`}>
        <span className="text-[#1A9BB3]">User</span> {state === "login" ? "Login" : "Sign Up"}
      </p>

      {state === "register" && (
        <div className="w-full">
          <p className="text-xs mb-1 font-medium">Name</p>
          <input onChange={(e) => setName(e.target.value)} value={name} type="text" required 
            className={`border rounded-xl w-full p-2.5 outline-[#1A9BB3] transition-colors
              ${theme === 'dark' ? 'border-white/10 bg-[#252525] text-white' : 'border-gray-200 bg-gray-50 text-gray-900'}`} />
        </div>
      )}

      <div className="w-full">
        <p className="text-xs mb-1 font-medium">Email</p>
        <input onChange={(e) => setEmail(e.target.value)} value={email} type="email" required 
          className={`border rounded-xl w-full p-2.5 outline-[#1A9BB3] transition-colors
              ${theme === 'dark' ? 'border-white/10 bg-[#252525] text-white' : 'border-gray-200 bg-gray-50 text-gray-900'}`} />
      </div>

      <div className="w-full">
        <p className="text-xs mb-1 font-medium">Password</p>
        <input onChange={(e) => setPassword(e.target.value)} value={password} type="password" required 
          className={`border rounded-xl w-full p-2.5 outline-[#1A9BB3] transition-colors
              ${theme === 'dark' ? 'border-white/10 bg-[#252525] text-white' : 'border-gray-200 bg-gray-50 text-gray-900'}`} />
      </div>

      <button type="submit" className="bg-[#1A9BB3] hover:opacity-90 text-white w-full py-3 rounded-xl font-bold mt-2 transition-all active:scale-95 shadow-lg">
        {state === "register" ? "Create Account" : "Login"}
      </button>

      <p className="text-xs m-auto mt-1">
        {state === "register" ? "Already have account?" : "New to UniAsk?"}
        <span onClick={() => setState(state === 'login' ? 'register' : 'login')} className="text-[#1A9BB3] cursor-pointer font-bold ml-1 hover:underline">Click here</span>
      </p>
    </form>
  );
}

export default Login;